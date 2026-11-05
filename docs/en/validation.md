# Validation record

[中文](../zh-CN/validation.md)

Validation performed on 5 November 2026 using the bundled Python 3.12 runtime.

| Check | Outcome |
|---|---|
| Complete analysis execution | Passed; four disclosed entity-year observations, two decompositions, 18 reverse-stress combinations, seven risk neighborhoods, and 12 credit parameter combinations processed. |
| Disclosure reconciliation | All four RWA component sums equal the disclosed totals. Computed capital ratios match published ratios within 0.001 percentage points. |
| Accounting identity | Symmetric capital and RWA contributions exhaust each ratio change within numerical tolerance. |
| Budget reconciliation | Six proposed allocations sum to RM26.5m. This validates arithmetic, not feasibility or optimality. |
| Independent unit tests | Four tests passed: ratio attribution with offsetting changes, fixed-RWA attribution, reverse-stress reference/shortfall boundary, and classification boundaries. |
| Deterministic reproduction | A second run to `local/reproduction/` reproduced the result JSON and all three SVG files byte-for-byte. |
| Documentation and assets | Relative file links resolve; SVG XML parses. All three figures were rendered to PNG and visually inspected for readable labels, consistent units, clipping and overlap. |
| Bilingual review | Research scope, reported ratios, entity distinctions, decomposition values, scenario bounds, proposed budget, corrections and execution status checked across English and Chinese documents. |
| Public-file boundary | The upload manifest excludes `local/`, caches, source PDF, identifiers, signatures and administrative appendices. |

The local renderer emitted font-cache permission notices but generated all three previews successfully; the previews were inspected. PNG previews are local quality-control files, not additional research observations. The analysis itself uses only the Python standard library; no rendering package is needed for reproduction.

This record does not establish independent validation of source scenario inputs, statistical calibration, accounting-standard compliance, regulatory compliance, internal bank conditions, deployment, realized transformation benefits, or peer review. Repository publication is verified separately at delivery rather than inferred from these local checks.
