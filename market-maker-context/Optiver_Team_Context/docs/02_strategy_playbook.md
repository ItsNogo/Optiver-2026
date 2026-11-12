# 02 — Strategy Playbook: From Evidence to Orders

## 1. The decision we should make now

**Recommended starting point:** a small passive quoting experiment with a neutral midpoint reference, inventory-aware prices/sizes, reliable execution, and actual-fill diagnostics. Next, test one bounded fair-value improvement or one execution improvement. Keep the aggressive directional module disabled until fresh evidence supports its complete entry/exit economics.

This recommendation follows from the actual diagnostic: the tested directional signals do not show robust positive crossing edge across both chronological partitions at the stated minimum observation count. It does not follow that all aggressive strategies fail, or that passive market making is profitable. Passive execution has different costs and fill selection, which must be measured. [E3; full audit in Chapter 03]

The strategy should answer five questions in order:

1. **What do we estimate the instrument is worth, at what horizon, and using what information?**
2. **At what prices could we actually buy or sell, and how likely is a passive fill?**
3. **What happens to value conditional on us getting that fill?**
4. **How much risk can the account take after every outstanding order executes in the worst direction?**
5. **How will the position be reduced, and will that plan remain feasible near the final deadline?**

A forecasting idea that cannot answer questions 2–5 is a research hypothesis. A correct order-management system with no profitable mechanism is an engineering baseline. The team needs both, but should build and evaluate them separately.

## 2. Shared notation and units

| Symbol | Meaning | Unit |
| --- | --- | --- |
| `b`, `a` | Best bid and best ask | Price units per lot under the simulator's contract convention |
| `Vb`, `Va` | Displayed quantities at those prices | Lots |
| `m = (a+b)/2` | Midpoint | Price |
| `s = a-b` | Full displayed spread | Price |
| `delta` | Runtime-confirmed minimum price increment | Price |
| `q` | Filled inventory; positive long, negative short | Lots |
| `B`, `S` | Remaining buy/sell quantities, including uncertain exposure reservations | Lots |
| `f` | Our estimated fair value for a specified horizon | Price |
| `h` | Intended quote half-width | Price |
| `ell` | Decision-to-entry latency assumption or measurement | Seconds |
| `H` | Holding or evaluation horizon | Seconds |
| `c` | Fee per side, if charged in price units per lot | Price per lot |

If the simulator uses multipliers or another fee convention, convert explicitly. Do not mix price units, ticks, basis points, account PnL, or percentages. The recovered median spreads are observations, not tick sizes. [E2, E3]

## 3. Fair value is an estimate, not the price available to trade

The midpoint is a convenient local reference. It is generally neither the price for an immediate purchase nor the price for an immediate sale. A marketable buy consumes the ask side; a marketable sell consumes the bid side. For more than the available best-level quantity, compute a depth-weighted execution price.

An aggressive long candidate needs the expected **future executable exit bid** to exceed its expected entry ask, fees, slippage, and an uncertainty margin. A forecast that the midpoint will rise by 0.03 is not enough when the round trip costs 0.20 in spread before fees. The same reasoning applies with sides reversed for a short.

For a one-lot long under the historical screen's simplified assumptions:

```text
entry at t + ell
exit at t + ell + H
crossing_edge_long = future_bid - entry_ask - 2 * fee_per_side
crossing_edge_short = entry_bid - future_ask - 2 * fee_per_side
```

These are hypothetical price-unit edges, not a complete strategy's PnL. Rows describe different hypothetical rules evaluated on shared, often overlapping market data. They are not independent experiments. Do not sum the signal-screen rows as if one account traded all of them. [E3]

### Worked example from the supplied fair-value slide

The slide gives an estimated fair value of **100.60** for example stock ABC and displays offers of **15 at 100.30**, **50 at 100.40**, and **110 at 100.50**. These are teaching numbers, not an active instrument or a guaranteed fair value. [E1]

If inventory is zero and no buys are outstanding, the event limit permits at most 100 additional lots. Buying 100 would consume 15 + 50 + 35 lots if those offers were still present:

```text
cost = 15*100.30 + 50*100.40 + 35*100.50 = 10,042
average execution price = 100.42
estimated value = 100*100.60 = 10,060
model-marked edge before fees = 18
```

