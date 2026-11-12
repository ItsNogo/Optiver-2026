# 05 — Team Operating Plan and GitHub Workflow

## 1. Organize around ownership and observable outputs

The following is a proposed division of work. Teammate names, skills, and the permitted team-size maximum were not supplied, so assign roles at the first team check-in instead of assuming them. Each task needs one owner and a definition of completion. More people can contribute without creating more live account connections.

| Role | Owns | First deliverable | Ongoing responsibility |
| --- | --- | --- | --- |
| Execution and risk owner | Live account connection, SDK adapter, position/order ledger, message budget, emergency behavior | A small working baseline with reliable fills, cancellations, and capacity checks | Sole authority for starting, stopping, and switching the live trader |
| Research and strategy owner | Historical data, features, fair value, parameter hypotheses, instrument selection | A short evidence memo and one candidate improvement | Keeps research causal and prevents validation results from becoming unsupported certainty |
| Evaluation and integration owner | Rule sheet, code integration, experiment IDs, comparison metrics, release artifacts | Baseline result record and reproducible config/commit | Decides with the team what is promoted and prepares the judging evidence |
| Optional fourth role | Data quality, monitoring, organizer questions, presentation | Verified rules and a concise status view | Frees the other owners from context switching |

With two people, combine research/evaluation and execution/integration. With three, use the first three rows. With a larger permitted team, assign additional independent research/review tasks; do not add concurrent order senders.

**Bernie's useful position is coordinator of the shared context and evidence unless the team explicitly assigns another role.** This is a proposed role, not an assumption about teammates' abilities. The package gives Bernie the material to explain the problem, keep decisions aligned, and identify when an idea conflicts with rules or observed results.

## 2. A ten-minute team briefing

The purpose is to synchronize decisions, not to read the entire handbook aloud.

| Minute | Topic | Required output |
| --- | --- | --- |
| 0–2 | Event universe, ±100 per symbol, reset, 20-minute final, qualitative judging | Everyone can state the actual objective and hard constraints |
| 2–4 | What the historical analysis actually showed | Agreement that no tested aggressive signal has established robust profitability |
| 4–6 | Baseline and one improvement | A precise experiment, chosen instruments, and initial small size |
| 6–8 | Owners and interfaces | One live owner; research outputs and proposed orders have clear boundaries |
| 8–10 | Open rules and next check-in | Named questions, deadlines, a baseline acceptance gate, and a freeze time |

End with a written decision card: “We are testing X, because Y, with size/limit Z; we stop or revert if W.” Replace vague statements such as “improve the algorithm” with a measurable task.

## 3. Milestones and completion criteria

| Priority | Milestone | Definition of done |
| --- | --- | --- |
| P0 | Rules and environment | Symbols/limits verified; official clock and remaining open questions recorded; correct Python/SDK identified |
| P0 | Single execution ownership | Only the assigned process controls the live account; teammates use files or the historical loader |
| P0 | State and risk correctness | Partial fills, outstanding buys/sells, unknown requests, and cancellation races cannot silently understate exposure |
| P0 | Minimal observable baseline | Small practice orders produce identifiable fills and account records; errors and stale data have explicit behavior |
| P1 | Comparable measurements | Experiment ID, commit, configuration, start/end, PnL marks, inventory, fills, and errors are recorded |
| P1 | One evidence-backed improvement | A changed mechanism is compared against the same baseline; keep/revert decision is documented |
| P1 | Restart and final procedure | Team can stop, reconcile, archive the prior run, recognize reset, and restart the frozen version |
| P1 | Explanation and submission | The final strategy, evidence, risks, novelty, and run command are concise and internally consistent |
| P2 | Additional instruments or signals | Added only if earlier gates are stable and time remains for measurement and rollback |
| P3 | Larger models, dashboards, architectural rewrites | Defer unless a concrete measured bottleneck makes them necessary |

P0 failures can invalidate every later result. P2 work must not take the only execution owner away from fixing a P0 failure.

## 4. Time allocation according to what remains

Use these as planning budgets, not official event times. They begin when the team adopts the plan. Adapt to the current state: do not rebuild a verified baseline simply to follow a timetable.

| Work | If about 120 minutes remain | If about 60 minutes remain |
| --- | ---: | ---: |
| Confirm rules and assign owners | 10 min | 5 min |
| Bring baseline to a small controlled practice run | 25 min | 15 min |
| Measure baseline and identify its actual weakness | 20 min | 10 min |
| Implement and compare one change | 30 min | 15 min |
| Recovery, final rehearsal, release freeze | 20 min | 10 min |
| Explanation and contingency buffer | 15 min | 5 min |

If fewer than 30 minutes remain, prioritize the working version, state correctness, a clean start after reset, and the explanation. A late model rewrite has little opportunity for honest evaluation. Do not interpret this as permission to operate without essential controls; select the smallest behavior whose risk and state can be verified.

Research can run in parallel with execution work when it uses historical files or the historical loader. Integration and account mutations remain sequential. The operator should not be interrupted for every interesting plot; researchers send a small proposal with an expected effect and rejection condition.

## 5. Define the interface before parallel coding

The proposed strategy interface consumes a validated market/account snapshot and produces **order intentions**, not SDK calls. The risk and order-management layers decide whether to submit them.

