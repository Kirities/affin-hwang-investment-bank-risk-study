"""Reproduce disclosure analysis and explicitly separate scenario calculations.

Python 3.10+; standard library only. Run from any working directory.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    """Keep data checks active under python -O as well as normal execution."""
    if not condition:
        raise ValueError(message)


def finite_nonnegative(*values):
    return all(math.isfinite(x) and x >= 0 for x in values)


def read_csv(name):
    with (ROOT / 'data' / name).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def classify(score):
    require(isinstance(score, int) and 1 <= score <= 25, 'Risk score must be an integer from 1 to 25')
    return 'High' if score >= 10 else 'Medium' if score >= 5 else 'Low'


def ratio_decomposition(c0, c1, r0, r1):
    """Symmetric two-factor (Shapley) attribution, in percentage points."""
    require(finite_nonnegative(c0, c1, r0, r1) and min(r0, r1) > 0,
            'Capital must be finite/nonnegative and RWA finite/positive')
    capital = 50 * (c1 - c0) * (1 / r0 + 1 / r1)
    denominator = 50 * (c0 + c1) * (1 / r1 - 1 / r0)
    paths = [
        {'path': 'capital_then_rwa', 'capital_contribution_pp': 100*(c1-c0)/r0,
         'rwa_contribution_pp': 100*c1*(1/r1-1/r0)},
        {'path': 'rwa_then_capital', 'capital_contribution_pp': 100*(c1-c0)/r1,
         'rwa_contribution_pp': 100*c0*(1/r1-1/r0)},
    ]
    return {'capital_contribution_pp': capital, 'rwa_contribution_pp': denominator,
            'sequential_paths': paths,
            'total_change_pp': 100 * (c1 / r1 - c0 / r0)}


def reverse_stress(capital, rwa, threshold, rwa_multiplier):
    """Loss capacity in input units; fixed denominator scenario, no tax offset."""
    validate_stress(capital, rwa, threshold)
    require(math.isfinite(rwa_multiplier) and rwa_multiplier > 0, 'RWA multiplier must be finite/positive')
    return capital - threshold / 100 * rwa * rwa_multiplier


def validate_stress(capital, rwa, threshold):
    require(finite_nonnegative(capital, rwa, threshold) and rwa > 0 and 0 < threshold <= 100,
            'Stress inputs require finite nonnegative capital, positive RWA, and reference in (0,100]')


def capital_frontier(capital, rwa, threshold, loss):
    """Largest RWA multiplier at the reference; negative means no positive feasible RWA."""
    validate_stress(capital, rwa, threshold)
    require(finite_nonnegative(loss), 'Loss must be finite/nonnegative')
    return (capital-loss)/(threshold/100*rwa)


def expected_loss(rows, exposure_key='gross_rm_million', pd_scale=1, lgd_shift_pp=0):
    require(finite_nonnegative(pd_scale) and math.isfinite(lgd_shift_pp), 'Invalid sensitivity parameters')
    loss = 0
    for row in rows:
        ead, pd, lgd = float(row[exposure_key]), float(row['pd_pct']), float(row['lgd_pct'])
        require(finite_nonnegative(ead, pd, lgd) and pd <= 100 and lgd <= 100, 'Invalid credit input')
        loss += ead * min(1, pd/100*pd_scale) * max(0, min(1, (lgd+lgd_shift_pp)/100))
    return loss


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def svg_start(title, subtitle, width=1100, height=640):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">',
            f'<title id="title">{escape(title)}</title><desc id="description">{escape(subtitle)}</desc>',
            '<rect width="100%" height="100%" fill="#f7f9fc"/>',
            '<style>text{font-family:Arial,sans-serif;fill:#14283f} .title{font-size:26px;font-weight:bold} .sub{font-size:15px;fill:#526277} .label{font-size:16px} .small{font-size:14px}</style>',
            f'<text x="45" y="48" class="title">{escape(title)}</text>',
            f'<text x="45" y="78" class="sub">{escape(subtitle)}</text>']


def write_figures(out, disclosed, reverse, risks):
    assets = out / 'figures'
    assets.mkdir(parents=True, exist_ok=True)
    group = sorted([x for x in disclosed if x['entity'] == 'AHIBB consolidated group'], key=lambda row: row['year'])
    colors = ['#1f5a85', '#945b13', '#386e68']
    keys = ['credit_rwa_rm_thousand', 'market_rwa_rm_thousand', 'operational_rwa_rm_thousand']
    parts = svg_start('RWA composition: aggregate decline masks credit growth',
                      'Public disclosure | AHIBB consolidated group | RM million | 2024-2025')
    for tick in range(0, 3501, 500):
        y = 505 - tick * .105
        parts += [f'<path d="M120 {y}H1010" stroke="#dce2eb"/>', f'<text x="60" y="{y+5}" class="small">{tick:,}</text>']
    for row, x in zip(group, [300, 680]):
        y = 505
        for key, color, category in zip(keys, colors, ['Credit', 'Market', 'Operational']):
            val = float(row[key]) / 1000
            h = val * .105
            y -= h
            parts += [f'<rect x="{x}" y="{y}" width="190" height="{h}" fill="{color}" stroke="#f7f9fc" stroke-width="1.5"/>',
                      f'<text x="{x+95}" y="{y+h/2+5}" text-anchor="middle" style="fill:white;font-size:16px">{category} {val:,.1f}</text>']
        total = float(row['total_rwa_rm_thousand']) / 1000
        parts += [f'<text x="{x+95}" y="{y-15}" text-anchor="middle" class="label">Total {total:,.1f}</text>',
                  f'<text x="{x+95}" y="535" text-anchor="middle" class="label">{row["year"]}</text>']
    for x, name, color in zip([160, 450, 730], ['Credit RWA', 'Market RWA', 'Operational RWA'], colors):
        parts += [f'<rect x="{x}" y="572" width="18" height="18" fill="{color}"/>', f'<text x="{x+27}" y="587" class="label">{name}</text>']
    parts += ['<text x="45" y="620" class="small">Source: FY2025 Pillar 3, Table 2, PDF p.9. RWA is a regulatory measure, not realized loss.</text>', '</svg>']
    (assets / 'rwa-composition.svg').write_text('\n'.join(parts), encoding='utf-8', newline='\n')

    parts = svg_start('Reverse stress: loss capacity at a 20% CET1 reference',
                      'Conditional scenario | 2025 starting capital | no tax benefit | RM million')
    rows = [r for r in reverse if r['reference_cet1_pct'] == 20]
    for tick in range(0, 501, 100):
        x = 270 + tick * 1.3
        parts += [f'<path d="M{x} 110V510" stroke="#dce2eb"/>',
                  f'<text x="{x}" y="535" text-anchor="middle" class="small">{tick}</text>']
    for i, row in enumerate(rows):
        y = 125 + i * 65
        val = row['loss_capacity_rm_million']
        label = ('Group' if row['entity'].endswith('group') else 'Bank') + f' | RWA x{row["rwa_multiplier"]:.2f}'
        parts += [f'<text x="45" y="{y+22}" class="label">{label}</text>',
                  f'<rect x="270" y="{y}" width="{max(val,0)*1.3}" height="32" fill="{"#1f5a85" if i<3 else "#386e68"}"/>',
                  f'<text x="{280+max(val,0)*1.3}" y="{y+23}" class="label">{val:.1f}</text>']
    parts += ['<text x="45" y="575" class="small">20% is an analytical reference, not a claimed regulatory requirement or bank risk appetite.</text>',
              '<text x="45" y="603" class="small">Capacity = starting CET1 - reference ratio x stressed RWA. No event likelihood is estimated.</text>', '</svg>']
    (assets / 'reverse-stress.svg').write_text('\n'.join(parts), encoding='utf-8', newline='\n')

    parts = svg_start('Risk prioritization and sensitivity to ordinal inputs',
                      'Illustrative source assumptions | baseline score and local +/-1 input range')
    for i, row in enumerate(risks):
        y = 120 + i * 57
        x0 = 280 + row['local_min_score'] * 25
        x1 = 280 + row['local_max_score'] * 25
        xb = 280 + row['score'] * 25
        parts += [f'<text x="45" y="{y+6}" class="label">{row["risk"]}</text>',
                  f'<path d="M{x0} {y}H{x1}" stroke="#526b85" stroke-width="8"/>',
                  f'<circle cx="{xb}" cy="{y}" r="8" fill="#1f5a85"/>',
                  f'<text x="940" y="{y+6}" class="label">{row["score"]} ({row["class"]})</text>']
    for tick in [1,5,10,15,20,25]:
        parts.append(f'<text x="{280+tick*25}" y="550" text-anchor="middle" class="small">{tick}</text>')
    parts += ['<text x="45" y="598" class="small">Ranges enumerate valid neighboring score pairs; they are not confidence intervals.</text>', '</svg>']
    (assets / 'risk-sensitivity.svg').write_text('\n'.join(parts), encoding='utf-8', newline='\n')

    parts = svg_start('Capital frontier: joint loss and RWA expansion',
                      'Conditional boundary | AHIBB consolidated group, 2025 | no tax benefit')
    c, r = float(group[1]['cet1_rm_thousand'])/1000, float(group[1]['total_rwa_rm_thousand'])/1000
    # Common signed y-axis retains shortfalls instead of clipping them to zero.
    px = lambda m: 150 + (m-1)*1500
    py = lambda loss: 115 + (550-loss)*.5
    for tick in [-200,0,200,400]:
        y = py(tick)
        parts += [f'<path d="M150 {y}H900" stroke="{"#526277" if tick==0 else "#dce2eb"}"/>',
                  f'<text x="125" y="{y+5}" text-anchor="end" class="small">{tick}</text>']
    for m in [1,1.1,1.2,1.3,1.4,1.5]:
        parts += [f'<text x="{px(m)}" y="540" text-anchor="middle" class="small">{m:.1f}</text>']
    parts += ['<text x="150" y="105" class="label">Loss capacity / shortfall (RM million)</text>',
              '<text x="525" y="570" text-anchor="middle" class="label">RWA multiplier relative to year-end 2025</text>']
    for ref, color, dash in [(20,'#1f5a85',''),(30,'#945b13','stroke-dasharray="10 6"')]:
        points = ' '.join(f'{px(m)},{py(reverse_stress(c,r,ref,m))}' for m in [1,1.25,1.5])
        parts += [f'<polyline points="{points}" stroke="{color}" stroke-width="3" fill="none" {dash}/>',
                  f'<text x="920" y="{py(reverse_stress(c,r,ref,1.5))+5}" class="label">{ref}% reference</text>']
    mstar = capital_frontier(c,r,30,0)
    parts += [f'<circle cx="{px(mstar)}" cy="{py(0)}" r="6" fill="#945b13"/>',
              f'<text x="{px(mstar)+14}" y="{py(0)-15}" class="small">Zero-loss boundary: {mstar:.3f}x RWA</text>',
              '<text x="45" y="610" class="small">Lines are accounting boundaries, not forecasts. Values below zero indicate a reference-ratio shortfall.</text>', '</svg>']
    (assets/'capital-frontier.svg').write_text('\n'.join(parts), encoding='utf-8', newline='\n')


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    disclosed = read_csv('disclosed_capital.csv')
    decompositions = []
    reverse = []
    frontiers = []
    require(len(disclosed) == 4 and len({(r['entity'],r['year']) for r in disclosed}) == 4,
            'Expected four distinct disclosure entity-year observations')
    for entity in sorted({r['entity'] for r in disclosed}):
        a, b = sorted([r for r in disclosed if r['entity'] == entity], key=lambda x: x['year'])
        require([a['year'], b['year']] == ['2024','2025'], 'Unexpected disclosure years')
        for row in (a, b):
            components = sum(float(row[k]) for k in ['credit_rwa_rm_thousand','market_rwa_rm_thousand','operational_rwa_rm_thousand'])
            require(components == float(row['total_rwa_rm_thousand']), 'RWA reconciliation failed')
            for amount, ratio in [('cet1_rm_thousand','reported_cet1_pct'), ('total_capital_rm_thousand','reported_total_capital_pct')]:
                require(abs(100*float(row[amount])/components-float(row[ratio])) < .001, 'Capital ratio reconciliation failed')
        c0, c1 = float(a['cet1_rm_thousand']), float(b['cet1_rm_thousand'])
        r0, r1 = float(a['total_rwa_rm_thousand']), float(b['total_rwa_rm_thousand'])
        d = ratio_decomposition(c0,c1,r0,r1)
        require(abs(d['capital_contribution_pp'] + d['rwa_contribution_pp'] - d['total_change_pp']) < 1e-10,
                'Ratio decomposition identity failed')
        for path in d['sequential_paths']:
            require(abs(path['capital_contribution_pp']+path['rwa_contribution_pp']-d['total_change_pp']) < 1e-10,
                    'Sequential decomposition identity failed')
        d.update(entity=entity, total_rwa_change_pct=100*(r1/r0-1),
                 credit_rwa_change_pct=100*(float(b['credit_rwa_rm_thousand'])/float(a['credit_rwa_rm_thousand'])-1),
                 evidence_status='computed_from_public_disclosure')
        decompositions.append(d)
        for ref in [7, 20, 30]:
            for loss in [0,100,200]:
                frontiers.append({'entity':entity,'reference_cet1_pct':ref,'assumed_loss_rm_million':loss,
                                  'maximum_rwa_multiplier':capital_frontier(c1,r1,ref,loss*1000),
                                  'evidence_status':'conditional_scenario_not_forecast'})
            for mult in [1, 1.25, 1.5]:
                reverse.append({'entity':entity,'reference_cet1_pct':ref,'rwa_multiplier':mult,
                                'loss_capacity_rm_million':reverse_stress(c1,r1,ref,mult)/1000,
                                'evidence_status':'conditional_scenario_not_forecast'})
    risks = []
    for row in read_csv('scenario_risks.csv'):
        p, i = int(row['probability_score']), int(row['impact_score'])
        require(1 <= p <= 5 and 1 <= i <= 5, 'Ordinal grades must be in [1,5]')
        neighbors = [pp*ii for pp in range(max(1,p-1),min(5,p+1)+1) for ii in range(max(1,i-1),min(5,i+1)+1)]
        risks.append({'risk':row['risk'],'score':p*i,'class':classify(p*i),
                      'local_min_score':min(neighbors),'local_max_score':max(neighbors),
                      'possible_classes':sorted({classify(x) for x in neighbors}),
                      'evidence_status':row['evidence_status']})
    credit = []
    credit_rows = read_csv('scenario_credit.csv')
    for row in credit_rows:
        pd, lgd = float(row['pd_pct'])/100, float(row['lgd_pct'])/100
        credit.append({'counterparty':row['counterparty'],
                       'gross_ead_assumption_rm_million':float(row['gross_rm_million']),
                       'gross_basis_el_rm_million':float(row['gross_rm_million'])*pd*lgd,
                       'net_basis_el_rm_million':float(row['net_rm_million'])*pd*lgd})
    sensitivity = []
    for pd_scale in [.5,1,1.5,2]:
        for lgd_shift in [-10,0,10]:
            loss = expected_loss(credit_rows, pd_scale=pd_scale, lgd_shift_pp=lgd_shift)
            sensitivity.append({'pd_multiplier':pd_scale,'lgd_shift_pp':lgd_shift,'el_rm_million':loss,
                                'evidence_status':'illustrative_unvalidated_source_assumption'})
    budgets = read_csv('proposed_budget.csv')
    total_budget = sum(float(x['budget_rm_million']) for x in budgets)
    require(abs(total_budget - 26.5) < 1e-10, 'Proposed budget does not reconcile')
    summary = {'disclosure_decomposition':decompositions,'reverse_stress':reverse,'capital_frontier':frontiers,
               'illustrative_risk_sensitivity':risks,'illustrative_credit':credit,
               'illustrative_gross_basis_el_rm_million':sum(x['gross_basis_el_rm_million'] for x in credit),
               'illustrative_net_basis_el_rm_million':sum(x['net_basis_el_rm_million'] for x in credit),
               'illustrative_credit_sensitivity':sensitivity,'proposed_budget_rm_million':total_budget,
               'technology_budget_share_pct':100*8.5/total_budget}
    (output/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8', newline='\n')
    write_csv(output/'capital-frontier.csv',frontiers)
    write_csv(output/'reverse-stress.csv',reverse)
    write_csv(output/'credit-sensitivity.csv',sensitivity)
    write_csv(output/'decomposition-paths.csv',[
        dict(entity=d['entity'],**p,evidence_status=d['evidence_status'])
        for d in decompositions for p in d['sequential_paths']])
    write_figures(output, disclosed, reverse, risks)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'results')
    run(parser.parse_args().output)
