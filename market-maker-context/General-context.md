Optiver x Bona Fide Delft: Complete Team Context

12 November 2026 · English team handover and competition playbook

This single-document edition contains the complete handbook and working templates. The companion GitHub package also contains the research scripts and numerical evidence tables. The separate research-data archive supplies original raw inputs for offline reproduction.

Contents

Overview

Chapter 01

Chapter 02

Chapter 03

Chapter 04

Chapter 05

Chapter 06

Chapter 07

Chapter 08

Chapter 09

Chapter 10

Research tools

Evidence files

Instructions for permitted coding assistants

Template: Readme

Template: Decision Log

Template: Experiment Card

Template: Final Run Card

Template: Incident Card

Template: Rules Sheet

overview

Overview

Event: 12 November 2026 · Language: English · Platform: Optibook / Python
Purpose: give every teammate and permitted coding assistant the same factual context, research evidence, implementation priorities, and operating procedure.

Start here

The team needs a working, observable trading system, an honest explanation of its edge, and disciplined execution during the final 20-minute round. The strongest current recommendation is to test a simple, inventory-aware passive quoting baseline, measure its actual fills and adverse selection, and promote only improvements that survive fresh evidence. This is a proposed experimental direction, not an already profitable strategy.

The most consequential research result: the recovered diagnostic contains 212,509 order-book snapshots and 8,955 public trades. None of the four non-control directional signal families, at any tested instrument/horizon combination, had a positive hypothetical crossing edge in both chronological partitions with at least 30 observations in each. The apparently attractive small-sample results are insufficient grounds for an aggressive trading bot. [E3; see the data audit]

The most consequential operational rule: the organizers will reset positions and PnL after approximately 21:00 local time and then run a 20-minute competition. The team must start its algorithm after the reset. Treat the organizer's actual reset/start announcement as authoritative; 21:00 is approximate. [E1]

Confirmed event snapshot

Item

Current evidence

Instruments

AMD, AVGO, CRWV, MU, NBIS, NVDA, SNDK, VRT

Position limit

Maximum 100 lots long or short per instrument

Research inputs

Historical orders, public trades, and order-book snapshots are available in the supplied environment

Actual recovered diagnostic

Public trades and pricebooks; no raw orders file

Practice

Until approximately 21:00 on the event date; practice resets may occur

Final

Positions and PnL reset; 20-minute scored competition; team initiates its algorithm

Judging

PnL, trading approach, risk taken, novelty, and potentially other considerations; weights not published in supplied slides

Account ownership

One coordinated live execution owner; recovered event context reports one connection per team account

Research access

HistoricalDataLoader can be used without constructing an Exchange connection

Unresolved

Fees, exact message limits, terminal valuation, AI/external-code policy, submission/presentation requirements, and any later organizer clarifications

Sources and confidence levels are explained in context and rules and the source register. The photographs supplied by Bernie were inspected directly. Older preparation documents are superseded wherever those photographs or the actual dataset provide better evidence.

Reading paths

Available time / responsibility

Read

Everyone, first 10 minutes

This README; context/rules; first section of the strategy playbook; final-round checklist

Strategy owner

Strategy playbook; full data audit; experiment card template

Execution and risk owner

Execution/risk chapter; final-round checklist; incident card

Research and evaluation owner

Data audit; curated evidence CSVs; validation standards; experiment log

Integration or team lead

Team operating plan; decision log; release checklist; judging narrative

A permitted AI assistant

AGENTS.md, the relevant chapter, current rule sheet, and the exact code/config it is asked to review

Full preparation context

MASTER_CONTEXT.md, the assembled single-document edition of the handbook

Documentation map

File

What it explains

01 — Context and rules

Recovered preparation, authoritative event facts, superseded assumptions, and remaining decisions

02 — Strategy playbook

Fair value, passive quoting, inventory, execution costs, adverse selection, candidate signals, and concrete decision rules

03 — Actual data and research audit

What was run, exact data coverage, signal results, reproducibility, limitations, and next experiments

04 — Execution and risk

API semantics, order state, capacity, partial fills, reconciliation, failure recovery, and final-round mechanics

05 — Team operating plan

Roles, work allocation, milestones, Git workflow, acceptance criteria, and time budgets

06 — Final-round checklist

Before reset, after reset, during the 20 minutes, and at the finish

07 — Prior competitions and resources

What public winners and participants actually disclosed, with evidence limits

08 — Reading map and learning exercises

All 20 sources from the earlier preparation, priority readings, and worked checks

09 — Judging and handover

Evidence-based explanation, likely questions, final report structure, and continuity

10 — Sources and provenance

Source authority, evidence dates, recovered artifacts, and what remains unavailable

Templates

Rules, experiments, decision records, incidents, and final results

Research

Recovered research tool, reproduction instructions, and separation from live execution

Evidence

Machine-readable summaries and sensitivity checks

The next five actions

Assign one execution owner, one research owner, and one integration/evaluation owner. Combine roles if necessary; do not assume a particular team size is permitted.

Fill the rule sheet's open fields from the organizer or installed environment. Focus on fees, limits, the actual final-start procedure, terminal inventory, and permitted tools.

Establish a baseline that reads valid books, reconciles positions and orders, respects worst-case outstanding exposure, and records private fills. Start a small permitted practice experiment promptly once these controls work.

Compare a neutral passive baseline against one bounded improvement on fresh practice data. Keep code, limits, sizes, and evaluation windows comparable. Measure conditional fill quality, not just price prediction.

Freeze a version, rehearse restart and cancellation/reconciliation, and prepare the short explanation. Keep an operator watching through the reset and final start.

What this package is

This is a consolidated handover of the relevant retrievable preparation, supplied event materials, actual diagnostic outputs, and explicit new recommendations. It is not a verbatim transcript of every past conversation. It does not contain a deployed trading bot or evidence of a successful scored run. The research script is a diagnostic; any live algorithm must still be implemented and validated in the official environment.

The package is ready to place in a GitHub repository. Use a private team repository while event-material sharing permissions remain unresolved. Keep credentials, account configuration, raw participant data, licensed books, and local execution logs outside version control. The package contains derived research evidence and source descriptions, rather than redistributing the original books or event photographs.

Evidence labels: Confirmed = supplied event source; Observed = inspected data/code; Recommended = a proposed decision; Open = unresolved; Historical = another event or older preparation. A recommendation becomes a team decision only when it is recorded with an owner and evidence.

chapter-01

Chapter 01

1. Mission and current strategic position

The event is Optiver x Bona Fide Delft, 12 November 2026, also advertised as an Optiver Coding Challenge / Mini Hackathon. The supplied mission is to investigate historical market activity for a small stock universe, understand its dynamics, and use that research to build a profitable trading strategy. The implementation environment is Python and Optibook. [E1, E2, E4]