| Object | Minimum content | Important distinction |
| --- | --- | --- |
| Market snapshot | Symbol, best prices/depth, exchange time, receipt time, validity, instrument tick/bands | Last-known book does not mean freshly received book |
| Account state | Filled positions/cash, live residual orders, in-flight reservations, reconciliation status | Absolute positions must not be added to already applied fill deltas |
| Signal output | Fair value, horizon, confidence/status, feature timestamps, reason | No signal is a valid result; missing data is not zero price |
| Quote intention | Symbol, side, price, size, passive/aggressive purpose, expiry/reason | An intention is not an accepted or filled order |
| Execution event | Request ID, exchange order ID when available, event type, filled/residual quantity, timestamps | Unknown delivery must retain its risk reservation |
| Run record | Experiment ID, commit, config, environment, official session/time, starting state | Restarting a process does not reset the official competition clock |

Keep schema changes small and versioned. An owner changing a field name should update the consumer in the same reviewed change. A few explicit data structures are sufficient; a complex distributed system is unnecessary for this task.

## 6. A practical Git workflow

This handover is prepared as a repository folder; it has not been published to a remote GitHub repository. Add the folder to the team's chosen repository, then keep a stable main branch and short task branches. Use whichever GitHub collaboration process the team already understands.

Recommended branch names describe one change: `feature/imbalance-reference`, `fix/cancel-capacity`, or `docs/final-run-results`. Merge only after the integration owner can explain what changed, why it should help, and how to revert it.

Every candidate needs:

1. A commit identifier.
2. A versioned configuration or a saved exact configuration snapshot.
3. The same experiment card fields as the baseline.
4. Evidence that execution/risk behavior remains valid.
5. A rollback target that the operator has already run.

The live operator announces the active commit/config. A merged commit does not automatically change the running process. Do not let multiple people edit the active bot in place during a measurement window.

Use the provided `.gitignore` for local credentials, caches, raw data, runtime logs, and Python artifacts. Put intentional derived summaries in `evidence/`. Keep raw datasets in `data/raw/` locally and make their source/time/checksums discoverable without uploading participant records by default. Public distribution depends on the event's sharing policy.

The repository contains original summaries and an English adaptation of the user's recovered diagnostic. It does not grant a license to third-party repositories, books, slides, or the Optibook SDK. Link to those sources and use any reused source under its actual license and event rules.

## 7. How to compare experiments usefully

A candidate should change one mechanism. If a team simultaneously changes the signal, quote width, instrument set, size, and soft limit, a larger PnL does not identify what worked.

Before a run, record its hypothesis, changed parameter, unchanged controls, intended duration, starting inventory, and stop condition. Afterward, record:

- Official marked PnL change and the marking convention.
- Depth-aware liquidation estimate where feasible, with stale/missing marks identified.
- Per-symbol and buy/sell results; maximum absolute inventory and time near soft/hard limits.
- Number and volume of fills, fees, aggressive reduction costs, and markouts by horizon.
- Drawdown, exposure at the end, rejections, unknown requests, stale-data time, and disconnections.
- Whether different market conditions make comparison inconclusive.

Use absolute PnL differences when the denominator makes a percentage misleading. For example, a change from -1 to +1 is not usefully described as a standard percentage improvement. Do not annualize a 20-minute Sharpe estimate as if it were a stable investment track record.

## 8. Promotion and rollback

Promote only when the implementation is reliable, the explanation is coherent, and the new evidence is better than the baseline at comparable risk. Weak evidence can justify another small practice experiment; it does not justify immediate scaling to ±100.

Revert when the change introduces state uncertainty, repeated errors, unexplained inventory growth, materially worse conditional fill quality, or no measurable benefit before the freeze. Keep the negative result in the log. A reverted idea still improves the team's knowledge and can support a disciplined explanation to judges.

Establish the authority to stop clearly. Any teammate may flag a concrete problem; the operator executes the stop/cancel/reconciliation procedure. A model problem can disable that model while preserving the execution service. An account-state problem requires stopping new exposure and restoring reliable state.

## 9. Use coding assistants for bounded work, if permitted

The event's policy controls whether AI tools may be used. If allowed, useful tasks include reviewing a risk invariant, checking a CSV, translating a rule into an acceptance test, or finding an off-by-one timestamp error. Give the assistant the exact source and desired output. Require it to distinguish observed facts from suggestions.

A useful request is: “Review this order manager against the ±100 limit including cancel-pending and unknown inserts; produce a concrete counterexample if it can breach the limit.” A less useful request is: “Make us a winning bot.”

Keep AI inference and exploratory research outside the live order/hedge loop. The system must remain safe and operational if an assistant, browser, or research notebook is unavailable. `AGENTS.md` supplies concise project constraints for permitted assistance; it is not event authorization to use AI.

## 10. The handover between teammates

Before someone leaves or takes over, communicate the active mode, commit/config, current positions and open orders, unresolved requests, last confirmed PnL time, any disabled instruments, official remaining time, and the next decision. The handover is complete only when the receiver can state those facts back and the old/new execution ownership is unambiguous.

A short reliable status note is more valuable than a stream of unlabelled screenshots. Maintain one current run card and link detailed evidence from it.
