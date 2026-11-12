# CONTEXT.md — researching and market-making the 8 Optibook stocks

Read this before writing bot code. It covers one thing: how to research this market and build a
correct, competitive market maker with the `optibook` client. Nothing here was run against the
exchange. Section 7 was exercised against a fake exchange only; treat all code as **untested**.

**Tags.** `[doc: X]` = stated in file X. `[slides]` = documented in the organizers' challenge slides.
`[obs]` = seen in real exchange output captured in `your_optiver_workspace/optibook_guides/code_snippets.ipynb`
(2026-11-12, about 17:09–17:10 UTC). `[inferred]` = my reading of the evidence, not stated anywhere.
`[unverified]` = nobody knows yet; use the safe assumption and run the check in section 9.

**Evidence base.** `AGENTS.md`, `api_reference.md`, the notebook. `Docs/*.md` are five identical copies
of an older subset of `api_reference.md` (no `price_limit`, no `HistoricalDataLoader`); ignore them.
The templates, `common/` and PDF guides that `AGENTS.md` lists are **not in this repo copy**, so no
pattern below comes from an organizer template. If you have them in the live environment, read them.

---

## 1. The challenge in brief

| Item | Value | Source |
|---|---|---|
| Instruments | AMD, AVGO, CRWV, MU, NBIS, NVDA, SNDK, VRT, all `InstrumentType.STOCK`, `paused=False`, `expired=False` | [obs] |
| Tick size | 0.1 for all 8 | [obs] |
| Price change limit | `absolute_change=5.0`, `relative_change=10%` for all 8 | [obs] |
| Price limit (`instrument.price_limit`) | not shown in the instrument printout; may be `None` | [unverified] |
| Fixed order range | price in `[0, 1000000]`, volume in `[1, 100000]` | [doc: AGENTS.md] |
| Position limit | 100 lots long or short per instrument ("hold 75 NVDA, bid for at most 25 more") | [slides] |
| Price levels seen | NVDA about 140.6–142.2 (1-hour VWAP 146.74); VRT about 69.2–69.5 | [obs] |

- **Mission** [slides]: (1) research the historical orders, trades and book snapshots; (2) trade on it.
- **Counterparties** [slides]: other teams plus organizer-run bots.
- **Timeline** [slides]: free practice until about 21:00 Europe/Amsterdam, then positions and PnL are
  reset once and a 20-minute competition runs. Each team starts its own algorithm after the reset.
  Exchange timestamps are UTC [obs]; 21:00 Amsterdam in November is 20:00 UTC [inferred].
- **Judging** [slides]: competition PnL, trading approach, amount of risk taken, novelty, and the
  team must explain its approach.

**What the judging means for design.** PnL alone does not win. Build for:
- **Controlled inventory**: a self-imposed cap well below 100 (start at 40–60), a skew that fights
  inventory, and a flat book at the end. Log max and average |position| so you can show it.
- **Explainability**: every quote should follow from "fair value, minus inventory skew, plus or minus
  an edge". Avoid magic thresholds you cannot justify from the research.
- **One novel, evidence-backed idea** (section 6), switchable with a flag, so the safe core still runs
  if it misbehaves.
- A bot that makes slightly less with a flat, bounded position profile beats one that makes slightly
  more while sitting at ±100.

---

## 2. API cheat sheet

All signatures are from `api_reference.md`. `price`, `volume`, `side`, `order_type`, `order_id` are
**keyword-only**.

```python
from optibook.synchronous_client import Exchange
exchange = Exchange(max_nr_trade_history=5000)   # default cap is 100 trades per instrument
exchange.connect()                                # -> None. Credentials are automatic [doc: AGENTS.md]
```

| Call | Returns | Gotchas |
|---|---|---|
| `connect()` / `disconnect()` | `None` | Connecting kicks any other connection of the team. A "someone was already connected" message is normal [doc: AGENTS.md]. |
| `is_connected()` | `bool` | The only way to notice you were kicked; nothing raises. |
| `get_instruments()` / `get_tradable_instruments()` | `Dict[str, Instrument]` | Tradable excludes paused and expired. Fields: `tick_size`, `price_change_limit.absolute_change/.relative_change`, `price_limit` (`.min/.max` or `None`). Use `getattr(inst, "price_limit", None)`. |
| `get_last_price_book(iid)` | `PriceBook` (`.timestamp`, `.bids`, `.asks` as `List[PriceVolume]`, best first) | "Last received" book. Either side can be empty, the book can be falsy. Check `.timestamp` for staleness. |
| `insert_order(iid, *, price, volume, side, order_type='limit')` | `InsertOrderResponse(success, order_id, error_reason)` | `side` is `'bid'`/`'ask'`; type is `'limit'`/`'ioc'`. A limit order that crosses trades immediately and rests the remainder. Always check `success`. |
| `amend_order(iid, *, order_id, volume)` | `AmendOrderResponse(success, error_reason)` | **Volume only.** A new price means delete then insert. |
| `delete_order(iid, *, order_id)` | `DeleteOrderResponse(success, error_reason)` | Returned `success=False`, "Could not find order id to delete" for an unknown id [obs]. Expect the same when the order just filled [inferred]; treat a failed delete as "check for a fill". |
| `delete_orders(iid)` | **`None`** | No confirmation. Re-read `get_outstanding_orders` if you need to be sure. |
| `get_outstanding_orders(iid)` | `Dict[int, OrderStatus]` (`order_id`, `instrument_id`, `price`, `volume`, `side`) | Source of truth for resting orders; the exchange can cancel them itself, e.g. on a price-limit change. `volume` is presumably the remaining volume [unverified]. |
| `get_positions()` | `Dict[str, int]` | All 8 instruments, signed lots [obs]. |
| `get_positions_and_cash()` | `Dict[str, {'volume', 'cash'}]` | Per-instrument cash [obs]: `{'NVDA': {'volume': -10, 'cash': 1406.0}, ...}`. |
| `get_cash()` | `float` | Total cash over all instruments. |
| `get_pnl(valuations=None)` | `float` | Positions valued at the last public trade price unless you pass `{iid: price}`. "No PnL can be calculated" without a tick or valuation; guard for `None`. |
| `poll_new_trades(iid)` | `List[Trade]` | **Your** fills since the last call for that instrument. |
| `get_trade_history(iid)` | `List[Trade]` | Your fills since this client started, capped. |
| `poll_new_trade_ticks(iid)` | `List[TradeTick]` | Public trades since the last call for that instrument. Includes your own trades [obs]. |
| `get_trade_tick_history(iid)` | `List[TradeTick]` | Public trades since this client started, capped. |
| `poll_new_social_media_feeds()` / `get_social_media_feeds_history()` | `List[SocialMediaFeed]` (`timestamp`, `post`, `meta_data`) | Whether this event has a feed is [unverified]. The reference says "for admin clients, the feed contains the post and metadata", so fields may be empty for teams. |