The eight supplied symbols are AMD, AVGO, CRWV, MU, NBIS, NVDA, SNDK, and VRT. Their names alone do not establish the simulator's economic relationships, real-world price feeds, common factors, fundamental values, or instrument convertibility. Treat the supplied market and its rules as the problem definition. [E1; interpretation]

Preparation originally explored several possible Optibook formats: single-asset market making, dual listings, options, ETFs, news, and predictive datasets. Those were branches to prepare for before the problem was known. The current materials support a historical-data-driven stock trading challenge. No supplied source establishes a guaranteed dual-listing identity, basket conversion, option payoff, or news-based mechanism for this edition. Consequently, the active plan centers on data quality, stock fair-value estimation, order execution, inventory, and experiment design. [E1–E4]

The goal is to improve the team's probability of producing the strongest defensible submission. No recovered evidence supports a guaranteed winning strategy or a numerical probability of winning.

2. How the preparation developed

Stage

Material recovered

What to retain now

Initial preparation, 11 November

A 15-page preparation guide, public event research, comparable competitions, and a reading map of 20 supplied finance sources

Microstructure, executable prices, inventory, validation, team discipline; conditional branches remain reference material

Deeper preparation, 11–12 November

A 14-page winner/case-study dossier and user-supplied Optibook API/common types

Distinguish official results from participant claims; implement actual SDK semantics

Event briefing, 12 November

Photographs of mission, risk, fair-value, competition, and recommendation slides

Actual symbols; ±100 lots; approximate practice cutoff; reset and 20-minute final; qualitative judging criteria

Early event tooling

optibook_market_scout.py

A read-only scout that still opens Exchange; it must not compete with the live owner for the account connection

Supplied notebook

Setup, instrument metadata, orders, fills, PnL, and HistoricalDataLoader examples

Official paths and method semantics; distinguish historical research from a live account connection

Historical research tooling

optibook_research.py and an earlier research-kit ZIP

A diagnostic that uses the historical loader without opening Exchange or sending orders

Completed historical run

diagnostico_optibook.zip, uploaded on 12 November

Inspectable raw trades/books, report, metadata, summary, and signal screen

This handover

Source reconciliation, offline reproduction, sensitivity checks, strategy/engineering/operations chapters

A common reference that prevents stale assumptions and unsupported claims from propagating

The two older PDFs are preparation artifacts, not official rules. The original set of 20 books was previously reviewed through contents and selected passages; this handover preserves that reading map without claiming a fresh cover-to-cover audit. [E4, E5]

3. Rules confirmed from the supplied slides

Rule

Operational meaning

Evidence

Universe contains the eight named stocks

Validate instruments against the current runtime and keep the active configuration explicit

Mission photographs, IMG_3362 / IMG_3363

Maximum 100 lots long or short per instrument

Treat -100 <= q_i <= 100 as the hard filled-position limit; also reserve capacity for outstanding and uncertain orders

Risk photographs, IMG_3364 / IMG_3365

Practice until approximately 21:00 today

Use the live organizer announcement for the actual cutoff

Competition photograph, IMG_3367

Positions and PnL reset before the final

Archive practice evidence, begin a new final-run ledger epoch, and reconcile the actual post-reset state; do not treat practice balances or positions as current

IMG_3367

Final competition lasts 20 minutes

Use elapsed time from the official competition start, separate from bot launch; a restart does not create another 20 minutes

IMG_3367

Team is responsible for starting its algorithm after reset

Assign a named operator and rehearse the procedure

IMG_3367

PnL matters, along with approach, risk, and novelty

Produce measured performance and a clear explanation; do not optimize an invented weighted score

IMG_3367

Start simple, iterate, get connected/trading early in practice, and ask for help

Prefer small, controlled experiments once core controls work; avoid spending the whole event refining an untested model

Recommendation photograph, IMG_3368

The competition slide describes AirPods 5 for members of the winning team and speakers for runners-up. This supersedes the earlier public advertisement's possible iPhone incentive; it has no effect on trading design. It does not establish a team-size limit. [E1, E4]

The relevant local clock is Delft time. On this date Delft and Madrid share CET (UTC+1). Store machine timestamps in UTC and display the competition countdown against the organizer's stated start. The historical dataset timestamps are UTC, not local time.

4. What the supplied platform material establishes

The event notebook uses Exchange() with configuration-derived access and illustrates the synchronous client. It demonstrates instrument metadata, order-book access, order insertion/deletion/amendment, public trade ticks, private fills, positions/cash, and get_pnl(). It also supplies HistoricalDataLoader for trades, orders, and pricebooks. [E2]

Relevant distinctions:

An accepted order is not a confirmed fill. The insert response and the fill record answer different questions.

IOC means an unfilled remainder does not rest. It does not promise all-or-nothing execution.

Cancel on disconnect removes resting orders; it does not liquidate inventory.

A process that only reads through Exchange still consumes a live connection. The older scout is not safe to start casually alongside the trader.

Historical-loader research is a separate access path; the recovered diagnostic used it without an Exchange connection.

Last-trade marked PnL is not guaranteed liquidation value, and the method's marking behavior does not establish the judges' terminal rule.

The generic client supports instrument types beyond this event's stocks. The presence of options/news fields is not evidence those features are active here.

Broad API validators such as prices up to 1,000,000 or volumes up to 100,000 are not useful quote levels, position limits, or permission to submit those sizes.

See the execution chapter for the exact recovered signatures, response semantics, and reconciliation requirements. Do not treat any copied tutorial order as a safe production order merely because its syntax is valid.

5. Reconciliation of old and new assumptions

Earlier assumption / example

Current treatment

Instruments and final duration were unknown

Resolved by the event slides: eight stocks and a 20-minute post-reset final

A generic FAQ showed ±300

Superseded for this event by ±100 per instrument

Other mini-hackathons allowed four people

Does not prove the current team-size rule

Dual listing might be the challenge

No identity is established for this universe; do not create a synthetic equivalence

News/LLM methods helped other winners

Retain as historical context; current event evidence has not established an actionable news feed

A high positive predictive metric might justify trading

Must survive executable prices, costs, latency, fills, limits, and fresh evidence

A historical run completed successfully

Confirms a data/analysis pipeline, not profitability

The requested interval was 30 minutes

Actual observed books span approximately 28 minutes 39 seconds and stop about 80.7 seconds before the requested end

The historical loader supports orders

The actual recovered diagnostic ZIP contains no raw orders dataset

The final begins at exactly 21:00

The slide says approximately; the actual organizer signal controls

A read-only market scout is operationally harmless

It opens the account connection and can interfere with the sole live owner

6. Questions that still change implementation

