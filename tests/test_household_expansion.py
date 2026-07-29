import unittest
from engine.main_engine import EconomyEngine

class TestHouseholdExpansion(unittest.TestCase):
    def setUp(self):
        self.engine = EconomyEngine()

    def test_default_household_expansion_metrics(self):
        state = self.engine.state
        metrics = state["metrics"]
        govt = state["government"]
        
        self.assertEqual(metrics["ron95_price"], 2.05)
        self.assertEqual(metrics["diesel_price"], 2.15)
        self.assertEqual(govt["petrol_subsidy_regime"], "blanket")
        self.assertEqual(govt["diesel_subsidy_regime"], "blanket")
        self.assertEqual(govt["electricity_tariff_policy"], "subsidized")

    def test_petrol_rationalization_floats_price_and_spikes_cpi(self):
        # Rationalized petrol floats RON95 relative to Brent Crude (baseline Brent is 80.0)
        # Brent at 90.0 should increase RON95: 2.05 + 0.02 * (90 - 80) = 2.25
        self.engine.state["external"]["brent_crude"] = 90.0
        
        policies = {
            "opr": 3.00,
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "blanket",
            "development_expenditure": 22.0,
            "foreign_labor_policy": "balanced",
            "tax_regime": "sst",
            "epf_withdrawal_policy": "none",
            "exchange_rate_policy": "floating",
            "east_malaysia_allocation": 4.0,
            
            "petrol_subsidy_regime": "rationalized",
            "diesel_subsidy_regime": "blanket",
            "electricity_tariff_policy": "subsidized"
        }
        res = self.engine.step(policies)
        
        # RON95 price should float to 2.25
        self.assertEqual(res["metrics"]["ron95_price"], 2.25)
        
        # Inflation should be higher due to rationalization shock (+1.2%)
        self.assertGreater(res["metrics"]["cpi"], 2.0)

    def test_electricity_tariff_increases_commitments(self):
        policies_market = {
            "opr": 3.00,
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "blanket",
            "development_expenditure": 22.0,
            "foreign_labor_policy": "balanced",
            "tax_regime": "sst",
            "epf_withdrawal_policy": "none",
            "exchange_rate_policy": "floating",
            "east_malaysia_allocation": 4.0,
            
            "petrol_subsidy_regime": "blanket",
            "diesel_subsidy_regime": "blanket",
            "electricity_tariff_policy": "market_rate"  # increases B40 utilities to 1.25x and T20 to 1.5x
        }
        res = self.engine.step(policies_market)
        
        # B40 utilities cost: 150 * 1.25 = 187.50
        # T20 utilities cost: 1000 * 1.50 = 1500.00
        self.assertEqual(res["households"]["b40"]["commitments"]["utilities"], 187.50)
        self.assertEqual(res["households"]["t20"]["commitments"]["utilities"], 1500.00)

if __name__ == '__main__':
    unittest.main()
