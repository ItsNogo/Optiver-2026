"""extract_bot_data.py - pull historical orders, trades and order books for all stocks and
fingerprint the bots that are trading (organizer walls, takers, small quoters, other teams).

Run in the Optibook environment as a plain script:

    python extract_bot_data.py          # last 4 hours
    python extract_bot_data.py 12       # last 12 hours
    python extract_bot_data.py all      # everything since the exchange started (slow, needs several GB of RAM)

It uses only the HistoricalDataLoader (HTTP). It never creates Exchange(), so by design it should
not kick a running bot. Outputs go to ./bot_data/:

    summary.txt        text report - paste this back for analysis
    orders_life.pkl.gz one row per order: size, side, price, lifetime, how it ended, where it sat
    orders_raw.pkl.gz  every order event (new / fill / cancelled)
    books.pkl.gz       one row per book snapshot: best prices, wall prices and sizes, inside volume
    trades.pkl.gz      every public trade
    aggr.pkl.gz        one row per aggressive order (trades sharing a timestamp), with markouts

UNTESTED against the live exchange. Assumption used throughout: in the orders feed, `volume` is the
REMAINING volume of the order after the event (0 on the cancelled / fully filled rows seen so far).
"""
import json
import os
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
from optibook.historical_data_loader import HistoricalDataLoader

HOURS_BACK = 4.0            # default look-back; override on the command line
OUT = "bot_data"
TICK = 0.1
WALL_MIN = 1000             # a book level with at least this many lots is an organizer "wall"
BURST_NS = 5_000_000        # new orders less than 5 ms apart in one stock = one burst (one bot action)
EXCHANGE_START = datetime(2026, 11, 11, 12, 28)      # naive UTC, from the exchange_started_at column
SIZE_BINS = [0, 1, 4, 9, 19, 49, 199, 999, 1999, 2999, 10**9]
SIZE_LABELS = ["1", "2-4", "5-9", "10-19", "20-49", "50-199", "200-999", "1000-1999", "2000-2999", "3000+"]

pd.set_option("display.width", 220, "display.max_columns", 40, "display.max_rows", 300,
              "display.float_format", lambda v: f"{v:.3f}")
os.makedirs(OUT, exist_ok=True)
_report = []


def P(*parts):
    """Print and keep for summary.txt."""
    line = " ".join(str(p) for p in parts)
    print(line, flush=True)
    _report.append(line)


def section(title, fn, *args):
    """Run one analysis; a failure must not stop the others."""
    P("\n" + "=" * 100 + "\n" + title + "\n" + "=" * 100)
    try:
        return fn(*args)
    except Exception:
        P("SECTION FAILED:\n" + traceback.format_exc())
        return None


def naive_utc(d):
    return d.astimezone(timezone.utc).replace(tzinfo=None) if d.tzinfo else d


def hours(start, end):
    t = start
    while t < end:
        yield t, min(t + timedelta(hours=1), end)
        t += timedelta(hours=1)


def download(loader, start, end):
    """One download for the whole range. Files are cached, so a retry resumes where it stopped."""
    for attempt in range(8):
        try:
            return loader.download_all(start, end)
        except ValueError as e:                    # 429 rate limit: the message names the wait
            print(f"download attempt {attempt + 1} refused: {e} -> sleeping 65 s", flush=True)
            time.sleep(65)
    raise SystemExit("download kept failing; try again in a few minutes or use a shorter range")


def load(fn, start, end, name, transform=None):
    """Load from the local cache hour by hour (the loader caps a load at 1 day)."""
    parts = []
    for s, e in hours(start, end):
        try:
            df = fn(s, e)
        except Exception as ex:
            print(f"  {name}: load {s:%H:%M} failed: {ex!r}", flush=True)
            continue
        print(f"  {name}: {s:%m-%d %H:%M} {0 if df is None else len(df)} rows", flush=True)
        if df is not None and len(df):
            df = df.drop(columns=[c for c in ("timestamp_str",) if c in df.columns])
            if "exchange_started_at" in df.columns:
                df["exchange_started_at"] = df["exchange_started_at"].astype("category")
            parts.append(transform(df) if transform else df)       # books are reduced per hour to save memory
    if not parts:
        raise SystemExit(f"no {name} data in the range - is the range before the exchange start?")
    df = pd.concat(parts, ignore_index=True)
    df["timestamp_ns"] = df["timestamp_ns"].astype("int64")
    return df