That 18 is an estimate relative to the assumed fair value. It is not realized profit. The fair value could be wrong, the offers could disappear, only part could fill, and liquidation could cost a spread or more. If current inventory is +75 with no outstanding buys, capacity is only 25: 15 at 100.30 plus 10 at 100.40 would cost 2,508.50 and have model-marked edge 6.50. Existing buy reservations reduce the capacity further.

The practical lesson is to combine valuation, executable depth, and risk capacity before selecting size. Do not buy every visible offer below an uncertain model value up to the hard limit.

## 4. What passive market making actually earns

A passive bid can buy below the midpoint and a passive ask can sell above it. The apparent spread capture is compensation for uncertainty, waiting, adverse selection, and inventory exposure. It is not free profit.

Let `d = +1` for a buy fill and `d = -1` for a sell fill, `p` the fill price, and `m_fill` the valid midpoint at the fill reference time. Define:

```text
spread_component = d * (m_fill - p)
subsequent_move(H) = d * (m_after_H - m_fill)
markout(H) = d * (m_after_H - p)
           = spread_component + subsequent_move(H)
```

A buy at 99.90 when midpoint is 100.00 appears to capture 0.10. If midpoint becomes 99.60, its markout is -0.30. This is how a bot can get many fills and lose despite quoting a positive spread.

Markout is a diagnostic, not realized account PnL. It uses a reference mark and does not automatically subtract the cost of closing the position. Use time-causal marks, separate buy and sell results, apply fees consistently, and retain volume-weighted and unweighted summaries.

The relevant research question is **expected value conditional on being filled**. The distribution of all market observations differs from the distribution of moments when someone chooses to trade against our quotes. Optiver's own research discussion emphasizes this counterfactual and the limitations of treating historical touches as guaranteed fills. [R10 in Chapter 07]

## 5. Baseline design, step by step

### 5.1 Select a small initial trading universe

Use the actual summary as a shortlist, then measure live execution. NVDA had the most trades in the sample, 1,636, and a median spread of 0.10; AMD and AVGO had median spreads of 0.20 and material activity. These facts make them sensible candidates for an initial **comparison**, not proven winners. MU and VRT had unusually large median top-level quantities around 3,000; joining such a queue may produce few fills, while improving its price gives away edge. [E3]

Start with one or two instruments so the operator can inspect behavior and the team can attribute results. Add symbols only after evaluating their fill quality, inventory cost, and message burden. Eight listed instruments do not imply that all eight should be quoted continuously.

### 5.2 Start with a transparent reference

Set `f = m` for the neutral baseline. This is not a fundamental valuation model; it is an interpretable benchmark against which an extra signal can be measured. Require a nonempty, noncrossed, sufficiently fresh book and valid instrument metadata. If those requirements fail, produce no new risk-increasing quote for that instrument.

### 5.3 Penalize inventory in prices and sizes

One transparent proposal uses:

```text
center = f - inventory_skew_ticks * tick_size * q / soft_inventory_scale
raw_bid = center - half_width
raw_ask = center + half_width
```

All coefficients are team-chosen parameters, not Optiver rules or calibrated outputs from this diagnostic. Positive inventory moves the center down, discouraging additional buys and encouraging sales. Negative inventory does the reverse. Separate quote sizes can further reduce the risk-increasing side.

Use a **soft inventory threshold** below the ±100 hard limit. The soft threshold is where the system reduces new exposure; the hard limit is a constraint that must never be breached. A one-lot quote and a soft threshold of roughly 10–20 lots can be an initial practice setting if the team chooses it, but these numbers require evaluation and are not a profit-maximizing recommendation. Account for all live and uncertain orders even at small sizes.

When inventory reaches the soft threshold, suppress the risk-increasing side or materially reduce its size. Continue only a controlled risk-reducing side if market/state quality allows. Escalate to bounded aggressive reduction only under an explicit inventory, loss, time, or failure policy. Canceling a quote does not reduce filled inventory.

### 5.4 Choose width according to the behavior being tested

The simplest baseline joins the best bid/ask where a meaningful margin around the reference exists. A more explicit rule sets `half_width` from a minimum tick-based width and an uncertainty/short-horizon volatility component. Do not tune both reference and width in the same first experiment.

Wider quotes improve nominal edge per fill but often reduce fills. Narrower quotes can attract more trades while increasing adverse selection. Optimize measured net performance under comparable risk, not spread width alone, fill count alone, or an arbitrary target win rate.

Measure short-horizon volatility in price units over the relevant quote/holding interval. A daily volatility number copied from a real stock has no established relationship to this simulated market. If using an exponentially weighted estimate, document its sampling interval, half-life, missing-data policy, warm-up, and reset behavior.

