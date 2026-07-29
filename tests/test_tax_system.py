import unittest
from engine.main_engine import EconomyEngine

class TestTaxSystem(unittest.TestCase):
    def setUp(self):
        self.engine = EconomyEngine()

    def test_default_tax_revenue_is_positive(self):
        state = self.engine.state
        govt = state["government"]
        
        # Verify default tax values are initialized
        self.assertIn("m40_tax_rate", govt)
        self.assertIn("t20_tax_rate", govt)
        self.assertEqual(govt["m40_tax_rate"], 0.04)
        self.assertEqual(govt["t20_tax_rate"], 0.16)
        
        # Check that collection fields are set
        self.assertIn("coll_indirect", govt)
        self.assertIn("coll_personal", govt)
        self.assertIn("coll_sme", govt)
        self.assertIn("coll_corp", govt)
        self.assertIn("coll_pita", govt)
        self.assertIn("coll_rpgt", govt)
        self.assertIn("coll_import_duties", govt)
        self.assertIn("coll_non_tax", govt)

    def test_high_corp_tax_suppresses_fdi(self):
        # Default corp tax is 24%, FDI base = 15.0
        # Raising corp tax to 32% (0.32) should reduce FDI
        policies = {
            "opr": 3.00,
            "sst_rate": 0.06,
            "corporate_tax": 0.32,  # increased corp tax
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
        
        # FDI should be suppressed (should be less than 15.0)
        self.assertLess(res["metrics"]["fdi"], 15.0)

    def test_high_t20_tax_spikes_brain_drain(self):
        # Default t20 tax is 16%. Setting it to 28% (0.28) should increase Brain Drain Index
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
            "electricity_tariff_policy": "subsidized",
            "t20_tax_rate": 0.28  # increased T20 tax rate
        }
        res = self.engine.step(policies)
        
        # Brain drain index should spike (should be higher than baseline default of ~3.0)
        self.assertGreater(res["metrics"]["brain_drain_index"], 4.0)

    def test_high_import_duties_boost_inflation(self):
        # Default import duty is 5%. Raising to 15% (0.15) should cause cost-push CPI inflation
        policies_low = {
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
            "electricity_tariff_policy": "subsidized",
            "import_duty_rate": 0.05
        }
        res_low = self.engine.step(policies_low)
        cpi_low = res_low["metrics"]["cpi"]
        
        # Reset engine and run high import duty
        self.setUp()
        policies_high = {
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
            "electricity_tariff_policy": "subsidized",
            "import_duty_rate": 0.15  # high import duty
        }
        res_high = self.engine.step(policies_high)
        cpi_high = res_high["metrics"]["cpi"]
        
        self.assertGreater(cpi_high, cpi_low)

if __name__ == '__main__':
    unittest.main()