These are concrete missing fields to resolve once with an organizer or the running environment, then record in templates/rules_sheet.md. They are not reasons to stop all preparation.

Question

Why the answer changes the system

Interim behavior

What fees or rebates apply to each execution?

Changes the minimum profitable edge and maker/taker comparison

Historical zero-fee results remain conditional; reserve an explicit fee field

How is final inventory valued or liquidated?

Determines ending policy and whether residual exposure is penalized

Maintain manageable inventory and preserve the ability to close; do not assume forced liquidation

What are message/order limits and burst rules?

Determines polling, cancel/replace frequency, and emergency capacity

Use a conservative budget and measured pacing; obtain exact limits

Are there extra gross/net/notional or outstanding-order limits?

Per-symbol ±100 alone may be insufficient

Apply conservative local caps and do not infer missing global rules

What are each instrument's tick, lot size, and price bands?

Determines valid prices, sizes, units, and guards

Read metadata; do not infer ticks from median spread

How exactly does the reset affect live connections, orders, histories, and caches?

Determines restart and ledger-clearing sequence

Stop new submissions, wait for announced reset, reconcile, and start explicitly

What code/submission/presentation is required and when?

Determines what must be frozen and handed in

Prepare a commit, config, run command, logs, and short explanation

Are AI, internet, prewritten code, and external packages allowed?

Determines permitted workflows

Use materials according to the event's actual rules; keep the trading loop independent of AI

Can event data, code, and materials be shared publicly?

Determines repository visibility and included files

Use team-private collaboration and summarized sources

Are there precise judging weights or tie-breakers?

Determines the optimization target

Report PnL, exposure, drawdown, approach, and novelty separately

7. What “complete context” means in this handover

The package preserves the relevant retrievable event preparation, its changes over time, the original problem's concrete constraints, the actual research results, and explicit proposed next steps. It does not fill gaps with invented meeting details, teammate names, hidden scoring weights, measured latency, transaction fees, a proven alpha, or final competition results. It also excludes unrelated personal history: the group needs the competition context and working decisions.

Source authority is: current organizer clarification, supplied event slides, installed event SDK and supplied notebook, observed data, earlier preparation, then external analogies. Record any later rule change with its source and time so the whole team makes the same update.

chapter-02

Chapter 02

1. The decision we should make now

Recommended starting point: a small passive quoting experiment with a neutral midpoint reference, inventory-aware prices/sizes, reliable execution, and actual-fill diagnostics. Next, test one bounded fair-value improvement or one execution improvement. Keep the aggressive directional module disabled until fresh evidence supports its complete entry/exit economics.

This recommendation follows from the actual diagnostic: the tested directional signals do not show robust positive crossing edge across both chronological partitions at the stated minimum observation count. It does not follow that all aggressive strategies fail, or that passive market making is profitable. Passive execution has different costs and fill selection, which must be measured. [E3; full audit in Chapter 03]

The strategy should answer five questions in order:

What do we estimate the instrument is worth, at what horizon, and using what information?

At what prices could we actually buy or sell, and how likely is a passive fill?

What happens to value conditional on us getting that fill?

How much risk can the account take after every outstanding order executes in the worst direction?

How will the position be reduced, and will that plan remain feasible near the final deadline?

A forecasting idea that cannot answer questions 2–5 is a research hypothesis. A correct order-management system with no profitable mechanism is an engineering baseline. The team needs both, but should build and evaluate them separately.

2. Shared notation and units

Symbol

Meaning

Unit

b, a

Best bid and best ask

Price units per lot under the simulator's contract convention

Vb, Va

Displayed quantities at those prices

Lots

m = (a+b)/2

Midpoint

Price

s = a-b

Full displayed spread

Price

delta

Runtime-confirmed minimum price increment

Price

q

Filled inventory; positive long, negative short

Lots

B, S

Remaining buy/sell quantities, including uncertain exposure reservations

Lots

f

Our estimated fair value for a specified horizon

Price

h

Intended quote half-width

Price

ell

Decision-to-entry latency assumption or measurement

Seconds

H

Holding or evaluation horizon

Seconds

c

Fee per side, if charged in price units per lot

Price per lot

If the simulator uses multipliers or another fee convention, convert explicitly. Do not mix price units, ticks, basis points, account PnL, or percentages. The recovered median spreads are observations, not tick sizes. [E2, E3]

3. Fair value is an estimate, not the price available to trade

The midpoint is a convenient local reference. It is generally neither the price for an immediate purchase nor the price for an immediate sale. A marketable buy consumes the ask side; a marketable sell consumes the bid side. For more than the available best-level quantity, compute a depth-weighted execution price.

An aggressive long candidate needs the expected future executable exit bid to exceed its expected entry ask, fees, slippage, and an uncertainty margin. A forecast that the midpoint will rise by 0.03 is not enough when the round trip costs 0.20 in spread before fees. The same reasoning applies with sides reversed for a short.

For a one-lot long under the historical screen's simplified assumptions:

entry at t + ell
exit at t + ell + H
crossing_edge_long = future_bid - entry_ask - 2 * fee_per_side
crossing_edge_short = entry_bid - future_ask - 2 * fee_per_side

These are hypothetical price-unit edges, not a complete strategy's PnL. Rows describe different hypothetical rules evaluated on shared, often overlapping market data. They are not independent experiments. Do not sum the signal-screen rows as if one account traded all of them. [E3]

Worked example from the supplied fair-value slide

The slide gives an estimated fair value of 100.60 for example stock ABC and displays offers of 15 at 100.30, 50 at 100.40, and 110 at 100.50. These are teaching numbers, not an active instrument or a guaranteed fair value. [E1]

If inventory is zero and no buys are outstanding, the event limit permits at most 100 additional lots. Buying 100 would consume 15 + 50 + 35 lots if those offers were still present:

cost = 15*100.30 + 50*100.40 + 35*100.50 = 10,042
average execution price = 100.42
estimated value = 100*100.60 = 10,060
model-marked edge before fees = 18

That 18 is an estimate relative to the assumed fair value. It is not realized profit. The fair value could be wrong, the offers could disappear, only part could fill, and liquidation could cost a spread or more. If current inventory is +75 with no outstanding buys, capacity is only 25: 15 at 100.30 plus 10 at 100.40 would cost 2,508.50 and have model-marked edge 6.50. Existing buy reservations reduce the capacity further.

The practical lesson is to combine valuation, executable depth, and risk capacity before selecting size. Do not buy every visible offer below an uncertain model value up to the hard limit.

4. What passive market making actually earns

A passive bid can buy below the midpoint and a passive ask can sell above it. The apparent spread capture is compensation for uncertainty, waiting, adverse selection, and inventory exposure. It is not free profit.

