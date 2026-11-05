# Validation record

[中文](../zh-CN/validation.md)

Validation performed on 5 November 2026 using the bundled Python 3.12 runtime.

| Check | Outcome |
|---|---|
| Complete analysis execution | Passed; four disclosed entity-year observations, two symmetric decompositions and four sequential paths, 18 reverse-stress combinations, 18 capital-frontier combinations, seven risk neighborhoods, and 12 credit parameter combinations processed. |
| Disclosure reconciliation | All four RWA component sums equal the disclosed totals. Computed capital ratios match published ratios within 0.001 percentage points. |
| Accounting identity | Symmetric capital and RWA contributions exhaust each ratio change within numerical tolerance. |
| Budget reconciliation | Six proposed allocations sum to RM26.5m. This validates arithmetic, not feasibility or optimality. |
| Independent unit tests | Eight tests passed in normal and optimized (`python -O`) execution: the four initial financial/classification checks plus sequential-path attribution, frontier inversion, credit scaling/bounds, and invalid numerical domains. Explicit data checks remain enabled under optimization. |
| Deterministic reproduction | A second run to `local/reproduction/` reproduced the JSON, four result CSVs and four SVG files byte-for-byte. Generated text uses explicit LF newlines. |
| Documentation and assets | Relative file links and local heading anchors resolve; SVG XML parses. Four figures were rendered and visually inspected for readable labels, units, clipping and overlap. Formula delimiters use GitHub-compatible dollar syntax. |
| Figure contrast | Plotted colors against the pale background exceed 5.23:1; white labels against filled bars exceed 5.57:1. Pairwise grayscale screening flags similar luminance, addressed with direct category/value labels, band boundaries, and distinct frontier line styles. This is a numerical screen and visual inspection, not accessibility certification. |
| Bilingual review | Research scope, reported ratios, entity distinctions, decomposition values, scenario bounds, proposed budget, corrections and execution status checked across English and Chinese documents. |
| Public-file boundary | The upload manifest excludes `local/`, caches, source PDF, identifiers, signatures and administrative appendices. |

The local renderer emitted font-cache permission notices but generated all four previews successfully; the previews were inspected. PNG previews and palette-screen JSON are local quality-control files, not additional research observations. The analysis itself uses only the Python standard library; no rendering package is needed for reproduction. The supplementary plotting tools were used to screen contrast, without importing publisher profiles or asserting journal compliance.

This record does not establish independent validation of source scenario inputs, statistical calibration, accounting-standard compliance, regulatory compliance, internal bank conditions, deployment, realized transformation benefits, or peer review. Repository publication is verified separately at delivery rather than inferred from these local checks.