### 5.5 Round, validate, and reserve

For passive intent, round the bid down and the ask up to the runtime tick grid, then check the result again. A passive-intended bid must be strictly below the observed best ask, and a passive-intended ask strictly above the observed best bid; equality is already marketable. Also check against the team's own outstanding orders. Change or suppress an invalid quote according to an explicit rule. These checks at decision time cannot guarantee passive execution after the market moves before order arrival. “Limit” does not mean “passive”: a marketable limit order can execute immediately. [E2]

Integer tick indices avoid accumulating floating-point rounding errors. After rounding, enforce price bands, quote order, self-crossing rules, maximum size, worst-case capacity, and message budget. If a candidate fails these checks, record the rejection reason rather than silently altering it in several unrelated places.

### 5.6 Avoid replacing orders without purpose

Refreshing on every book event consumes messages and can lose queue priority. Replacing too slowly leaves stale quotes. Compare the new desired price to the current order and use a documented change threshold or age condition. Keep emergency cancellations ahead of routine quote refreshes. Do not guess which methods count against the exchange's rate limiter; confirm that rule.

If the public book includes our own orders, a large quote can distort our measured imbalance. Remove our known contribution only when the book/order views and inclusion semantics make that adjustment reliable. Otherwise flag contamination, cap the signal, and avoid a feedback loop where our quote creates the signal that expands the quote.

## 6. Candidate signal improvements

### 6.1 Best-level imbalance and microprice

For valid positive displayed depth:

```text
OBI = (Vb - Va) / (Vb + Va)
microprice = (a*Vb + b*Va) / (Vb + Va)
microprice - midpoint = (spread / 2) * OBI
```

Thus OBI and this microprice are the same information transformed by the spread. They are not two independent votes. With bid 99, ask 101, and depth 90/10, midpoint is 100, OBI is 0.8, and microprice is 100.8.

A bounded improvement could be:

```text
f = midpoint + clip(alpha * (microprice - midpoint), -max_shift, +max_shift)
```

Compare it to `alpha = 0` with the rest of the system fixed. `max_shift` is in price units, not lots. Use held-out or new practice observations to set or assess it. Current data does not justify interpreting strong OBI as an instruction to cross the spread. The actual OBI screen and its sensitivity checks are in Chapter 03.

### 6.2 Aggressive trade flow

The recovered screen uses the preceding five seconds of signed public trade volume, divided by total volume in that window. The supplied convention is aggressive buys on `bid` and aggressive sells on `ask`. Verify the field's semantics; do not interpret an aggressor's side as the side of the resting order it consumed. [E2, E3]

Flow can help describe short-term buying/selling pressure. It can also be a response to a price move that already happened. Its incremental value must be assessed after timestamp alignment and realistic execution delay. A large volume window is not automatically a large information advantage.

### 6.3 Momentum and reversion

The recovered screen compares the midpoint with its value five seconds earlier. Momentum follows the sign; reversion reverses it. Neither family establishes a robust crossing edge in the current audit. Do not rescue a negative result by choosing a different horizon after repeatedly inspecting validation without reserving new data.

A reversion strategy needs a credible reference and a horizon over which deviations tend to contract. A moving average is an estimate, not a contractual redemption price. Cap position, define when the hypothesis has failed, and avoid increasing size solely because the deviation grew.

### 6.4 Cross-instrument information

A possible later hypothesis is whether one instrument's past move improves another's forecast after accounting for the second instrument's own recent move. Fit only using earlier data, use synchronized causal timestamps, and check incremental executable edge. Similar company names or visual chart similarity are insufficient.

Even a statistically useful relationship leaves convergence, hedge, and basis risk. A zero sum of lots across two differently priced instruments is not neutral notional exposure. A beta hedge is estimated and can change; a per-symbol limit remains binding after hedging.

### 6.5 Order-flow imbalance is a different object

Snapshot OBI measures current displayed depth. Order-flow imbalance describes changes caused by arrivals, cancellations, and executions over an interval. The current raw archive has no orders file, and order-event semantics must be understood before reconstructing that process. Do not rename snapshot OBI as OFI or infer reliable cancellation counts from sparsely sampled book differences. [E3]

## 7. When an aggressive order is reasonable

There are two distinct purposes:

