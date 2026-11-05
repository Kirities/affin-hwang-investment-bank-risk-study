"""Independent boundary and financial-identity checks."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from analyze import classify, ratio_decomposition, reverse_stress


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


if __name__ == '__main__':
    unittest.main()
