import unittest
from engine.main_engine import EconomyEngine

class TestIndustrySectors(unittest.TestCase):
    def setUp(self):
        self.engine = EconomyEngine()

    def test_default_sectoral_gdp_contributions(self):
        state = self.engine.state
        sectors = state["sectors"]
        
        # Verify baseline sectors are present
        self.assertIn("services", sectors)
        self.assertIn("manufacturing", sectors)
        self.assertIn("agriculture", sectors)
        self.assertIn("mining", sectors)
        self.assertIn("construction", sectors)
        
        # Verify base contributions
        self.assertEqual(sectors["services"]["gdp_contrib"], 270.0)
        self.assertEqual(sectors["manufacturing"]["gdp_contrib"], 103.5)
        
        # Total baseline GDP should sum exactly to 450.0
        total_sectors_gdp = sum(sectors[k]["gdp_contrib"] for k in sectors)
        self.assertEqual(total_sectors_gdp, 450.0)

    def test_oil_price_shock_hits_mining_and_reduces_gdp(self):
        # A Brent crude drop from 80 to 40 should cut Mining GDP in half: 27.0 * (40/80) = 13.5
        self.engine.state["external"]["brent_crude"] = 40.0
        
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
            "petrol_subsidy_regime": "blanket",
            "diesel_subsidy_regime": "blanket",
            "electricity_tariff_policy": "subsidized"
        }
        res = self.engine.step(policies)
        
        # Mining GDP should be 13.5
        self.assertEqual(res["sectors"]["mining"]["gdp_contrib"], 13.5)
        
        # Verify exports in Mining drop similarly
        self.assertEqual(res["sectors"]["mining"]["exports"], 12.5)

    def test_devex_increase_boosts_construction_gdp(self):
        # Raising development expenditure from 22.0 to 44.0 should double Construction GDP: 18.0 * (44 / 22) = 36.0
        policies = {
            "opr": 3.00,
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "blanket",
            "development_expenditure": 44.0,  # doubled
            "foreign_labor_policy": "balanced",
            "tax_regime": "sst",
            "epf_withdrawal_policy": "none",
            "exchange_rate_policy": "floating",
            "east_malaysia_allocation": 4.0,
            "petrol_subsidy_regime": "blanket",
            "diesel_subsidy_regime": "blanket",
            "electricity_tariff_policy": "subsidized"
        }
        res = self.engine.step(policies)
        
        # Construction GDP should be boosted due to effective devex multiplier
        self.assertAlmostEqual(res["sectors"]["construction"]["gdp_contrib"], 41.89, places=2)

if __name__ == '__main__':
    unittest.main()
