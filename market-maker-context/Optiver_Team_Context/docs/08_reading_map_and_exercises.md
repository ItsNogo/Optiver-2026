# Reading Map and Worked Readiness Exercises

## Purpose and provenance

This chapter preserves the complete **20-source inventory** from the original preparation guide, with priorities adjusted to the current eight-stock universe: **AMD, AVGO, CRWV, MU, NBIS, NVDA, SNDK and VRT**. Options, ETFs, conversions and contractual relationships between these instruments have not been established. Read to resolve an implementation decision, then return to the working strategy.

The earlier guide reports extracting text and contents from **20 PDFs totaling 7,011 pages**, inspecting contents and selected passages. **Neither that guide nor this handover claims a complete reading of those 7,011 pages.** The page references below are inherited from that inspection; the underlying books have not been freshly audited or their code comprehensively tested here. They refer to **one-based PDF viewer pages in the original copies**, which may differ from printed page numbers and other editions. A `+` means “from this page onward,” as recorded previously. [P1]

These books are independent references. Their inclusion does not identify the authors as Optiver employees or their advice as an official competition requirement.

## 1. Complete reading inventory

| ID and source | Inherited PDF references | Priority and decision to extract now |
| --- | --- | --- |
| **B01 — Finding Alphas**, Igor Tulchinsky and contributors. Second edition, 2020; 321 PDF pages. | Chapter 9: **88–95**; chapter 10: **96–100**; robustness **108+**. Earlier focused selection: **91–94, 97–99**. | **High.** Define an independent validation interval, realistic costs and information available at the decision timestamp. Keep few parameters. Longer-horizon stock signals need separate evidence before use in this simulator. |
| **B02 — Option Volatility and Pricing**, Sheldon Natenberg. Second edition; 588 pages. Copy shows copyright 2015 although filename says 2014. | Delta **117–122**; delta convention **119**; dynamic hedging **136+**, focused **136–139**; market making **445–447**; arbitrage **282+**. | **Selective now: 445–447.** Defer option-specific material unless options are confirmed. If used later, verify whether delta is on a 0–1 or 0–100 scale and apply contract multipliers. |
| **B03 — An Introduction to Quantitative Finance**, Stephen Blyth. 2014; 192 pages. | No-arbitrage **64–68**, focused **64–66**; replication **88+**; delta/vega **118**. | **Medium.** Understand why identical payoffs differ from correlated prices. Useful before anyone labels an eight-stock pair an arbitrage. |
| **B04 — Paul Wilmott Introduces Quantitative Finance**, Paul Wilmott. Second edition, 2007; 724 pages. | Greeks **211–225**; delta hedging **254–273**. | **Defer.** An alternative deeper reference if derivatives appear; not an additional mandatory reading alongside Natenberg. |
| **B05 — Quantitative Finance for Dummies**, Steve Bell. 2016; 412 pages. | Greeks **227–233**; overfitting **334–335**. | **Targeted reference.** Consult a specific conceptual gap. Prioritize overfitting over option terminology for the current task. |
| **B06 — Python for Quants, Volume I**, Paweł Lachowicz. First edition, November 2015; 235 pages. | Exceptions **51–52**; numerical precision **56–58**; NaN/arrays **159–161**. | **Low.** Useful reminders for invalid data and numerical checks. Its Python 3.5 installation material is historical; use the supplied event environment. |
| **B07 — Algorithmic Short Selling with Python**, Laurent Bernut. 2021; 377 pages. | Edge **130–134**; sizing **192–198**; gross exposure **262**; net exposure **275**; beta **277**. | **Medium for risk; low for signals.** Distinguish expected profit from win rate and gross exposure from net exposure. Daily trend rules are unvalidated here. |
| **B08 — Machine Learning in Trading**, Ishan Shah and Rekhit Pachanekar / QuantInsti. 205 pages; publication year unclear in the inspected copy. | Train/test **32–38**, especially **35–38**; metrics **43+**; backtesting **53+**. | **Medium.** Preserve temporal order and distinguish forecast quality from profit after execution costs. |
| **B09 — Mastering Financial Pattern Recognition**, Sofien Kaabar. Publication October 2022 / copyright 2023; 291 pages. | Biases **77–79**; risk **273–280**. | **Low.** Bias and risk passages may help. Candlesticks and RSI have no established edge in this event. |
| **B10 — Positive Alpha Generation**, Claude Diderich. Copyright 2009; 369 pages. | Chapter 13 **212–218**; costs **213**; depth **214**; valuation versus execution **215**. | **Medium to high.** Translate theoretical edge into executable prices and available size; reject profits that disappear when filled realistically. |
| **B11 — How I Became a Quant**, edited by Richard R. Lindsey and Barry Schachter. 2007; 402 pages. | Introduction **17–24**; interviews **25+**. | **Defer.** Career context and networking, with little immediate help for implementing or validating this bot. |
| **B12 — How Markets Really Work**, Laurence A. Connors and Conor Sen. 2004; 164 pages. | Market Edges **9–13**; highs/lows **16–29**. | **Low.** Historical S&P 500 observations from 1989–2003 do not establish predictive behavior in this simulated market. |
| **B13 — Quantitative Finance with Python**, Chris Kelliher. 2022; 698 pages. | Greeks **305–320**; hedging **318–319**; trading models **586–592**; costs **588**; biases **590–591**. Earlier selection **318–319, 588–591**. | **High for 586–592.** Connect signal, position, costs and evaluation. Defer Greeks and option hedging; unnecessary rebalancing can consume an edge. |
| **B14 — Advanced Algorithmic Trading**, copy referencing QuantStart. 517 pages; author/year not unequivocal on inspected cover. | Cointegration **168+**; Kalman **198–213**; selection **288–303**; decay **502–505**. | **Conditional.** Relevant if a statistical pair is supported by adequate data. Cointegration is unnecessary for an actual contractual identity and does not convert correlation into guaranteed convergence. |
| **B15 — Machine Learning in Finance**, Matthew F. Dixon, Igor Halperin and Paul Bilokon. 2020; 565 pages. | Temporal validation **234–235**; limit-order-book prediction **277–278**; reinforcement learning **299+**. | **Selective.** Validation and book representation are useful. Recurrent networks and RL have low priority within this implementation window. |
| **B16 — Trading Strategies for Cryptocurrencies Based on Machine Learning Scenarios**, Xiangyang Gao and Yuchen Hou. EMFRM 2022 article in a 2023 volume; 9 pages. | Arbitrage classification **3–5**; trend-following limitations **8**. | **Low.** This is an article, not a book or documentation of Optibook. Use only for terminology. |
| **B17 — Handbook of Artificial Intelligence and Big Data Applications in Investments, Part III**, CFA Institute Research Foundation. Copyright 2023; 16-page extract. | Chapter 8, Peer Nagy, James Powrie and Stefan Zohren: **10–16**; matching **11**; OFI/OBI/microprice **12**; execution **14**. Earlier selection **10–12**. | **Highest.** Direct connection between order-book observations, matching, features and a simple algorithm. Check the microprice exercise below before combining signals. |
| **B18 — Algorithmic Trading Methods**, Robert Kissell. Second edition, copyright 2021; 614 pages; filename says 2020. | Fees/rebates **70**; priority **71**; market making **75–76**; costs **82–90**. | **High.** Understand queue priority and adverse selection. Executing a prescribed order cheaply and generating profitable trades are different objectives. |
| **B19 — Artificial Intelligence and Machine Learning in Finance: Addressing Complex Problems and ESG Applications**, Annalisa Ferrari. 2025; 108 pages. | Data **13–17**; trading **44–48**; ESG **65–79**; risk **83–88**. | **Low.** Extract data quality and timestamp alignment if needed. ESG material does not establish an input or signal for this simulator. |
| **B20 — Quantitative Trading: How to Build Your Own Algorithmic Trading Business**, Ernest P. Chan. Copyright 2009; 204 pages; filename says 2008. | Pitfalls **72–76**, focused **73–74**; sensitivity/costs **82–83**; execution **109–110**; risk **117+**. | **High.** Apply simple baselines, cost-aware tests and parameter sensitivity. Adapt old vendor and installation examples rather than copying them. |

