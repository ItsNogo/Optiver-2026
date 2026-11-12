# 01 — Recovered Context, Event Rules, and Open Decisions

## 1. Mission and current strategic position

The event is **Optiver x Bona Fide Delft, 12 November 2026**, also advertised as an Optiver Coding Challenge / Mini Hackathon. The supplied mission is to investigate historical market activity for a small stock universe, understand its dynamics, and use that research to build a profitable trading strategy. The implementation environment is Python and Optibook. [E1, E2, E4]

The eight supplied symbols are `AMD`, `AVGO`, `CRWV`, `MU`, `NBIS`, `NVDA`, `SNDK`, and `VRT`. Their names alone do not establish the simulator's economic relationships, real-world price feeds, common factors, fundamental values, or instrument convertibility. Treat the supplied market and its rules as the problem definition. [E1; interpretation]

Preparation originally explored several possible Optibook formats: single-asset market making, dual listings, options, ETFs, news, and predictive datasets. Those were branches to prepare for before the problem was known. The current materials support a historical-data-driven stock trading challenge. No supplied source establishes a guaranteed dual-listing identity, basket conversion, option payoff, or news-based mechanism for this edition. Consequently, the active plan centers on data quality, stock fair-value estimation, order execution, inventory, and experiment design. [E1–E4]

The goal is to improve the team's probability of producing the strongest defensible submission. No recovered evidence supports a guaranteed winning strategy or a numerical probability of winning.

## 2. How the preparation developed

| Stage | Material recovered | What to retain now |
| --- | --- | --- |
| Initial preparation, 11 November | A 15-page preparation guide, public event research, comparable competitions, and a reading map of 20 supplied finance sources | Microstructure, executable prices, inventory, validation, team discipline; conditional branches remain reference material |
| Deeper preparation, 11–12 November | A 14-page winner/case-study dossier and user-supplied Optibook API/common types | Distinguish official results from participant claims; implement actual SDK semantics |
| Event briefing, 12 November | Photographs of mission, risk, fair-value, competition, and recommendation slides | Actual symbols; ±100 lots; approximate practice cutoff; reset and 20-minute final; qualitative judging criteria |
| Early event tooling | `optibook_market_scout.py` | A read-only scout that still opens `Exchange`; it must not compete with the live owner for the account connection |
| Supplied notebook | Setup, instrument metadata, orders, fills, PnL, and `HistoricalDataLoader` examples | Official paths and method semantics; distinguish historical research from a live account connection |
| Historical research tooling | `optibook_research.py` and an earlier research-kit ZIP | A diagnostic that uses the historical loader without opening `Exchange` or sending orders |
| Completed historical run | `diagnostico_optibook.zip`, uploaded on 12 November | Inspectable raw trades/books, report, metadata, summary, and signal screen |
| This handover | Source reconciliation, offline reproduction, sensitivity checks, strategy/engineering/operations chapters | A common reference that prevents stale assumptions and unsupported claims from propagating |

The two older PDFs are preparation artifacts, not official rules. The original set of 20 books was previously reviewed through contents and selected passages; this handover preserves that reading map without claiming a fresh cover-to-cover audit. [E4, E5]

## 3. Rules confirmed from the supplied slides

| Rule | Operational meaning | Evidence |
| --- | --- | --- |
| Universe contains the eight named stocks | Validate instruments against the current runtime and keep the active configuration explicit | Mission photographs, `IMG_3362` / `IMG_3363` |
| Maximum 100 lots long or short per instrument | Treat `-100 <= q_i <= 100` as the hard filled-position limit; also reserve capacity for outstanding and uncertain orders | Risk photographs, `IMG_3364` / `IMG_3365` |
| Practice until approximately 21:00 today | Use the live organizer announcement for the actual cutoff | Competition photograph, `IMG_3367` |
| Positions and PnL reset before the final | Archive practice evidence, begin a new final-run ledger epoch, and reconcile the actual post-reset state; do not treat practice balances or positions as current | `IMG_3367` |
| Final competition lasts 20 minutes | Use elapsed time from the official competition start, separate from bot launch; a restart does not create another 20 minutes | `IMG_3367` |
| Team is responsible for starting its algorithm after reset | Assign a named operator and rehearse the procedure | `IMG_3367` |
| PnL matters, along with approach, risk, and novelty | Produce measured performance and a clear explanation; do not optimize an invented weighted score | `IMG_3367` |
| Start simple, iterate, get connected/trading early in practice, and ask for help | Prefer small, controlled experiments once core controls work; avoid spending the whole event refining an untested model | Recommendation photograph, `IMG_3368` |

The competition slide describes AirPods 5 for members of the winning team and speakers for runners-up. This supersedes the earlier public advertisement's possible iPhone incentive; it has no effect on trading design. It does not establish a team-size limit. [E1, E4]

The relevant local clock is Delft time. On this date Delft and Madrid share CET (UTC+1). Store machine timestamps in UTC and display the competition countdown against the organizer's stated start. The historical dataset timestamps are UTC, not local time.

