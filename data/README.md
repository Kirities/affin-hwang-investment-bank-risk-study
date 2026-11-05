# Data dictionary and provenance

[中文](README.zh-CN.md)

All CSV files are UTF-8 with a header. No customer, employee, account-level, or confidential bank data are supplied. Each observation carries an evidence status and source locator. `SOURCE-REPORT` refers to the locally retained 38-page group report; its pages are one-based PDF pages. `P3-2025` refers to the public disclosure linked in [references](../docs/en/references.md); PDF page 9 is printed page 8.

| File | Meaning | Units and limits |
|---|---|---|
| `disclosed_capital.csv` | Four entity-year observations, manually transcribed and checked against Table 2 of P3-2025 | Monetary amounts in RM thousand; ratios in percent. The AHIBB consolidated group is distinct from both the standalone bank and the wider AFFIN banking group. |
| `scenario_risks.csv` | Seven score pairs reconstructible from Appendix B | Integers from 1 to 5; ordinal assumptions, not measured event probabilities. Reputational risk is excluded because its factor pair is not explicitly supplied in Appendix B. |
| `scenario_credit.csv` | Four illustrative counterparty classes from Table A3 | Exposure and the original mislabeled column in RM million; PD and LGD in percent. Values are not verified institution-level exposures or calibrated parameters. |
| `proposed_budget.csv` | Six proposed allocations from Appendix C | RM million; neither approved expenditure nor implemented controls. |

The model uses gross scenario exposure as an explicit EAD assumption and also reports a net-exposure sensitivity. Neither treatment establishes a valid accounting provision. No currency conversion, interpolation, imputation, or random simulation is performed. These are transcriptions of supplied illustrative inputs, not a newly simulated dataset. The scripts require no original PDF or internet access.

Ratios calculated from rounded disclosure amounts can differ slightly from the published ratios. The published ratios are preserved, and computed values are recorded separately. This dataset intentionally excludes unverified 2023 values and group-associated CIR/liquidity claims. Third-party disclosure rights remain with their owners; no general redistribution license is asserted.