`Trade`: `timestamp, order_id, trade_id, instrument_id, price, volume, side` (`'bid'` = you bought).
`TradeTick`: `timestamp, instrument_id, price, volume, aggressor_side, buyer, seller, trade_id`
(`aggressor_side='bid'` = the initiator bought; `buyer`/`seller` are empty strings [obs]).

**`poll_*` versus `get_*_history`.**
- `poll_*` drains a per-instrument cursor: each event is returned once. Call each poll from exactly
  one place in your code, or events get split between callers [inferred].
- `get_*_history` returns everything since this client object started, but keeps only the most
  recent `max_nr_trade_history` items per instrument (default 100). Older ones are dropped silently.
- Whether the cap can also drop events between two polls is [unverified]. Safe: construct with
  `max_nr_trade_history=5000` and poll every loop.
- Trade and tick history start when the client connects [doc: AGENTS.md]; use the loader for the past.

**Other gotchas.**
- **Float prices.** The exchange hands out `140.70000000000002` and `142.20000000000002` [obs].
  Never compare prices with `==`. Convert to integer ticks (`int(round(price / tick))`) for all logic
  and send `round(ticks * tick, 2)`.
- **`error_reason` on success printed as `'None'`** [obs]:
  `InsertOrderResponse(success=True, order_id=1843932, error_reason='None')`. Whether that is the
  string `"None"` or a real `None` is [unverified]. Test `response.success` only, never
  `if response.error_reason:`.
- **IOC `success=True` does not mean filled.** An IOC bid at 10 with nothing to match returned
  `success=True` [obs]. Detect fills from positions or `poll_new_trades`.
- **A private `Trade` and its public `TradeTick` share `trade_id` but not the timestamp** (they
  differed by about 40 µs [obs]). Match on `trade_id`.
- **The client prints failures itself** ("order delete failed with reason: ...") [obs]. The notebook
  silences it with `logging.getLogger("client").setLevel("ERROR")`.
- **The book presumably includes your own orders** [unverified]. A fair value taken from the best
  bid/ask will chase your own quotes; anchor on the walls (section 4) or subtract your own volume.

---

## 3. Exchange rules that break bots

