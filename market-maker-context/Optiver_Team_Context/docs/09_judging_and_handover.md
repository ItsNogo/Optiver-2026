# 09 — Judging, Explanation, and Final Handover

## 1. What the judges are known to consider

The supplied competition slide identifies PnL, trading approach, risk taken, and novelty among the considerations. It does not publish numerical weights, a precise risk statistic, or an equation for choosing the winner. Present the evidence for each dimension separately rather than claiming to optimize a score that has not been specified. [E1]

| Dimension | What the team should show | Weak substitute to avoid |
| --- | --- | --- |
| PnL | Official scoring interval, observed result, terminal inventory, fees/marking assumptions | A favorable historical midpoint forecast or a practice profit labelled as final profit |
| Approach | A causal explanation from data to valuation, quote, fill, inventory, and exit | A list of model names without a mechanism |
| Risk | Exposure limits, actual worst inventory/drawdown, uncertain-order handling, and ending behavior | Claiming a position is safe because the exchange accepts the order |
| Novelty | A specific original adaptation, test, or diagnostic supported by evidence | Renaming a standard formula or attributing external work to the team |
| Engineering quality, if examined | Reproducible code/config, coherent state, error handling, and a working run | Elaborate architecture that cannot be restarted or explained |

The final item is useful preparation, not a separately confirmed scoring weight. Likewise, a presentation format or length remains to be confirmed. Prepare a two-minute core explanation and expandable evidence so the team can adapt.

## 2. A two-minute explanation template

The bracketed fields are to be completed from actual team results, not guessed.

> We built an inventory-aware quoting strategy for [enabled instruments]. We began with the actual event limits and a simple midpoint-based baseline. Our historical diagnostic covered 212,509 book snapshots and 8,955 trades. It did not establish a robust aggressive trading edge after crossing costs, so we used it to prioritize a controlled passive-execution experiment rather than treating a positive prediction as profit.
>
> Our final version estimates fair value using [actual reference and any verified signal], then adjusts quote prices and sizes for inventory. One process owns execution. The risk layer reserves capacity for live, in-flight, and cancel-pending orders before submitting anything.
>
> We tested [specific change] against [baseline] over [actual intervals], with [sample sizes]. The result was [measured improvement, failure, or uncertainty], at [comparable exposure or stated difference]. We retained [feature] and rejected [alternative] because [evidence].
>
> During the official 20-minute round, the recorded result was [official PnL], with [terminal positions], [maximum inventory/drawdown], and [material errors or none observed]. Our main contribution was [specific original adaptation]. The main limitation is [remaining uncertainty], which we handled by [concrete control].

If the final has not happened, use future tense and omit final-performance fields. If no candidate beat the baseline convincingly, say that and explain why the baseline was retained. A negative result does not justify fabricating a success story.

## 3. Evidence to have immediately available

Prepare one compact table and a small set of charts or logs if the event allows them. The minimum evidence is the strategy's exact commit/config, the best baseline comparison, and the final run's measured result.

| Evidence | Questions it answers |
| --- | --- |
| Rule sheet | Which constraints and scoring assumptions did you use? |
| Baseline/candidate comparison | What did your change improve, and under what conditions? |
| Inventory and PnL over time | Did you make money through repeatable execution or carry a large directional position? |
| Fill markouts by side/instrument | Were you being adversely selected? |
| Exposure and error summary | Did the algorithm remain within limits and operate reliably? |
| Experiment/decision log | What did you reject, and why? |
| Final commit, configuration, and run card | Can someone reproduce what actually ran? |

Use identical axes and intervals when comparing runs. Label reset boundaries. Mark missing data instead of joining a line through an outage. Keep practice and final results distinct.

## 4. Likely questions and what a sound answer contains

**Why this strategy?** Explain the evidence and time constraint. The recovered aggressive screen lacked robust positive execution edge; a passive baseline tests a different mechanism with measurable conditional fills. Do not say passive market making is automatically profitable.

**Where does your fair value come from?** State the equation, the horizon, the available timestamps, and whether parameters were fixed, fitted on training data, or chosen during practice. Distinguish the original neutral benchmark from any learned component.

**Why should imbalance predict anything?** Describe the pressure hypothesis and its limits. Explain that best-level microprice and OBI are algebraically related. Show incremental evidence against the same baseline and acknowledge that fills select a different distribution of events.

**How do you avoid exceeding 100 lots?** Give the `q + B + x <= 100` and `q - S - y >= -100` scenarios, including unresolved inserts and cancellations. Explain how actual fills transfer quantity from outstanding exposure to inventory without double counting.

**What happens if the connection drops?** Outstanding orders may be canceled under the supplied behavior, but positions remain. The process restores authoritative account state, retains uncertainty until resolved, and resumes only under the documented ownership and recovery procedure.

**What if a signal stops working?** State the feature-disable or fallback condition and show how the baseline/risk service continues, or explain why the affected instrument is paused. Avoid claiming that a stop loss by itself proves the model is robust.

**What did you test that did not work?** Give a specific example: a crossing signal that failed in validation, a result dominated by an outlier, or an execution change that reduced fills without improving net economics. State its rejection criterion.

**What is original?** Explain a concrete team decision, measurement, or adaptation. The originality might be per-instrument inventory/quote behavior justified by observed liquidity, disciplined handling of resets, or a clear rejection of a misleading signal. Attribute standard formulas and external inspiration.

**How much of the PnL is realized?** Use the actual accounting convention. Separate official last-trade marks, cash/closed trades, and a depth-aware liquidation estimate. Explain what remains in terminal inventory and what the official ending rule does with it.

**Could this work outside the simulator?** Explain that the event demonstrates a workflow and mechanisms under specific rules. Real exchange fees, latency, queue rules, data quality, and market impact would require separate validation. Do not translate a short competition result into a real-market return claim.

## 5. Final result record

Immediately after the round, save the official start/end, bot launch/restarts, active commit/config, official result, final positions, known remaining orders, drawdown/exposure summary, and any unresolved state. Preserve the scoring evidence before continuing exploratory work. Do not overwrite the final configuration with a later cleanup change.

If a bug is found afterward, document it alongside the original run. A corrected version is a new version, not what ran in the competition. If the source of an apparent profit remains uncertain, label the uncertainty explicitly.

## 6. What a new teammate should inherit

The handover should contain: the rule sheet; the active commit and run command; the best verified configuration; the experiment/decision log; current known limitations; the actual data sources and time windows; the final-round checklist; and one named person responsible for live execution.

The repository's written context is useful only if it matches the actual system. When the team learns a new fee, rate limit, scoring detail, or API behavior, update the relevant rule entry and link the evidence. Do not let an old chat summary remain the authority after a new organizer clarification.