Let d = +1 for a buy fill and d = -1 for a sell fill, p the fill price, and m_fill the valid midpoint at the fill reference time. Define:

spread_component = d * (m_fill - p)
subsequent_move(H) = d * (m_after_H - m_fill)
markout(H) = d * (m_after_H - p)
           = spread_component + subsequent_move(H)

A buy at 99.90 when midpoint is 100.00 appears to capture 0.10. If midpoint becomes 99.60, its markout is -0.30. This is how a bot can get many fills and lose despite quoting a positive spread.

Markout is a diagnostic, not realized account PnL. It uses a reference mark and does not automatically subtract the cost of closing the position. Use time-causal marks, separate buy and sell results, apply fees consistently, and retain volume-weighted and unweighted summaries.

The relevant research question is expected value conditional on being filled. The distribution of all market observations differs from the distribution of moments when someone chooses to trade against our quotes. Optiver's own research discussion emphasizes this counterfactual and the limitations of treating historical touches as guaranteed fills. [R10 in Chapter 07]

5. Baseline design, step by step

5.1 Select a small initial trading universe

Use the actual summary as a shortlist, then measure live execution. NVDA had the most trades in the sample, 1,636, and a median spread of 0.10; AMD and AVGO had median spreads of 0.20 and material activity. These facts make them sensible candidates for an initial comparison, not proven winners. MU and VRT had unusually large median top-level quantities around 3,000; joining such a queue may produce few fills, while improving its price gives away edge. [E3]

Start with one or two instruments so the operator can inspect behavior and the team can attribute results. Add symbols only after evaluating their fill quality, inventory cost, and message burden. Eight listed instruments do not imply that all eight should be quoted continuously.

5.2 Start with a transparent reference

Set f = m for the neutral baseline. This is not a fundamental valuation model; it is an interpretable benchmark against which an extra signal can be measured. Require a nonempty, noncrossed, sufficiently fresh book and valid instrument metadata. If those requirements fail, produce no new risk-increasing quote for that instrument.

5.3 Penalize inventory in prices and sizes

One transparent proposal uses:

center = f - inventory_skew_ticks * tick_size * q / soft_inventory_scale
raw_bid = center - half_width
raw_ask = center + half_width

All coefficients are team-chosen parameters, not Optiver rules or calibrated outputs from this diagnostic. Positive inventory moves the center down, discouraging additional buys and encouraging sales. Negative inventory does the reverse. Separate quote sizes can further reduce the risk-increasing side.

Use a soft inventory threshold below the ±100 hard limit. The soft threshold is where the system reduces new exposure; the hard limit is a constraint that must never be breached. A one-lot quote and a soft threshold of roughly 10–20 lots can be an initial practice setting if the team chooses it, but these numbers require evaluation and are not a profit-maximizing recommendation. Account for all live and uncertain orders even at small sizes.

When inventory reaches the soft threshold, suppress the risk-increasing side or materially reduce its size. Continue only a controlled risk-reducing side if market/state quality allows. Escalate to bounded aggressive reduction only under an explicit inventory, loss, time, or failure policy. Canceling a quote does not reduce filled inventory.

5.4 Choose width according to the behavior being tested

The simplest baseline joins the best bid/ask where a meaningful margin around the reference exists. A more explicit rule sets half_width from a minimum tick-based width and an uncertainty/short-horizon volatility component. Do not tune both reference and width in the same first experiment.

Wider quotes improve nominal edge per fill but often reduce fills. Narrower quotes can attract more trades while increasing adverse selection. Optimize measured net performance under comparable risk, not spread width alone, fill count alone, or an arbitrary target win rate.

Measure short-horizon volatility in price units over the relevant quote/holding interval. A daily volatility number copied from a real stock has no established relationship to this simulated market. If using an exponentially weighted estimate, document its sampling interval, half-life, missing-data policy, warm-up, and reset behavior.

5.5 Round, validate, and reserve

For passive intent, round the bid down and the ask up to the runtime tick grid, then check the result again. A passive-intended bid must be strictly below the observed best ask, and a passive-intended ask strictly above the observed best bid; equality is already marketable. Also check against the team's own outstanding orders. Change or suppress an invalid quote according to an explicit rule. These checks at decision time cannot guarantee passive execution after the market moves before order arrival. “Limit” does not mean “passive”: a marketable limit order can execute immediately. [E2]

Integer tick indices avoid accumulating floating-point rounding errors. After rounding, enforce price bands, quote order, self-crossing rules, maximum size, worst-case capacity, and message budget. If a candidate fails these checks, record the rejection reason rather than silently altering it in several unrelated places.

5.6 Avoid replacing orders without purpose

Refreshing on every book event consumes messages and can lose queue priority. Replacing too slowly leaves stale quotes. Compare the new desired price to the current order and use a documented change threshold or age condition. Keep emergency cancellations ahead of routine quote refreshes. Do not guess which methods count against the exchange's rate limiter; confirm that rule.

If the public book includes our own orders, a large quote can distort our measured imbalance. Remove our known contribution only when the book/order views and inclusion semantics make that adjustment reliable. Otherwise flag contamination, cap the signal, and avoid a feedback loop where our quote creates the signal that expands the quote.

6. Candidate signal improvements

6.1 Best-level imbalance and microprice

For valid positive displayed depth:

OBI = (Vb - Va) / (Vb + Va)
microprice = (a*Vb + b*Va) / (Vb + Va)
microprice - midpoint = (spread / 2) * OBI

Thus OBI and this microprice are the same information transformed by the spread. They are not two independent votes. With bid 99, ask 101, and depth 90/10, midpoint is 100, OBI is 0.8, and microprice is 100.8.

A bounded improvement could be:

f = midpoint + clip(alpha * (microprice - midpoint), -max_shift, +max_shift)

Compare it to alpha = 0 with the rest of the system fixed. max_shift is in price units, not lots. Use held-out or new practice observations to set or assess it. Current data does not justify interpreting strong OBI as an instruction to cross the spread. The actual OBI screen and its sensitivity checks are in Chapter 03.

6.2 Aggressive trade flow

The recovered screen uses the preceding five seconds of signed public trade volume, divided by total volume in that window. The supplied convention is aggressive buys on bid and aggressive sells on ask. Verify the field's semantics; do not interpret an aggressor's side as the side of the resting order it consumed. [E2, E3]

Flow can help describe short-term buying/selling pressure. It can also be a response to a price move that already happened. Its incremental value must be assessed after timestamp alignment and realistic execution delay. A large volume window is not automatically a large information advantage.

6.3 Momentum and reversion

The recovered screen compares the midpoint with its value five seconds earlier. Momentum follows the sign; reversion reverses it. Neither family establishes a robust crossing edge in the current audit. Do not rescue a negative result by choosing a different horizon after repeatedly inspecting validation without reserving new data.