| Purpose | Required justification | Evaluation |
| --- | --- | --- |
| Seek predicted profit | Forecast survives full entry/exit spread, fees, latency, depth, and uncertainty on fresh data | Actual realized result, markout, and exposure relative to a benchmark |
| Reduce an existing risk | Carrying the position violates a documented risk/time policy or has worse expected cost than an immediate reduction | Risk reduced, slippage incurred, residual position, and whether the action stayed within bounds |

The second can intentionally realize a loss. That is not evidence the first has alpha. Tag the reason for each aggressive order so the team can distinguish trading profits from inventory-control costs.

Use a price-bounded IOC for a deliberate immediate attempt when supported. Observe actual fills and the unfilled residual. The notebook's very low/high liquidation limits are teaching examples with explicit warnings; they are not suitable default competition settings. [E2]

## 8. A practical experiment ladder

| Experiment | What changes | What must remain fixed | Keep only if |
| --- | --- | --- | --- |
| B0: neutral passive baseline | First controlled operation | Small universe, small size, reliable risk accounting | It produces interpretable fills/logs without state/limit failures |
| B1: bounded microprice shift | Reference signal only | Width, size, inventory policy, measurement method | Fresh actual-fill evidence improves net economics at comparable exposure |
| B2: inventory response | One skew or soft-limit parameter | Signal and base width | Inventory tails/carrying cost improve without destroying net result |
| B3: refresh policy | Quote age or change threshold | Signal/size/limits | Fewer stale losses or messages without excessive missed fills |
| B4: instrument selection | One instrument added/removed | Policy and risk per active instrument | Its marginal result and operational cost justify inclusion |
| B5: selective aggressive signal | One predeclared signal/horizon | Explicit risk/fees/slippage model | New data supports executable edge and live fills corroborate it |

Do not force every rung before the final. A stable B0 or B1 with credible evidence is preferable to an unfinished combination. Record negative and inconclusive experiments; they explain why the final system is as simple as it is.

Practice blocks occur in a changing market. A sequential A/B comparison is not a randomized controlled trial. Log market regime, spread, activity, and inventory at block boundaries; use repeated alternation only if time and operational cost allow. Avoid changing code while the same account is still executing the previous experiment.

## 9. Decisions under weak evidence

The recovered sample is short. Many displayed snapshots are correlated views of one market, not independent experiments. Thirty nonoverlapping observations is only a reporting threshold, not a statistical guarantee. An average can be dominated by one jump, and a favorable validation row selected from many candidates is no longer a clean untouched test. [E3]

When uncertainty is high, reduce complexity, size, and claims. Choose the next experiment for information value: can it distinguish a broken execution mechanism from an unprofitable pricing mechanism? For example, zero fills may mean a queue problem; negative post-fill markouts may mean adverse selection; profitable marks with large inventory may mean directional luck.

If the team is behind on the practice leaderboard, do not increase risk merely to chase the displayed number. The final starts from reset, human judges also consider risk, and practice market conditions may change. Use practice losses to find failures that can be corrected before the scored round.

## 10. Conditional branches retained from preparation

These branches preserve context but are inactive unless the actual problem establishes their prerequisites.

| Branch | Trigger required | Essential distinction |
| --- | --- | --- |
| Exact dual listing or basket arbitrage | Explicit equivalent payouts/conversion/settlement and usable execution | Buy ask, sell bid; account for partial fills, inventory by instrument, and conversion limits |
| Statistical pairs | Causal evidence of a relationship that survives later data and costs | Correlation is not a guaranteed payoff identity |
| Options/futures | Those instruments and terms are actually present | Read expiry, strike, underlying, multiplier, Greeks, and price bands; delta neutral leaves other risks |
| News | A permitted timely feed with a demonstrated connection to simulated prices | Arrival timestamps, inference delay, missing news, and price reaction matter |
| Larger ML model | Enough independent data, evaluation time, and measurable baseline advantage | Prediction quality must translate into net trading performance; inference must not stall risk management |
| Participant-specific patterns | Stable permitted identities with actual populated data | The recovered buyer/seller columns are empty; identity-based tactics have no support here |

## 11. What the team should be able to explain

Before promoting a strategy, every owner should be able to state its mechanism in one sentence, identify the price and quantity it will submit in a worked example, explain its maximum possible position with outstanding orders, name the assumption most likely to fail, and show the experiment that led to the current configuration.

If that explanation depends on a large unexplained stack of indicators, a historical winner's reputation, or the largest number found in a parameter sweep, simplify the system until the explanation is testable.
