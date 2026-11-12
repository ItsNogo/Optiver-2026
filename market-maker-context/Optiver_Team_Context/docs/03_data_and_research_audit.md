# Historical research audit and the strategy it supports

**Evidence date: 12 November 2026. This chapter separates recovered results, additional offline checks, and proposed experiments.**

## 1. The decision the team should make now

The recovered diagnostic does **not** establish a profitable aggressive trading strategy. Among the 128 non-control instrument/signal/horizon combinations, none has positive average crossing edge in both the training and validation intervals with at least 30 observations in each. The only combination with positive means in both intervals is VRT order-book imbalance at a 30-second horizon, based on only 7 training and 12 validation observations. Its validation mean is just 0.008333 price units per hypothetical lot. Treat that as insufficient evidence, not a winner to deploy.

Several order-book imbalance tests predict a small movement in the expected direction, but that movement is generally too small to pay the cost of crossing the spread at entry and exit. This distinction suggests a productive next experiment: compare a small, inventory-aware passive quoting baseline with the same baseline using one bounded imbalance adjustment. The historical screen does not simulate passive fills, so it cannot tell us whether either version is profitable. Only execution-aware validation and actual practice fills can answer that.

Our practical research sequence is therefore:

1. Prove that the system observes current state, reconciles fills, obeys limits, and records reliable measurements.
2. Run a small passive baseline on a deliberately limited set of instruments.
3. Compare the baseline with one bounded signal change, keeping risk and execution settings fixed.
4. Promote an improvement only if it survives fresh data, realistic costs, and a clear attribution of where the improvement came from.
5. Keep aggressive entries disabled as an alpha strategy until their complete expected edge clears execution costs. Aggressive risk reduction remains a separate, explicitly costed action.

Sources: recovered `diagnostico_optibook.zip`, especially `metadata.json`, `summary.csv`, and `signal_screen.csv`; recovered `optibook_research.py`; independent offline reproduction described below. These are direct project artifacts, not an external claim about real securities markets.

## 2. Exactly what was collected

| Item | Verified value | Interpretation |
|---|---|---|
| Requested start | 2026-11-12 17:03:20.715896 UTC | 18:03:20.715896 CET in Delft and Madrid |
| Requested end | 2026-11-12 17:33:20.715896 UTC | 18:33:20.715896 CET |
| Earliest observed book | 2026-11-12 17:03:20.954666844 UTC | First returned book, not the requested boundary |
| Latest observed book | 2026-11-12 17:31:59.993202268 UTC | Approximately 80.723 seconds earlier than the requested end |
| Observed book span | Approximately 28 minutes 39.039 seconds | A requested 30-minute window is not 30 minutes of complete returned observations |
| Training/validation boundary | 2026-11-12 17:23:24.281641640 UTC | 70% of the observed book time span |
| Raw book snapshots | 212,509 | Across all eight instruments |
| Raw trades | 8,955 | Across all eight instruments |
| Invalid snapshots after deduplication | 13 | Kept as invalid observations; not replaced with an earlier valid book |
| Duplicate instrument/timestamp book rows | 0 | No such duplicates detected in this archive |
| Duplicate trade ID/session pairs | 0 | Additional offline audit |
| Exchange session IDs | One | `2026-11-11T12:28:39.801042+00:00`; no session-ID break observed |
| Historical orders file | Absent | The archive contains books and trades; the mission's availability of orders does not mean this run downloaded them |
| Buyer/seller fields | 100% missing in both columns | Counterparty identity and participant persistence cannot be studied from this archive |
| Recorded endpoint errors | None | Does not explain the missing final approximately 81 seconds |
| Exchange connection opened | False | Metadata and code agree that this research uses the historical loader |
| Orders sent | 0 | The script is a diagnostic, not a trading bot |

One session identifier does not prove that no administrative change or position reset occurred without a change of that identifier. Before combining later downloads, compare session identifiers, known reset times, schemas, and market behavior. Do not silently concatenate pre-reset and post-reset observations as if they came from the same regime.

