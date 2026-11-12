# 10 — Sources, Provenance, and Confidence

## 1. Evidence hierarchy

Use the latest organizer clarification first, then the supplied event slides and installed SDK, then the supplied notebook/API snapshot and actual data. Earlier preparation and other competitions inform hypotheses; they do not override this event's rules.

This handover was prepared on **12 November 2026**. It reconstructs the relevant preparation from retrievable conversations and saved artifacts. It is a structured synthesis, not a claim to possess a verbatim export of every earlier chat or all subsequent live developments.

| Label | Source | What it establishes | Limitation |
| --- | --- | --- | --- |
| **E1** | User-supplied event photographs `IMG_3362` through `IMG_3368` | Mission/universe, ±100 per instrument, fair-value teaching example, approximate 21:00 cutoff, reset, 20-minute final, team launch responsibility, judging dimensions, simple iteration advice | Not a full technical rulebook; later organizer clarifications may supersede them |
| **E2** | User-supplied event notebook (`Pasted text(1).txt`), API reference (`Pasted text (3).txt`), and common types (`Pasted text.txt`) | Documented methods, response semantics, data schemas, historical-loader access, PnL marking, tutorial examples | Supplied snapshots, not a fresh live installation audit; exact runtime configuration remains to be checked |
| **E3** | Uploaded `diagnostico_optibook.zip` and recovered `optibook_research.py` | Actual historical inputs, settings, signal-screen outputs, and diagnostic behavior | Short period; no executed strategy, passive-fill model, or final PnL |
| **E3a** | New offline reproduction and fixed five-second OBI sensitivity checks | Reproducibility, offset sensitivity, outlier sensitivity, and observed data-quality properties | Reanalysis of already seen data; not an independent holdout |
| **E4** | `Guia_Optiver_Delft_12_Nov_2026.pdf`, 15 pages, initial preparation dated 11 November | Early strategy branches, learning plan, 20-source reading map, initial public event facts | Superseded by actual slides where the initial guide had unknowns or examples |
| **E5** | `Dossier_Casos_Ganadores_Optiver_Delft.pdf`, 14 pages, deeper preparation dated 11–12 November | Historical competition cases, API caveats, Pullen lecture map, books and risk resources | Some historical links are unavailable; preserved inherited findings are explicitly labelled |
| **E6** | Recovered relevant conversation context | Environment path `/opt/venv/bin/python`, account-ownership notes, preparation sequence, purpose of tooling | Use supplied files/runtime evidence where available; no credentials are reproduced |

The mission, risk, fair-value, competition, and recommendation photographs were inspected directly during this handover. The two original PDFs were read as extracted text. The diagnostic ZIP was unpacked and its original numeric outputs reproduced offline. The earlier guide's 20-book map is inherited; its 7,011 pages were not reread in full.

## 2. Recovered artifacts and where their information now lives

| Earlier artifact | Current location or treatment |
| --- | --- |
| Initial preparation guide | Context, strategy, reading map, and source qualifications |
| Winners dossier | Chapter 07, with public source links and distinctions between awards, PnL claims, and inspectable code |
| API and common-type text attachments | Chapter 04's exact method/behavior map and implementation cautions |
| Event notebook | Historical-loader instructions, execution/PnL semantics, and explanation of why the extreme-price liquidation sample is not a default exit policy |
| Event photographs | Confirmed rules and a worked fair-value/depth calculation; original images are not redistributed |
| `optibook_market_scout.py` | Described in Chapters 01 and 04; not bundled because the historical research path suffices and the scout opens the live account connection |
| `optibook_research.py` | English prose adaptation in `research/optibook_research.py`, with analytical behavior preserved |
| Earlier research-kit ZIP | Superseded for this handover by the recovered script, actual output archive, and current reproduction instructions |
| Actual historical diagnostic ZIP | Original statistics in `evidence/`; raw numeric inputs available in the separate English research-data companion |
| Additional audit | `research/audit_research.py` and the curated `evidence/` CSVs |

## 3. External sources and access limitations

Chapter 07 contains its own ordinary-URL source register, with competition sources labelled `C1` onward and educational resources labelled `R1` onward. Its evidence table distinguishes organizer results, participant reports, public code, explanatory code, and unavailable implementations. Chapter 08 uses inherited book labels `B01` through `B20`; their page ranges refer to the original supplied PDF copies, not universal printed page numbers.

The specific event URLs were recorded in the earlier preparation:

- [Bona Fide event announcement](https://sbvbonafide.nl/elementor-1764/)
- [Event Optibook instance](https://2026-bona-fide.optibook.net/)
- [Event API reference](https://2026-bona-fide.optibook.net/docs/optibook)
- [Synchronous client](https://2026-bona-fide.optibook.net/docs/synchronous_client)
- [Common types](https://2026-bona-fide.optibook.net/docs/common_types)
- [Lectures](https://2026-bona-fide.optibook.net/lectures)
- [Introductory exercises](https://2026-bona-fide.optibook.net/intro-exercises)

Direct public retrieval of the event pages failed during this handover. Their contents are therefore grounded in the supplied snapshots and earlier saved preparation, rather than represented as freshly downloaded web text. This retrieval failure does not prove the event workspace is unavailable to participants.

External competition evidence has several deliberate boundaries: no verified previous Bona Fide winning implementation was found; Budlahkee is a participant repository, not the Ready Trader Go champion's code; TUM's first place is a reported PnL result rather than a verified overall judging award; and different teams' headline PnL claims at the same event are not silently reconciled. The historical videos' timestamps were carried forward from the prior dossier, not newly transcribed.

## 4. Reproducibility and source identity

The original uploaded diagnostic ZIP has SHA-256:

```text
5fcde81f472ce0079c358349241c52c38076127564d4fd8c24d9786f3c99cab4
```

The recovered original Python source has SHA-256:

```text
70d015ff9dfa29aaf84e4125bb882e30d56b29d3938f5da4a51b222f08006f2d
```

`evidence/source_checksums.json` records original input identities, the translated diagnostic, and verification details. The English diagnostic changes explanatory strings/comments, not the underlying numerical logic. Its eight-row summary, 384-row signal screen, and 1,000-row feature sample reproduce the original to the stated numerical tolerance. The new audit script provides the fixed OBI sensitivity checks.

The research-data companion uses the original raw numeric files and original metadata, with the report prose translated into English. Its archive bytes therefore differ from the original uploaded ZIP; the raw input checksums remain traceable. Extract it locally into `data/raw/diagnostic/` for reproduction. Raw files are deliberately outside the versioned documentation/evidence set.

## 5. What was not established

No live Exchange connection was opened for this handover, and no orders were submitted. It did not determine the final competition result, run a passive strategy, measure actual latency, confirm fees or message limits, establish a hidden instrument equivalence, obtain internal Optiver manuals, or discover the judges' private weights.

The package offers a concrete strategy-development and operating process. A later team run must supply the missing performance evidence and current runtime facts. Record those additions in the rules, experiment, decision, and final-run templates so the next teammate can distinguish the original context from subsequent results.