def to_ticks(series):
    return (series / TICK).round()


def size_bucket(vol):
    return pd.cut(vol, SIZE_BINS, labels=SIZE_LABELS).astype(str)


def quantiles(s, qs=(0.05, 0.25, 0.5, 0.75, 0.95)):
    s = pd.Series(s).dropna()
    return "n=%d " % len(s) + " ".join(f"p{int(q * 100)}={s.quantile(q):.3f}" for q in qs) if len(s) else "n=0"


# ----------------------------------------------------------------------------- feature building
def book_features(pb):
    """Book snapshots -> best prices, first wall level on each side, volume resting inside the walls."""
    rows, nan = [], np.nan
    for ts, iid, bj, aj in zip(pb.timestamp_ns.values, pb.instrument_id.values, pb.bids_json.values, pb.asks_json.values):
        b = json.loads(bj) if isinstance(bj, str) else list(bj)
        a = json.loads(aj) if isinstance(aj, str) else list(aj)
        wb = next(((p, v) for p, v in b if v >= WALL_MIN), (nan, nan))
        wa = next(((p, v) for p, v in a if v >= WALL_MIN), (nan, nan))
        rows.append((ts, iid, b[0][0] if b else nan, a[0][0] if a else nan, wb[0], wb[1], wa[0], wa[1],
                     sum(v for p, v in b if p > wb[0]) if wb[0] == wb[0] else nan,
                     sum(v for p, v in a if p < wa[0]) if wa[0] == wa[0] else nan, len(b), len(a)))
    F = pd.DataFrame(rows, columns=["timestamp_ns", "instrument_id", "bid", "ask", "wall_bid", "wall_bid_vol",
                                    "wall_ask", "wall_ask_vol", "in_bid_vol", "in_ask_vol", "n_bid_levels", "n_ask_levels"])
    for c in ("bid", "ask", "wall_bid", "wall_ask"):
        F[c + "_t"] = to_ticks(F[c])
    F["wall_mid"] = (F.wall_bid + F.wall_ask) / 2
    F["wall_mid_t"] = (F.wall_bid_t + F.wall_ask_t) / 2
    F["wall_spread_t"] = F.wall_ask_t - F.wall_bid_t
    F["spread_t"] = F.ask_t - F.bid_t
    return F


def book_before(df, F, on):
    """Attach the last book snapshot strictly before each row (same instrument)."""
    cols = ["timestamp_ns", "instrument_id", "bid_t", "ask_t", "wall_bid_t", "wall_ask_t", "wall_mid_t", "wall_mid"]
    left = df.sort_values(on, kind="stable")
    return pd.merge_asof(left, F[cols].rename(columns={"timestamp_ns": "book_ns"}), left_on=on, right_on="book_ns",
                         by="instrument_id", allow_exact_matches=False)


def order_life(O, F):
    """One row per order: what it was, where it sat relative to the walls, how long it lived, how it ended."""
    O = O.sort_values("timestamp_ns", kind="stable")
    O = O.assign(is_fill=O.action.eq("fill"), live_vol=O.volume.where(O.action.ne("cancelled")))
    agg = dict(t0=("timestamp_ns", "first"), t1=("timestamp_ns", "last"), side=("side", "first"),
               price=("price", "first"), vol0=("volume", "first"), vol_last=("volume", "last"),
               first_action=("action", "first"), last_action=("action", "last"), n_events=("action", "size"),
               n_fills=("is_fill", "sum"), live_vol_min=("live_vol", "min"))
    for c in ("order_type", "username"):
        if c in O.columns:
            agg[c] = (c, "first")
    L = O.groupby(["instrument_id", "order_id"], sort=False).agg(**agg).reset_index()
    L["born_in_window"] = L.first_action.eq("new")
    L["ended"] = L.vol_last.eq(0)
    L["life_s"] = np.where(L.ended, (L.t1 - L.t0) / 1e9, np.nan)
    L["filled_vol"] = (L.vol0 - L.live_vol_min.fillna(L.vol0)).clip(lower=0)
    L["end"] = np.select([~L.ended, L.last_action.eq("cancelled") & L.filled_vol.eq(0),
                          L.last_action.eq("cancelled"), L.last_action.eq("fill")],
                         ["open", "cancelled", "part_fill_then_cancel", "filled"], default="other")
    # A wall-sized order defines the wall, so judge it against the book just after its burst;
    # every other order is judged against the book just before it arrived.
    L["t_ref"] = np.where(L.vol0 >= WALL_MIN, L.t0 + BURST_NS, L.t0)
    L = book_before(L, F, "t_ref")
    s = np.where(L.side.eq("bid"), 1, -1)
    px = to_ticks(L.price)
    own_wall = np.where(L.side.eq("bid"), L.wall_bid_t, L.wall_ask_t)
    opp_best = np.where(L.side.eq("bid"), L.ask_t, L.bid_t)
    better = s * (px - own_wall)                       # > 0: priced inside the walls
    L["px_t"] = px
    L["depth_t"] = s * (L.wall_mid_t - px)             # ticks from the wall mid; negative = through the mid
    L["zone"] = np.select([np.isnan(own_wall), s * (px - opp_best) >= 0, better > 0, better == 0, better >= -2, better >= -20],
                          ["no_wall", "marketable", "inside", "at_wall", "wall_ladder", "deep"], default="far")
    L["size"] = size_bucket(L.vol0)
    return L.sort_values("t0", kind="stable").reset_index(drop=True)