All edition details, page counts and ranges in this inventory are carried forward from [P1], not independently verified bibliographic claims.

## 2. A 45-minute reading path

This is a proposed maximum, not a prerequisite for trading. If the baseline has an unresolved operational problem, assign one person the relevant passage while the others fix it.

| Minutes | Read or do | Required output |
| --- | --- | --- |
| **0–8** | B17 **10–12**, then execution context on **14**. | Define midpoint, spread, imbalance, microprice, IOC and a partial fill in the team's own words. |
| **8–15** | B18 **70–71, 75–76**. | List why a quote at a displayed price might not fill, or might fill just before an adverse move. |
| **15–23** | B01 **91–94, 97–99**. | Specify the chronological holdout and exclude features unavailable at decision time. |
| **23–29** | B20 **73–74, 82–83**. | Record costs, two plausible parameter perturbations and a failure condition. |
| **29–35** | B13 **588–591**. | Define the difference between signal accuracy, simulated PnL and measured live PnL. |
| **35–45** | Solve the exercises below aloud. | Every member can calculate capacity and explain why apparent profit may not be executable. |

For a specific arbitrage dispute, substitute B03 **64–66** for part of the validation reading. For quoting fundamentals, B02 **445–447** is an optional substitute. Neither substitution requires studying options first.