A reversion strategy needs a credible reference and a horizon over which deviations tend to contract. A moving average is an estimate, not a contractual redemption price. Cap position, define when the hypothesis has failed, and avoid increasing size solely because the deviation grew.

6.4 Cross-instrument information

A possible later hypothesis is whether one instrument's past move improves another's forecast after accounting for the second instrument's own recent move. Fit only using earlier data, use synchronized causal timestamps, and check incremental executable edge. Similar company names or visual chart similarity are insufficient.

Even a statistically useful relationship leaves convergence, hedge, and basis risk. A zero sum of lots across two differently priced instruments is not neutral notional exposure. A beta hedge is estimated and can change; a per-symbol limit remains binding after hedging.

6.5 Order-flow imbalance is a different object

Snapshot OBI measures current displayed depth. Order-flow imbalance describes changes caused by arrivals, cancellations, and executions over an interval. The current raw archive has no orders file, and order-event semantics must be understood before reconstructing that process. Do not rename snapshot OBI as OFI or infer reliable cancellation counts from sparsely sampled book differences. [E3]

7. When an aggressive order is reasonable

There are two distinct purposes:

Purpose

Required justification

Evaluation

Seek predicted profit

Forecast survives full entry/exit spread, fees, latency, depth, and uncertainty on fresh data

Actual realized result, markout, and exposure relative to a benchmark

Reduce an existing risk

Carrying the position violates a documented risk/time policy or has worse expected cost than an immediate reduction

Risk reduced, slippage incurred, residual position, and whether the action stayed within bounds

The second can intentionally realize a loss. That is not evidence the first has alpha. Tag the reason for each aggressive order so the team can distinguish trading profits from inventory-control costs.

Use a price-bounded IOC for a deliberate immediate attempt when supported. Observe actual fills and the unfilled residual. The notebook's very low/high liquidation limits are teaching examples with explicit warnings; they are not suitable default competition settings. [E2]

8. A practical experiment ladder

Experiment

What changes

What must remain fixed

Keep only if

B0: neutral passive baseline

First controlled operation

Small universe, small size, reliable risk accounting

It produces interpretable fills/logs without state/limit failures

B1: bounded microprice shift

Reference signal only

Width, size, inventory policy, measurement method

Fresh actual-fill evidence improves net economics at comparable exposure

B2: inventory response

One skew or soft-limit parameter

Signal and base width

Inventory tails/carrying cost improve without destroying net result

B3: refresh policy

Quote age or change threshold

Signal/size/limits

Fewer stale losses or messages without excessive missed fills

B4: instrument selection

One instrument added/removed

Policy and risk per active instrument

Its marginal result and operational cost justify inclusion

B5: selective aggressive signal

One predeclared signal/horizon

Explicit risk/fees/slippage model

New data supports executable edge and live fills corroborate it

Do not force every rung before the final. A stable B0 or B1 with credible evidence is preferable to an unfinished combination. Record negative and inconclusive experiments; they explain why the final system is as simple as it is.

Practice blocks occur in a changing market. A sequential A/B comparison is not a randomized controlled trial. Log market regime, spread, activity, and inventory at block boundaries; use repeated alternation only if time and operational cost allow. Avoid changing code while the same account is still executing the previous experiment.

9. Decisions under weak evidence

The recovered sample is short. Many displayed snapshots are correlated views of one market, not independent experiments. Thirty nonoverlapping observations is only a reporting threshold, not a statistical guarantee. An average can be dominated by one jump, and a favorable validation row selected from many candidates is no longer a clean untouched test. [E3]

When uncertainty is high, reduce complexity, size, and claims. Choose the next experiment for information value: can it distinguish a broken execution mechanism from an unprofitable pricing mechanism? For example, zero fills may mean a queue problem; negative post-fill markouts may mean adverse selection; profitable marks with large inventory may mean directional luck.

If the team is behind on the practice leaderboard, do not increase risk merely to chase the displayed number. The final starts from reset, human judges also consider risk, and practice market conditions may change. Use practice losses to find failures that can be corrected before the scored round.

10. Conditional branches retained from preparation

These branches preserve context but are inactive unless the actual problem establishes their prerequisites.

Branch

Trigger required

Essential distinction

Exact dual listing or basket arbitrage

Explicit equivalent payouts/conversion/settlement and usable execution

Buy ask, sell bid; account for partial fills, inventory by instrument, and conversion limits

Statistical pairs

Causal evidence of a relationship that survives later data and costs

Correlation is not a guaranteed payoff identity

Options/futures

Those instruments and terms are actually present

Read expiry, strike, underlying, multiplier, Greeks, and price bands; delta neutral leaves other risks

News

A permitted timely feed with a demonstrated connection to simulated prices

Arrival timestamps, inference delay, missing news, and price reaction matter

Larger ML model

Enough independent data, evaluation time, and measurable baseline advantage

Prediction quality must translate into net trading performance; inference must not stall risk management

Participant-specific patterns

Stable permitted identities with actual populated data

The recovered buyer/seller columns are empty; identity-based tactics have no support here

11. What the team should be able to explain

Before promoting a strategy, every owner should be able to state its mechanism in one sentence, identify the price and quantity it will submit in a worked example, explain its maximum possible position with outstanding orders, name the assumption most likely to fail, and show the experiment that led to the current configuration.

If that explanation depends on a large unexplained stack of indicators, a historical winner's reputation, or the largest number found in a parameter sweep, simplify the system until the explanation is testable.

chapter-03

Chapter 03

Evidence date: 12 November 2026. This chapter separates recovered results, additional offline checks, and proposed experiments.

1. The decision the team should make now

The recovered diagnostic does not establish a profitable aggressive trading strategy. Among the 128 non-control instrument/signal/horizon combinations, none has positive average crossing edge in both the training and validation intervals with at least 30 observations in each. The only combination with positive means in both intervals is VRT order-book imbalance at a 30-second horizon, based on only 7 training and 12 validation observations. Its validation mean is just 0.008333 price units per hypothetical lot. Treat that as insufficient evidence, not a winner to deploy.

Several order-book imbalance tests predict a small movement in the expected direction, but that movement is generally too small to pay the cost of crossing the spread at entry and exit. This distinction suggests a productive next experiment: compare a small, inventory-aware passive quoting baseline with the same baseline using one bounded imbalance adjustment. The historical screen does not simulate passive fills, so it cannot tell us whether either version is profitable. Only execution-aware validation and actual practice fills can answer that.

Our practical research sequence is therefore:

Prove that the system observes current state, reconciles fills, obeys limits, and records reliable measurements.

Run a small passive baseline on a deliberately limited set of instruments.

Compare the baseline with one bounded signal change, keeping risk and execution settings fixed.