The two global counts are data volume, not independent sample sizes. After causally sampling a one-second grid, separating training and validation, purging boundary-crossing labels, and spacing hypothetical trades, a signal/horizon may have only a few dozen observations.

`book_features_sample.csv` is the final 1,000 flattened book rows from the combined dataset. It is a diagnostic sample, not a uniform sample across time or instruments, and not the complete feature history. Reconstruct the full grids from the raw files when reproducing the signal screen.

## 3. Instrument-level facts and their practical meaning

The following figures are directly recovered from `summary.csv`. Spreads are price units; basis points are relative to each instrument's midpoint. Top-of-book depth is the median visible quantity at the best price, not guaranteed fill capacity at the time we submit an order.

| Instrument | Book snapshots | Trades | Usable one-second observations | Usable fraction | Median spread | Median spread, bps | Median best-bid size | Median best-ask size |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| AMD | 33,864 | 1,017 | 1,709 / 1,718 | 99.48% | 0.20 | 12.41 | 22 | 17 |
| AVGO | 38,171 | 1,162 | 1,708 / 1,718 | 99.42% | 0.20 | 9.47 | 20 | 15 |
| CRWV | 21,986 | 1,167 | 1,699 / 1,718 | 98.89% | 0.20 | 14.60 | 20 | 18 |
| MU | 21,699 | 1,106 | 1,703 / 1,717 | 99.18% | 0.20 | 27.59 | 3,003 | 3,002 |
| NBIS | 20,706 | 1,094 | 1,706 / 1,717 | 99.36% | 0.20 | 20.83 | 13 | 16 |
| NVDA | 39,939 | 1,636 | 1,712 / 1,717 | 99.71% | 0.10 | 7.26 | 26 | 24 |
| SNDK | 17,458 | 976 | 1,711 / 1,718 | 99.59% | 0.20 | 32.95 | 24 | 31 |
| VRT | 18,686 | 797 | 1,706 / 1,719 | 99.24% | 0.20 | 28.69 | 3,003 | 3,004 |

**NVDA is useful for an execution smoke test:** it has the most observed trades, the most book snapshots, the highest usable-grid fraction, and the smallest median spread. Those are operational reasons to inspect it first, not evidence that its passive strategy has the highest expected profit. More activity can also mean more competition and faster adverse selection.

**AMD and AVGO are useful passive-experiment candidates:** both have substantial observed activity, a median spread of 0.20, and relatively small median displayed queues at the best prices. This provides a concrete reason to measure their actual fills and post-fill movement. It does not justify assuming that joining the best quote will fill, or that improving by one tick remains profitable.

**MU and VRT require special queue awareness:** their median best-level depths are around 3,000 lots. A one-lot quote joining that level may sit behind a large queue. A large visible queue can facilitate aggressive risk reduction while making passive entry less likely. It is not a reason to quote a large quantity. The team's ±100-lot position cap is much smaller than the displayed level sizes.

**NBIS deserves caution for the imbalance overlay:** its imbalance signal changes direction between the training and validation intervals at several horizons. Retain it in the data inventory, but do not enable the same signal coefficient on every instrument merely for symmetry.

**The actual runtime instrument metadata remains authoritative.** The research script deliberately does not infer `tick_size`, lot multipliers, position limits, or price bands from historical price increments. A median spread of 0.20 is not a tick size. Determine whether one-tick improvement is possible from the official tick and the current spread.

## 4. How the original screen works

### 4.1 Books and the causal time grid

For each instrument, the script parses the JSON bid and ask levels. It chooses the highest bid and the lowest ask and sums quantities at identical best prices. It rejects malformed, empty, crossed, locked, or otherwise unusable books. A locked book has bid equal to ask; this diagnostic excludes it, which is an analytical choice rather than a statement that every locked market is intrinsically invalid.

It then creates one decision timestamp per second, starting at the first complete second after the first book and ending at the last complete second before the final book. Every decision uses the most recent book whose exchange timestamp is at or before the decision time, subject to a maximum age of two seconds. This is a backward as-of join. It never fills a missing decision with a book from the future.