def aggressive_orders(T, F, horizons=(1, 5, 30)):
    """Trades sharing instrument, timestamp and aggressor side = one aggressive order. Adds markouts."""
    A = (T.assign(pv=T.price * T.volume).groupby(["instrument_id", "timestamp_ns", "aggressor_side"], sort=False)
           .agg(vol=("volume", "sum"), pv=("pv", "sum"), n_fills=("volume", "size")).reset_index())
    A["px"] = A.pv / A.vol
    A = book_before(A, F, "timestamp_ns").reset_index(drop=True)
    sign = np.where(A.aggressor_side.eq("bid"), 1, -1)
    px_t = A.px / TICK
    A["paid_t"] = sign * (px_t - A.wall_mid_t)         # ticks the taker paid versus the wall mid
    hit_wall = np.where(sign > 0, px_t >= A.wall_ask_t - 1e-6, px_t <= A.wall_bid_t + 1e-6)
    A["where"] = np.where(A.wall_mid_t.isna(), "no_wall", np.where(hit_wall, "at_wall", "inside"))
    later_cols = F[["timestamp_ns", "instrument_id", "wall_mid_t"]].dropna()
    for h in horizons:
        probe = A[["timestamp_ns", "instrument_id"]].assign(timestamp_ns=A.timestamp_ns + int(h * 1e9))
        later = pd.merge_asof(probe, later_cols, on="timestamp_ns", by="instrument_id")
        A[f"mid_move_{h}s_t"] = sign * (later.wall_mid_t.values - A.wall_mid_t.values)   # > 0: mid followed the taker
    A["size"] = size_bucket(A.vol)
    return A


def bars(F, freq):
    """Wall mid (in ticks) per instrument on a regular time grid."""
    return (F.dropna(subset=["wall_mid_t"]).set_index("ts").groupby("instrument_id").wall_mid_t
             .resample(freq).last().unstack(0).ffill())


# ----------------------------------------------------------------------------- report sections
def rep_overview(O, T, F, L, start, end):
    P(f"range (UTC): {start} -> {end}   orders rows {len(O)}  orders {len(L)}  trades {len(T)}  book snapshots {len(F)}")
    for name, df in (("orders", O), ("trades", T)):
        if "exchange_started_at" in df.columns:
            P(f"{name}.exchange_started_at values: {df.exchange_started_at.astype(str).unique().tolist()[:5]}")
    P("order actions:", O.action.value_counts().to_dict())
    if "order_type" in O.columns:
        P("order types:", O.order_type.value_counts().to_dict())
    P("order action x order type:\n" + pd.crosstab(O.action, O.get("order_type", pd.Series("?", index=O.index))).to_string())
    P("volume on rows by action (checks the 'volume = remaining' assumption):\n"
      + O.groupby("action").volume.describe()[["count", "min", "50%", "max"]].to_string())
    named = O.get("username", pd.Series("", index=O.index)).fillna("").astype(str).str.len().gt(0).mean()
    P(f"share of order rows with a username: {named:.3f}  (0 = counterparty data hidden)")
    per = pd.DataFrame({
        "new_orders": L[L.born_in_window].groupby("instrument_id").size(),
        "trades": T.groupby("instrument_id").size(), "traded_lots": T.groupby("instrument_id").volume.sum(),
        "wall_spread_med": F.groupby("instrument_id").wall_spread_t.median(),
        "no_wall_share": F.groupby("instrument_id").wall_mid_t.apply(lambda s: s.isna().mean()),
        "in_bid_vol": F.groupby("instrument_id").in_bid_vol.mean(), "in_ask_vol": F.groupby("instrument_id").in_ask_vol.mean(),
        "mid_first": F.groupby("instrument_id").wall_mid.first(), "mid_last": F.groupby("instrument_id").wall_mid.last()})
    P("per instrument:\n" + per.to_string())


