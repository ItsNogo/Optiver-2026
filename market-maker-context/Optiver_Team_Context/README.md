# Optiver x Bona Fide Delft — Team Context and Competition Playbook

**Event:** 12 November 2026 · **Language:** English · **Platform:** Optibook / Python  
**Purpose:** give every teammate and permitted coding assistant the same factual context, research evidence, implementation priorities, and operating procedure.

## Start here

The team needs a working, observable trading system, an honest explanation of its edge, and disciplined execution during the final 20-minute round. The strongest current recommendation is to test a simple, inventory-aware passive quoting baseline, measure its actual fills and adverse selection, and promote only improvements that survive fresh evidence. This is a proposed experimental direction, not an already profitable strategy.

**The most consequential research result:** the recovered diagnostic contains **212,509 order-book snapshots and 8,955 public trades**. None of the four non-control directional signal families, at any tested instrument/horizon combination, had a positive hypothetical crossing edge in both chronological partitions with at least 30 observations in each. The apparently attractive small-sample results are insufficient grounds for an aggressive trading bot. [E3; see the data audit]

**The most consequential operational rule:** the organizers will reset positions and PnL after approximately 21:00 local time and then run a 20-minute competition. **The team must start its algorithm after the reset.** Treat the organizer's actual reset/start announcement as authoritative; 21:00 is approximate. [E1]

## Confirmed event snapshot

| Item | Current evidence |
| --- | --- |
| Instruments | `AMD`, `AVGO`, `CRWV`, `MU`, `NBIS`, `NVDA`, `SNDK`, `VRT` |
| Position limit | Maximum 100 lots long or short **per instrument** |
| Research inputs | Historical orders, public trades, and order-book snapshots are available in the supplied environment |
| Actual recovered diagnostic | Public trades and pricebooks; **no raw orders file** |
| Practice | Until approximately 21:00 on the event date; practice resets may occur |
| Final | Positions and PnL reset; 20-minute scored competition; team initiates its algorithm |
| Judging | PnL, trading approach, risk taken, novelty, and potentially other considerations; weights not published in supplied slides |
| Account ownership | One coordinated live execution owner; recovered event context reports one connection per team account |
| Research access | `HistoricalDataLoader` can be used without constructing an `Exchange` connection |
| Unresolved | Fees, exact message limits, terminal valuation, AI/external-code policy, submission/presentation requirements, and any later organizer clarifications |

Sources and confidence levels are explained in [context and rules](docs/01_context_and_rules.md) and the [source register](docs/10_sources_and_provenance.md). The photographs supplied by Bernie were inspected directly. Older preparation documents are superseded wherever those photographs or the actual dataset provide better evidence.

## Reading paths

| Available time / responsibility | Read |
| --- | --- |
| Everyone, first 10 minutes | This README; context/rules; first section of the strategy playbook; final-round checklist |
| Strategy owner | Strategy playbook; full data audit; experiment card template |
| Execution and risk owner | Execution/risk chapter; final-round checklist; incident card |
| Research and evaluation owner | Data audit; curated evidence CSVs; validation standards; experiment log |
| Integration or team lead | Team operating plan; decision log; release checklist; judging narrative |
| A permitted AI assistant | `AGENTS.md`, the relevant chapter, current rule sheet, and the exact code/config it is asked to review |
| Full preparation context | `MASTER_CONTEXT.md`, the assembled single-document edition of the handbook |

## Documentation map

| File | What it explains |
| --- | --- |
| [01 — Context and rules](docs/01_context_and_rules.md) | Recovered preparation, authoritative event facts, superseded assumptions, and remaining decisions |
| [02 — Strategy playbook](docs/02_strategy_playbook.md) | Fair value, passive quoting, inventory, execution costs, adverse selection, candidate signals, and concrete decision rules |
| [03 — Actual data and research audit](docs/03_data_and_research_audit.md) | What was run, exact data coverage, signal results, reproducibility, limitations, and next experiments |
| [04 — Execution and risk](docs/04_execution_and_risk.md) | API semantics, order state, capacity, partial fills, reconciliation, failure recovery, and final-round mechanics |
| [05 — Team operating plan](docs/05_team_operating_plan.md) | Roles, work allocation, milestones, Git workflow, acceptance criteria, and time budgets |
| [06 — Final-round checklist](docs/06_final_round_checklist.md) | Before reset, after reset, during the 20 minutes, and at the finish |
| [07 — Prior competitions and resources](docs/07_competition_evidence.md) | What public winners and participants actually disclosed, with evidence limits |
| [08 — Reading map and learning exercises](docs/08_reading_map_and_exercises.md) | All 20 sources from the earlier preparation, priority readings, and worked checks |
| [09 — Judging and handover](docs/09_judging_and_handover.md) | Evidence-based explanation, likely questions, final report structure, and continuity |
| [10 — Sources and provenance](docs/10_sources_and_provenance.md) | Source authority, evidence dates, recovered artifacts, and what remains unavailable |
| [Templates](templates/README.md) | Rules, experiments, decision records, incidents, and final results |
| [Research](research/README.md) | Recovered research tool, reproduction instructions, and separation from live execution |
| [Evidence](evidence/README.md) | Machine-readable summaries and sensitivity checks |

## The next five actions

1. Assign one execution owner, one research owner, and one integration/evaluation owner. Combine roles if necessary; do not assume a particular team size is permitted.
2. Fill the rule sheet's open fields from the organizer or installed environment. Focus on fees, limits, the actual final-start procedure, terminal inventory, and permitted tools.
3. Establish a baseline that reads valid books, reconciles positions and orders, respects worst-case outstanding exposure, and records private fills. Start a small permitted practice experiment promptly once these controls work.
4. Compare a neutral passive baseline against one bounded improvement on fresh practice data. Keep code, limits, sizes, and evaluation windows comparable. Measure conditional fill quality, not just price prediction.
5. Freeze a version, rehearse restart and cancellation/reconciliation, and prepare the short explanation. Keep an operator watching through the reset and final start.

## What this package is

This is a consolidated handover of the relevant retrievable preparation, supplied event materials, actual diagnostic outputs, and explicit new recommendations. It is not a verbatim transcript of every past conversation. It does not contain a deployed trading bot or evidence of a successful scored run. The research script is a diagnostic; any live algorithm must still be implemented and validated in the official environment.

The package is ready to place in a GitHub repository. Use a private team repository while event-material sharing permissions remain unresolved. Keep credentials, account configuration, raw participant data, licensed books, and local execution logs outside version control. The package contains derived research evidence and source descriptions, rather than redistributing the original books or event photographs.

**Evidence labels:** `Confirmed` = supplied event source; `Observed` = inspected data/code; `Recommended` = a proposed decision; `Open` = unresolved; `Historical` = another event or older preparation. A recommendation becomes a team decision only when it is recorded with an owner and evidence.