Keeping invalid snapshots in the event sequence is important: if an empty or unusable book occurs, the code does not simply skip it and pretend an earlier valid book remained executable. Nevertheless, exchange timestamps do not tell us exactly when our live process received the update. The causal offline join avoids one form of lookahead, but it does not model feed latency or the delay between observation and a live decision.

### 4.2 Signals tested before any model fitting

The original script fits no predictive model. It tests six fixed rules for each instrument at four horizons.

| Signal name | Definition at decision time | Direction of a nonzero trade |
|---|---|---|
| `obi_0.5` | Best-level imbalance has absolute value strictly greater than 0.5 | Positive imbalance means long; negative means short |
| `flow_5s_0.4` | Signed aggressive volume divided by total aggressive volume in the previous five seconds has absolute value strictly greater than 0.4 | Follow the sign of net aggressive flow |
| `momentum_5s` | Current midpoint minus the midpoint five seconds earlier is nonzero | Follow the sign of the change |
| `reversion_5s` | Same five-second midpoint change | Trade against the change |
| `control_long` | Always positive | Long control, useful for detecting market drift |
| `control_short` | Always negative | Short control, useful for detecting market drift |

The flow convention in the recovered code is `aggressor_side='bid'` for an aggressive buy and `'ask'` for an aggressive sale. Preserve this convention only while it agrees with the actual historical-data API specification. Do not reinterpret it from the everyday phrase "trade at the bid," which can refer to the passive price side instead.

The signed-flow window is `(t-5 seconds, t]`. Missing or invalid flow information produces a neutral signal, not a guessed direction. Momentum uses a five-row lag on the one-second grid. Where the current or lagged midpoint is missing, the signal is neutral.

### 4.3 Timing, labels, and hypothetical transaction prices

The settings were:

- One-second decision grid.
- Two-second maximum book age.
- One-second assumed execution delay.
- Holding horizons of 1, 5, 10, and 30 seconds after hypothetical entry.
- Zero assumed fee per side, explicitly not verified.
- A warning threshold of 30 observations, explicitly not a statistical significance test.

For a signal at time `t`, assumed delay `L`, and horizon `H`, the hypothetical long trade uses:

`long_edge = bid(t + L + H) - ask(t + L) - 2 × fee_per_side`

The corresponding short trade uses:

`short_edge = bid(t + L) - ask(t + L + H) - 2 × fee_per_side`

The code selects the long or short value from the signal's sign. This is a one-lot, top-of-book, aggressive round trip. It accounts for paying the entry and exit spreads through the quoted prices. It does not establish that those prices would still be available after submitting real orders, and it does not model volume larger than the available depth.

`mean_signed_mid_move` is a different statistic:

`signal_sign × [mid(t + L + H) - mid(t)]`

It measures movement from decision time, including the assumed one-second delay. It is not entry-to-exit PnL. A favorable move during that delay may be unavailable to the trader because entry occurs later. Do not subtract a generic spread from this midpoint number and label the remainder a verified trading edge.

### 4.4 Time split, purging, and non-overlap

The first 70% of the observed time span is the training interval. The final 30% is validation. A training example is dropped if its hypothetical exit reaches or passes the boundary. This prevents training labels from borrowing returns from validation.

Within each instrument, horizon, and phase, the script samples candidate decision times every `L + H + 1` seconds before filtering by the signal. With `L=1` and `H=5`, decisions are spaced seven seconds apart. This prevents overlapping round trips within that one test. It does not make returns independent; neighboring examples can remain exposed to the same trend or volatility burst. It also does not make different instruments or different signal tests independent.

There are `8 × 6 × 4 = 192` instrument/signal/horizon combinations and 384 phase rows. Excluding the two always-directional controls leaves 128 candidate combinations. Looking across all validation results to choose a favorite is itself a form of tuning. A fresh, later interval is needed for an honest subsequent check.

