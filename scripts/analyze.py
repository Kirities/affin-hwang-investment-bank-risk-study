"""Reproduce disclosure analysis and explicitly separate scenario calculations.

Python 3.10+; standard library only. Run from any working directory.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]


def read_csv(name):
    with (ROOT / 'data' / name).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def classify(score):
    return 'High' if score >= 10 else 'Medium' if score >= 5 else 'Low'


def ratio_decomposition(c0, c1, r0, r1):
    """Symmetric two-factor (Shapley) attribution, in percentage points."""
    capital = 50 * (c1 - c0) * (1 / r0 + 1 / r1)
    denominator = 50 * (c0 + c1) * (1 / r1 - 1 / r0)
    return {'capital_contribution_pp': capital, 'rwa_contribution_pp': denominator,
            'total_change_pp': 100 * (c1 / r1 - c0 / r0)}


def reverse_stress(capital, rwa, threshold, rwa_multiplier):
    """Loss capacity in input units; fixed denominator scenario, no tax offset."""
    return capital - threshold / 100 * rwa * rwa_multiplier


def svg_start(title, subtitle, width=1100, height=640):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
            f'<title>{escape(title)}</title><desc>{escape(subtitle)}</desc>',
            '<rect width="100%" height="100%" fill="#f7f9fc"/>',
            '<style>text{font-family:Arial,sans-serif;fill:#14283f} .title{font-size:26px;font-weight:bold} .sub{font-size:15px;fill:#526277} .label{font-size:16px} .small{font-size:14px}</style>',
            f'<text x="45" y="48" class="title">{escape(title)}</text>',
            f'<text x="45" y="78" class="sub">{escape(subtitle)}</text>']


def write_figures(out, disclosed, reverse, risks):
    assets = out / 'figures'
    assets.mkdir(parents=True, exist_ok=True)
    group = [x for x in disclosed if x['entity'] == 'AHIBB consolidated group']
    colors = ['#1f5a85', '#d18b37', '#6b9a94']
    keys = ['credit_rwa_rm_thousand', 'market_rwa_rm_thousand', 'operational_rwa_rm_thousand']
    parts = svg_start('RWA composition: aggregate decline masks credit growth',
                      'Public disclosure | AHIBB consolidated group | RM million | 2024-2025')
    for tick in range(0, 3501, 500):
        y = 505 - tick * .105
        parts += [f'<path d="M120 {y}H1010" stroke="#dce2eb"/>', f'<text x="60" y="{y+5}" class="small">{tick:,}</text>']
    for row, x in zip(group, [300, 680]):
        y = 505
        for key, color in zip(keys, colors):
            val = float(row[key]) / 1000
            h = val * .105
            y -= h
            parts += [f'<rect x="{x}" y="{y}" width="190" height="{h}" fill="{color}"/>',
                      f'<text x="{x+95}" y="{y+h/2+5}" text-anchor="middle" style="fill:white;font-size:16px">{val:,.1f}</text>']
        total = float(row['total_rwa_rm_thousand']) / 1000
        parts += [f'<text x="{x+95}" y="{y-15}" text-anchor="middle" class="label">Total {total:,.1f}</text>',
                  f'<text x="{x+95}" y="535" text-anchor="middle" class="label">{row["year"]}</text>']
    for x, name, color in zip([160, 450, 730], ['Credit RWA', 'Market RWA', 'Operational RWA'], colors):
        parts += [f'<rect x="{x}" y="572" width="18" height="18" fill="{color}"/>', f'<text x="{x+27}" y="587" class="label">{name}</text>']
    parts += ['<text x="45" y="620" class="small">Source: FY2025 Pillar 3, Table 2, PDF p.9. RWA is a regulatory measure, not realized loss.</text>', '</svg>']
    (assets / 'rwa-composition.svg').write_text('\n'.join(parts), encoding='utf-8')

    parts = svg_start('Reverse stress: loss capacity at a 20% CET1 reference',
                      'Conditional scenario | 2025 starting capital | no tax benefit | RM million')
    rows = [r for r in reverse if r['reference_cet1_pct'] == 20]
    for i, row in enumerate(rows):
        y = 125 + i * 65
        val = row['loss_capacity_rm_million']
        label = ('Group' if row['entity'].endswith('group') else 'Bank') + f' | RWA x{row["rwa_multiplier"]:.2f}'
        parts += [f'<text x="45" y="{y+22}" class="label">{label}</text>',
                  f'<rect x="270" y="{y}" width="{max(val,0)*1.3}" height="32" fill="{"#1f5a85" if i<3 else "#6b9a94"}"/>',
                  f'<text x="{280+max(val,0)*1.3}" y="{y+23}" class="label">{val:.1f}</text>']
    parts += ['<text x="45" y="575" class="small">20% is an analytical reference, not a claimed regulatory requirement or bank risk appetite.</text>',
              '<text x="45" y="603" class="small">Capacity = starting CET1 - reference ratio x stressed RWA. No event likelihood is estimated.</text>', '</svg>']
    (assets / 'reverse-stress.svg').write_text('\n'.join(parts), encoding='utf-8')

    parts = svg_start('Risk prioritization and sensitivity to ordinal inputs',
                      'Illustrative source assumptions | baseline score and local +/-1 input range')
    for i, row in enumerate(risks):
        y = 120 + i * 57
        x0 = 280 + row['local_min_score'] * 25
        x1 = 280 + row['local_max_score'] * 25
        xb = 280 + row['score'] * 25
        parts += [f'<text x="45" y="{y+6}" class="label">{row["risk"]}</text>',
                  f'<path d="M{x0} {y}H{x1}" stroke="#8ca3bb" stroke-width="8"/>',
                  f'<circle cx="{xb}" cy="{y}" r="8" fill="#1f5a85"/>',
                  f'<text x="940" y="{y+6}" class="label">{row["score"]} ({row["class"]})</text>']
    for tick in [1,5,10,15,20,25]:
        parts.append(f'<text x="{280+tick*25}" y="550" text-anchor="middle" class="small">{tick}</text>')
    parts += ['<text x="45" y="598" class="small">Ranges enumerate valid neighboring score pairs; they are not confidence intervals.</text>', '</svg>']
    (assets / 'risk-sensitivity.svg').write_text('\n'.join(parts), encoding='utf-8')


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    disclosed = read_csv('disclosed_capital.csv')
    decompositions = []
    reverse = []
    for entity in sorted({r['entity'] for r in disclosed}):
        a, b = sorted([r for r in disclosed if r['entity'] == entity], key=lambda x: x['year'])
        for row in (a, b):
            components = sum(float(row[k]) for k in ['credit_rwa_rm_thousand','market_rwa_rm_thousand','operational_rwa_rm_thousand'])
            assert components == float(row['total_rwa_rm_thousand']), 'RWA reconciliation failed'
            for amount, ratio in [('cet1_rm_thousand','reported_cet1_pct'), ('total_capital_rm_thousand','reported_total_capital_pct')]:
                assert abs(100*float(row[amount])/components-float(row[ratio])) < .001
        c0, c1 = float(a['cet1_rm_thousand']), float(b['cet1_rm_thousand'])
        r0, r1 = float(a['total_rwa_rm_thousand']), float(b['total_rwa_rm_thousand'])
        d = ratio_decomposition(c0,c1,r0,r1)
        assert abs(d['capital_contribution_pp'] + d['rwa_contribution_pp'] - d['total_change_pp']) < 1e-10
        d.update(entity=entity, total_rwa_change_pct=100*(r1/r0-1),
                 credit_rwa_change_pct=100*(float(b['credit_rwa_rm_thousand'])/float(a['credit_rwa_rm_thousand'])-1),
                 evidence_status='computed_from_public_disclosure')
        decompositions.append(d)
        for ref in [7, 20, 30]:
            for mult in [1, 1.25, 1.5]:
                reverse.append({'entity':entity,'reference_cet1_pct':ref,'rwa_multiplier':mult,
                                'loss_capacity_rm_million':reverse_stress(c1,r1,ref,mult)/1000,
                                'evidence_status':'conditional_scenario_not_forecast'})
    risks = []
    for row in read_csv('scenario_risks.csv'):
        p, i = int(row['probability_score']), int(row['impact_score'])
        assert 1 <= p <= 5 and 1 <= i <= 5
        neighbors = [pp*ii for pp in range(max(1,p-1),min(5,p+1)+1) for ii in range(max(1,i-1),min(5,i+1)+1)]
        risks.append({'risk':row['risk'],'score':p*i,'class':classify(p*i),
                      'local_min_score':min(neighbors),'local_max_score':max(neighbors),
                      'possible_classes':sorted({classify(x) for x in neighbors}),
                      'evidence_status':row['evidence_status']})
    credit = []
    for row in read_csv('scenario_credit.csv'):
        pd, lgd = float(row['pd_pct'])/100, float(row['lgd_pct'])/100
        credit.append({'counterparty':row['counterparty'],
                       'gross_ead_assumption_rm_million':float(row['gross_rm_million']),
                       'gross_basis_el_rm_million':float(row['gross_rm_million'])*pd*lgd,
                       'net_basis_el_rm_million':float(row['net_rm_million'])*pd*lgd})
    sensitivity = []
    for pd_scale in [.5,1,1.5,2]:
        for lgd_shift in [-10,0,10]:
            loss = sum(float(row['gross_rm_million'])*min(1,float(row['pd_pct'])/100*pd_scale)*max(0,min(1,(float(row['lgd_pct'])+lgd_shift)/100)) for row in read_csv('scenario_credit.csv'))
            sensitivity.append({'pd_multiplier':pd_scale,'lgd_shift_pp':lgd_shift,'el_rm_million':loss})
    budgets = read_csv('proposed_budget.csv')
    total_budget = sum(float(x['budget_rm_million']) for x in budgets)
    assert abs(total_budget - 26.5) < 1e-10
    summary = {'disclosure_decomposition':decompositions,'reverse_stress':reverse,
               'illustrative_risk_sensitivity':risks,'illustrative_credit':credit,
               'illustrative_gross_basis_el_rm_million':sum(x['gross_basis_el_rm_million'] for x in credit),
               'illustrative_net_basis_el_rm_million':sum(x['net_basis_el_rm_million'] for x in credit),
               'illustrative_credit_sensitivity':sensitivity,'proposed_budget_rm_million':total_budget,
               'technology_budget_share_pct':100*8.5/total_budget}
    (output/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    write_figures(output, disclosed, reverse, risks)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'results')
    run(parser.parse_args().output)
