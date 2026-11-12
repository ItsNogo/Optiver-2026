# Evidence from Previous Competitions and Public Optiver Resources

**Research date: 12 November 2026.** This chapter distinguishes an organizer-confirmed result, a participant's account, and our own practical inference. These are different levels of evidence. None establishes the strategy that will win the current Bona Fide event.

## 1. What the evidence can and cannot tell us

Previous competitions help us prioritize ideas worth testing. They do not establish the current exchange mechanics, scoring weights, asset relationships, allowed libraries, or final valuation rules. A winning team's public write-up also cannot establish causation: a useful component may have helped, but the result alone does not reveal its marginal contribution. Unpublished components remain unknown.

The useful recurring pattern is a manageable quoting model, inventory control, careful inspection of the particular simulator, and an efficient research-to-execution workflow. This is an inference across the sources below, not an official Optiver judging rule. In the current eight-instrument event, use those lessons to build and evaluate a baseline. Add news, pair trading, or machine learning only when the current data and rules support the specific mechanism.

## 2. Evidence matrix

| Competition and team | Result and evidence status | What the public material establishes | What we can transfer | What must not be assumed |
| --- | --- | --- | --- | --- |
| **HackTheBurgh X, 2024 — Team LAB** | Devpost marks the project as the winner of the Optiver challenge. The creators claim the highest hourly PnL. | Optibook strategy combining market making with ML sentiment for directional news trades; the submission names Osi Obomighie, Bram Silue, Lulu Liu and Aurora. [C1] | Separate routine quoting from a special information-driven regime; explain the purpose of each component. | No exact model, thresholds, complete execution code, attribution study, or Delft news feed is established by this page. |
| **IC Hack 2025 — Dylan Beharall's team** | Participant's public account says the team won the Optiver Transistor Trades challenge; an organizer comments with congratulations. | Over a 24-hour event, the final approach used price forecasts, competitive two-sided quotes and inventory-based price adjustments. Named teammates: Damian Špigút, James Shao, Freddie Mao, Thomas Johnson and Xiuqi Zhang. [C2] | Make fair value and inventory explicit; learn from fill quality as well as PnL. | Exact forecasting model and code were not disclosed in the retrieved post. The wider hackathon's 750+ attendees are not a count of trading teams. |
| **Optiver Hackathon at TUM, June 2025 — Fabian Baier's team** | First place in PnL out of 70+ teams is participant-reported, not independently confirmed here as an overall judging win. | A short development window; microprice-based quoting, bounded imbalance influence, volatility adjustment, inventory control and a news/LLM overlay. The author says the implementation was withheld, although explanatory files are public. [C3–C4] | Bound signal contributions in ticks; expose few interpretable parameters; separate strategy from API adaptation and exchange limits. | Five approximately uncorrelated stocks and supplied news/LLM belong to that event. Its max-position news bets and execution assumptions should not be imported. |
| **Ready Trader Go 2023 — KPW / Jakub Szulc** | Optiver's announcement names Jakub Szulc as winner; its leaderboard lists KPW first, JKK second and FrankfurtHedgehogs third. [C5–C6] | A real winning result in Optiver's simulated-exchange competition. | A useful benchmark for what a competition result means when supported by organizer evidence. | These retrieved organizer sources do not expose the winning algorithm. Do not present another team's repository as KPW's winning code. |
| **Ready Trader Go 2023 — Budlahkee** | The team reports a finish in the **17–32 bracket**, outside the final 16. This is a strong participant example, not a winner. | Public Python/C++ artifacts; a volume-weighted trade-price estimate, dynamically adjusted spread, order-age cancellation and delayed hedging. The team says some volatility features underperformed and a C++ rewrite improved latency. [C7] | Use a simple measured baseline; reject additions that fail comparative testing; include explicit order lifecycle handling. | ETF/hedge mechanics, fees, message limits, performance from switching language and the team's reported participant denominator do not transfer to Delft. |
| **IMC Prosperity 2023 — Stanford Cardinal** | Second place is reported in the team's repository. | Public `trader.py`; product-specific models, a shared backtesting entry point and investigation of an apparent scoring problem using logs. The write-up includes fixed-value assets, basket relationships and participant-specific signals. [C8] | Investigate unexplained results; run the same strategy logic in research and submission; identify the mechanism separately for each product. | Fictional prices, conversion ratios, identity signals and hardcoded event timings are simulator-specific. None proves an AMD/NVDA arbitrage. |
| **IMC Prosperity 2024 — Linear Utility** | Second globally is reported in the team's repository. | Research, trader versions, a backtester and a synchronized dashboard. The team studied simulator details and found a less noisy reference quote for one product. [C9] | Inspect profitable trades the strategy missed and losing trades it accepted; verify how PnL is marked; make experiments reproducible. | The team's passive-fill approximation is a model, not proof of fills in Optibook. Fifteen days of research is not comparable to a short final round. |
| **IMC Prosperity 3, 2025 — Frankfurt Hedgehogs** | Second globally is reported in the team's repository, with an extensive public write-up and polished algorithm. | Five-round, fifteen-day contest against simulated participants; prepared visualization/backtesting tools; strategies tailored to market making, baskets, options, conversion and participant information. [C10] | Prepare diagnostic tools; understand failure cases; use a causal explanation for each product-specific edge. | These instruments and information channels are not confirmed for Delft. Copying its algorithm cannot create absent relationships. |
| **Optiver Realized Volatility Prediction, 2021–2022 — nyanp** | Kaggle's final leaderboard and winning write-up identify first place. | Forecasting volatility rather than sending orders; nearest-neighbor aggregation, time-order reconstruction and a LightGBM/MLP/CNN ensemble. A later ablation discusses the contribution of features and a tick-size leak. [C11–C14] | Validate chronology, run ablations and question unusually strong features. | Forecast accuracy is not executable trading PnL. Dataset reconstruction tricks, multi-hour training and cross-sectional data access may not be available live. |
| **Optiver Trading at the Close, 2023–2024 — hyd** | Kaggle labels the author's write-up first place. | Closing-price-movement forecasting with an ensemble of CatBoost, GRU and Transformer models, plus online updating and post-processing. The official metric is mean absolute error. [C15–C16] | Separate train/validation performance, evaluate added components and respect information availability. | A predictive leaderboard does not measure order fills, inventory risk, slippage or exchange reliability. This result does not justify building a large ensemble during the hackathon. |