## 5. The most useful exact results

### 5.1 Promising-looking examples that do not pass a deployment gate

All edges below are price units per hypothetical lot, not dollars of total profit, returns on capital, or a portfolio result.

| Instrument and rule | Horizon | Training n | Training mean crossing edge | Validation n | Validation mean crossing edge | Decision |
|---|---:|---:|---:|---:|---:|---|
| AVGO imbalance | 30 s | 15 | +0.140000 | 9 | -0.011111 | Best training mean among non-control tests; tiny samples and negative validation |
| VRT imbalance | 30 s | 7 | +0.071429 | 12 | +0.008333 | Positive in both phases, but far too little evidence and negligible validation margin |
| AMD reversion | 30 s | 28 | -0.003571 | 12 | +0.133333 | Validation-only improvement does not establish a repeatable edge |
| CRWV reversion | 30 s | 28 | -0.139286 | 8 | +0.837500 | A large validation mean with eight observations is especially vulnerable to exceptional moves |
| MU imbalance | 10 s | 30 | -0.096667 | 24 | +0.112500 | Changes sign between phases; validation sample below warning threshold |
| VRT imbalance | 5 s | 61 | -0.124590 | 44 | +0.015909 | Negative training; positive validation is highly outlier-sensitive |
| NVDA imbalance | 10 s | 58 | -0.132759 | 30 | -0.063333 | More data, but both crossing means are negative |

### 5.2 Why imbalance is still a reasonable research candidate

At a five-second holding horizon, several instruments show a small positive signed midpoint move in both phases while their aggressive round-trip edges remain negative:

| Instrument | Train n | Train signed midpoint move | Train crossing edge | Validation n | Validation signed midpoint move | Validation crossing edge |
|---|---:|---:|---:|---:|---:|---:|
| AMD | 104 | +0.056250 | -0.135577 | 32 | +0.070313 | -0.084375 |
| AVGO | 99 | +0.046465 | -0.152525 | 50 | +0.117000 | -0.040000 |
| MU | 72 | +0.022222 | -0.144444 | 44 | +0.010227 | -0.127273 |
| NVDA | 97 | +0.049485 | -0.129897 | 49 | +0.053061 | -0.077551 |
| SNDK | 89 | +0.024719 | -0.178652 | 39 | +0.047436 | -0.112821 |
| VRT | 61 | +0.046721 | -0.124590 | 44 | +0.172727 | +0.015909 |

This is evidence to test whether an imbalance-aware quote has better fill quality than a neutral quote. It is not permission to turn the signal into immediate market orders. Passive fills occur conditionally: the market may choose to trade against our quote precisely when our valuation is stale. The unconditional midpoint association may disappear, or reverse, among the subset of quotes that actually fill.

NBIS illustrates why one universal coefficient is questionable. At a five-second horizon its training signed midpoint move is +0.037952, while validation is -0.094444; crossing means are -0.139759 and -0.255556 respectively. This is a reason to withhold or disable its imbalance overlay pending fresh evidence.

### 5.3 Additional offline checks performed for this handover

The audit independently loaded the raw compressed CSVs and reran the original analysis functions. All 384 result rows reproduced the stored observation counts, mean and median crossing edges, signed midpoint means, and long/short counts to numerical tolerance. The reported pandas `FutureWarning` concerns future dtype behavior in `fillna`; it did not prevent the current run or change this reproduction. It is not an exchange error.

Two deliberately limited diagnostics were then applied to the existing imbalance rule at the five-second horizon. They are **additional exploratory checks on already observed data**, not a new untouched holdout and not a search for a more favorable threshold.

**Sampling-offset check.** The same non-overlapping sample was shifted through all seven possible one-second offsets. For every instrument, the training crossing mean stayed negative at every offset. Some validation results changed sign substantially. VRT's validation mean ranged from -0.183333 to +0.023913; AVGO's from -0.165854 to +0.142553. These offsets share the same underlying data and must not be pooled as seven independent experiments. Selecting the best offset would be another overfitting step.

