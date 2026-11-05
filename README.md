# Capital Resilience and Risk Transformation at Affin Hwang Investment Bank

[����](README.zh-CN.md)

A research report on the relationship between regulatory capital strength, changes in risk composition, and the design of operational transformation. The study combines verified FY2024�CFY2025 disclosures with a separately identified scenario framework for risk prioritization and credit sensitivity.

**Central finding:** the improvement in the consolidated CET1 ratio is predominantly associated with a smaller RWA denominator. Credit RWA increased even as total RWA declined. Capital adequacy therefore supports a narrower conclusion than a claim of comprehensive risk reduction.

![RWA composition](results/figures/rwa-composition.svg)

## Findings and contribution

| Analysis | Result | Evidence status |
|---|---|---|
| Consolidated CET1 ratio | 35.273% in 2024 to 37.573% in 2025 | Public disclosure |
| Symmetric ratio decomposition | +0.108 percentage points from capital and +2.193 from RWA | Computed from disclosed amounts |
| Consolidated risk composition | Total RWA ?5.84%; credit RWA +13.10% | Computed from public disclosure |
| Standalone comparison | CET1 improvement +0.872 percentage points; total RWA ?1.96% | Computed from disclosed amounts |
| Reverse stress at a 20% analytical reference | Consolidated loss capacity falls from RM506.6m to RM218.3m when RWA rises by 50% | Conditional scenario, not a forecast |
| Credit sensitivity | RM9.025m gross-basis expected loss; RM8.017m net-basis sensitivity | Illustrative source inputs, not a bank provision |

The contribution is an auditable connection between evidence scope, financial identities, sensitivity analysis, and decision design. It is a single-institution analytical study; it does not estimate causal effects or bank-specific event probabilities.

## Read the study

- [Research report and methods](docs/en/report.md): business model, entity comparison, capital decomposition, reverse stress, ordinal risk sensitivity, and implementation design.
- [Evidence audit and material corrections](docs/en/evidence-audit.md): sources, rejected interpretations, and unresolved claims.
- [References and attribution](docs/en/references.md): verified external sources and source authorship.
- [Data dictionary](data/README.md) and [machine-readable results](results/summary.json).

## Reproduce

Use Python 3.10 or later. There are **no third-party runtime dependencies**, and the analysis runs offline from the included CSV files.

```bash
python scripts/analyze.py
python -m unittest discover -s tests -v
```

The first command regenerates `results/summary.json` and three SVG figures. To preserve committed outputs while verifying a new run:

```bash
python scripts/analyze.py --output local/reproduction
```

Checks reconcile RWA components, compare calculated and published ratios, verify the ratio decomposition identity, and reconcile the proposed RM26.5m budget. Independent tests cover decomposition identities, reverse-stress boundaries, and classification thresholds. See [validation](docs/en/validation.md) for actual execution status.

## Evidence and research status

Public disclosure observations, arithmetic results, illustrative assumptions, and proposed actions are labeled separately throughout. The risk matrix and credit scenarios do not constitute measured internal bank data. The proposed budget is not approved expenditure, and transformation benefits have not been measured. No investment recommendation, regulatory certification, or operational deployment is claimed.

The source report is retained locally with its fingerprint. The public repository omits student identifiers, signatures, similarity-check material, grading forms, and duplicate third-party financial-report screenshots. Legitimate source authorship is preserved in [attribution](docs/en/references.md#source-report-and-authorship). No open license is asserted without establishing the rights of all relevant contributors and third-party owners.
