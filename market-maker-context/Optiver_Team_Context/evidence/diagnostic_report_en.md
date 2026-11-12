# Historical diagnostic — not a bot or a PnL backtest

HistoricalDataLoader only: does not create Exchange or submit/cancel orders.

## Interpretation
- summary.csv: visible liquidity and temporal data coverage.
- signal_screen.csv: fixed, predeclared signals versus subsequent movements.
- mean_crossing_edge: buy at the entry ask and sell at the exit bid;
  for shorts, sell at the bid and buy back at the ask. One hypothetical lot, no impact.
- Price units, NOT total portfolio profit. Do not sum rows as PnL.
- Includes the spread at both executions and the fee ASSUMED through the parameter.
- Signal is calculated at t; entry uses t+latency and exit uses t+latency+horizon.
- Backward alignment; does not fill using snapshots after the evaluated time.
- max_age_s is an analytical choice, not an Optibook rule.
- First 70% of time: train. Last 30%: validation. Labels purged at the boundary.
- Signals/thresholds are not fitted here. Choosing the best by looking at validation requires
  a later test on fresh data; many alternatives are being compared.
- Non-overlapping observations within each test; they may still be correlated.
- n >= minimum does NOT imply statistical significance or a proven edge.
- Does not estimate passive fills, queues, actual latency, impact, or portfolio risk.
- OBI and microprice use the same best level: they are not two independent tests.
- Does not reconstruct cancellation events from orders without knowing their semantics.
- Does not assume persistent identities for anonymized counterparties.
- Does not infer tick_size or limits from historical price differences.
- Avoid ranges spanning administrative resets or sessions with different dynamics.

## Observed data
Raw snapshots: 212509
Invalid snapshots (after deduplication): 13
Duplicate symbol/timestamp rows: 0
Assumed fee per side: 0.0 (not verified).

## Instrument summary
```
instrument_id  snapshots  trades  grid_seconds  usable_grid_seconds  usable_fraction  median_spread  median_spread_bps  median_top_bid_volume  median_top_ask_volume
          AMD      33864    1017          1718                 1709         0.994761            0.2          12.414649                   22.0                   17.0
         AVGO      38171    1162          1718                 1708         0.994179            0.2           9.465215                   20.0                   15.0
         CRWV      21986    1167          1718                 1699         0.988941            0.2          14.598540                   20.0                   18.0
           MU      21699    1106          1717                 1703         0.991846            0.2          27.586207                 3003.0                 3002.0
         NBIS      20706    1094          1717                 1706         0.993593            0.2          20.833333                   13.0                   16.0
         NVDA      39939    1636          1717                 1712         0.997088            0.1           7.259528                   26.0                   24.0
         SNDK      17458     976          1718                 1711         0.995925            0.2          32.948929                   24.0                   31.0
          VRT      18686     797          1719                 1706         0.992437            0.2          28.694405                 3003.0                 3004.0
```

## Next decision
Look for signals with stable direction in train and validation, sufficient observations
and margin after spreads. Then test in practice with small size and actual limits.
A negative crossing result does not rule out passive market making: it requires measuring
fills and adverse selection separately. Do not activate trading automatically.
