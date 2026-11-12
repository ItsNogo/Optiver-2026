# Project instructions for permitted coding assistants

## Context

This repository documents the Optiver x Bona Fide Delft hackathon on 12 November 2026. Read `README.md`, `docs/01_context_and_rules.md`, and the chapter relevant to the assigned task. The task is a simulated exchange competition; do not assume any real brokerage integration.

## Authoritative facts

- Instruments: AMD, AVGO, CRWV, MU, NBIS, NVDA, SNDK, VRT.
- Hard position limit: ±100 lots per instrument, superseding generic ±300 examples.
- Practice until approximately 21:00 local; positions and PnL reset; final lasts 20 minutes. Team must start its algorithm after reset.
- Official start time controls the deadline. A process restart does not restart the competition clock.
- Judging considers PnL, approach, risk, and novelty; numeric weights are unknown.
- No exact equivalence, option structure, or news mechanism has been established for this universe.
- Recovered historical research does not establish a robust profitable aggressive signal. Read the actual audit before claiming alpha.

## Working rules

1. Distinguish confirmed rules, observed data, proposed changes, and unresolved questions. New organizer instructions supersede older preparation.
2. Do not invent Optibook methods, fee schedules, tick sizes, rate limits, fill probabilities, source results, or performance numbers.
3. Keep one live order owner. Research uses offline files or the historical loader. Do not open `Exchange()` for an analysis task or run the old market scout alongside the trader.
4. Do not connect, submit, cancel, amend, or liquidate from this documentation/research task. A separate explicit execution task and the team's operating procedure are required for live account actions.
5. Count filled positions, outstanding residuals, unknown inserts, and cancel-pending risk. Potential sells do not offset potential buys for hard-limit admission.
6. An accepted order is not a fill. IOC can fill partially. Disconnect cancels resting orders but does not flatten positions.
7. One collector owns each consuming `poll_new_*` stream; distribute normalized events internally.
8. Use causal data and chronological validation. Never report midpoint prediction, spread capture, turnover, or last-trade marks as realized executable profit.
9. Keep experiments small, isolated, and reproducible. Record commit/config and a rejection condition. Avoid broad rewrites close to the final.
10. Preserve practice records and start a new reconciliation epoch after reset. Keep the official start and bot-launch timestamps separate.
11. Do not publish account credentials, configuration secrets, raw participant records, original books, or event photographs. Preserve source attribution and repository licenses.
12. Write all team-facing material in English. Explain equations, units, assumptions, and failure behavior.

## Useful entry points

- Strategy: `docs/02_strategy_playbook.md`
- Data and existing diagnostic: `docs/03_data_and_research_audit.md`, `research/README.md`
- API/risk state: `docs/04_execution_and_risk.md`
- Final operations: `docs/06_final_round_checklist.md`
- Evidence templates: `templates/`

Only use AI assistance if the event permits it. This file defines project behavior; it does not override the organizer's policy.