**3.1 One connection per team** [doc: AGENTS.md, api_reference.md]. A second `connect()` kicks the
first silently. Only one bot per team trades at a time, and that includes teammates testing, a
notebook left open, and a research script that constructs `Exchange()`. `HistoricalDataLoader` uses
HTTP, not the exchange connection, so historical research does not kick the bot [inferred from the
loader's Basic Auth API description]. Agree in the team chat who holds the connection.
Pattern: every pass, `if not exchange.is_connected(): raise SystemExit("KICKED")`. Do not
auto-reconnect: two bots that both reconnect kick each other forever. Restart by hand
[doc: AGENTS.md says reconnect logic is not needed].

**3.2 Cancel on disconnect** [doc: AGENTS.md]. When the program stops, all resting orders are pulled.
**Positions remain.** A crash therefore leaves you with inventory and no quotes. Restart quickly, and
make the bot safe to start with a non-zero position (read `get_positions()` at start, never assume 0).
`AGENTS.md` says positions "never expire or reset"; the one reset before the competition [slides] is
an organizer action. Verify it happened instead of assuming it.

**3.3 The 100-lot limit** [slides]. Whether resting orders count is [unverified]: the slide example
suggests the check is at order entry; `AGENTS.md` says "Trades that would exceed the limit are
rejected". Safe assumption that is right under both readings: before every insert keep
`position + resting same-side volume + new volume <= 100`, mirrored for asks (`room()` in section 7).
Positions are per instrument and never reset or transfer except by trading [doc: AGENTS.md].

**3.4 Price rules.**
- Tick grid: prices must be multiples of `tick_size` [doc: AGENTS.md].
- Fixed range: price `[0, 1000000]`, volume `[1, 100000]`, else `success=False` [doc: AGENTS.md].
- Price limits: if `instrument.price_limit` is set, orders outside `[min, max]` are rejected, and if
  an admin changes it your resting orders outside the new range are cancelled [doc: api_reference.md].
  So re-read `get_outstanding_orders` every loop instead of trusting a local list.
- Price change limit: `AGENTS.md` says orders "priced too far from the last traded price are
  rejected". **Conflicting observation:** with NVDA last trading at 140.6, the notebook's limit bid at
  10, limit ask at 20 and both IOCs returned `success=True` [obs], and the organizers' own flatten
  snippet uses prices 0.10 and 100000. The exact rule is [unverified]. Safe: quote near the market
  (always fine), check every response, and never rely on a far-away order being rejected or accepted.

**3.5 Rate limits** [doc: AGENTS.md]. Requests are throttled per team across all instruments; sleep
at least 0.2 s per loop iteration. The thresholds and the penalty are [unverified]. A loop that
re-reads and re-sends everything makes up to 9 calls per instrument per pass, about 75 over 8 names.
Rules (all in section 7):
- Requote only when the target price or size changed. Leaving a correct order alone also keeps its
  queue position.
- Space order actions with a minimum gap (`pace()`), and back off when responses start failing.
- Which calls cost a request is [unverified]. `get_last_price_book` and `poll_*` read "last
  received" data, which suggests a local cache; do not assume it.

**3.6 No fill notifications** [doc: AGENTS.md]. Each loop: `poll_new_trades(iid)` for fills and
`get_positions()` for the truth. Size orders from `get_positions()`, not from a local counter.

**3.7 PnL is valued at the last traded price** [doc: AGENTS.md, api_reference.md]. One odd print
moves the PnL of every open position. For your own monitoring pass a valuation you trust:
`exchange.get_pnl(valuations={iid: fair_price})`. Whether final scoring uses the last trade is
[unverified]. Ending flat makes the question irrelevant.

---

## 4. What the market looks like

All of this comes from one NVDA live book, one hour of history ending 17:09 UTC, and a few VRT and
NVDA snapshots [obs]. It is a small sample from the practice period; confirm it with section 5.

**NVDA live book, 17:10:22 UTC** [obs]:
```
asks: 140.8 x10 | 140.9 x44 | 141.0 x3000 | 141.1 x2001 | 141.2 x1002
bids: 140.6 x3018 | 140.5 x2027 | 140.4 x1009 | 50.0 x1 | 10.0 x10
```

- **Walls.** Each side has roughly 3000 / 2000 / 1000 lots on three consecutive ticks. Same shape in
  history: VRT bids `69.2 x3015, 69.1 x2000`, asks `69.5 x3013, 69.6 x2003`; NVDA at 17:08:59 bid wall
  `141.8 x3000`, ask wall `142.2 x3018`. The round sizes on every stock point to one organizer
  liquidity bot [inferred].
- **Wall spread is 3–4 ticks** (NVDA 140.6/141.0 and 141.8/142.2 = 4 ticks; VRT 69.2/69.5 = 3 ticks).
  That leaves only 2–3 free price levels inside, holding small orders of 10, 44, 8, 16, 18 lots
  [obs]: presumably teams and smaller organizer bots competing there [inferred].
- **Small two-sided quoters exist.** NVDA: cancel an ask, then new bid `142.0 x10` and new ask
  `142.2 x10` within about 3 ms. VRT: new ask `69.6 x2` and new bid `69.1 x2` within 2 ms [obs]. They
  look like quoting bots doing cancel-and-replace; nothing proves each group is one actor [inferred].
- **Stray far orders** (`50.0 x1`, `10.0 x10`) are almost certainly teams running the notebook, which
  inserts a bid at 10 [inferred]. They carry no information, but they matter: if the walls ever
  vanish, the "best bid" becomes 50.0. Sanity-check any price you act on against the wall mid or the
  last trade.
- **Trades are small and frequent.** NVDA: 853 trades in the hour (one every 4.2 s), 12,769 lots,
  about 15 lots per trade [obs]. History tail: 2, 2, 6, 10, 5 lots; live ticks 80 s later: 10, 5, 5,
  10, 5, 5, where the last two are the notebook's own sells [obs]. Several trades share one
  timestamp: probably one aggressive order of 10–15 lots sweeping a few resting orders [inferred].
- **Trades print inside the walls and at the wall price** (140.7 and 140.8 inside; 140.6 and 142.2 at
  the wall; one of the three 140.6 prints was market flow, two were the notebook's own) [obs]. At
  142.2 one 10-lot buy filled resting orders of 2, 2 and 6 lots, not the 3000-lot level in one print,
  so small orders at the wall price can have priority over the wall [inferred, one observation].
- **The 8 stocks look alike.** Identical instrument settings; hourly volume between 12,405 and 13,530
  lots for every name (about 215 lots per minute per stock, about 4,300 lots per stock in 20
  minutes); 152,084 order events per hour over 8 names, about 5 per second per name [obs]. The flow
  is probably generated by the same organizer process in every stock [inferred].
- **The price moves.** NVDA wall mid was 142.0 at 17:08:59 and 140.8 at 17:10:22: 12 ticks in
  83 seconds. The 1-hour VWAP of 146.74 was about 4.6 above the 17:08:59 price [obs].

**What this suggests about the participants** [inferred]:
- An organizer liquidity bot quotes the walls around a moving hidden fair value. The **wall mid**
  (midpoint of the first big level on each side) is the best available estimate of it.
- A steady stream of small aggressive orders hits both sides. Whether they are noise or informed is
  the key research question (analysis A3).
- You get fills only by quoting **inside** the walls. At the wall price you queue behind 3000 lots.
- **Edge is small, inventory risk is large.** Edge is 1–2 ticks (0.1–0.2) per round-trip lot. Even
  capturing 10% of a stock's flow for 20 minutes at 0.1 per lot is about 43 per stock. A 50-lot
  position during one move like the 12-tick one above loses 60. Inventory control decides the result.
- While the walls hold, a position can always be closed into a 3000-lot level one or two ticks away.
  The risk is the wall moving, not a lack of liquidity.

---

## 5. Research plan for the historical data

**Loader facts.**
- Feeds: trades, orders, pricebooks. `get_*_df` downloads and loads; `download_*` only downloads;
  `load_*_df` reads the local cache only [doc: api_reference.md].
- Limits [doc: api_reference.md]: 30 query requests per minute per user (bursts of 10), a 429 becomes
  a `ValueError` naming the wait; loading is capped at 1 day per call. **Download once, then use only
  `load_*`.** Never call `get_*` inside a loop.
- Files are per minute (59 files for an hour) and the newest data was at least 80 s old [obs]. History
  is not a live signal.
- Every row carries `exchange_started_at = 2026-11-11T12:28:39 UTC`, and a week-long download listed
  1721 trade files, which matches the minutes since then [obs]. So history starts at the exchange
  start, and a change in that column would mean a restart [inferred].
- Pass naive UTC datetimes, as the notebook does with `datetime.utcnow()` [obs].
- Actual columns [obs], more than the reference lists:
  - trades: `timestamp_ns, timestamp_str, instrument_id, price, volume, aggressor_side, buyer, seller, trade_id, exchange_started_at`
  - orders: `timestamp_ns, timestamp_str, instrument_id, order_id, price, volume, side, username, action, order_type, exchange_started_at`.
    `action` values seen: `new`, `cancelled`, `fill` (maybe not all). `volume` is 0 on the `cancelled`
    and `fill` rows seen, so it is probably the remaining volume [inferred]. Use the DataFrame: the
    typed `get_orders()` objects document `action` as empty for historical data.
  - pricebooks: `timestamp_ns, timestamp_str, instrument_id, bids_json, asks_json, exchange_started_at`;
    the JSON is `[[price, volume], ...]`, best first, with float noise in prices.
- Size: one hour is about 6k trades, 152k order rows, 135k book rows [obs]. Work in 1-hour chunks and
  reduce books to features immediately.
- `buyer`, `seller`, `username` are empty unless the organizers open a counterparty window:
  `loader.get_counterparty_data_window()` returns `(start, end)` or `None`. If it is set, request a
  range entirely inside it to see who the organizer bots are.
- The social feed is **not** in the historical data. It can only be recorded live (A6).

**Shared helper** (run once, save the result for the whole team):
```python
# research_common.py                                                    [untested]
import json, time
from datetime import datetime, timedelta
import numpy as np, pandas as pd
from optibook.historical_data_loader import HistoricalDataLoader

loader = HistoricalDataLoader()
START = datetime(2026, 11, 11, 12, 29)                      # naive UTC, just after exchange start
END = datetime.utcnow() - timedelta(minutes=3)
TICK, WALL_MIN = 0.1, 1000

def cache(start=START, end=END):                             # call ONCE, then only load_*
    for _ in range(20):                                      # cached files are skipped, so retrying resumes
        try:
            return loader.download_all(start, end)
        except ValueError as e:                              # 429: rate limited, message names the wait
            print(e); time.sleep(65)

def hours(start=START, end=END):
    t = start
    while t < end:
        yield t, min(t + timedelta(hours=1), end)
        t += timedelta(hours=1)

def book_features(pb):
    """pricebooks df -> one row per snapshot: best prices, wall prices, volume inside the walls."""
    def f(r):
        b, a = json.loads(r.bids_json), json.loads(r.asks_json)
        wb = next((p for p, v in b if v >= WALL_MIN), np.nan)
        wa = next((p for p, v in a if v >= WALL_MIN), np.nan)
        return (b[0][0] if b else np.nan, a[0][0] if a else np.nan, wb, wa,
                sum(v for p, v in b if p > wb) if wb == wb else np.nan,       # NaN when there is no wall
                sum(v for p, v in a if p < wa) if wa == wa else np.nan)
    cols = ["bid", "ask", "wall_bid", "wall_ask", "in_bid_vol", "in_ask_vol"]
    out = pd.DataFrame([f(r) for r in pb.itertuples()], columns=cols, index=pb.index)
    out["timestamp_ns"], out["instrument_id"] = pb.timestamp_ns, pb.instrument_id
    out["wall_mid"] = (out.wall_bid + out.wall_ask) / 2
    out["wall_spread_t"] = ((out.wall_ask - out.wall_bid) / TICK).round()
    out["spread_t"] = ((out.ask - out.bid) / TICK).round()
    return out

def load_all():
    fs, ts = [], []
    for s, e in hours():                                     # cache only: no API requests
        pb, tr = loader.load_pricebooks_df(s, e), loader.load_trades_df(s, e)
        if len(pb): fs.append(book_features(pb))
        if len(tr): ts.append(tr)
    F = pd.concat(fs, ignore_index=True).drop_duplicates(["timestamp_ns", "instrument_id"])
    T = pd.concat(ts, ignore_index=True).drop_duplicates("trade_id")          # hour edges may overlap
    F["ts"] = pd.to_datetime(F.timestamp_ns, unit="ns", utc=True)
    return F.sort_values("timestamp_ns"), T.sort_values("timestamp_ns")

def bars(F, freq="1s"):                                      # wall mid per instrument on a time grid
    return (F.dropna(subset=["wall_mid"]).set_index("ts").groupby("instrument_id").wall_mid
             .resample(freq).last().unstack(0).ffill())
# cache(); F, T = load_all(); F.to_pickle("F.pkl"); T.to_pickle("T.pkl")
```

**A1. Spread and depth per stock.** Sets where you can quote and how crowded it is.
```python
F.groupby("instrument_id").wall_spread_t.value_counts(normalize=True).unstack()   # share of 2/3/4-tick walls
F.groupby("instrument_id")[["spread_t", "in_bid_vol", "in_ask_vol"]].describe()   # competition inside
F.assign(hour=F.ts.dt.floor("h")).groupby(["instrument_id", "hour"]).in_bid_vol.mean().unstack(0)
```
Decides: quote 1 tick inside both walls, or one side only when the wall spread is 2 ticks. Rising
inside volume over time means other teams have switched on.

**A2. Trade size and frequency.** Sets quote size.
```python
A = (T.assign(pv=T.price * T.volume).groupby(["instrument_id", "timestamp_ns", "aggressor_side"])
       .agg(vol=("volume", "sum"), pv=("pv", "sum"), n=("volume", "size")).reset_index())   # one row per aggressive order
A["px"] = A.pv / A.vol                                                         # average price paid
A.groupby("instrument_id").vol.describe()                                      # aggressive order size
A.groupby("instrument_id").timestamp_ns.diff().div(1e9).describe()             # seconds between orders
A.assign(s=np.where(A.aggressor_side == "bid", A.vol, -A.vol)).groupby("instrument_id").s.sum()  # buy/sell balance
```
Decides: quote size about the median aggressive order, so one hit fills you without tripling inventory.

**A3. Markout: does the mid revert or continue after a trade?** The most important number.
```python
def markout(A, F, horizons=(1, 5, 30)):
    rows = []
    for iid, a in A.groupby("instrument_id"):
        f = F.loc[F.instrument_id == iid, ["timestamp_ns", "wall_mid"]].dropna()
        a = a.sort_values("timestamp_ns"); sign = np.where(a.aggressor_side == "bid", 1, -1)
        m0 = pd.merge_asof(a, f, on="timestamp_ns", allow_exact_matches=False).wall_mid.values
        for h in horizons:
            mh = pd.merge_asof(a.assign(timestamp_ns=a.timestamp_ns + int(h * 1e9)), f, on="timestamp_ns").wall_mid.values
            rows.append((iid, h, np.nanmean(sign * (mh - m0)) / TICK, np.nanmean(sign * (a.px.values - m0)) / TICK))
    return pd.DataFrame(rows, columns=["iid", "horizon_s", "mid_move_ticks", "taker_paid_ticks"])
```
Reading: `mid_move_ticks` near 0 means takers are noise, so quote tight and often. Clearly positive
means takers are informed: a maker who sold to them at `taker_paid_ticks` keeps
`taker_paid_ticks − mid_move_ticks`. If that is negative at 5–30 s, plain market making loses and you
must skew with the flow. Split by `vol` buckets to see whether large orders are the toxic ones.

**A4. How the organizer bots quote and react.**
```python
B = bars(F); r = B.diff()
(r / TICK).round().stack().value_counts().sort_index()          # wall-mid step sizes: drift or jumps?
r.std(), r.apply(lambda s: s.autocorr(1))                       # per-second vol; trend (>0) or reversion (<0)
O = pd.concat(loader.load_orders_df(s, e) for s, e in list(hours())[-3:])   # last 3 hours is enough
big = O[(O.action == "new") & (O.volume >= 1000)].sort_values("timestamp_ns")
big.volume.value_counts().head(); big.groupby("instrument_id").timestamp_ns.diff().div(1e9).describe()   # refresh cadence
life = O.groupby("order_id").agg(t0=("timestamp_ns", "min"), t1=("timestamp_ns", "max"), last=("action", "last"))
```
Questions: Are the walls re-inserted on a timer (then they lose time priority and small orders at
the wall price fill first)? Does the wall move after trades (price impact, exploitable) or on its own
clock? Does a wall thin out before it moves (a warning signal)? Is the taker flow evenly timed
(a bot) and symmetric?

**A5. Correlations and lead-lag across the 8 stocks.**
```python
r5 = bars(F, "5s").diff().dropna()
r5.corr().round(2)                                                             # same-time correlation
pd.DataFrame({k: r5.shift(k).corrwith(r5["NVDA"]) for k in (1, 2, 6)}).round(2)  # does stock X lead NVDA by k*5 s?
w, v = np.linalg.eigh(r5.corr().values); w[-1] / w.sum()                       # share of variance in one common factor
```
Decides: whether cross-name risk offsetting is real (section 6) and whether one name leads the rest.

**A6. Social feed** (live only, and it needs the single exchange connection, so put it in the bot):
```python
for p in exchange.poll_new_social_media_feeds():
    log_row("feed.csv", [str(getattr(p, "timestamp", "")), str(getattr(p, "post", "")), str(getattr(p, "meta_data", ""))])
```
If posts appear: for each post, compare the wall mid from −10 s to +120 s (`bars(F)` around
`p.timestamp`) by keyword or ticker. Decides whether to pull quotes on a post, or lean.

**A7. Volatility per stock, for inventory limits.**
```python
vol10 = bars(F, "10s").diff().std()          # price units per 10 s
(vol10 * 50).round(1)                        # typical 10-second PnL swing of a 50-lot position
```
Decides `SOFT_CAP` per stock: a 1-minute adverse move should cost less than a few minutes of spread income.

---

## 6. Market-making playbook (20 minutes, 100-lot limit, judged on risk)

**Fair value.** Work in integer ticks.
- **Wall mid** (recommended anchor): midpoint of the first level with volume ≥ `WALL_MIN` on each
  side. It ignores small orders, stray orders and your own quotes. If either wall is missing, do not
  quote that instrument.
- **Plain mid**: polluted by 1-lot orders and by your own quotes. Fallback only.
- **Microprice** (`(bid·ask_vol + ask·bid_vol)/(bid_vol + ask_vol)`): at the wall levels it is nearly
  constant (3000 vs 3000). The useful version uses only the volume **inside** the walls: more inside
  volume on the ask side means sellers are leaning. Test with A3 before trusting it.
- **Depth-weighted**: the walls are symmetric (3000/2000/1000), so it equals the wall mid. Skip.
- **Trade-based**: signed aggressive volume over the last 10–30 s as a predictor of the next wall
  move. Use only if A3 or A4 shows that flow moves the wall.
- A 3-tick wall spread puts the wall mid between ticks (69.35); a 4-tick one puts it on a tick
  (142.0). Keep the half tick; do not round fair value.

**Spread and size.**
- Quote inside the walls: reservation price `r = fair + skew`, bid = `floor(r − h)`, ask =
  `ceil(r + h)` in ticks, with `h = 0.25` tick. That gives one tick inside each wall for both 3-tick
  and 4-tick wall spreads when flat, and keeps 3-tick names two-sided for the first few lots.
- When flat, never quote through fair value; only the inventory-reducing side may reach or cross it.
  A 2-tick wall spread leaves no room when flat; under 2 or over 8 ticks, quote nothing.
- Size 5–15 lots per side (the aggressive order size seen). Raise it only if A2 says so.
- Per-stock inventory cap `SOFT_CAP` of 40–60, lower for the more volatile names (A7).

**Inventory skew that steepens near the cap** (`targets()` in section 7). With `x = pos / SOFT_CAP`:
`skew_ticks = -(x + 3x³)`, which is 0 when flat, about −0.9 at half the cap and −4 at the cap. The
size of the side that adds inventory shrinks linearly to 0 at the cap. Ticks are coarse, so the skew
acts in steps. On a 4-tick wall, long half the cap: the bid falls back to the wall (no fills) and the
ask steps one tick closer. On a 3-tick wall the bid drops out after about 10 lots. At the cap: no
bid, ask one tick above the bid wall. At `HARD_CAP` (80): cut to `SOFT_CAP/2` with a bounded IOC.

**When to cancel and requote.**
- Requote only when the target price or size changed: the wall moved, you were filled, or the
  inventory step changed. Otherwise leave the order (queue position, rate limit).
- Pull all quotes in an instrument at once when: a wall is missing or thin; the book is empty or its
  timestamp is older than about 2 s; the wall mid moved 2 ticks or more in the last few seconds;
  a feed post arrives (if A6 shows posts move prices); `is_connected()` is false.
- After pulling, wait for a stable wall for 1–2 s before quoting again.

**Signs of adverse selection** (log them; react by raising `H` to 1.5 or pausing the name):
- fills come on one side only, several in a row;
- the wall mid moves against your fills within 5 s (live markout: `sign × (fair_5s_later − fill_price)`);
- the wall on your filled side thins or steps away right after the fill;
- the same-direction move already happened in the other 7 names (if A5 shows lead-lag);
- you are the only quote left inside the walls.

**Wind-down plan** (times relative to the end of the 20 minutes):
- T−3:00: halve the quote size.
- T−2:00: quote only the side that reduces inventory.
- T−1:00: delete all orders; flatten with bounded IOCs into the walls (section 7); repeat until flat.
- At the end: positions all 0, no orders resting; the bot stays connected and idle.
- Cost is at most 1–2 ticks per lot. It removes mark-to-last-trade noise from the final PnL and is
  the easiest risk story to tell the judges. `T_END` is an absolute UTC time, so a restart keeps the
  schedule; set it from the announced start.

**Offsetting exposure across names.**
- Positions cannot be netted across instruments [doc: AGENTS.md]; each name has its own 100 limit.
  Risk can still be offset if A5 shows high correlation.
- Cheap use: a **portfolio skew**. Add a term to every name's skew proportional to the team's total
  exposure in price-weighted lots, `sum(pos_i × price_i)`, so that when the book is net long, all 8
  names lean toward selling. No extra trades, easy to explain.
- Expensive use: actively hedging one name by crossing the spread in another costs 3–4 ticks. Only
  worth it with correlation above about 0.7 at the 5–30 s horizon; otherwise reduce the position itself.
- Size any hedge by beta or volatility (A5, A7), not lot for lot, and keep it under the hedge
  name's own `SOFT_CAP`.
- If A5 shows low correlation, drop this and say so; it is a valid research finding.

**Where a novel twist can come from.**
1. **Wall-anchored fair value with sub-tick information** from the 3-tick versus 4-tick wall spread.
2. **Flow toxicity filter**: classify aggressive orders (size, clustering) by markout from A3 and
   widen only against the toxic kind.
3. **Common-factor lean**: use the first principal component or a leading stock from A5 to shift
   fair value in the laggards before their walls move.
4. **Organizer-bot model**: if A4 shows walls thin or refresh in a pattern before moving, pull early.
5. **Feed reaction**: pull on a post, then lean in the direction A6 shows.

**Three variants.** One connection per team means these are not three bots. Build one bot with a
shared core and flags; each teammate owns a module (`fair_adjust(iid) -> ticks`, `should_pause(iid)`).

| Variant | What it adds | Main risk | Pitch for the judges |
|---|---|---|---|
| **A. Wall-anchored inventory-aware maker** (safest; build first) | Wall-mid fair value, one tick inside the walls, cubic inventory skew, soft and hard caps, timed wind-down | The hidden fair value jumps while you hold inventory; crowded inside levels mean few fills | "We earn the spread inside the organizers' walls, never hold more than N lots, and finish flat." |
| **B. A + toxicity-aware quoting and portfolio skew** | Live markout tracking, widening or pausing on toxic flow, a skew term on total exposure across the 8 names | Thresholds overfitted to about a day of practice data; more code paths to break | "We measure who we trade against and manage the 8 stocks as one risk book." |
| **C. A/B + predictive lean** (most ambitious) | Fair value shifted by the cross-stock factor, wall behaviour or feed posts; may hold a small deliberate position | The signal may not exist in the competition; directional losses | "A market maker that leans its quotes on a researched signal, with the position still capped." |

Give C a hard switch-off: if its lean has lost more than a set amount after 5 minutes, fall back to A.

---

## 7. Reusable code idioms — all untested

Never run against the exchange. The logic was exercised only against a fake exchange object.

```python
import csv, logging, math, time
from datetime import datetime, timezone
from optibook.synchronous_client import Exchange

logging.getLogger("client").setLevel("ERROR")          # as in the notebook
LIMIT, SOFT_CAP, HARD_CAP, BASE = 100, 50, 80, 10      # lots
WALL_MIN, MAX_WALL_SPREAD, H = 1000, 8, 0.25           # lots, ticks, ticks
T_END = datetime(2026, 11, 12, 20, 20, tzinfo=timezone.utc).timestamp()   # SET THIS: announced end, UTC
# practice runs: T_END = time.time() + 20 * 60

def connect():
    ex = Exchange(max_nr_trade_history=5000)
    ex.connect()                                        # "already connected" message is normal
    if not ex.is_connected():
        raise SystemExit("not connected")
    return ex

def to_ticks(price, tick):  return int(round(price / tick))
def to_price(ticks, tick):  return round(ticks * tick, 2)   # tick = 0.1; kills 140.70000000000002

def best(book):
    """(best_bid, best_ask) as PriceVolume or None. For display only: may be a stray or our own order."""
    if not book:
        return None, None
    return (book.bids[0] if book.bids else None), (book.asks[0] if book.asks else None)

def wall(levels):
    """Price of the first level holding >= WALL_MIN lots, else None."""
    for lv in levels or []:
        if lv.volume >= WALL_MIN:
            return lv.price
    return None

def walls(book, tick):
    """(bid_wall, ask_wall) in ticks, or None when a wall is missing or the pair is implausible."""
    wb, wa = wall(book.bids if book else None), wall(book.asks if book else None)
    if wb is None or wa is None:
        return None
    wb, wa = to_ticks(wb, tick), to_ticks(wa, tick)
    return (wb, wa) if 2 <= wa - wb <= MAX_WALL_SPREAD else None   # rejects a far-away 1000-lot stray

_last_action = [0.0]
def pace(gap=0.05):
    """Call before every order action: at most 1/gap actions per second. Tune after section 9 test 4."""
    wait = _last_action[0] + gap - time.time()
    if wait > 0:
        time.sleep(wait)
    _last_action[0] = time.time()

def insert(ex, iid, price, volume, side, order_type="limit"):
    """Insert with response checking. Returns order_id or None."""
    if volume < 1:
        return None
    pace()
    r = ex.insert_order(iid, price=price, volume=int(volume), side=side, order_type=order_type)
    if not r.success:
        print(f"INSERT FAIL {iid} {side} {volume}@{price}: {r.error_reason}")
        return None
    return r.order_id

def room(side, pos, outstanding, cap=LIMIT):
    """Largest new volume that keeps position + resting same-side volume within the limit."""
    resting = sum(o.volume for o in outstanding.values() if o.side == side)
    return max(0, cap - pos - resting) if side == "bid" else max(0, cap + pos - resting)
```

**Target quotes from the walls and the inventory.**
```python
def targets(w, pos, adjust=0.0):
    """w = walls() result. -> (bid, bid_size, ask, ask_size) in ticks and lots. adjust = signal in ticks."""
    wb, wa = w
    x = max(-1.5, min(1.5, pos / SOFT_CAP))
    r = (wb + wa) / 2 + adjust - (1.0 * x + 3.0 * x ** 3)       # reservation price: fair minus skew
    bid = min(math.floor(r - H + 1e-9), wa - 1)                  # never at or through the opposite wall
    ask = max(math.ceil(r + H - 1e-9), wb + 1)
    bid_size = round(BASE * min(1.0, max(0.0, 1 - x)))           # shrink only the side that adds inventory
    ask_size = round(BASE * min(1.0, max(0.0, 1 + x)))
    if bid <= wb: bid_size = 0                                   # at or behind the wall: no fills, skip
    if ask >= wa: ask_size = 0
    return bid, bid_size, ask, ask_size                          # bid < ask always holds
```
The inventory-reducing quote may cross another team's small order inside the walls and trade at once.
That is intended, but it is a taker fill; do not report it as spread capture.

**Cancel-and-replace that keeps correct orders.** Deletes first, re-reads state, then inserts.
```python
def requote(ex, iid, tick, tgt):
    """Make resting orders match tgt = (bid, bid_size, ask, ask_size); tgt=None pulls everything."""
    want = {"bid": (tgt[0], tgt[1]), "ask": (tgt[2], tgt[3])} if tgt else {"bid": (0, 0), "ask": (0, 0)}
    kept = set()
    for o in ex.get_outstanding_orders(iid).values():            # exchange state, not a local list
        px, size = want[o.side]
        if size > 0 and o.side not in kept and to_ticks(o.price, tick) == px and size / 2 <= o.volume <= size:
            kept.add(o.side)                                     # leave it: keeps queue position
        else:
            pace(); ex.delete_order(iid, order_id=o.order_id)    # can fail: just filled, or throttled
    if all(size == 0 or side in kept for side, (px, size) in want.items()):
        return                                                   # nothing to insert
    outstanding = ex.get_outstanding_orders(iid)                 # orders first, position second: a fill in
    pos = ex.get_positions().get(iid, 0)                         # between is counted twice (the safe side)
    for side in ("bid", "ask"):
        px, size = want[side]
        same = [o for o in outstanding.values() if o.side == side]
        opp = [to_ticks(o.price, tick) for o in outstanding.values() if o.side != side]
        crosses = bool(opp) and (px >= min(opp) if side == "bid" else px <= max(opp))
        if size > 0 and not same and not crosses:                # no duplicates, never cross our own order
            insert(ex, iid, to_price(px, tick), min(size, room(side, pos, outstanding)), side)
```
To shrink an order without losing its place: `ex.amend_order(iid, order_id=o.order_id, volume=new)`.
Use it only to **reduce** volume until section 9 confirms increases work.

**Reduce a position with a bounded IOC.** Do not copy the notebook's flatten snippet for the
competition: it sells at 0.10 and buys at 100000 without checking responses, and would hit the stray
50.0 and 10.0 bids if the walls were gone.
```python
_last_ioc = {}                                                   # iid -> (time sent, position before)

def cut(ex, iid, tick, pos, volume, w, fair_t, slip=2):
    """IOC that reduces |pos| by volume, priced at most `slip` ticks through the wall. Non-blocking."""
    t0, p0 = _last_ioc.get(iid, (0.0, None))
    if volume < 1 or pos == 0 or (p0 == pos and time.time() - t0 < 1.0):
        return                                                   # last IOC may not show in positions yet
    if w:
        bound = w[0] - slip if pos > 0 else w[1] + slip
    elif fair_t is not None:                                     # no walls: within 5 ticks of a recent fair
        bound = math.floor(fair_t) - 5 if pos > 0 else math.ceil(fair_t) + 5
    else:
        print(f"CUT {iid}: no reference price, position {pos} left open"); return
    if insert(ex, iid, to_price(bound, tick), min(volume, abs(pos)), "ask" if pos > 0 else "bid", "ioc") is not None:
        _last_ioc[iid] = (time.time(), pos)
```

**Logging for the judges.** Plain CSV. (`optibook.exporter.Exporter().export({"file.csv": [[...]]})`
also works: it appends to an `exports/` folder and prepends a UTC timestamp [doc: api_reference.md].)
```python
def log_row(name, row):
    with open(name, "a", newline="") as f:
        csv.writer(f).writerow([datetime.now(timezone.utc).isoformat()] + list(row))

def log_fills(ex, iid, fair_t, tick):                            # fair_t: wall mid in ticks (x.5 possible) or None
    for t in ex.poll_new_trades(iid):                            # the only place this poll is called
        edge = None if fair_t is None else (fair_t - to_ticks(t.price, tick)) * (1 if t.side == "bid" else -1)
        log_row("fills.csv", [iid, t.trade_id, t.side, t.price, t.volume, edge])   # edge: ticks earned vs fair

def log_state(ex, fair_t, ticks):
    pc = ex.get_positions_and_cash()
    val = {i: fair_t[i] * ticks[i] for i in fair_t}              # names without a fair: last trade is used
    log_row("state.csv", [ex.get_pnl(valuations=val)] + [pc[i]["volume"] for i in sorted(pc)])
```
From these two files you can report: PnL curve and maximum drawdown, maximum and average |position|
per stock, edge captured per lot, fill counts per side, and markout.

**Main loop** with pacing, exception handling, the hard cap and the wind-down.
```python
def main():
    ex = connect()
    ticks = {i: inst.tick_size for i, inst in ex.get_tradable_instruments().items()}
    fair_t, last_log = {}, 0.0                                   # last valid wall mid per name, in ticks
    fair_at, seen, checked = {}, {}, {}                          # time of last fair; last (target, position); last requote
    try:
        while True:
            if not ex.is_connected():
                raise SystemExit("KICKED: someone else connected")
            left = T_END - time.time()                           # absolute clock: survives a restart
            if left < -5:
                print("past T_END: idle", ex.get_positions()); time.sleep(5); continue
            positions = ex.get_positions()                       # once per pass
            for iid, tick in ticks.items():
                try:
                    pos = positions.get(iid, 0)
                    w = walls(ex.get_last_price_book(iid), tick)
                    if w:
                        fair_t[iid], fair_at[iid] = (w[0] + w[1]) / 2, time.time()
                    fresh = fair_t.get(iid) if time.time() - fair_at.get(iid, 0) < 10 else None
                    log_fills(ex, iid, fresh, tick)
                    if left < 60 or abs(pos) >= HARD_CAP:        # final flatten, or emergency cut
                        requote(ex, iid, tick, None)
                        vol = abs(pos) if left < 60 else abs(pos) - SOFT_CAP // 2
                        cut(ex, iid, tick, pos, vol, w, fresh)
                        continue
                    tgt = targets(w, pos) if w else None         # no valid walls: pull quotes
                    if tgt and left < 180:                       # T-3:00: half size
                        b, bsz, a, asz = tgt
                        bsz, asz = min(bsz, BASE // 2), min(asz, BASE // 2)
                        if left < 120:                           # T-2:00: reduce only, never past flat
                            bsz, asz = min(bsz, max(0, -pos)), min(asz, max(0, pos))
                        tgt = (b, bsz, a, asz)
                    if (tgt, pos) != seen.get(iid) or time.time() - checked.get(iid, 0) > 2:
                        requote(ex, iid, tick, tgt)              # only on a change, plus a 2 s safety re-check
                        seen[iid], checked[iid] = (tgt, pos), time.time()
                except Exception as e:                           # one bad instrument must not stop the rest
                    print(f"ERR {iid}: {e!r}")
            if time.time() - last_log > 2:
                log_state(ex, fair_t, ticks); last_log = time.time()
            time.sleep(0.25)                                     # at least 0.2 s per pass [doc: AGENTS.md]
    finally:
        for iid in ticks:                                        # explicit, although disconnect cancels too
            try: ex.delete_orders(iid)
            except Exception: pass
```
Still missing, add as you build: back-off when responses fail, a stale-book check on
`book.timestamp`, pausing a name after a fast wall move, and the `adjust` signal hook for variants B and C.

---

## 8. Competition-day checklist

**Before 21:00 Amsterdam (20:00 UTC)**
- [ ] One named person runs the bot. Everyone else closes notebooks and scripts that create `Exchange()`.
- [ ] The bot ran a full 20 minutes in practice without an exception, including the wind-down.
- [ ] Section 9 checks done; parameters frozen (`SOFT_CAP`, `BASE`, `H`, pacing, flags).
- [ ] `T_END` set to the announced end in UTC. Old log files moved away.
- [ ] The bot runs as a plain script (`python your_algo.py`), not in a notebook [doc: AGENTS.md].

**Right after the reset**
- [ ] Start exactly one bot. Confirm `is_connected()` is true.
- [ ] `get_positions()` is all zeros and `get_pnl()` is about 0. If not, tell the organizers.
- [ ] `get_outstanding_orders(iid)` is empty for all 8; otherwise `delete_orders(iid)`.
- [ ] Instruments and tick sizes are unchanged, and the walls are present before the first quote.

**During the 20 minutes** (console plus `state.csv`)
- [ ] Still connected. A "KICKED" exit means a teammate connected: restart at once.
- [ ] |position| per stock stays under `SOFT_CAP` and never sits at the hard cap.
- [ ] Fills arrive on both sides. One-sided fills with falling PnL mean adverse selection: widen or pause that name.
- [ ] No stream of `INSERT FAIL`. Read the reason: limit, price rule or rate limit.
- [ ] If the bot crashes, restart it. Positions survive, orders do not, `T_END` still holds.

**Wind-down**
- [ ] T−3:00 half size; T−2:00 reduce-only; T−1:00 flatten; at the end all positions 0, no orders.
- [ ] Any `CUT ...: no reference price` message means a position is still open: close it by hand.
- [ ] Keep the bot connected until the end is announced. Save `fills.csv`, `state.csv` and the
      parameters for the explanation to the judges.

---

## 9. Open questions to verify live

Run in practice, one person at a time (each test needs the connection), with section 7 loaded:
```python
ex = connect(); iid, tick = "NVDA", 0.1
w = walls(ex.get_last_price_book(iid), tick); assert w, "no walls right now"
far = to_price(w[0] - 30, tick)      # passive bid 3.0 below the bid wall, inside the 5.0 change limit
# wrap every test:   try: <test>   finally: ex.delete_orders(iid)
```
1. **Do resting orders count toward the 100 limit?** Safe: yes.
   ```python
   print(ex.get_positions()[iid])                                   # run this test when it is 0
   print(ex.insert_order(iid, price=far, volume=60, side="bid"))
   print(ex.insert_order(iid, price=far, volume=60, side="bid"))    # rejected => resting orders count
   ```
2. **Can `amend_order` increase volume?** Safe: decrease only.
   ```python
   oid = ex.insert_order(iid, price=far, volume=5, side="bid").order_id
   print(ex.amend_order(iid, order_id=oid, volume=10), ex.get_outstanding_orders(iid))
   print(ex.amend_order(iid, order_id=oid, volume=3), ex.get_outstanding_orders(iid))
   ```
3. **What does the price change limit reject?** Safe: stay near the market, check every response.
   ```python
   mid = (w[0] + w[1]) / 2 * tick
   for d in (4, 6, 15):                                             # inside and outside absolute_change=5
       print(d, ex.insert_order(iid, price=round(mid - d, 1), volume=1, side="bid"))
   ```
4. **Rate limit threshold and penalty.** Safe: `pace()` at 20 order actions per second or fewer.
   This test may get you throttled or disconnected; practice only.
   ```python
   t0 = time.time()
   for k in range(60):
       r = ex.insert_order(iid, price=far, volume=1, side="bid")
       if not r.success: print("failed at", k, time.time() - t0, r.error_reason); break
   print(k + 1, "inserts in", time.time() - t0, "s; connected:", ex.is_connected())
   ```
5. **Which calls are local (no request)?** Safe: assume every call costs one.
   ```python
   for name, f in [("book", lambda: ex.get_last_price_book(iid)), ("positions", ex.get_positions),
                   ("orders", lambda: ex.get_outstanding_orders(iid)), ("poll", lambda: ex.poll_new_trade_ticks(iid))]:
       t0 = time.time(); [f() for _ in range(10)]; print(name, (time.time() - t0) / 10)   # microseconds => local
   ```
6. **Does the book include your own orders?** Safe: yes.
   ```python
   ex.insert_order(iid, price=to_price(w[0] - 37, tick), volume=1, side="bid"); time.sleep(0.5)
   print([(l.price, l.volume) for l in ex.get_last_price_book(iid).bids])     # is the 1-lot level there?
   ```
7. **Is `OrderStatus.volume` the remaining volume, and how fast does `get_positions()` show a fill?**
   Safe: remaining; assume a short lag (`cut()` waits 1 s before repeating). Quote 10 lots one tick
   inside a wall, and when `ex.poll_new_trades(iid)` shows a partial fill print
   `ex.get_outstanding_orders(iid)` and `ex.get_positions()[iid]` at once and 0.2 s later.
8. **Fixed price limits, social feed, counterparty data.**
   ```python
   print({k: getattr(v, "price_limit", "no attribute") for k, v in ex.get_instruments().items()})
   time.sleep(60); print(ex.get_social_media_feeds_history()[-5:])           # posts? are the fields filled?
   from optibook.historical_data_loader import HistoricalDataLoader
   print(HistoricalDataLoader().get_counterparty_data_window())              # (start, end) or None
   print(ex.is_connected())                                                   # did the loader call kick us?
   ```
9. **Can your own bid and ask trade with each other?** Do not test. `requote()` never inserts a
   quote that would cross one of your own resting orders.
10. **Ask the organizers:** is the final PnL marked at the last traded price; is the reset a restart
    of the exchange (new `exchange_started_at`); do the organizer bots and walls behave the same in
    the competition as in practice; the exact start and end times.