**Outlier check.** The original VRT five-second validation result has 44 observations, only three positive edges, and a median of -0.10. Its largest observation is +3.40. Excluding that one observation changes the mean from +0.015909 to -0.062791. This does not justify deleting an inconvenient observation from the official result; it demonstrates that the apparent average benefit is fragile.

For NVDA at the same horizon, the original validation mean is -0.077551, and removing its largest positive observation changes it to -0.114583. Its training crossing means across the seven offsets range from -0.148980 to -0.113861; validation ranges from -0.142553 to -0.051220. A favorable midpoint signal and a profitable crossing strategy remain different propositions.

A six-block chronological check used fixed five-minute windows from the first whole observed second, with exits required to remain inside each block. The final window is shorter because the data end early. For NVDA, all six crossing means remained negative. For VRT, all six remained negative. Small samples and different sampling origins mean block values will not average mechanically to the original phase values. These checks strengthen the reason to avoid treating a positive isolated cell as a stable aggressive strategy.

Curated audit tables: `evidence/signal_comparison.csv`, `evidence/obi_5s_blocks.csv`, `evidence/obi_5s_sampling_offsets.csv`, and `evidence/obi_5s_outlier_sensitivity.csv`. The original observations remain unchanged.

## 6. A precise passive-baseline experiment

### 6.1 Define the components separately

Let `b` and `a` be the best observed bid and ask; `Vb` and `Va` their displayed sizes; `m=(a+b)/2`; `s=a-b`; `q` the executed inventory; and `tau` the verified tick size.

`I = (Vb - Va) / (Vb + Va)`

`microprice = (a × Vb + b × Va) / (Vb + Va)`

`microprice - m = (s / 2) × I`

The last equation shows that top-level imbalance and this microprice displacement contain the same snapshot information. Including both as if they were independent votes double-counts the signal. Actual order-flow imbalance measures changes in supply and demand through time and is a different feature; the current archive screen did not implement that full event-based feature.

Define a neutral baseline fair value `f=m`. Define one experimental variant as:

`f = m + alpha × (microprice - m)`

Choose the trial value of `alpha` before the trial, keep it bounded, and compare it with `alpha=0`. The data do not supply an optimal value. For a first controlled test, an illustrative small coefficient such as 0.25 is an experimental choice, not a discovered constant. A quote tick may erase this adjustment, so record the actual rounded quotes; do not attribute a performance change to a signal that never changed an order.

Apply the inventory adjustment separately:

`reservation_price = f - k_inventory × q`

Here `k_inventory` has price-per-lot units. A positive inventory lowers the reservation price, discouraging additional buying and encouraging selling. A negative inventory raises it. Do not use one unscaled numerical coefficient across assets with different prices, tick sizes, or volatility simply because all symbols share a ±100-lot limit.

Construct desired bid and ask around that reservation price with a half-width that covers costs, adverse-selection uncertainty, and inventory tolerance. A simple formula is a control surface for experiments, not a calibration proof:

`desired_bid = floor_to_tick(reservation_price - half_width)`

`desired_ask = ceil_to_tick(reservation_price + half_width)`

After rounding, recheck the spread, current opposite-side quotes, price bands, size limits, and outstanding-order reservations. A passive limit order can become marketable if the market moves before it arrives. The supplied insert_order signature supports limit and ioc, with no documented post-only argument. A passive-intended bid must be strictly below the observed ask and an ask strictly above the observed bid, also avoiding the team's own orders. Use a conservative non-crossing margin and observe actual executions; a market move before arrival can still make a limit order marketable.

### 6.2 What changes and what stays fixed in an experiment

The first comparison should hold the following fixed: instrument set, lot size, inventory budgets, quote lifetime policy, stale-data rule, execution implementation, and evaluation duration. Change only the signal adjustment. If several components change together, a better outcome cannot be attributed to imbalance.