def rep_order_sizes(L):
    N = L[L.born_in_window]
    P("most common exact order sizes (lots: count):", N.vol0.value_counts().head(25).to_dict())
    P("\norders by size bucket x zone at insertion (count):\n" + pd.crosstab(N["size"], N.zone).reindex(SIZE_LABELS).dropna(how="all").to_string())
    g = N.groupby(["size", "zone"])
    tab = pd.DataFrame({"n": g.size(), "bid_share": g.side.apply(lambda s: s.eq("bid").mean()),
                        "cancelled": g.end.apply(lambda s: s.eq("cancelled").mean()),
                        "any_fill": g.filled_vol.apply(lambda s: s.gt(0).mean()),
                        "life_p10": g.life_s.quantile(0.1), "life_med": g.life_s.median(), "life_p90": g.life_s.quantile(0.9),
                        "depth_med_t": g.depth_t.median(), "events_med": g.n_events.median()})
    tab = tab[tab.n >= max(20, 0.002 * len(N))].sort_values("n", ascending=False)
    P("\nfingerprint per (size bucket, zone) - each row is a candidate bot behaviour:\n" + tab.to_string())
    if "order_type" in N.columns:
        P("\nzone x order type:\n" + pd.crosstab(N.zone, N.order_type).to_string())


def rep_bursts(L):
    """New orders that arrive together are one bot action; the pattern of sizes and prices identifies the bot."""
    N = L[L.born_in_window].sort_values(["instrument_id", "t0"], kind="stable")
    new_burst = (N.t0.diff() > BURST_NS) | (N.instrument_id != N.instrument_id.shift())
    N = N.assign(burst=new_burst.cumsum(),
                 tag=N.side.str[0] + N.vol0.astype(int).astype(str) + "@" + N.depth_t.map(lambda d: "?" if d != d else f"{d:+.1f}"))
    B = N.groupby("burst").agg(instrument_id=("instrument_id", "first"), t=("t0", "first"), n=("tag", "size"),
                               sig=("tag", lambda s: " ".join(sorted(s)) if len(s) <= 8 else f"<{len(s)} orders>"))
    P("orders per burst (count of bursts):", B.n.value_counts().sort_index().head(12).to_dict())
    P("tag format: side(b/a) size @ ticks from the wall mid (positive = passive side of the mid)")
    top = B.sig.value_counts().head(30)
    rows = []
    for sig, cnt in top.items():
        gaps = B[B.sig == sig].sort_values("t").groupby("instrument_id").t.diff().dropna() / 1e9
        rows.append((cnt, round(gaps.median(), 3) if len(gaps) else np.nan, round(gaps.quantile(0.1), 3) if len(gaps) else np.nan, sig))
    P("top burst signatures:\n" + pd.DataFrame(rows, columns=["count", "gap_med_s", "gap_p10_s", "signature"]).to_string())
    return B


