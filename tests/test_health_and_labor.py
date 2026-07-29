import unittest
from engine.engine import EconomyEngine

class TestHealthAndLabor(unittest.TestCase):
    def setUp(self):
        self.engine = EconomyEngine()

    def test_default_health_values(self):
        state = self.engine.state
        self.assertEqual(state["metrics"]["family_health"], 80.0)
        self.assertEqual(state["metrics"]["sme_health"], 75.0)
        self.assertEqual(state["metrics"]["poverty_rate"], 5.6)
        self.assertEqual(state["external"]["foreign_labor_policy"], "balanced")

    def test_strict_labor_policy(self):
        # Strict labor policy prioritizes locals, raises B40 wage base, lowers foreign workers
        policies = {
            "opr": 3.00,
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "blanket",
            "development_expenditure": 22.0,
            "foreign_labor_policy": "strict"
        }
        next_state = self.engine.step(policies)
        
        # B40 wage base should increase (3500 * 1.10 = 3850)
        # under healthy employment (job_factor close to 1.0), salary should be > 3500
        b40_salary = next_state["households"]["b40"]["salary"]
        self.assertGreater(b40_salary, 3500.0)
        
        # Registered foreign workers should drop to 1.8 Million
        self.assertEqual(next_state["external"]["registered_foreign_workers"], 1.8)
        self.assertEqual(next_state["external"]["foreign_labor_policy"], "strict")

    def test_loose_labor_policy(self):
        # Loose labor policy allows cheap labor, suppresses B40 wages, raises foreign workers
        policies = {
            "opr": 3.00,
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "blanket",
            "development_expenditure": 22.0,
            "foreign_labor_policy": "loose"
        }
        next_state = self.engine.step(policies)
        
        # B40 wage base should decrease (3500 * 0.95 = 3325)
        # under healthy employment, salary should be < 3500
        b40_salary = next_state["households"]["b40"]["salary"]
        self.assertLess(b40_salary, 3500.0)
        
        # Registered foreign workers should rise to 2.5 Million
        self.assertEqual(next_state["external"]["registered_foreign_workers"], 2.5)

    def test_health_metrics_updating(self):
        policies = {
            "opr": 3.00,
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "blanket",
            "development_expenditure": 22.0,
            "foreign_labor_policy": "balanced"
        }
        next_state = self.engine.step(policies)
        
        # Verify that all health indicators are present as floats
        metrics = next_state["metrics"]
        self.assertIsInstance(metrics["family_health"], float)
        self.assertIsInstance(metrics["sme_health"], float)
        self.assertIsInstance(metrics["utilities_health"], float)
        self.assertIsInstance(metrics["banking_health"], float)
        self.assertIsInstance(metrics["govt_health"], float)
        self.assertIsInstance(metrics["poverty_rate"], float)
        self.assertIsInstance(metrics["fdi"], float)
        self.assertIsInstance(metrics["ddi"], float)

if __name__ == '__main__':
    unittest.main()