Promote an improvement only if it survives fresh data, realistic costs, and a clear attribution of where the improvement came from.

Keep aggressive entries disabled as an alpha strategy until their complete expected edge clears execution costs. Aggressive risk reduction remains a separate, explicitly costed action.

Sources: recovered diagnostico_optibook.zip, especially metadata.json, summary.csv, and signal_screen.csv; recovered optibook_research.py; independent offline reproduction described below. These are direct project artifacts, not an external claim about real securities markets.

2. Exactly what was collected

Item

Verified value

Interpretation

Requested start

2026-11-12 17:03:20.715896 UTC

18:03:20.715896 CET in Delft and Madrid

Requested end

2026-11-12 17:33:20.715896 UTC

18:33:20.715896 CET

Earliest observed book

2026-11-12 17:03:20.954666844 UTC

First returned book, not the requested boundary

Latest observed book

2026-11-12 17:31:59.993202268 UTC

Approximately 80.723 seconds earlier than the requested end

Observed book span

Approximately 28 minutes 39.039 seconds

A requested 30-minute window is not 30 minutes of complete returned observations

Training/validation boundary

2026-11-12 17:23:24.281641640 UTC

70% of the observed book time span

Raw book snapshots

212,509

Across all eight instruments

Raw trades

8,955

Across all eight instruments

Invalid snapshots after deduplication

13

Kept as invalid observations; not replaced with an earlier valid book

Duplicate instrument/timestamp book rows

0

No such duplicates detected in this archive

Duplicate trade ID/session pairs

0

Additional offline audit

Exchange session IDs

One

2026-11-11T12:28:39.801042+00:00; no session-ID break observed

Historical orders file

Absent

The archive contains books and trades; the mission's availability of orders does not mean this run downloaded them

Buyer/seller fields

100% missing in both columns

Counterparty identity and participant persistence cannot be studied from this archive

Recorded endpoint errors

None

Does not explain the missing final approximately 81 seconds

Exchange connection opened

False

Metadata and code agree that this research uses the historical loader

Orders sent

0

The script is a diagnostic, not a trading bot

One session identifier does not prove that no administrative change or position reset occurred without a change of that identifier. Before combining later downloads, compare session identifiers, known reset times, schemas, and market behavior. Do not silently concatenate pre-reset and post-reset observations as if they came from the same regime.

The two global counts are data volume, not independent sample sizes. After causally sampling a one-second grid, separating training and validation, purging boundary-crossing labels, and spacing hypothetical trades, a signal/horizon may have only a few dozen observations.

book_features_sample.csv is the final 1,000 flattened book rows from the combined dataset. It is a diagnostic sample, not a uniform sample across time or instruments, and not the complete feature history. Reconstruct the full grids from the raw files when reproducing the signal screen.

3. Instrument-level facts and their practical meaning

The following figures are directly recovered from summary.csv. Spreads are price units; basis points are relative to each instrument's midpoint. Top-of-book depth is the median visible quantity at the best price, not guaranteed fill capacity at the time we submit an order.

Instrument

Book snapshots

Trades

Usable one-second observations

Usable fraction

Median spread

Median spread, bps

Median best-bid size

Median best-ask size

AMD

33,864

1,017

1,709 / 1,718

99.48%

0.20

12.41

22

17

AVGO

38,171

1,162

1,708 / 1,718

99.42%

0.20

9.47

20

15

CRWV

21,986

1,167

1,699 / 1,718

98.89%

0.20

14.60

20

18

MU

21,699

1,106

1,703 / 1,717

99.18%

0.20

27.59

3,003

3,002

NBIS

20,706

1,094

1,706 / 1,717

99.36%

0.20

20.83

13

16

NVDA

39,939

1,636

1,712 / 1,717

99.71%

0.10

7.26

26

24

SNDK

17,458

976

1,711 / 1,718

99.59%

0.20

32.95

24

31

VRT

18,686

797

1,706 / 1,719

99.24%

0.20

28.69

3,003

3,004

NVDA is useful for an execution smoke test: it has the most observed trades, the most book snapshots, the highest usable-grid fraction, and the smallest median spread. Those are operational reasons to inspect it first, not evidence that its passive strategy has the highest expected profit. More activity can also mean more competition and faster adverse selection.

AMD and AVGO are useful passive-experiment candidates: both have substantial observed activity, a median spread of 0.20, and relatively small median displayed queues at the best prices. This provides a concrete reason to measure their actual fills and post-fill movement. It does not justify assuming that joining the best quote will fill, or that improving by one tick remains profitable.

MU and VRT require special queue awareness: their median best-level depths are around 3,000 lots. A one-lot quote joining that level may sit behind a large queue. A large visible queue can facilitate aggressive risk reduction while making passive entry less likely. It is not a reason to quote a large quantity. The team's ±100-lot position cap is much smaller than the displayed level sizes.

NBIS deserves caution for the imbalance overlay: its imbalance signal changes direction between the training and validation intervals at several horizons. Retain it in the data inventory, but do not enable the same signal coefficient on every instrument merely for symmetry.

The actual runtime instrument metadata remains authoritative. The research script deliberately does not infer tick_size, lot multipliers, position limits, or price bands from historical price increments. A median spread of 0.20 is not a tick size. Determine whether one-tick improvement is possible from the official tick and the current spread.

4. How the original screen works

4.1 Books and the causal time grid

For each instrument, the script parses the JSON bid and ask levels. It chooses the highest bid and the lowest ask and sums quantities at identical best prices. It rejects malformed, empty, crossed, locked, or otherwise unusable books. A locked book has bid equal to ask; this diagnostic excludes it, which is an analytical choice rather than a statement that every locked market is intrinsically invalid.

It then creates one decision timestamp per second, starting at the first complete second after the first book and ending at the last complete second before the final book. Every decision uses the most recent book whose exchange timestamp is at or before the decision time, subject to a maximum age of two seconds. This is a backward as-of join. It never fills a missing decision with a book from the future.

Keeping invalid snapshots in the event sequence is important: if an empty or unusable book occurs, the code does not simply skip it and pretend an earlier valid book remained executable. Nevertheless, exchange timestamps do not tell us exactly when our live process received the update. The causal offline join avoids one form of lookahead, but it does not model feed latency or the delay between observation and a live decision.

4.2 Signals tested before any model fitting

The original script fits no predictive model. It tests six fixed rules for each instrument at four horizons.

Signal name

Definition at decision time

Direction of a nonzero trade

obi_0.5

Best-level imbalance has absolute value strictly greater than 0.5

Positive imbalance means long; negative means short

flow_5s_0.4

Signed aggressive volume divided by total aggressive volume in the previous five seconds has absolute value strictly greater than 0.4

Follow the sign of net aggressive flow

