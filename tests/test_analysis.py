"""Independent boundary and financial-identity checks."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from analyze import classify, ratio_decomposition, reverse_stress, capital_frontier, expected_loss


class FinancialIdentities(unittest.TestCase):
    def test_ratio_attribution_exhausts_change(self):
        result = ratio_decomposition(100, 110, 500, 550)
        self.assertAlmostEqual(result['total_change_pp'], 0)
        self.assertGreater(result['capital_contribution_pp'], 0)
        self.assertAlmostEqual(result['capital_contribution_pp'], -result['rwa_contribution_pp'])

    def test_no_rwa_change(self):
        result = ratio_decomposition(100, 120, 500, 500)
        self.assertAlmostEqual(result['capital_contribution_pp'], 4)
        self.assertEqual(result['rwa_contribution_pp'], 0)

    def test_reverse_stress_reaches_reference(self):
        loss = reverse_stress(100, 400, 20, 1.1)
        self.assertAlmostEqual((100-loss)/(400*1.1), .2)
        self.assertLess(reverse_stress(100,400,30,1), 0)

    def test_class_boundaries(self):
        self.assertEqual([classify(x) for x in [1,4,5,9,10,25]],
                         ['Low','Low','Medium','Medium','High','High'])

    def test_sequential_paths_and_symmetric_mean(self):
        result = ratio_decomposition(100,120,500,400)
        capital_first, rwa_first = result['sequential_paths']
        self.assertAlmostEqual(capital_first['capital_contribution_pp'],4)
        self.assertAlmostEqual(capital_first['rwa_contribution_pp'],6)
        self.assertAlmostEqual(rwa_first['capital_contribution_pp'],5)
        self.assertAlmostEqual(rwa_first['rwa_contribution_pp'],5)
        self.assertAlmostEqual(result['capital_contribution_pp'],4.5)
        self.assertAlmostEqual(result['rwa_contribution_pp'],5.5)

    def test_frontier_is_inverse_of_loss_capacity(self):
        self.assertAlmostEqual(capital_frontier(100,400,20,20),1)
        for loss in [0,20,100,120]:
            multiplier = capital_frontier(100,400,20,loss)
            if multiplier > 0:
                self.assertAlmostEqual(reverse_stress(100,400,20,multiplier),loss)
        self.assertEqual(capital_frontier(100,400,20,100),0)
        self.assertLess(capital_frontier(100,400,20,120),0)

    def test_expected_loss_scale_and_parameter_bounds(self):
        rows = [{'gross_rm_million':100,'pd_pct':2,'lgd_pct':40}]
        self.assertAlmostEqual(expected_loss(rows),.8)
        self.assertAlmostEqual(expected_loss(rows,pd_scale=2,lgd_shift_pp=10),2)
        self.assertAlmostEqual(expected_loss(rows,pd_scale=100,lgd_shift_pp=100),100)
        self.assertEqual(expected_loss(rows,lgd_shift_pp=-100),0)

    def test_invalid_domains_fail_explicitly(self):
        invalid_calls = [lambda: ratio_decomposition(100,120,0,500),
                         lambda: ratio_decomposition(float('nan'),120,500,500),
                         lambda: reverse_stress(100,400,0,1),
                         lambda: reverse_stress(100,400,20,float('inf')),
                         lambda: capital_frontier(100,400,20,-1),
                         lambda: classify(0),
                         lambda: expected_loss([{'gross_rm_million':100,'pd_pct':101,'lgd_pct':40}])]
        for call in invalid_calls:
            with self.assertRaises(ValueError):
                call()


if __name__ == '__main__':
    unittest.main()