def rep_walls(L, F):
    big = L[L.born_in_window & (L.vol0 >= WALL_MIN)]
    P("wall-sized orders: exact sizes", big.vol0.value_counts().head(8).to_dict(), " ends:", big.end.value_counts().to_dict())
    P("wall order lifetime s:", quantiles(big.life_s))
    gaps = big.sort_values("t0").groupby(["instrument_id", "side"]).t0.diff() / 1e9
    P("gap between consecutive wall orders (same stock and side) s:", quantiles(gaps))
    P("most common gaps rounded to 0.1 s:", gaps.round(1).value_counts().head(8).to_dict())
    P("wall spread in ticks (share of snapshots):", F.wall_spread_t.value_counts(normalize=True).head(8).round(3).to_dict())
    P("wall level size (share):", pd.concat([F.wall_bid_vol, F.wall_ask_vol]).round(-2).value_counts(normalize=True).head(8).round(3).to_dict())
    for freq in ("1s", "5s", "30s"):
        r = bars(F, freq).diff().dropna(how="all")
        steps = r.stack()
        P(f"wall-mid change per {freq} (ticks): std {steps.std():.3f}  share non-zero {(steps != 0).mean():.3f}  "
          f"lag-1 autocorr (mean over stocks) {r.apply(lambda s: s.autocorr(1)).mean():.3f}")
    one = bars(F, "1s").diff().stack()
    P("size of non-zero 1 s wall-mid moves in ticks (share):", one[one != 0].round(1).value_counts(normalize=True).sort_index().round(3).to_dict())
    r5 = bars(F, "5s").diff().dropna()
    P("5 s wall-mid return correlation between stocks:\n" + r5.corr().round(2).to_string())
    lead = pd.DataFrame({f"lead_{k * 5}s": pd.concat([r5.shift(k).corrwith(r5[c]).drop(c) for c in r5.columns]).groupby(level=0).mean()
                         for k in (1, 2, 6)})
    P("does a stock's move predict the OTHER stocks' later moves (mean corr of its move with the others k s later):\n" + lead.round(3).to_string())


