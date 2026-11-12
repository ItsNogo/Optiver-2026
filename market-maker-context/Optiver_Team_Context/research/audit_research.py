#!/usr/bin/env python3
"""Reproduce and audit a local Optibook historical diagnostic, entirely offline.

Example, from the repository root:
    python research/audit_research.py \
        --input data/raw/diagnostic \
        --out runs/audit_20261112 \
        --research-script research/optibook_research.py

The input directory must contain the unpacked original diagnostic. The supplied
research script is imported for its pure analytical functions; its main() is not
called. Use the reviewed research script supplied with this repository. This
audit does not create Exchange, call HistoricalDataLoader, or submit orders.

The five-second imbalance sensitivity checks inspect already observed data.
They are exploratory robustness checks, not a new holdout or executable PnL.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd


def load_analysis_module(path: Path):
    spec = importlib.util.spec_from_file_location("reviewed_optibook_research", path)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load the supplied research script.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in ("flatten_books", "causal_grid", "screen_one", "signal_series"):
        if not callable(getattr(module, name, None)):
            raise ValueError(f"Research script is missing required function: {name}")
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", type=Path, required=True, help="Unpacked original diagnostic directory.")
    parser.add_argument("--out", type=Path, required=True, help="New output directory; must not already exist.")
    parser.add_argument("--research-script", type=Path, required=True, help="Reviewed optibook_research.py or its original equivalent.")
    args = parser.parse_args()
    for filename in ("raw_pricebooks.csv.gz", "raw_trades.csv.gz", "metadata.json", "signal_screen.csv"):
        if not (args.input / filename).is_file():
            parser.error(f"Input directory is missing {filename}.")
    if not args.research_script.is_file():
        parser.error("The supplied research-script path is not a regular file.")
    if args.out.exists():
        parser.error("Output directory already exists; choose a new directory to avoid mixing runs.")

    research = load_analysis_module(args.research_script)
    metadata = json.loads((args.input / "metadata.json").read_text(encoding="utf-8"))
    settings = metadata["analysis_settings"]
    required_settings = {
        "grid_seconds": 1,
        "max_book_age_seconds": 2.0,
        "horizons_seconds": [1, 5, 10, 30],
        "assumed_latency_seconds": 1,
        "assumed_fee_per_side_price_units": 0.0,
    }
    for name, expected in required_settings.items():
        if settings.get(name) != expected:
            parser.error(f"This audit reproduces the recovered settings; unexpected {name}: {settings.get(name)!r}.")

    raw = pd.read_csv(args.input / "raw_pricebooks.csv.gz")
    trades = pd.read_csv(args.input / "raw_trades.csv.gz")
    books, quality = research.flatten_books(raw)
    split = pd.Timestamp(metadata["split_70_percent_utc"])
    first = pd.Timestamp(metadata["observed_start_utc"]).ceil("s")
    block_rows, offset_rows, outlier_rows, reproductions = [], [], [], []

    for symbol, instrument_books in books.groupby("instrument_id", sort=True):
        grid = research.causal_grid(instrument_books, 2.0)
        instrument_trades = trades.loc[trades.instrument_id == symbol]
        reproductions.append(research.screen_one(
            grid, instrument_trades, str(symbol), split, [1, 5, 10, 30],
            1, 0.0, int(settings["minimum_observations_warning"])))

        sign = research.signal_series(grid, instrument_trades)["obi_0.5"]
        horizon, latency = 5, 1
        offset = latency + horizon
        long_edge = (grid.bid.shift(-offset) - grid.ask.shift(-latency)).to_numpy()
        short_edge = (grid.bid.shift(-latency) - grid.ask.shift(-offset)).to_numpy()
        edge = np.where(sign > 0, long_edge, short_edge)
        move = sign * (grid.mid.shift(-offset).to_numpy() - grid.mid.to_numpy())
        valid = grid.valid.to_numpy() & np.isfinite(long_edge) & np.isfinite(short_edge) & (sign != 0)

        # Fixed chronological blocks; an exit must remain inside its block.
        # The last block is shorter when the returned dataset ends early.
        for block in range(6):
            low = first + pd.Timedelta(minutes=5 * block)
            high = low + pd.Timedelta(minutes=5)
            block_mask = (grid.index >= low) & (grid.index + pd.Timedelta(seconds=offset) < high)
            candidates = np.flatnonzero(block_mask)[::offset + 1]
            selected = candidates[valid[candidates]]
            block_rows.append({
                "instrument_id": symbol, "signal": "obi_0.5", "horizon_s": horizon,
                "block": block + 1, "start_utc": str(low), "end_utc": str(min(high, grid.index.max())),
                "n": len(selected),
                "mean_crossing_edge": float(np.mean(edge[selected])) if len(selected) else np.nan,
                "mean_signed_mid_move": float(np.mean(move[selected])) if len(selected) else np.nan,
            })

        phases = (
            ("train", (grid.index < split) & (grid.index + pd.Timedelta(seconds=offset) < split)),
            ("validation", grid.index >= split),
        )
        for phase, phase_mask in phases:
            candidates = np.flatnonzero(phase_mask)
            # These seven offsets share data. Do not add their sample counts or
            # pick the best offset and call it an independent validation result.
            for sampling_offset in range(offset + 1):
                selected = candidates[sampling_offset::offset + 1]
                selected = selected[valid[selected]]
                outcomes = edge[selected]
                offset_rows.append({
                    "instrument_id": symbol, "signal": "obi_0.5", "horizon_s": horizon,
                    "phase": phase, "sampling_offset_s": sampling_offset, "n": len(selected),
                    "mean_crossing_edge": float(np.mean(outcomes)) if len(outcomes) else np.nan,
                    "mean_signed_mid_move": float(np.mean(move[selected])) if len(outcomes) else np.nan,
                })
                if sampling_offset == 0:
                    outlier_rows.append({
                        "instrument_id": symbol, "phase": phase, "n": len(outcomes),
                        # A small tolerance avoids treating roundoff at zero as profit.
                        "positive": int((outcomes > 1e-10).sum()),
                        "mean": float(np.mean(outcomes)) if len(outcomes) else None,
                        "median": float(np.median(outcomes)) if len(outcomes) else None,
                        "min": float(np.min(outcomes)) if len(outcomes) else None,
                        "max": float(np.max(outcomes)) if len(outcomes) else None,
                        "mean_without_largest": float(np.mean(np.delete(outcomes, np.argmax(outcomes)))) if len(outcomes) > 1 else None,
                    })

    original = pd.read_csv(args.input / "signal_screen.csv")
    reproduced = pd.concat(reproductions, ignore_index=True)
    keys = ["instrument_id", "signal", "horizon_s", "phase"]
    original = original.sort_values(keys).reset_index(drop=True)
    reproduced = reproduced.sort_values(keys).reset_index(drop=True)
    pd.testing.assert_frame_equal(original[keys], reproduced[keys])
    compared_metrics = ["n_nonoverlap", "mean_crossing_edge", "median_crossing_edge", "mean_signed_mid_move", "n_long", "n_short"]
    for metric in compared_metrics:
        if not np.allclose(original[metric], reproduced[metric], rtol=1e-12, atol=1e-12, equal_nan=True):
            raise AssertionError(f"Original diagnostic does not reproduce for {metric}.")

    # Write only after reproduction succeeds. Original files are never modified.
    args.out.mkdir(parents=True, exist_ok=False)
    pd.DataFrame(block_rows).to_csv(args.out / "curated_obi_5s_blocks.csv", index=False)
    pd.DataFrame(offset_rows).to_csv(args.out / "curated_obi_5s_sampling_offsets.csv", index=False)
    pd.DataFrame(outlier_rows).to_csv(args.out / "curated_obi_5s_outlier_sensitivity.csv", index=False)
    training = original.loc[original.phase == "train"]
    validation = original.loc[original.phase == "validation"]
    training.merge(validation, on=["instrument_id", "signal", "horizon_s"], suffixes=("_train", "_val")).to_csv(
        args.out / "curated_signal_comparison.csv", index=False)

    audit_metadata = {
        "mode": "offline_only",
        "exchange_connection_opened": False,
        "orders_sent": 0,
        "research_script_sha256": hashlib.sha256(args.research_script.read_bytes()).hexdigest(),
        "original_screen_rows_reproduced": len(original),
        "compared_metrics": compared_metrics,
        "quality": quality,
        "sensitivity_rule": "obi_0.5",
        "sensitivity_horizon_s": 5,
        "sampling_offsets": 7,
        "fixed_block_minutes": 5,
        "fixed_block_count": 6,
        "positive_outcome_numerical_tolerance": 1e-10,
        "interpretation": "Exploratory sensitivity on existing data, not a new holdout or executable PnL.",
        "buyer_null_fraction": float(trades.buyer.isna().mean()),
        "seller_null_fraction": float(trades.seller.isna().mean()),
        "duplicate_trade_id_session_pairs": int(trades.duplicated(["trade_id", "exchange_started_at"]).sum()),
        "exchange_session_ids": raw.exchange_started_at.drop_duplicates().tolist(),
    }
    (args.out / "audit_metadata.json").write_text(json.dumps(audit_metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Reproduced {len(original)} original screen rows. Saved four sensitivity tables and audit_metadata.json.")
    print("Offline audit only. No Exchange connection or orders. Sensitivity tables are not a new holdout.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
