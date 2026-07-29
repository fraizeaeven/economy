import unittest
from engine.main_engine import EconomyEngine

class TestDOSMAndForecasting(unittest.TestCase):
    def setUp(self):
        self.engine = EconomyEngine()

    def test_gini_inequality_index_response(self):
        # Default starting Gini should calibrate around 0.390 (DOSM standard)
        state = self.engine.state
        self.assertAlmostEqual(state["metrics"]["gini"], 0.390, places=2)
        
        # Test that giving more STR aid to B40 reduces inequality (reduces Gini)
        # Baseline B40 STR is 150.
        policies_targeted = {
            "opr": 3.00,
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "targeted",  # raises B40 STR aid to 280, raising B40 income
            "development_expenditure": 22.0,
            "foreign_labor_policy": "balanced",
            "tax_regime": "sst",
            "epf_withdrawal_policy": "none",
            "exchange_rate_policy": "floating",
            "east_malaysia_allocation": 4.0,
            "petrol_subsidy_regime": "blanket",
            "diesel_subsidy_regime": "blanket",
            "electricity_tariff_policy": "subsidized"
        }
        res = self.engine.step(policies_targeted)
        gini_after_str = res["metrics"]["gini"]
        
        # Increasing B40 income share should lower Gini inequality
        self.assertLess(gini_after_str, 0.390)

    def test_linear_regression_forecast_solver(self):
        # We simulate 3 quarters of data manually to create a clear trend line
        # GDP: Q1=450, Q2=460, Q3=470 (m = 10, c = 440)
        self.engine.history = [
            {"quarter": 1, "metrics": {"gdp": 450.0, "debt_to_gdp": 60.0, "public_satisfaction": 50.0, "cpi": 2.0}},
            {"quarter": 2, "metrics": {"gdp": 460.0, "debt_to_gdp": 59.0, "public_satisfaction": 52.0, "cpi": 2.2}}
        ]
        self.engine.state["quarter"] = 3
        self.engine.state["metrics"] = {"gdp": 470.0, "debt_to_gdp": 58.0, "public_satisfaction": 54.0, "cpi": 2.4}
        
        forecasts = self.engine.forecast_metrics()
        
        # Equation for GDP: y = 10x + 440
        self.assertEqual(forecasts["gdp"]["m"], 10.0)
        self.assertEqual(forecasts["gdp"]["c"], 440.0)
        
        # Forecast for Q4 should be 10 * 4 + 440 = 480
        self.assertEqual(forecasts["gdp"]["forecasts"][0], (4, 480.0))

if __name__ == '__main__':
    unittest.main()