def rep_takers(A):
    P("aggressive orders:", len(A), " buy share:", round(A.aggressor_side.eq("bid").mean(), 3),
      " hit:", A["where"].value_counts(normalize=True).round(3).to_dict())
    P("most common aggressive order sizes:", A.vol.value_counts().head(15).to_dict())
    P("resting orders hit per aggressive order:", A.n_fills.value_counts().sort_index().head(8).to_dict())
    gaps = A.sort_values("timestamp_ns").groupby("instrument_id").timestamp_ns.diff() / 1e9
    P("gap between aggressive orders in one stock s:", quantiles(gaps), f" cv={gaps.std() / gaps.mean():.2f} (1 = random, <<1 = timer)")
    P("most common gaps rounded to 0.1 s:", gaps.round(1).value_counts().head(8).to_dict())
    same = A.assign(b=A.timestamp_ns // 10_000_000).groupby("b").instrument_id.nunique()
    P("stocks hit within the same 10 ms (share of moments):", same.value_counts(normalize=True).sort_index().round(3).to_dict())
    cols = ["paid_t"] + [c for c in A.columns if c.startswith("mid_move_")]
    P("\nmarkout by taker size (ticks; paid_t = paid vs wall mid; mid_move > 0 = informed, maker keeps paid - mid_move):\n"
      + A.groupby("size")[cols].mean().join(A.groupby("size").size().rename("n")).reindex(SIZE_LABELS).dropna(how="all").to_string())
    P("\nmarkout by where it traded:\n" + A.groupby("where")[cols].mean().join(A.groupby("where").size().rename("n")).to_string())
    P("\nmarkout by stock:\n" + A.groupby("instrument_id")[cols].mean().join(A.groupby("instrument_id").size().rename("n")).to_string())


def rep_timeline(L, A, start, end):
    freq = "10min" if (end - start) <= timedelta(hours=8) else "30min"
    N = L[L.born_in_window]
    t = pd.to_datetime(N.t0, unit="ns", utc=True).dt.floor(freq)
    tab = pd.crosstab(t, N["size"]).reindex(columns=[c for c in SIZE_LABELS if c in set(N["size"])])
    tab["inside_orders"] = N.zone.eq("inside").groupby(t).sum()
    tab["aggr_orders"] = pd.to_datetime(A.timestamp_ns, unit="ns", utc=True).dt.floor(freq).value_counts()
    P(f"new orders per {freq} by size bucket (a jump in small sizes = teams switching bots on):\n" + tab.to_string())


def rep_names(L, T):
    if "username" not in L.columns or not L.username.fillna("").astype(str).str.len().gt(0).any():
        P("no usernames in this data (counterparty window closed). Nothing to report.")
        return
    g = L[L.born_in_window].groupby("username")
    tab = pd.DataFrame({"orders": g.size(), "stocks": g.instrument_id.nunique(), "size_med": g.vol0.median(),
                        "life_med_s": g.life_s.median(), "cancelled": g.end.apply(lambda s: s.eq("cancelled").mean()),
                        "any_fill": g.filled_vol.apply(lambda s: s.gt(0).mean()),
                        "inside": g.zone.apply(lambda s: s.eq("inside").mean()),
                        "marketable": g.zone.apply(lambda s: s.eq("marketable").mean()), "depth_med_t": g.depth_t.median()})
    if {"buyer", "seller"} <= set(T.columns):
        aggr = np.where(T.aggressor_side.eq("bid"), T.buyer, T.seller)
        pasv = np.where(T.aggressor_side.eq("bid"), T.seller, T.buyer)
        cash = T.assign(v=T.price * T.volume)
        tr = pd.DataFrame({"taker_lots": T.groupby(aggr).volume.sum(), "maker_lots": T.groupby(pasv).volume.sum(),
                           "net_cash": cash.groupby("seller").v.sum().sub(cash.groupby("buyer").v.sum(), fill_value=0),
                           "net_lots": T.groupby("buyer").volume.sum().sub(T.groupby("seller").volume.sum(), fill_value=0)})
        tab = tab.join(tr, how="outer")                      # keeps names that only ever trade (pure takers)
    tab = tab.sort_values("orders", ascending=False, na_position="last").head(80)
    P("per username (net_cash + net_lots x price = PnL over the window):\n" + tab.to_string())


# ----------------------------------------------------------------------------- main
def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    end = datetime.utcnow() - timedelta(minutes=3)           # the newest minutes are not published yet
    try:
        start = EXCHANGE_START if arg.lower() == "all" else end - timedelta(hours=float(arg))
    except ValueError:
        start = end - timedelta(hours=HOURS_BACK)
    start = max(start, EXCHANGE_START)
    loader = HistoricalDataLoader()
    try:
        window = loader.get_counterparty_data_window()
    except Exception as ex:
        window = None
        P("could not read the counterparty window:", repr(ex))
    P("counterparty data window:", window)
    if window:                                               # names are only served for requests entirely inside it
        w0, w1 = naive_utc(window[0]), naive_utc(window[1])
        ws, we = max(w0, min(start, w1 - timedelta(hours=1))), min(w1, end)
        if ws < we:
            start, end = ws, we
            loader = HistoricalDataLoader(data_dir=os.path.join(OUT, "named_cache"))   # fresh cache: old files are anonymized
            P(f"window is open -> using {start} .. {end} with a separate cache so usernames are included")
    P(f"downloading {start} -> {end} UTC (cached files are skipped)")
    t0 = time.time()
    download(loader, start, end)
    P(f"download done in {time.time() - t0:.0f} s; loading from cache")
    O = load(loader.load_orders_df, start, end, "orders").drop_duplicates()
    T = load(loader.load_trades_df, start, end, "trades").drop_duplicates(["instrument_id", "trade_id"])
    T = T.sort_values("timestamp_ns", kind="stable").reset_index(drop=True)
    F = load(loader.load_pricebooks_df, start, end, "pricebooks", transform=book_features)
    F = F.drop_duplicates(["timestamp_ns", "instrument_id"]).sort_values("timestamp_ns", kind="stable").reset_index(drop=True)
    F["ts"] = pd.to_datetime(F.timestamp_ns, unit="ns", utc=True)
    print("building order lifecycles ...", flush=True)
    L = order_life(O, F)
    A = section("AGGRESSIVE ORDERS: build", aggressive_orders, T, F)
    for name, df in (("orders_raw", O), ("orders_life", L), ("books", F), ("trades", T), ("aggr", A)):
        if df is not None:
            df.to_pickle(os.path.join(OUT, name + ".pkl.gz"))
    section("1. OVERVIEW", rep_overview, O, T, F, L, start, end)
    section("2. ORDER SIZES AND WHERE THEY REST", rep_order_sizes, L)
    section("3. ORDER BURSTS (orders sent together)", rep_bursts, L)
    section("4. WALLS AND FAIR-VALUE MOVES", rep_walls, L, F)
    if A is not None:
        section("5. TAKERS", rep_takers, A)
        section("6. ACTIVITY OVER TIME", rep_timeline, L, A, start, end)
    section("7. NAMED PARTICIPANTS", rep_names, L, T)
    with open(os.path.join(OUT, "summary.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(_report) + "\n")
    print(f"\nDone in {time.time() - t0:.0f} s. Report: {os.path.join(OUT, 'summary.txt')}  (paste it back for analysis)")


main()
