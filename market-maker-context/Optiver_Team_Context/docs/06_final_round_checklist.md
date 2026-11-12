# 06 — Final-Round Checklist

## 1. Official facts and the clock

The event slide says practice continues until approximately **21:00 on 12 November 2026**. After 21:00, organizers reset **positions and PnL** one final time and run a **20-minute competition**. **Starting the algorithm after reset is the team's responsibility.** PnL, approach, risk taken, and novelty contribute to judging; no numerical weights are supplied. [E1]

Use **Delft local time: CET, UTC+1**. Madrid uses the same offset on this date. Thus 21:00 CET corresponds to 20:00 UTC, but that conversion does not establish an exact start time. Define `T0` as the organizer's actual competition start, and record the bot's launch time separately. A late launch or restart does not create another 20-minute scoring window. Use monotonic elapsed time for the countdown and UTC for stored event timestamps.

The schedule below is a **recommended operating plan**, not an official timetable. The organizer's announcement overrides every suggested checkpoint. There is **no established requirement to finish flat**; the ending policy depends on the confirmed scoring and inventory rules.

## 2. Stage-by-stage plan

| Stage | Operator's action | Evidence before proceeding |
| --- | --- | --- |
| While roughly 20 minutes of practice remain | Freeze the best validated commit/configuration; rehearse restart and stop; assign operator and backup | Commit, configuration, run procedure, and fallback are recorded |
| Organizer announces the approaching reset | Stop practice submissions and put the algorithm behind an explicit restart gate; archive practice evidence | No unattended loop can resume trading automatically |
| Reset/start announcement | Verify account, orders, books, scoring baseline, and official start; launch only after reset is confirmed | Start checklist below is complete |
| `T0` to approximately +2 min | Observe startup health, initial fills, capacity, and request budget | Positions/orders reconcile; valid books; no unexplained rejections |
| Approximately +2 to +15 min | Run the frozen configuration and monitor; record interventions | Performance and exposure are visible; one owner retains control |
| Approximately +15 to +18 min | Review residual exposure and ending policy; reduce internal caps if the chosen policy requires it | Enough observed liquidity/time remains for any planned reduction |
| Approximately +18 min to official end | Execute the preselected ending policy; avoid new experiments | Remaining orders and inventory are understood |
| Official end | Follow stop instructions; cancel where permitted; preserve final state and result | Official score, terminal positions, logs, commit, and configuration recorded |

These checkpoints do not justify continuing to trade through an uncertain reset, a broken ledger, or an organizer stop instruction. Practice may also contain resets; use the same reconciliation discipline. [E1, E2]

## 3. One owner and the start gate

Before the final launch, the operator checks each item aloud while another teammate verifies the visible state:

- **Ownership:** only one process owns the team account connection. No scout or tutorial notebook has opened a second `Exchange`. Historical-loader research remains separate.
- **Release:** the running commit and configuration match the frozen version. No dependency installation or unreviewed patch is pending.
- **Reset:** organizers have confirmed it; current positions and PnL agree with the expected new baseline. Unexpected residual positions or orders are investigated rather than ignored.
- **Ledger:** practice records are archived; a new run identifier and reconciliation epoch are created. Old order identifiers and unresolved requests are not silently carried into the final.
- **Market:** enabled instruments are tradable; books, ticks, price bands, and timestamps are valid. Warm-up-dependent features have sufficient history or use an already tested fallback.
- **Risk:** ±100 lots per instrument is enforced together with outstanding and uncertain order exposure. Internal caps and request budgets are loaded.
- **Timing:** official `T0`, expected end, actual launch time, and operator stop control are visible.
- **Monitoring:** private fills, positions, outstanding orders, PnL availability, and failures are being recorded. A second reader does not consume the trading process's `poll_new_*` events.

Then the named operator authorizes the launch. A fresh zero position alone does not prove reset completion or permission to trade. If launch is delayed, use the remaining official time. [E1, E2]

## 4. Pause, cancel, flatten, disconnect

| Action | What changes | What remains at risk |
| --- | --- | --- |
| Pause new submissions | Strategy stops adding orders | Existing resting orders can still fill; inventory remains |
| Cancel outstanding orders | Requests removal of resting orders | Cancellation races and existing inventory remain until reconciled |
| Flatten inventory | Executes offsetting trades | Partial fills, costs, slippage, and residual inventory are possible |
| Disconnect | Ends the client connection; recovered behavior cancels resting orders | Inventory remains; preceding fills may still need reconciliation |

A “stop” button must have a documented meaning. Do not assume it performs all four actions. Canceling an order is not selling the position. Flattening is not guaranteed by sending one IOC. The notebook's extremely broad liquidation prices are educational examples, not the recommended emergency exit policy. [E2]

When account state is uncertain, pause new exposure, preserve reservations, and cancel known quotes where feasible. Reconcile before deliberate inventory reduction. Never send an unbounded exit merely because information is missing.

## 5. Fallback decisions

| Situation | Default response |
| --- | --- |
| One optional signal fails; account and books remain healthy | Disable it only if the resulting baseline was already tested; otherwise pause the affected strategy |
| One instrument has stale/invalid data | Stop opening exposure there; cancel its quotes if feasible; keep healthy instruments only if portfolio controls remain valid |
| Orders or positions cannot be reconciled | Stop new speculative exposure; retain pending risk; enter recovery |
| Rate-limit errors repeat | Reduce activity, check for duplicate processes, and preserve cancellation capacity |
| Several losing trades occur without a technical failure | Compare with the predeclared risk thresholds; do not rewrite the model on a tiny sample |
| A preset loss/exposure threshold is reached | Apply the documented pause/reduction policy; record the trigger and action |
| Restart is necessary | Reconcile existing positions/orders, retain official `T0`, and relaunch the frozen release only when healthy |

The historical diagnostic is an exploratory screen, not an execution backtest or proof of a profitable fallback. Neither a complex model nor a neutral quoting baseline earns promotion solely by existing. [E3; interpretation]

## 6. End the round deliberately

Resolve terminal inventory treatment before the final if possible. If flatness is required, begin bounded reduction early enough for observed depth and rate limits. If positions are marked without a flatness requirement, weigh reduced exposure against crossing costs. If treatment remains unresolved, keep inventory manageable and preserve exit capacity; do not invent compulsory liquidation at the last second.

At the official end, follow the organizer's instruction, record the score and terminal exposure, and confirm remaining order state. Preserve unavailable values as unavailable. A last-trade PnL figure and an executable liquidation estimate can differ. Do not replace the official result with a preferred custom mark. [E1, E2]

## 7. Minimal filled handover card

```text
Event: Optiver x Bona Fide Delft — 12 November 2026
Hard position cap: ±100 lots per instrument
Scored duration: 20 minutes from official start
Clock: CET (UTC+1); logs in UTC
Execution owner / backup: [names]
Frozen commit / configuration: [identifiers]
Official T0 / official end / actual launch: [timestamps]
Verified terminal-inventory rule: [rule + source, or unresolved]
Validated fallback / stop meaning: [exact procedure]
Internal caps / intervention thresholds: [recorded values]
Final score / terminal positions / incidents: [observed results]
```

**Sources:** E1 = supplied event slides; E2 = supplied API, notebook, and platform context; E3 = inspected diagnostic data. Earlier preparation documents E4/E5 provide background but do not override the event's reset/start instructions.