Keep one live account owner. A second strategy can calculate shadow quotes from the same snapshots without sending orders; this helps compare decisions but is not an executable PnL test because its fills are unknown. Never compare the live strategy's real fills with the shadow strategy's assumption that every touched quote fills.

Sequential trials are affected by changing market conditions and other teams' bots. Use short, predeclared trial blocks, retain an unchanged baseline configuration, and record which market regime each trial encountered. An A/B/A sequence can reveal a gross deterioration, but a few minutes of each remains weak statistical evidence. Do not repeatedly switch until one run happens to look good.

### 6.3 What to measure after each actual fill

For a fill at price `p` with sign `d=+1` for a buy and `d=-1` for a sell, compute:

`signed_mid_markout(H) = d × [mid(fill_time + H) - p]`

This measures the fill against the later midpoint. It is useful for detecting adverse selection, but it is not liquidation profit. A buy can have positive midpoint markout and still lose after crossing the future bid to exit.

Also compute executable exit marks, with depth awareness:

- Bought lot: future executable bid minus fill price minus actual costs.
- Sold lot: fill price minus future executable ask minus actual costs.
- Larger inventory: use the volume-weighted value of sufficient available levels; do not value every lot at the top quote when its quantity is too small.

Log fill time, receipt time, signal at decision time, quote age, order size, filled size, inventory before/after, realized cash change, midpoint markout, and executable exit mark. Preserve both profitable and unprofitable fills. If the data feed misses a future mark, record it as missing rather than silently treating it as zero.

Useful summaries include: actual PnL under the official marking rule; inventory marked at executable liquidation prices; fill count and fill rate; mean and lower-tail markouts; time at soft limits; maximum absolute inventory; cancel/reject rates; stale-data pauses; and the fraction of gains attributable to directional inventory drift.

### 6.4 A promotion gate the whole team can apply

Promote the signal variant only if the team can answer all of these questions:

1. Was it tested on data or practice time not used to choose it?
2. Did it alter actual quotes after rounding and execution controls?
3. Are the results based on real fills or a defensible execution model?
4. Are fees, spread costs, quote delays, and inventory disposal represented?
5. Is the gain present in more than one short period and not explained by one extreme trade?
6. Does it improve the relevant performance measure without creating unacceptable inventory tails or operational errors?
7. Can the execution owner revert immediately to the stable configuration?

A failed gate can mean "keep researching" rather than "the idea is impossible." It means the available evidence is insufficient to risk the final version on that modification.

## 7. Which strategies to postpone, and the reason for each

| Idea | Why it is currently unsupported | Evidence that would change the decision |
|---|---|---|
| Aggressive imbalance trades | Crossing costs generally exceed the observed signal; isolated positives are unstable | Fresh, execution-aware, cost-adjusted positive results with enough independent events |
| Universal momentum or reversion | Training crossing means are negative across the tested variants | A predeclared rule surviving a later regime and an actual execution check |
| Cross-stock arbitrage | Distinct stock tickers have no demonstrated conversion or payoff identity | Explicit contract equivalence, or a separately validated statistical relationship with residual risk |
| Sector-neutral pairs trades | Correlation is not mean reversion; exposure in lots is not exposure in price sensitivity | Stable residual definition, chronological estimation, realistic leg execution and stop criteria |
| Counterparty-following | Buyer and seller identities are absent in the downloaded trades | Documented, persistent participant identifiers and permitted use |
| Passive backtest from book touches | A displayed/touched price does not establish our queue position or fill | Matching-engine semantics, order-event reconstruction, or actual own-fill logs |
| News or external real-stock prediction | No causal mapping from real-world news to this simulated session has been demonstrated | Event-provided news with known timing and a tested price-response mechanism |
| Large neural model | The current usable time span is short, the metric is execution-sensitive, and integration time is scarce | Substantially more relevant data, a stable baseline, and evidence that complexity adds out-of-sample value |
| Size proportional to validation mean | The means are noisy and selected across many tests | A stable uncertainty-aware estimator and risk/impact validation |

