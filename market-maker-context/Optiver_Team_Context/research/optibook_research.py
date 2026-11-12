#!/usr/bin/env python3
"""Optibook historical diagnostic. Does NOT open Exchange or submit orders.

Based on the supplied official Bona Fide examples, 2026-11-12.
Uses only HistoricalDataLoader and the documented trades/pricebooks schemas.
Results are an exploratory signal screen, NOT an executable backtest.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

RAW_NAMES = ("trades", "pricebooks", "orders")
BASE_COLS = ["timestamp_ns", "instrument_id", "bid", "ask", "bid_volume",
             "ask_volume", "mid", "spread", "imbalance", "microprice", "valid"]


def utc_argument(value: str) -> datetime:
    """Accepts ISO 8601; a time without a timezone is explicitly interpreted as UTC."""
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def clean_times(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    needed = {"timestamp_ns", "instrument_id"}
    if not needed.issubset(df.columns):
        raise ValueError("Missing timestamp_ns/instrument_id: inspect the actual schema.")
    out = df.copy()
    out["timestamp_ns"] = pd.to_numeric(out["timestamp_ns"], errors="coerce")
    out = out.dropna(subset=["timestamp_ns", "instrument_id"])
    out = out[np.isfinite(out["timestamp_ns"])]
    out["timestamp_ns"] = out["timestamp_ns"].astype("int64")
    out["instrument_id"] = out["instrument_id"].astype(str)
    return out.sort_values("timestamp_ns", kind="mergesort").reset_index(drop=True)


def best_level(value: Any, bid_side: bool) -> Tuple[float, float]:
    """Documented format: JSON [price, volume] pairs. Aggregates identical prices."""
    levels = json.loads(value) if isinstance(value, str) else value
    if not isinstance(levels, (list, tuple)) or len(levels) == 0:
        raise ValueError("Empty side or unexpected format.")
    usable = []
    for level in levels:
        if not isinstance(level, (list, tuple)) or len(level) != 2:
            raise ValueError("Expected [price, volume].")
        p, v = float(level[0]), float(level[1])
        if not (math.isfinite(p) and math.isfinite(v)) or p < 0 or v < 0:
            raise ValueError("Invalid level.")
        if v > 0:
            usable.append((p, v))
    if not usable:
        raise ValueError("No positive volume.")
    price = (max if bid_side else min)(p for p, _ in usable)
    return price, sum(v for p, v in usable if p == price)


def flatten_books(raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    quality = {"raw_snapshots": len(raw), "invalid_snapshots": 0,
               "duplicate_symbol_timestamp": 0}
    if raw.empty:
        return pd.DataFrame(columns=BASE_COLS), quality
    required = {"timestamp_ns", "instrument_id", "bids_json", "asks_json"}
    if not required.issubset(raw.columns):
        raise ValueError("Pricebooks does not contain the documented schema: " + str(sorted(required)))
    raw = clean_times(raw)
    quality["duplicate_symbol_timestamp"] = int(
        raw.duplicated(["instrument_id", "timestamp_ns"]).sum())
    # Without a sequence ID, retain the last received row for each timestamp.
    # Report duplicate counts; ordering within a timestamp is not established.
    raw = raw.drop_duplicates(["instrument_id", "timestamp_ns"], keep="last")
    rows = []
    for row in raw.itertuples(index=False):
        item = {"timestamp_ns": int(row.timestamp_ns), "instrument_id": row.instrument_id,
                **{k: np.nan for k in BASE_COLS[2:-1]}, "valid": False}
        try:
            b, vb = best_level(row.bids_json, True)
            a, va = best_level(row.asks_json, False)
            # Empty, locked, or crossed books are unusable for this test.
            if b >= a or (b + a) <= 0 or min(vb, va) < 1:
                raise ValueError("Unusable book.")
            item.update(bid=b, ask=a, bid_volume=vb, ask_volume=va,
                        mid=(a+b)/2, spread=a-b, imbalance=(vb-va)/(vb+va),
                        microprice=(a*vb+b*va)/(vb+va), valid=True)
        except (ValueError, TypeError, IndexError, OverflowError):
            quality["invalid_snapshots"] += 1
        # Retain invalid rows: do NOT extend an earlier book across an empty book.
        rows.append(item)
    return pd.DataFrame(rows, columns=BASE_COLS), quality


def causal_grid(books: pd.DataFrame, max_age_s: float) -> pd.DataFrame:
    """One-second grid. Uses only snapshots with timestamp <= decision time."""
    if books.empty:
        return pd.DataFrame()
    right = books.sort_values("timestamp_ns").copy()
    first = pd.to_datetime(int(right.timestamp_ns.min()), unit="ns", utc=True).ceil("s")
    last = pd.to_datetime(int(right.timestamp_ns.max()), unit="ns", utc=True).floor("s")
    if first > last:
        return pd.DataFrame()
    times = pd.date_range(first, last, freq="1s")
    left = pd.DataFrame({"decision_time": times})
    right["book_time"] = pd.to_datetime(right.timestamp_ns, unit="ns", utc=True)
    result = pd.merge_asof(left, right, left_on="decision_time", right_on="book_time",
                           direction="backward", tolerance=pd.Timedelta(seconds=max_age_s))
    result["age_s"] = (result.decision_time-result.book_time).dt.total_seconds()
    result["valid"] = result["valid"].fillna(False).astype(bool)
    return result.set_index("decision_time")


def trade_flow(grid: pd.DataFrame, trades: pd.DataFrame, window_s: int = 5) -> np.ndarray:
    """Signed flow in (t-window_s, t]; bid=aggressive buy, ask=aggressive sell."""
    if trades.empty or not {"volume", "aggressor_side"}.issubset(trades.columns):
        return np.full(len(grid), np.nan)
    t = clean_times(trades)
    t["volume"] = pd.to_numeric(t.volume, errors="coerce")
    side = t.aggressor_side.astype(str).str.lower()
    valid = t.volume.notna() & np.isfinite(t.volume) & (t.volume > 0) & side.isin(["bid", "ask"])
    t = t.loc[valid].copy()
    if t.empty:
        return np.full(len(grid), np.nan)
    ns = t.timestamp_ns.to_numpy(dtype=np.int64)
    v = t.volume.to_numpy(dtype=float)
    s = np.where(t.aggressor_side.astype(str).str.lower() == "bid", 1.0, -1.0)
    cv = np.concatenate([[0.0], np.cumsum(v)])
    cs = np.concatenate([[0.0], np.cumsum(v*s)])
    now = np.array([x.value for x in grid.index], dtype=np.int64)
    hi = np.searchsorted(ns, now, side="right")
    lo = np.searchsorted(ns, now-window_s*1_000_000_000, side="right")
    total, signed = cv[hi]-cv[lo], cs[hi]-cs[lo]
    return np.divide(signed, total, out=np.full(len(now), np.nan), where=total > 0)


def signal_series(grid: pd.DataFrame, trades: pd.DataFrame) -> Dict[str, np.ndarray]:
    imbalance = grid.imbalance.to_numpy(dtype=float)
    flow = trade_flow(grid, trades)
    momentum = (grid.mid-grid.mid.shift(5)).to_numpy(dtype=float)

    def threshold(x: np.ndarray, limit: float) -> np.ndarray:
        return np.where(np.isfinite(x) & (np.abs(x) > limit), np.sign(x), 0.0)

    return {
        "obi_0.5": threshold(imbalance, 0.5),
        "flow_5s_0.4": threshold(flow, 0.4),
        "momentum_5s": threshold(momentum, 0.0),
        "reversion_5s": -threshold(momentum, 0.0),
        # Controls, NOT recommendations: help detect simple market drift.
        "control_long": np.ones(len(grid)),
        "control_short": -np.ones(len(grid)),
    }


def screen_one(grid: pd.DataFrame, trades: pd.DataFrame, symbol: str,
               split: pd.Timestamp, horizons: List[int], latency_s: int,
               fee_per_side: float, min_observations: int) -> pd.DataFrame:
    """Each row represents a mean over HYPOTHETICAL one-lot trades.

    Signal at t; entry at the observed book at t+latency; exit at t+latency+H.
    Does not estimate priority, passive fills, impact, shared limits, or actual profits.
    """
    if grid.empty:
        return pd.DataFrame()
    signals = signal_series(grid, trades)
    rows = []
    for h in horizons:
        offset = latency_s + h
        entry_ask = grid.ask.shift(-latency_s)
        entry_bid = grid.bid.shift(-latency_s)
        exit_bid = grid.bid.shift(-offset)
        exit_ask = grid.ask.shift(-offset)
        long_edge = (exit_bid-entry_ask-2*fee_per_side).to_numpy(dtype=float)
        short_edge = (entry_bid-exit_ask-2*fee_per_side).to_numpy(dtype=float)
        future_mid = grid.mid.shift(-offset).to_numpy(dtype=float)
        valid = (grid.valid.to_numpy(dtype=bool) &
                 np.isfinite(long_edge) & np.isfinite(short_edge))
        end_times = grid.index + pd.Timedelta(seconds=offset)
        parts = {
            # Purge: training exits must not extend into validation.
            "train": (grid.index < split) & (end_times < split),
            "validation": grid.index >= split,
        }
        for phase, phase_mask in parts.items():
            # Space times before filtering the signal to avoid counting overlapping trades.
            candidates = np.flatnonzero(phase_mask)[::offset+1]
            sampling = np.zeros(len(grid), dtype=bool)
            sampling[candidates] = True
            for name, sign in signals.items():
                mask = sampling & valid & (sign != 0)
                edge = np.where(sign > 0, long_edge, short_edge)[mask]
                move = (sign*(future_mid-grid.mid.to_numpy(dtype=float)))[mask]
                n = int(mask.sum())
                rows.append({
                    "instrument_id": symbol, "signal": name, "horizon_s": h,
                    "phase": phase, "n_nonoverlap": n,
                    "mean_crossing_edge": float(np.mean(edge)) if n else np.nan,
                    "median_crossing_edge": float(np.median(edge)) if n else np.nan,
                    "q10_crossing_edge": float(np.quantile(edge, .1)) if n else np.nan,
                    "positive_edge_fraction": float(np.mean(edge > 0)) if n else np.nan,
                    "mean_signed_mid_move": float(np.mean(move)) if n else np.nan,
                    "n_long": int(np.sum(sign[mask] > 0)),
                    "n_short": int(np.sum(sign[mask] < 0)),
                    "evidence": "EXPLORATORY_ONLY" if n >= min_observations else "TOO_FEW_OBSERVATIONS",
                })
    return pd.DataFrame(rows)


def analyze(raw: Dict[str, pd.DataFrame], out: Path, args: argparse.Namespace,
            manifest: Dict[str, Any]) -> None:
    books, quality = flatten_books(raw.get("pricebooks", pd.DataFrame()))
    trades = clean_times(raw.get("trades", pd.DataFrame()))
    manifest["quality"] = quality
    summary, screens = [], []
    if not books.empty:
        ns_min, ns_max = int(books.timestamp_ns.min()), int(books.timestamp_ns.max())
        split_ns = ns_min + int(.7*(ns_max-ns_min))
        split = pd.to_datetime(split_ns, unit="ns", utc=True)
        manifest["split_70_percent_utc"] = split.isoformat()
        manifest["observed_start_utc"] = pd.to_datetime(ns_min, unit="ns", utc=True).isoformat()
        manifest["observed_end_utc"] = pd.to_datetime(ns_max, unit="ns", utc=True).isoformat()
        for symbol, b in books.groupby("instrument_id", sort=True):
            grid = causal_grid(b, args.max_age_s)
            t = trades.loc[trades.instrument_id == symbol] if not trades.empty else pd.DataFrame()
            usable = grid.loc[grid.valid] if not grid.empty else pd.DataFrame()
            summary.append({
                "instrument_id": symbol, "snapshots": len(b), "trades": len(t),
                "grid_seconds": len(grid), "usable_grid_seconds": len(usable),
                "usable_fraction": len(usable)/len(grid) if len(grid) else 0,
                "median_spread": float(usable.spread.median()) if len(usable) else np.nan,
                "median_spread_bps": float((10000*usable.spread/usable.mid).median()) if len(usable) else np.nan,
                "median_top_bid_volume": float(usable.bid_volume.median()) if len(usable) else np.nan,
                "median_top_ask_volume": float(usable.ask_volume.median()) if len(usable) else np.nan,
            })
            screens.append(screen_one(grid, t, str(symbol), split, args.horizons,
                                      args.latency_s, args.fee_per_side, args.min_observations))
    summary_df = pd.DataFrame(summary)
    screen_df = pd.concat(screens, ignore_index=True) if screens else pd.DataFrame()
    summary_df.to_csv(out/"summary.csv", index=False)
    screen_df.to_csv(out/"signal_screen.csv", index=False)
    if not books.empty:
        books.tail(1000).to_csv(out/"book_features_sample.csv", index=False)
    manifest["analysis_settings"] = {
        "grid_seconds": 1, "max_book_age_seconds": args.max_age_s,
        "horizons_seconds": args.horizons, "assumed_latency_seconds": args.latency_s,
        "assumed_fee_per_side_price_units": args.fee_per_side,
        "fees_verified": False, "minimum_observations_warning": args.min_observations,
        "models_trained": False, "orders_sent": 0, "exchange_connection_opened": False,
    }
    (out/"metadata.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# Historical diagnostic — not a bot or a PnL backtest",
        "", "HistoricalDataLoader only: does not create Exchange or submit/cancel orders.",
        "", "## Interpretation",
        "- summary.csv: visible liquidity and temporal data coverage.",
        "- signal_screen.csv: fixed, predeclared signals versus subsequent movements.",
        "- mean_crossing_edge: buy at the entry ask and sell at the exit bid;",
        "  for shorts, sell at the bid and buy back at the ask. One hypothetical lot, no impact.",
        "- Price units, NOT total portfolio profit. Do not sum rows as PnL.",
        "- Includes the spread at both executions and the fee ASSUMED through the parameter.",
        "- Signal is calculated at t; entry uses t+latency and exit uses t+latency+horizon.",
        "- Backward alignment; does not fill using snapshots after the evaluated time.",
        "- max_age_s is an analytical choice, not an Optibook rule.",
        "- First 70% of time: train. Last 30%: validation. Labels purged at the boundary.",
        "- Signals/thresholds are not fitted here. Choosing the best by looking at validation requires",
        "  a later test on fresh data; many alternatives are being compared.",
        "- Non-overlapping observations within each test; they may still be correlated.",
        "- n >= minimum does NOT imply statistical significance or a proven edge.",
        "- Does not estimate passive fills, queues, actual latency, impact, or portfolio risk.",
        "- OBI and microprice use the same best level: they are not two independent tests.",
        "- Does not reconstruct cancellation events from orders without knowing their semantics.",
        "- Does not assume persistent identities for anonymized counterparties.",
        "- Does not infer tick_size or limits from historical price differences.",
        "- Avoid ranges spanning administrative resets or sessions with different dynamics.",
        "", "## Observed data",
        f"Raw snapshots: {quality['raw_snapshots']}",
        f"Invalid snapshots (after deduplication): {quality['invalid_snapshots']}",
        f"Duplicate symbol/timestamp rows: {quality['duplicate_symbol_timestamp']}",
        f"Assumed fee per side: {args.fee_per_side} (not verified).",
        "", "## Instrument summary", "```",
        summary_df.to_string(index=False) if len(summary_df) else "NO USABLE PRICEBOOKS.",
        "```", "", "## Next decision",
        "Look for signals with stable direction in train and validation, sufficient observations",
        "and margin after spreads. Then test in practice with small size and actual limits.",
        "A negative crossing result does not rule out passive market making: it requires measuring",
        "fills and adverse selection separately. Do not activate trading automatically.",
    ]
    errors = manifest.get("endpoint_errors", {})
    if errors:
        lines += ["", "## Download warnings", json.dumps(errors, ensure_ascii=False)]
    (out/"REPORT.md").write_text("\n".join(lines)+"\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--minutes", type=int, default=30, help="Initial window; does not search other dates automatically.")
    p.add_argument("--start", type=utc_argument, help="ISO UTC; a time without a timezone is also interpreted as UTC.")
    p.add_argument("--end", type=utc_argument, help="ISO UTC; defaults to the current UTC time.")
    p.add_argument("--out", type=Path, default=Path("research_"+datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")))
    p.add_argument("--offline", type=Path, help="Reads raw_trades.csv.gz and raw_pricebooks.csv.gz without Optibook.")
    p.add_argument("--include-orders", action="store_true", help="Also downloads orders; does not reconstruct the book.")
    p.add_argument("--horizons", type=int, nargs="+", default=[1, 5, 10, 30])
    p.add_argument("--latency-s", type=int, default=1, help="Assumed delay on the one-second grid, not measured.")
    p.add_argument("--max-age-s", type=float, default=2.0, help="Maximum snapshot age used in the analysis.")
    p.add_argument("--fee-per-side", type=float, default=0.0, help="Assumed fee per lot per side in price units.")
    p.add_argument("--min-observations", type=int, default=30, help="Warning threshold, NOT a significance test.")
    args = p.parse_args()
    if not (1 <= args.minutes <= 1440) or args.latency_s < 0 or not (0 < args.max_age_s <= 86400):
        p.error("minutes must be between 1 and 1440; latency-s >= 0; max-age-s positive and <= 86400.")
    if not args.horizons or min(args.horizons) < 1 or max(args.horizons)+args.latency_s >= 86400:
        p.error("Positive integer horizons and horizon+latency shorter than one day.")
    if not math.isfinite(args.fee_per_side) or args.fee_per_side < 0 or args.min_observations < 1:
        p.error("fee-per-side must be finite and nonnegative; min-observations >= 1.")
    end = args.end or datetime.now(timezone.utc)
    start = args.start or end-timedelta(minutes=args.minutes)
    if end <= start or (end-start).total_seconds() > 86400:
        p.error("Each run must cover a positive range of at most one day.")
    try:
        args.out.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        p.error("The output directory already exists; use a different --out to avoid mixing sessions.")
    manifest = {"source": "offline" if args.offline else "HistoricalDataLoader",
                "requested_start_utc": start.isoformat(), "requested_end_utc": end.isoformat(),
                "endpoint_errors": {}, "schemas": {}}
    raw: Dict[str, pd.DataFrame] = {}
    names = ["trades", "pricebooks"]+(["orders"] if args.include_orders else [])
    if args.offline:
        for name in names:
            raw[name] = read_csv_or_empty(args.offline/f"raw_{name}.csv.gz")
    else:
        try:
            from optibook.historical_data_loader import HistoricalDataLoader
            loader = HistoricalDataLoader()
        except Exception as exc:
            print("Could not initialize HistoricalDataLoader: " + type(exc).__name__, file=sys.stderr)
            print("Use /opt/venv/bin/python in the official workspace and check the historical API.", file=sys.stderr)
            return 2
        print(f"UTC range: {start.isoformat()} to {end.isoformat()}", flush=True)
        # The official examples use UTC datetimes without tzinfo.
        api_start, api_end = start.replace(tzinfo=None), end.replace(tzinfo=None)
        for name in names:
            try:
                print(f"Downloading {name}...", flush=True)
                frame = getattr(loader, f"get_{name}_df")(api_start, api_end)
                if not isinstance(frame, pd.DataFrame):
                    raise TypeError("The endpoint does not return a DataFrame.")
                raw[name] = frame
                print(f"{name}: {len(frame)} rows", flush=True)
            except Exception as exc:
                # Do not copy messages that might contain URLs with tokens or credentials.
                manifest["endpoint_errors"][name] = type(exc).__name__
                raw[name] = pd.DataFrame()
                print(f"{name}: failure {type(exc).__name__}; downloaded data are retained.", flush=True)
            finally:
                time.sleep(0.5)
    for name, frame in raw.items():
        manifest["schemas"][name] = {"rows": len(frame), "columns": list(frame.columns),
                                     "dtypes": {str(k): str(v) for k, v in frame.dtypes.items()}}
        frame.to_csv(args.out/f"raw_{name}.csv.gz", index=False, compression="gzip")
    try:
        analyze(raw, args.out, args, manifest)
    except Exception as exc:
        manifest["analysis_error"] = type(exc).__name__
        (args.out/"metadata.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print("Analysis not completed: " + type(exc).__name__ + ". Raw data were retained.", file=sys.stderr)
    # Only files produced by this run. Does not package configuration or credentials.
    archive = args.out/"diagnostico_optibook.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(args.out.iterdir()):
            if f.is_file() and f.name != archive.name:
                z.write(f, arcname=f.name)
    print(f"\nArchive to review: {archive.resolve()}")
    print("No Exchange connection was opened and no orders were sent.")
    if raw.get("pricebooks", pd.DataFrame()).empty:
        print("No pricebooks: confirm the available historical interval with the organizer; no signals are invented.")
    return 0 if "analysis_error" not in manifest else 3


if __name__ == "__main__":
    raise SystemExit(main())