### Corrections that matter

- **Highest PnL and overall prize winner are different claims.** State the actual result supported by the source.
- **Budlahkee is not the Ready Trader Go champion.** It is useful because its code and trade-offs are inspectable.
- **A missing component is not a component the team deliberately rejected.** Say “not disclosed” unless a source actually says it was tested and rejected.
- **Participant counts use different denominators.** For example, an author's count of accepted teams and an organizer's count of participating teams need not match. Avoid converting them into a precise comparative success probability.
- **No verified previous Bona Fide winning strategy was found in the material checked.** Similar Optibook events are analogies, not a record of this event's hidden design.

### Additional cases preserved from the earlier preparation

**Slabbers — HackTheBurgh 2025.** Hwayeon Kang's public participant account reports an Optiver challenge win using arbitrage and market making, with emphasis on the first task, trading frequency, price tolerance, risk control, IOC orders, and multithreading. The reported PnL is a participant claim without a disclosed comparable score series or full implementation. The useful lesson is to finish and measure the core mechanism before expanding. Parallel order submission does not make two legs atomic, and it is not a reason to add threads to the current synchronous single-owner design. [C25]

**ShapeShifters — Ready Trader Go EU/UK 2021.** LSE confirms the victory by Sylvain Girard and Yohaï-Eliel Berreby. The four-week contest supplied simulation histories after rounds. Their university interview describes complementary work on low-latency heuristics, short-horizon modelling and visualization, retaining changes supported by tests; the final submission was relatively simple. The transferable lesson is to assign parallel responsibilities and use evidence to choose the final system. The public interview does not expose a complete winning implementation or establish which explored ML models remained in it. [C17–C18]

**Calculated Gamblers — HackTheBurgh X.** Its Devpost submission claims the highest PnL, 30% above the runner-up, and news sentiment with risk management. It does not supply enough detail to reconcile that claim with Team LAB's winning designation and hourly-PnL claim. Preserve both as differently supported statements; do not invent an explanation or relabel Calculated Gamblers as the official winner. This is a practical example of why outcome labels and evaluation windows matter. [C19]

