# Evidence files

All numerical evidence is from the recovered 12 November 2026 diagnostic or explicitly identified additional offline checks. Read Chapter 03 before choosing a strategy from a row.

| File | Source and meaning |
| --- | --- |
| `market_summary.csv` | Unchanged original instrument summary: snapshots, trades, grid coverage, spreads, and displayed depths |
| `signal_screen.csv` | Unchanged 384-row original screen: six fixed rules, eight instruments, four horizons, two phases |
| `analysis_metadata.json` | Unchanged original interval, settings, schemas, and quality record; zero fees were assumed, not verified |
| `diagnostic_report_en.md` | English prose version of the original diagnostic report |
| `signal_comparison.csv` | Original train/validation rows joined into 192 instrument/rule/horizon comparisons |
| `obi_5s_blocks.csv` | Additional fixed five-minute chronological-block sensitivity; last block can be shorter |
| `obi_5s_sampling_offsets.csv` | Additional seven-offset check for one fixed OBI rule/horizon; observations are dependent |
| `obi_5s_outlier_sensitivity.csv` | Additional comparison of average/median/extremes and removal of the single largest outcome for diagnosis |
| `audit_metadata.json` | Verified offline audit settings, reproduced rows, and source-data quality |
| `source_checksums.json` | Source identities and translation/reproduction verification |
| `verification_environment.json` | Actual software versions used for offline verification |
| `validation_summary.json` | Package-level checks and the verified offline audit outcome |

`mean_crossing_edge` is in price units per hypothetical lot. It uses a future bid or ask, an assumed one-second entry delay, and the specified fee. It is not total portfolio profit. `mean_signed_mid_move` begins at the decision timestamp and is a different statistic.

`EXPLORATORY_ONLY` is a label for a minimum observation count; it is not statistical significance. `TOO_FEW_OBSERVATIONS` identifies even thinner evidence. A validation result selected after screening many rows requires another independent evaluation interval.

The research-data companion provides raw files for reproduction. The main repository contains concise derived evidence, so teammates can review conclusions without loading the raw books.