## 3. Worked comprehension exercises

### Exercise 1 — Microprice and double counting

Best bid is **99**, best ask **101**, bid size **90**, ask size **10**. Calculate midpoint, top-level imbalance and the simple imbalance-weighted price.

$$
m=(99+101)/2=100,\qquad I=(90-10)/(90+10)=0.8.
$$

$$
p_\mu=\frac{101\times90+99\times10}{100}=100.8.
$$

With half-spread $h=1$, the exact identity is $p_\mu=m+hI$. Therefore, a forecast using both this price and imbalance already contains the same information twice if it treats them as independent confirmations. An additional fitted imbalance coefficient is possible, but needs validation; it is not a second independent signal. This simple estimator is not proof that the next trade or future midpoint will be 100.8.

### Exercise 2 — Capacity with pending orders

Hard position limit $L=100$, current position $q=80$, outstanding buys **15**, outstanding sells **30**. Can we submit another buy of 20?

**No.** The buy-side worst case is that buys fill while sells do not:

$$
q_{\max}=80+15=95,\qquad \text{additional buy capacity}=100-95=5.
$$

Buying another 20 could produce **115**, a breach. Netting the outstanding sells against buys incorrectly assumes those sells will execute. Include unacknowledged buy requests whose outcome remains uncertain in the reserved capacity too. A cancellation request releases capacity only after its outcome is reconciled.

### Exercise 3 — Midpoint difference versus executable arbitrage

Suppose two instruments genuinely have equivalent 1:1 payoffs. A quotes **100.00 / 100.04**; B quotes **100.02 / 100.06**. Their midpoints differ by 0.02. Is buying A and selling B profitable?

The executable gross edge is **bid B − ask A = 100.02 − 100.04 = −0.02 per pair**. The reverse direction gives **100.00 − 100.06 = −0.06**. Neither direction is profitable even before costs. Available depth, latency and leg execution also matter. For two independent stocks, first establish the proposed relationship: the numerical calculation alone cannot make their payoffs equivalent.

### Exercise 4 — Partial fills and the actual residual

Assume a real 1:1 economic identity with matching multipliers and currency. We request buys of **20 A** and sells of **20 B**, but only **12 A** and **20 B** execute.

Positions are $+12A,-20B$; net equivalent exposure is **−8**. Potential repairs include buying **8 A** to complete the intended hedge, or buying **8 B** to reduce the excessive short leg. Choose using capacity, depth and a permitted price bound. Reconcile uncertain requests first; do not resend the original quantity of 20. With IOC, verify the final fill and cancellation of the unfilled remainder.

A resulting $+12A,-12B$ pair still consumes both instruments' limits and may require later unwinding. If the instruments are merely correlated stocks, “−8” is not an adequate portfolio risk measure.

### Exercise 5 — Turnover, marked PnL and liquidation

**A. Turnover.** Buy 10 at 100.00 and sell 10 at 100.02. The round trip trades **20 lots**, has gross notional turnover **2,000.20**, and earns **0.20 before costs**. If total fees are 0.30, net PnL is **−0.10**. Trading more is not itself a profitable result.

**B. Valuation.** Start with zero cash and inventory. Buy 20 at 100.00, leaving cash **−2,000**. Last trade is 100.30; the current book is 100.10 / 100.14. The bid has 5 lots at 100.10 and 15 at 100.00. Assume no fees for this illustration.

- Last-trade marked PnL: $-2000+20(100.30)=6.00$.
- Midpoint marked PnL: $-2000+20(100.12)=2.40$.
- Liquidation estimate from displayed depth: $-2000+5(100.10)+15(100.00)=0.50$.

These are three valuations of the same position. Displayed depth can change before execution, so even 0.50 is an estimate until fills occur. Record the official score and a separate liquidation estimate; investigate the gap. A last-trade marking convention is not a reason to manufacture a favorable last trade.

## 4. Readiness standard and source

The team is ready to reason about the baseline when every member can explain these five exercises without guessing, identify which quantities are observed versus estimated, and locate the relevant rules in the current event documentation. Reading more pages is useful only when it resolves a concrete decision.

**[P1]** Original preparation artifact, *Guia_Optiver_Delft_12_Nov_2026.pdf*, section 12 on PDF pages **12–13**, and its readiness exercises on page **14**; prepared 11 November 2026. The inventory and navigation references are inherited. The 45-minute schedule, expanded explanations and turnover/valuation examples are proposals and worked calculations for this handover.