## 4. What the supplied platform material establishes

The event notebook uses `Exchange()` with configuration-derived access and illustrates the synchronous client. It demonstrates instrument metadata, order-book access, order insertion/deletion/amendment, public trade ticks, private fills, positions/cash, and `get_pnl()`. It also supplies `HistoricalDataLoader` for trades, orders, and pricebooks. [E2]

Relevant distinctions:

- An accepted order is not a confirmed fill. The insert response and the fill record answer different questions.
- IOC means an unfilled remainder does not rest. It does not promise all-or-nothing execution.
- Cancel on disconnect removes resting orders; it does not liquidate inventory.
- A process that only reads through `Exchange` still consumes a live connection. The older scout is not safe to start casually alongside the trader.
- Historical-loader research is a separate access path; the recovered diagnostic used it without an `Exchange` connection.
- Last-trade marked PnL is not guaranteed liquidation value, and the method's marking behavior does not establish the judges' terminal rule.
- The generic client supports instrument types beyond this event's stocks. The presence of options/news fields is not evidence those features are active here.
- Broad API validators such as prices up to 1,000,000 or volumes up to 100,000 are not useful quote levels, position limits, or permission to submit those sizes.

See the execution chapter for the exact recovered signatures, response semantics, and reconciliation requirements. Do not treat any copied tutorial order as a safe production order merely because its syntax is valid.

## 5. Reconciliation of old and new assumptions

| Earlier assumption / example | Current treatment |
| --- | --- |
| Instruments and final duration were unknown | Resolved by the event slides: eight stocks and a 20-minute post-reset final |
| A generic FAQ showed ±300 | Superseded for this event by ±100 per instrument |
| Other mini-hackathons allowed four people | Does not prove the current team-size rule |
| Dual listing might be the challenge | No identity is established for this universe; do not create a synthetic equivalence |
| News/LLM methods helped other winners | Retain as historical context; current event evidence has not established an actionable news feed |
| A high positive predictive metric might justify trading | Must survive executable prices, costs, latency, fills, limits, and fresh evidence |
| A historical run completed successfully | Confirms a data/analysis pipeline, not profitability |
| The requested interval was 30 minutes | Actual observed books span approximately 28 minutes 39 seconds and stop about 80.7 seconds before the requested end |
| The historical loader supports orders | The actual recovered diagnostic ZIP contains no raw orders dataset |
| The final begins at exactly 21:00 | The slide says approximately; the actual organizer signal controls |
| A read-only market scout is operationally harmless | It opens the account connection and can interfere with the sole live owner |

## 6. Questions that still change implementation

These are concrete missing fields to resolve once with an organizer or the running environment, then record in `templates/rules_sheet.md`. They are not reasons to stop all preparation.

| Question | Why the answer changes the system | Interim behavior |
| --- | --- | --- |
| What fees or rebates apply to each execution? | Changes the minimum profitable edge and maker/taker comparison | Historical zero-fee results remain conditional; reserve an explicit fee field |
| How is final inventory valued or liquidated? | Determines ending policy and whether residual exposure is penalized | Maintain manageable inventory and preserve the ability to close; do not assume forced liquidation |
| What are message/order limits and burst rules? | Determines polling, cancel/replace frequency, and emergency capacity | Use a conservative budget and measured pacing; obtain exact limits |
| Are there extra gross/net/notional or outstanding-order limits? | Per-symbol ±100 alone may be insufficient | Apply conservative local caps and do not infer missing global rules |
| What are each instrument's tick, lot size, and price bands? | Determines valid prices, sizes, units, and guards | Read metadata; do not infer ticks from median spread |
| How exactly does the reset affect live connections, orders, histories, and caches? | Determines restart and ledger-clearing sequence | Stop new submissions, wait for announced reset, reconcile, and start explicitly |
| What code/submission/presentation is required and when? | Determines what must be frozen and handed in | Prepare a commit, config, run command, logs, and short explanation |
| Are AI, internet, prewritten code, and external packages allowed? | Determines permitted workflows | Use materials according to the event's actual rules; keep the trading loop independent of AI |
| Can event data, code, and materials be shared publicly? | Determines repository visibility and included files | Use team-private collaboration and summarized sources |
| Are there precise judging weights or tie-breakers? | Determines the optimization target | Report PnL, exposure, drawdown, approach, and novelty separately |

## 7. What “complete context” means in this handover

The package preserves the relevant retrievable event preparation, its changes over time, the original problem's concrete constraints, the actual research results, and explicit proposed next steps. It does not fill gaps with invented meeting details, teammate names, hidden scoring weights, measured latency, transaction fees, a proven alpha, or final competition results. It also excludes unrelated personal history: the group needs the competition context and working decisions.

Source authority is: current organizer clarification, supplied event slides, installed event SDK and supplied notebook, observed data, earlier preparation, then external analogies. Record any later rule change with its source and time so the whole team makes the same update.