These are prioritization decisions for this event and dataset, not general claims that the methods cannot work elsewhere.

## 8. Reproducing the research

The recovered invocation itself is not in the archive. The effective settings are fully recorded in `metadata.json`. The following command reproduces the analytical settings against the downloaded files, using a new output directory and the team's Python environment:

```bash
/opt/venv/bin/python research/optibook_research.py \
  --offline /absolute/path/to/unpacked/diagnostico_optibook \
  --start 2026-11-12T17:03:20.715896+00:00 \
  --end 2026-11-12T17:33:20.715896+00:00 \
  --horizons 1 5 10 30 \
  --latency-s 1 \
  --max-age-s 2 \
  --fee-per-side 0 \
  --min-observations 30 \
  --out runs/reproduced_20261112
```

Use the actual local path to the unpacked archive. The output directory must not already exist; the script refuses to mix sessions. The `--start` and `--end` values preserve the recorded request metadata in offline mode; offline mode reads the supplied files and does not filter their rows to those arguments. Therefore, point it at the correct archive and verify its observed boundaries.

For a permitted fresh historical download in the official event workspace, omit `--offline` and use either explicit UTC boundaries or `--minutes 30`. The script then constructs `HistoricalDataLoader`, not `Exchange`. It calls `get_trades_df` and `get_pricebooks_df`; `--include-orders` additionally requests `get_orders_df`, but does not turn those orders into a reconstructed matching-engine history.

```bash
/opt/venv/bin/python research/optibook_research.py \
  --minutes 30 \
  --horizons 1 5 10 30 \
  --latency-s 1 \
  --max-age-s 2 \
  --fee-per-side 0 \
  --out runs/new_window_001
```

Zero fees in these examples reproduce the recovered assumption. Replace the argument with the verified fee in price units per lot per side when known, or record sensitivity scenarios. A fee of `c` per side lowers every hypothetical round-trip edge by `2c`; it cannot rescue a negative zero-fee crossing result. If fees depend on maker/taker status, instrument, or notional, the simple constant-fee parameter is inadequate and the evaluation must be extended before making claims about net returns.

The English translation included with the handover changes explanatory prose only. CLI option names, output filenames, CSV column names, numeric formulas, defaults, and network behavior are preserved. It passed Python compilation, an AST comparison confirming unchanged structure, identifiers, and numeric values, and an offline reproduction matching the original eight-row summary, 384-row signal screen, and 1,000-row feature sample to a numerical tolerance of 1e-12. It is not a new validated trading strategy.

## 9. Limits the team must remember when presenting results

The diagnostic observes one short period in a competition whose participants can change their strategies. The final reset and a different set of active bots may change the data-generating process. It is possible to have hundreds of thousands of book events and still have weak evidence about a 20-minute strategy.

No confidence interval, multiple-testing correction, or robust estimate of independent samples was produced by the original script. The minimum-observation label is only a warning. Do not describe an `EXPLORATORY_ONLY` row as statistically significant.

The code models a deterministic one-second delay, not the distribution of actual feed, process, network, matching, and response delays. Live measurements should determine whether that approximation is conservative or optimistic. Faster execution is not automatically better if it increases cancellation traffic or quotes on unreliable state.

The screen uses the book observed at a future timestamp as a hypothetical aggressive execution price. It omits order competition, partial fills, market impact, rejection, and shared inventory limits. The observed future quote may no longer be available by the time a real order would reach the exchange. The original results are therefore a cost-aware signal screen, not an executable replay.

The screen excludes examples without usable future books. If missing data are concentrated in unusual market states, that filter can bias the apparent results. Report coverage and investigate outages rather than treating a high average usable fraction as proof that every important state was captured.

There is no verified strategy PnL in this archive. The team can accurately say: "We inspected 212,509 book snapshots and 8,955 trades, tested fixed causal signals with purged chronological validation and crossing costs, rejected unsupported aggressive variants, and used the remaining directional evidence to design a controlled passive-execution experiment." Any stronger claim must be supported by a later actual run and its logs.