momentum_5s

Current midpoint minus the midpoint five seconds earlier is nonzero

Follow the sign of the change

reversion_5s

Same five-second midpoint change

Trade against the change

control_long

Always positive

Long control, useful for detecting market drift

control_short

Always negative

Short control, useful for detecting market drift

The flow convention in the recovered code is aggressor_side='bid' for an aggressive buy and 'ask' for an aggressive sale. Preserve this convention only while it agrees with the actual historical-data API specification. Do not reinterpret it from the everyday phrase "trade at the bid," which can refer to the passive price side instead.

The signed-flow window is (t-5 seconds, t]. Missing or invalid flow information produces a neutral signal, not a guessed direction. Momentum uses a five-row lag on the one-second grid. Where the current or lagged midpoint is missing, the signal is neutral.

4.3 Timing, labels, and hypothetical transaction prices

The settings were:

One-second decision grid.

Two-second maximum book age.

One-second assumed execution delay.

Holding horizons of 1, 5, 10, and 30 seconds after hypothetical entry.

Zero assumed fee per side, explicitly not verified.

A warning threshold of 30 observations, explicitly not a statistical significance test.

For a signal at time t, assumed delay L, and horizon H, the hypothetical long trade uses:

long_edge = bid(t + L + H) - ask(t + L) - 2 × fee_per_side

The corresponding short trade uses:

short_edge = bid(t + L) - ask(t + L + H) - 2 × fee_per_side

The code selects the long or short value from the signal's sign. This is a one-lot, top-of-book, aggressive round trip. It accounts for paying the entry and exit spreads through the quoted prices. It does not establish that those prices would still be available after submitting real orders, and it does not model volume larger than the available depth.

mean_signed_mid_move is a different statistic:

signal_sign × [mid(t + L + H) - mid(t)]

It measures movement from decision time, including the assumed one-second delay. It is not entry-to-exit PnL. A favorable move during that delay may be unavailable to the trader because entry occurs later. Do not subtract a generic spread from this midpoint number and label the remainder a verified trading edge.

4.4 Time split, purging, and non-overlap

The first 70% of the observed time span is the training interval. The final 30% is validation. A training example is dropped if its hypothetical exit reaches or passes the boundary. This prevents training labels from borrowing returns from validation.

Within each instrument, horizon, and phase, the script samples candidate decision times every L + H + 1 seconds before filtering by the signal. With L=1 and H=5, decisions are spaced seven seconds apart. This prevents overlapping round trips within that one test. It does not make returns independent; neighboring examples can remain exposed to the same trend or volatility burst. It also does not make different instruments or different signal tests independent.

There are 8 × 6 × 4 = 192 instrument/signal/horizon combinations and 384 phase rows. Excluding the two always-directional controls leaves 128 candidate combinations. Looking across all validation results to choose a favorite is itself a form of tuning. A fresh, later interval is needed for an honest subsequent check.

5. The most useful exact results

5.1 Promising-looking examples that do not pass a deployment gate

All edges below are price units per hypothetical lot, not dollars of total profit, returns on capital, or a portfolio result.

Instrument and rule

Horizon

Training n

Training mean crossing edge

Validation n

Validation mean crossing edge

Decision

AVGO imbalance

30 s

15

+0.140000

9

-0.011111

Best training mean among non-control tests; tiny samples and negative validation

VRT imbalance

30 s

7

+0.071429

12

+0.008333

Positive in both phases, but far too little evidence and negligible validation margin

AMD reversion

30 s

28

-0.003571

12

+0.133333

Validation-only improvement does not establish a repeatable edge

CRWV reversion

30 s

28

-0.139286

8

+0.837500

A large validation mean with eight observations is especially vulnerable to exceptional moves

MU imbalance

10 s

30

-0.096667

24

+0.112500

Changes sign between phases; validation sample below warning threshold

VRT imbalance

5 s

61

-0.124590

44

+0.015909

Negative training; positive validation is highly outlier-sensitive

NVDA imbalance

10 s

58

-0.132759

30

-0.063333

More data, but both crossing means are negative

5.2 Why imbalance is still a reasonable research candidate

At a five-second holding horizon, several instruments show a small positive signed midpoint move in both phases while their aggressive round-trip edges remain negative:

Instrument

Train n

Train signed midpoint move

Train crossing edge

Validation n

Validation signed midpoint move

Validation crossing edge

AMD

104

+0.056250

-0.135577

32

+0.070313

-0.084375

AVGO

99

+0.046465

-0.152525

50

+0.117000

-0.040000

MU

72

+0.022222

-0.144444

44

+0.010227

-0.127273

NVDA

97

+0.049485

-0.129897

49

+0.053061

-0.077551

SNDK

89

+0.024719

-0.178652

39

+0.047436

-0.112821

VRT

61

+0.046721

-0.124590

44

+0.172727

+0.015909

This is evidence to test whether an imbalance-aware quote has better fill quality than a neutral quote. It is not permission to turn the signal into immediate market orders. Passive fills occur conditionally: the market may choose to trade against our quote precisely when our valuation is stale. The unconditional midpoint association may disappear, or reverse, among the subset of quotes that actually fill.

NBIS illustrates why one universal coefficient is questionable. At a five-second horizon its training signed midpoint move is +0.037952, while validation is -0.094444; crossing means are -0.139759 and -0.255556 respectively. This is a reason to withhold or disable its imbalance overlay pending fresh evidence.

5.3 Additional offline checks performed for this handover

The audit independently loaded the raw compressed CSVs and reran the original analysis functions. All 384 result rows reproduced the stored observation counts, mean and median crossing edges, signed midpoint means, and long/short counts to numerical tolerance. The reported pandas FutureWarning concerns future dtype behavior in fillna; it did not prevent the current run or change this reproduction. It is not an exchange error.

Two deliberately limited diagnostics were then applied to the existing imbalance rule at the five-second horizon. They are additional exploratory checks on already observed data, not a new untouched holdout and not a search for a more favorable threshold.

Sampling-offset check. The same non-overlapping sample was shifted through all seven possible one-second offsets. For every instrument, the training crossing mean stayed negative at every offset. Some validation results changed sign substantially. VRT's validation mean ranged from -0.183333 to +0.023913; AVGO's from -0.165854 to +0.142553. These offsets share the same underlying data and must not be pooled as seven independent experiments. Selecting the best offset would be another overfitting step.

Outlier check. The original VRT five-second validation result has 44 observations, only three positive edges, and a median of -0.10. Its largest observation is +3.40. Excluding that one observation changes the mean from +0.015909 to -0.062791. This does not justify deleting an inconvenient observation from the official result; it demonstrates that the apparent average benefit is fragile.