**Baruch — Rotman International Trading Competition 2026.** The organizer confirms Baruch's overall win. The official case package converts performance into rankings and case scores, with five cases weighted 20% each. Consistent placement can therefore beat an extreme profit in one heat. We found no inspectable winning Baruch algorithm in this review. This university competition illustrates the importance of the scoring function; it is not an Optiver or hedge-fund event and its rank aggregation is not the Delft rubric. [C20–C21]

### Historical scoring formats that must stay separate

| Reference | Evidence recovered | Strategic implication |
| --- | --- | --- |
| Optiver TraderHack 2022 | The earlier dossier records strategy, risk, code structure/creativity and PnL, with 24 hours of development and a 20-minute final. Its official historical PDF remains indexed, but the direct URL currently returns 404; the scoring passage was not independently recovered again in this pass. [C22] | Retain it as historical preparation context with that access limitation, not a substitute for today's scoring rules. |
| Ready Trader Go 2023 | The earlier dossier records a hierarchy of hard-limit compliance, final PnL, then tie-breaks based on PnL standard deviation and fees from its historical rules. [C23] | A constraint, an objective and a tie-break are different mechanisms. Do not invent a Sharpe-ratio objective or import these tie-breaks into Delft. |
| Citadel Datathons / Terminals, historical terms | Datathons involve data analysis and a presentation judged against criteria communicated to participants. Terminals involves bots competing in an online game. [C24] | The first is useful for evidence and presentation discipline; the second is a distinct tournament. Neither is a source of Optibook order mechanics or a verified Delft winning trading strategy. |

## 3. How to turn the cases into an actual decision

The following procedure is our proposed workflow. It is not a claim that past teams used precisely this process.

### Step A — Extract a mechanism, not a brand name

Replace “the TUM strategy won” with a testable statement such as: “A bounded imbalance term may improve short-horizon fair-value estimates beyond the midpoint.” Specify the observation available at decision time, the prediction horizon, expected effect, cost of acting, and conditions under which the effect should disappear.

For news, the mechanism is an event feed that reveals relevant information before prices finish adjusting. Without such a feed, sentiment machinery has no established input. For a basket, the mechanism is a documented or strongly validated relation between the basket and components. Similar industry names are insufficient.

### Step B — Decide whether the mechanism exists here

The team should answer five questions before implementation:

1. Does the current API provide the input, with usable timestamps and enough history?
2. Does the proposed relationship persist in later data, beyond the observations that inspired it?
3. Can a position actually be opened and closed within the spread, depth, latency and position constraints?
4. Can the effect survive a pessimistic treatment of passive fills and inventory valuation?
5. Can it be integrated and rolled back before the code freeze?

Any “no” turns the idea into a research note rather than a production feature.

### Step C — Keep a comparable baseline

Compare candidate changes with the same baseline, instruments, chronological evaluation segment and cost assumptions. Changing the fair value, quote width, size and inventory policy simultaneously prevents useful attribution. If a change improves total marked PnL only by holding more directional exposure, record that separately from spread capture.

An experiment should record the hypothesis, changed parameters, data interval, eligible observations, fills or fill assumptions, PnL by instrument, inventory extrema, drawdown, rejection count, and the decision to keep or revert. A small result with a clear mechanism is more useful than a large unrepeatable headline number.

### Step D — Measure the deployed implementation

A paper forecast arrives instantly and never disconnects. A live strategy has delayed data, order acknowledgements, partial fills and outstanding orders. Reject a research improvement if its implementation creates unreliable state or misses the relevant horizon. Preserve a working baseline and a single owner of order submission.

### Step E — Explain originality honestly

Originality can be the team's evidence-driven adaptation: a measured inventory penalty, a regime filter, an execution improvement, or a useful diagnostic. Attribute the inspiration and show what the team tested. Calling a standard model by a new name does not add evidence.

## 4. Public Optiver resources, with the correct scope

