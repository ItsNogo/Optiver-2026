# Research tools and reproduction

## Contents and scope

`optibook_research.py` is the English adaptation of the diagnostic already created during preparation. It either reads a local raw archive or uses the official `HistoricalDataLoader`. It does not instantiate `Exchange`, insert, cancel, amend, or liquidate orders. Its output is a cost-aware exploratory signal screen, not an execution backtest or trading bot.

`audit_research.py` is an offline audit of the recovered dataset. It verifies the original screen and creates the fixed five-second OBI block, sampling-offset, and outlier summaries. It imports the reviewed diagnostic's analytical functions without invoking its `main()`.

Both need Python with NumPy and pandas. Use the working official environment for historical access; the recovered event interpreter is `/opt/venv/bin/python`. Local offline analysis does not require Optibook. The handover records the environment used for its verification in `evidence/verification_environment.json`; it is a reproduction record, not a demand to replace the event's dependencies.

## 1. Prepare the input

Extract the separate `Optiver_Delft_Research_Data_EN.zip` so these files exist:

| Local path | Purpose |
| --- | --- |
| `data/raw/diagnostic/raw_pricebooks.csv.gz` | Full returned pricebook snapshots |
| `data/raw/diagnostic/raw_trades.csv.gz` | Full returned public trades |
| `data/raw/diagnostic/metadata.json` | Original settings, interval, schemas, and quality information |
| `data/raw/diagnostic/signal_screen.csv` | Original 384-row result to verify |
| `data/raw/diagnostic/summary.csv` | Original instrument summary |
| `data/raw/diagnostic/book_features_sample.csv` | Tail sample; not the full reconstructed feature history |
| `data/raw/diagnostic/REPORT.md` | English explanation of the original diagnostic |

The companion ZIP contains a `diagnostic/` directory: extract it under `data/raw/`. Keep raw data local or in the team's permitted private data channel. The supplied `.gitignore` excludes `data/raw/` and raw compressed CSVs.

## 2. Reproduce the original screen offline

Run from the repository root with a Python interpreter that already has NumPy/pandas:

```bash
python3 research/optibook_research.py \
  --offline data/raw/diagnostic \
  --start 2026-11-12T17:03:20.715896+00:00 \
  --end 2026-11-12T17:33:20.715896+00:00 \
  --horizons 1 5 10 30 \
  --latency-s 1 \
  --max-age-s 2 \
  --fee-per-side 0 \
  --min-observations 30 \
  --out runs/reproduced_20261112
```

The output directory must not exist. Choose a new name for another run. In **offline mode**, `--start` and `--end` record request metadata; they do **not filter** the raw files. This command reproduces the original archive only when the correct archive is supplied. Verify observed boundaries in the result.

## 3. Reproduce the additional audit

```bash
python3 research/audit_research.py \
  --input data/raw/diagnostic \
  --out runs/audit_20261112 \
  --research-script research/optibook_research.py
```

The audit checks the recovered settings, reproduces the original signal metrics, and writes four curated CSVs plus audit metadata. It intentionally rejects a pre-existing output directory. It is designed for this recovered dataset/settings combination; change the audit explicitly if the experimental design changes.

Sampling offsets reuse the same data. They diagnose fragility; choosing the best offset or pooling their sample counts would misrepresent the evidence.

## 4. Obtain a fresh historical window when permitted

Only in the official event workspace, with the historical API available:

```bash
/opt/venv/bin/python research/optibook_research.py \
  --minutes 30 \
  --horizons 1 5 10 30 \
  --latency-s 1 \
  --max-age-s 2 \
  --fee-per-side 0 \
  --out runs/new_window_001
```

The zero-fee argument preserves the earlier unverified assumption. Replace it with a confirmed applicable constant per-side fee when available, or label cost-sensitivity runs. The parameter accepts nonnegative costs; a maker/taker rebate schedule needs an explicit model rather than forcing a negative fee into the original screen.

`--include-orders` also requests historical order records. The diagnostic does not reconstruct their lifecycle or matching priority. Confirm their semantics before inferring cancellations or queues.

Do not rerun the notebook's `Exchange()` setup merely to use historical data. The historical loader initializes from the event configuration independently. The older read-only market scout does open `Exchange` and is not included here.

## Verification already performed

- Original raw-data analysis reproduced the stored signal results.
- English script compiled successfully.
- AST comparison confirmed unchanged structure, identifiers, and numeric constants; explanatory strings/comments were translated.
- English offline results matched the 8-row summary, 384-row signal screen, and 1,000-row sample to `1e-12` tolerance.
- The packaged audit script compiled and ran successfully, reproducing all 384 original screen rows and its four sensitivity tables.

These checks validate the research transformation and numerical reproducibility. They do not validate a live trading bot, passive fill assumptions, or profitable final-round behavior.