For NVDA at the same horizon, the original validation mean is -0.077551, and removing its largest positive observation changes it to -0.114583. Its training crossing means across the seven offsets range from -0.148980 to -0.113861; validation ranges from -0.142553 to -0.051220. A favorable midpoint signal and a profitable crossing strategy remain different propositions.

A six-block chronological check used fixed five-minute windows from the first whole observed second, with exits required to remain inside each block. The final window is shorter because the data end early. For NVDA, all six crossing means remained negative. For VRT, all six remained negative. Small samples and different sampling origins mean block values will not average mechanically to the original phase values. These checks strengthen the reason to avoid treating a positive isolated cell as a stable aggressive strategy.

Curated audit tables: evidence/signal_comparison.csv, evidence/obi_5s_blocks.csv, evidence/obi_5s_sampling_offsets.csv, and evidence/obi_5s_outlier_sensitivity.csv. The original observations remain unchanged.

6. A precise passive-baseline experiment

6.1 Define the components separately

Let b and a be the best observed bid and ask; Vb and Va their displayed sizes; m=(a+b)/2; s=a-b; q the executed inventory; and tau the verified tick size.

I = (Vb - Va) / (Vb + Va)

microprice = (a × Vb + b × Va) / (Vb + Va)

microprice - m = (s / 2) × I

The last equation shows that top-level imbalance and this microprice displacement contain the same snapshot information. Including both as if they were independent votes double-counts the signal. Actual order-flow imbalance measures changes in supply and demand through time and is a different feature; the current archive screen did not implement that full event-based feature.

Define a neutral baseline fair value f=m. Define one experimental variant as:

f = m + alpha × (microprice - m)

Choose the trial value of alpha before the trial, keep it bounded, and compare it with alpha=0. The data do not supply an optimal value. For a first controlled test, an illustrative small coefficient such as 0.25 is an experimental choice, not a discovered constant. A quote tick may erase this adjustment, so record the actual rounded quotes; do not attribute a performance change to a signal that never changed an order.

Apply the inventory adjustment separately:

reservation_price = f - k_inventory × q

Here k_inventory has price-per-lot units. A positive inventory lowers the reservation price, discouraging additional buying and encouraging selling. A negative inventory raises it. Do not use one unscaled numerical coefficient across assets with different prices, tick sizes, or volatility simply because all symbols share a ±100-lot limit.

Construct desired bid and ask around that reservation price with a half-width that covers costs, adverse-selection uncertainty, and inventory tolerance. A simple formula is a control surface for experiments, not a calibration proof:

desired_bid = floor_to_tick(reservation_price - half_width)

desired_ask = ceil_to_tick(reservation_price + half_width)

After rounding, recheck the spread, current opposite-side quotes, price bands, size limits, and outstanding-order reservations. A passive limit order can become marketable if the market moves before it arrives. The supplied insert_order signature supports limit and ioc, with no documented post-only argument. A passive-intended bid must be strictly below the observed ask and an ask strictly above the observed bid, also avoiding the team's own orders. Use a conservative non-crossing margin and observe actual executions; a market move before arrival can still make a limit order marketable.

6.2 What changes and what stays fixed in an experiment

The first comparison should hold the following fixed: instrument set, lot size, inventory budgets, quote lifetime policy, stale-data rule, execution implementation, and evaluation duration. Change only the signal adjustment. If several components change together, a better outcome cannot be attributed to imbalance.

Keep one live account owner. A second strategy can calculate shadow quotes from the same snapshots without sending orders; this helps compare decisions but is not an executable PnL test because its fills are unknown. Never compare the live strategy's real fills with the shadow strategy's assumption that every touched quote fills.

Sequential trials are affected by changing market conditions and other teams' bots. Use short, predeclared trial blocks, retain an unchanged baseline configuration, and record which market regime each trial encountered. An A/B/A sequence can reveal a gross deterioration, but a few minutes of each remains weak statistical evidence. Do not repeatedly switch until one run happens to look good.

6.3 What to measure after each actual fill

For a fill at price p with sign d=+1 for a buy and d=-1 for a sell, compute:

signed_mid_markout(H) = d × [mid(fill_time + H) - p]

This measures the fill against the later midpoint. It is useful for detecting adverse selection, but it is not liquidation profit. A buy can have positive midpoint markout and still lose after crossing the future bid to exit.

Also compute executable exit marks, with depth awareness:

Bought lot: future executable bid minus fill price minus actual costs.

Sold lot: fill price minus future executable ask minus actual costs.

Larger inventory: use the volume-weighted value of sufficient available levels; do not value every lot at the top quote when its quantity is too small.

Log fill time, receipt time, signal at decision time, quote age, order size, filled size, inventory before/after, realized cash change, midpoint markout, and executable exit mark. Preserve both profitable and unprofitable fills. If the data feed misses a future mark, record it as missing rather than silently treating it as zero.

Useful summaries include: actual PnL under the official marking rule; inventory marked at executable liquidation prices; fill count and fill rate; mean and lower-tail markouts; time at soft limits; maximum absolute inventory; cancel/reject rates; stale-data pauses; and the fraction of gains attributable to directional inventory drift.

6.4 A promotion gate the whole team can apply

Promote the signal variant only if the team can answer all of these questions:

Was it tested on data or practice time not used to choose it?

Did it alter actual quotes after rounding and execution controls?

Are the results based on real fills or a defensible execution model?

Are fees, spread costs, quote delays, and inventory disposal represented?

Is the gain present in more than one short period and not explained by one extreme trade?

Does it improve the relevant performance measure without creating unacceptable inventory tails or operational errors?

Can the execution owner revert immediately to the stable configuration?

A failed gate can mean "keep researching" rather than "the idea is impossible." It means the available evidence is insufficient to risk the final version on that modification.

7. Which strategies to postpone, and the reason for each

Idea

Why it is currently unsupported

Evidence that would change the decision

Aggressive imbalance trades

Crossing costs generally exceed the observed signal; isolated positives are unstable

Fresh, execution-aware, cost-adjusted positive results with enough independent events

Universal momentum or reversion

Training crossing means are negative across the tested variants

A predeclared rule surviving a later regime and an actual execution check

Cross-stock arbitrage

Distinct stock tickers have no demonstrated conversion or payoff identity

Explicit contract equivalence, or a separately validated statistical relationship with residual risk

Sector-neutral pairs trades

Correlation is not mean reversion; exposure in lots is not exposure in price sensitivity

Stable residual definition, chronological estimation, realistic leg execution and stop criteria

Counterparty-following

Buyer and seller identities are absent in the downloaded trades

Documented, persistent participant identifiers and permitted use

Passive backtest from book touches

A displayed/touched price does not establish our queue position or fill

Matching-engine semantics, order-event reconstruction, or actual own-fill logs