| Priority | Resource | Verified relationship and useful content | Application to this event |
| --- | --- | --- | --- |
| **Immediate** | [Optiver: Market Making](https://www.optiver.com/insights/explainers/market-making/) | Official explanation of theoretical value, two-sided pricing, spread and inventory risk. [R1] | Establish shared language for fair value, required edge and the risk of a filled quote. |
| **Immediate** | [Optiver explainers](https://www.optiver.com/insights/explainers/) → Orders and the order book | Official collection includes order-book mechanics and order types. [R2] | Read together with the current event's API documentation; general exchange explanations are not event configuration. |
| **Useful after the baseline works** | [Designing for latency and research iteration](https://www.optiver.com/insights/technology-blog/designing-for-latency-and-iteration/) — Daniel B., 20 July 2026 | Official article identifies the author as an Optiver Shanghai engineering team lead and discusses the trade-off between latency, research iteration and faithful simulation. [R3] | Keep the research-to-live interface small and reproducible; remove unnecessary work from the order loop. It is not a prescription to rewrite the bot in C++. |
| **Useful research perspective** | [The trading problem: why market data is a deep learning challenge](https://prod-www.optiver.com/insights/technology-blog/why-market-data-is-a-deep-learning-challenge/) — Karun Rao, 6 October 2026 | Official article by an Optiver quantitative researcher on noisy, nonstationary, irregularly sampled order-book data and production latency. [R4] | Use it to sharpen timestamp discipline, validation and model skepticism. It does not establish that deep learning is feasible or needed here. |
| **Background only unless derivatives appear** | [How to Calculate Options Prices and Their Greeks](https://onlinelibrary.wiley.com/resolve/openurl?genre=book&isbn=9781119011651) — Pierino Ursone, Wiley, 2015 | Publisher biography confirms the author began as an Optiver market maker. His own career page dates that work to 1992–1996 and partnership from January 1994. [R5–R6] | A real former-Optiver author, useful for option pricing and sensitivities. It is an independently published book, not an Optiver internal manual; Greeks are not the first priority for the current cash-equity universe. |
| **Evidence of teaching approach, not a downloadable course** | [Optiver & Imperial Trading Academy](https://www.optiver.com/join-us/events/the-optiver-imperial-trading-academy/) — Robbert Pullen | Official course description links market foundations/options theory with Python algorithm development and Optibook testing. [R7] | Supports studying mechanics, implementation and testing together. This does not verify a public book authored by Pullen or reveal the Delft scoring rubric. |

No retrieved source provides a verified internal Optiver trading manual. Do not describe participant repositories, general quant textbooks, recruitment assessments or commercially sold interview preparation as internal Optiver training material.

### The five exact Robbert Pullen videos from the previous preparation

The earlier dossier records a complete transcript review of these videos and the navigation times below. The links and timings are carried forward from that preparation; the videos were not re-transcribed or re-timed for this handover, and direct video retrieval was unavailable during this pass.

| Video | Duration recorded in the dossier | Most useful navigation points |
| --- | --- | --- |
| [Introduction to Financial Markets](https://www.youtube.com/watch?v=agJUYbpcXxY) | 9:19 | Instruments and relationships among shares, futures, indices and ETFs. |
| [Market Participants](https://www.youtube.com/watch?v=gNomxbBBIVA) | 9:43 | Theoretical price around 5:03; hedging around 7:30; stale prices around 8:43. |
| [Exchanges and Order Books](https://www.youtube.com/watch?v=Yt-45z3reiw) | 8:18 | Priority around 2:42; IOC around 6:50. |
| [Pairs Trading](https://www.youtube.com/watch?v=4isu0n1GOWU) | 5:08 | Relationships breaking around 2:01; less-liquid leg first around 4:04. |
| [Calculating P&L / Portfolio Value](https://www.youtube.com/watch?v=OFIwLbmqzY0) | 6:35 | Stale last trade around 1:43–1:56; depth-aware liquidation around 4:59. |

The recorded total is 39:03; videos 3–5 total 20:01. Treat “trade the difficult leg first” as conditional on a credible ability to hedge the resulting fill, not as a guarantee of simultaneous execution. A lecture's discussion of an order type does not make that type available in the current API. The dossier specifically notes that the general lecture discusses FOK while the supplied client documents `limit` and `ioc`.

### Historical material on automation risk and recommended books

**Robert van Gulik, _Risk Management at Optiver_, TopQuants, 12 November 2014.** The deck identifies him as Group Head Risk at that time. Its hedging example shows delayed confirmation producing repeated hedges and a destabilizing position sequence. This historical primary material directly motivates pending-order accounting, reconciliation and a single execution owner. It does not describe Optiver's current internal system. [R8]

**_Trading and Research — A note on mathematical careers at Optiver_.** A 23-page historical brochure survives on an external host. Its resources section reports prior in-house use of Euan Sinclair's _Option Trading_ and suggests Ganapathy Vidyamurthy's _Pairs Trading_ for competitions such as Ready Trader Go; it also lists Skiena's _The Algorithm Design Manual_. Treat it as a historical Optiver-attributed document with an unofficial current host. It does not prove that Sinclair worked at Optiver or that those books are the present curriculum. [R9]

**Current perspective worth reading after the baseline is stable:** Optiver's 2026 article _Machine learning in trading: an adversarial research problem_ explains why a historical fill can conceal adverse selection and why the tested strategy itself can change the environment. Use that perspective to challenge optimistic backtests, not to infer an undisclosed competition strategy. [R10]

## 5. A reading plan that respects the competition clock

**If there are only ten minutes:** read the current event rules and API first, then the TUM bounded-parameter idea and the IC Hack inventory-adjustment account. Record a single hypothesis to test. Someone else should already be checking the working baseline.

**If there are thirty minutes:** one researcher inspects the Linear Utility and Frankfurt Hedgehogs tooling discussions while another validates the current eight-instrument dataset. Share a short decision memo containing an observation, a proposed change, and a rejection condition.

**If preparation continues after this event:** study the complete repositories and the forecasting competitions. Reimplement one mechanism in an isolated environment and compare it with a simpler baseline. Review any repository license and the event's reuse rules before copying source code into the team's repository; links and original summaries are sufficient for this handover.

## 6. Source register

This source record was assembled on 12 November 2026; entries distinguish fresh retrieval from findings explicitly carried forward from the earlier dossier. A participant-authored account remains a participant account even when hosted on GitHub or LinkedIn. Search-retrieved sources that could not be fetched directly are marked explicitly.

- **C1:** [Team LAB, HackTheBurgh X project submission](https://devpost.com/software/teamlab-optiver-team-014). Devpost winner designation plus participant description.
- **C2:** [Dylan Beharall, IC Hack 2025 account](https://www.linkedin.com/posts/dylan-beharall_over-the-weekend-my-team-and-i-won-the-optiver-activity-7292178250691211264-JgNE). Participant account and organizer congratulations.
- **C3:** [Fabian Baier, Optiver Hackathon TUM repository](https://github.com/fabianbaiertum/Optiver-Hackathon-TUM). Participant description and explanatory artifacts.
- **C4:** [TUM event write-up](https://github.com/fabianbaiertum/Optiver-Hackathon-TUM/blob/main/Test.md). June 2025/date and 70+ team claim.
- **C5:** [Optiver's Ready Trader Go 2023 winner announcement](https://www.linkedin.com/posts/optiver_readytradergo2023-algorithmictrading-studenttraders-activity-7049050847288152064-W3S6). Organizer announcement.
- **C6:** [Ready Trader Go leaderboard](https://readytradergo.optiver.com/leaderboard/). Organizer page, retrieved through search; direct open timed out. Numerical scores displayed by the old page were not used.
- **C7:** [Budlahkee repository](https://github.com/jakubtokarz/Trading-Algorithm_Ready-Trader-Go). Participant code and account.
- **C8:** [Stanford Cardinal repository](https://github.com/ShubhamAnandJain/IMC-Prosperity-2023-Stanford-Cardinal). Participant code and account.
- **C9:** [Linear Utility repository](https://github.com/ericcccsliu/imc-prosperity-2). Participant code, research tools and account.
- **C10:** [Frankfurt Hedgehogs, Prosperity 3](https://github.com/TimoDiehm/imc-prosperity-3). Participant code and account.
- **C11:** [Optiver volatility challenge overview](https://www.kaggle.com/c/optiver-realized-volatility-prediction). Official competition description.
- **C12:** [Final volatility leaderboard](https://www.kaggle.com/competitions/optiver-realized-volatility-prediction/leaderboard). Official placement.
- **C13:** [nyanp winning solution](https://www.kaggle.com/competitions/optiver-realized-volatility-prediction/discussion/274970). Winner-authored write-up.
- **C14:** [nyanp ablation study](https://www.kaggle.com/c/optiver-realized-volatility-prediction/discussion/302626). Winner-authored follow-up.
- **C15:** [Trading at the Close overview](https://www.kaggle.com/competitions/optiver-trading-at-the-close/overview). Official objective and metric.
- **C16:** [hyd winning solution](https://www.kaggle.com/competitions/optiver-trading-at-the-close/writeups/hyd-1st-place-solution). Winner-authored account retrieved through search; direct page provided no readable text.
- **R1:** [Optiver market-making explainer](https://www.optiver.com/insights/explainers/market-making/).
- **R2:** [Optiver explainer collection](https://www.optiver.com/insights/explainers/).
- **R3:** [Daniel B., latency and iteration](https://www.optiver.com/insights/technology-blog/designing-for-latency-and-iteration/).
- **R4:** [Karun Rao, market-data modelling](https://prod-www.optiver.com/insights/technology-blog/why-market-data-is-a-deep-learning-challenge/).
- **R5:** [Wiley, Ursone book and author biography](https://onlinelibrary.wiley.com/resolve/openurl?genre=book&isbn=9781119011651).
- **R6:** [Pierino Ursone career history](https://www.pierinoursone.com/how-i-got-there).
- **R7:** [Optiver & Imperial Trading Academy](https://www.optiver.com/join-us/events/the-optiver-imperial-trading-academy/).
- **C17:** [LSE: ShapeShifters' 2021 win](https://www.lse.ac.uk/news/latest-news-from-lse/l-december-21/lse-student-wins-market-making-competition). University announcement.
- **C18:** [Télécom Paris: interview with ShapeShifters](https://www.telecom-paris.fr/algorithmique-cybersecurite-etudiants-gagnent-concours?dest=wavegame). University-hosted participant interview.
- **C19:** [Calculated Gamblers submission](https://devpost.com/software/optiver-cylfh6). Participant claim; no reconciliation with Team LAB's award established.
- **C20:** [Rotman: Baruch's 2026 win](https://rotman.utoronto.ca/news-events-and-ideas/news-and-stories/2026/february/baruch-college-wins-rotman-international-trading-competition/). Organizer announcement.
- **C21:** [Rotman 2026 official case package](https://rotmanfrtl.github.io/RITC%202026%20Case%20Package.pdf). Scoring methodology, pages 43–46.
- **C22:** [TraderHack 2022 historical official rules](https://www.optiver.com/wp-content/uploads/2022/02/TraderHack-2022-Competition-Terms-and-Conditions-Official-Rules.pdf). Still indexed; direct retrieval returned 404. Detailed scoring retained from the prior dossier.
- **C23:** [Ready Trader Go March 2023 historical rules](https://readytradergo.optiver.com/wp-content/uploads/Ready-Trader-Go-2023-Terms-and-Conditions_version_March_2023.pdf). Detailed tie-break ordering retained from the prior dossier, not reverified in this pass.
- **C24:** [Citadel Datathon and Terminals historical terms](https://www.citadel.com/wp-content/uploads/2023/11/Citadel-Datathon-and-Terminals-Programs-Certification-and-Terms.pdf). Program Participation, pages 3–4.
- **R8:** [Robert van Gulik's TopQuants risk presentation](https://www.topquants.nl/wordpress/wp-content/uploads/2015/01/Van-Gulik-Risk-management-at-Optiver.pdf). Historical primary presentation; delayed-acknowledgement illustrations were visually inspected.
- **R9:** [Historical Optiver-attributed Trading and Research brochure](https://mathsfeedblog.wordpress.com/wp-content/uploads/2022/12/ff402-tradingandresearchatoptiver.pdf). External copy, resources on pages 22–23.
- **R10:** [Optiver: Machine learning in trading, an adversarial research problem](https://www.optiver.com/insights/technology-blog/machine-learning-in-trading-an-adversarial-research-problem/). Official research article, October 2026.

- **C25:** [Hwayeon Kang, Slabbers participant account](https://www.linkedin.com/posts/hwayeon-kang_im-excited-to-share-that-our-team-slabbers-activity-7302111254427406336-meco). Participant-reported result and approach, retrieved during this handover.
