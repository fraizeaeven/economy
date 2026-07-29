import unittest
from engine.main_engine import EconomyEngine

class TestAdvancedFeatures(unittest.TestCase):
    def setUp(self):
        self.engine = EconomyEngine()

    def test_default_advanced_state(self):
        state = self.engine.state
        self.assertEqual(state["metrics"]["brain_drain_index"], 3.0)
        self.assertEqual(state["metrics"]["east_malaysia_poverty"], 14.5)
        self.assertEqual(state["metrics"]["foreign_reserves"], 115.0)
        self.assertEqual(state["metrics"]["epf_pool"], 750.0)
        self.assertEqual(state["government"]["tax_regime"], "sst")
        self.assertEqual(state["government"]["epf_withdrawal_policy"], "none")
        self.assertEqual(state["government"]["exchange_rate_policy"], "floating")
        self.assertEqual(state["government"]["east_malaysia_allocation"], 4.0)

    def test_epf_withdrawal_injects_income_and_penalizes_ddi(self):
        # Base run with epf_withdrawal_policy: none
        policies_none = {
            "opr": 3.00,
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "blanket",
            "development_expenditure": 22.0,
            "foreign_labor_policy": "balanced",
            "tax_regime": "sst",
            "epf_withdrawal_policy": "none",
            "exchange_rate_policy": "floating",
            "east_malaysia_allocation": 4.0
        }
        res_none = self.engine.step(policies_none)
        pool_none = res_none["metrics"]["epf_pool"]
        ddi_none = res_none["metrics"]["ddi"]
        
        # New engine instance for unrestricted withdrawal comparison
        engine_withdrawal = EconomyEngine()
        policies_withdrawal = policies_none.copy()
        policies_withdrawal["epf_withdrawal_policy"] = "unrestricted"
        res_withdrawal = engine_withdrawal.step(policies_withdrawal)
        pool_withdrawn = res_withdrawal["metrics"]["epf_pool"]
        ddi_withdrawn = res_withdrawal["metrics"]["ddi"]
        
        # The withdrawn EPF pool must be significantly smaller than none
        self.assertLess(pool_withdrawn, pool_none)
        # DDI should be lower due to EPF reduction factor
        self.assertLess(ddi_withdrawn, ddi_none)

    def test_gst_regime_impacts(self):
        # Test GST implementation compared to SST
        # Base run with GST
        policies_gst = {
            "opr": 3.00,
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "blanket",
            "development_expenditure": 22.0,
            "foreign_labor_policy": "balanced",
            "tax_regime": "gst",
            "epf_withdrawal_policy": "none",
            "exchange_rate_policy": "floating",
            "east_malaysia_allocation": 4.0
        }
        res_gst = self.engine.step(policies_gst)
        tax_gst = res_gst["government"]["tax_revenue"]
        cpi_gst = res_gst["metrics"]["cpi"]
        
        # New engine for SST
        engine_sst = EconomyEngine()
        policies_sst = policies_gst.copy()
        policies_sst["tax_regime"] = "sst"
        res_sst = engine_sst.step(policies_sst)
        tax_sst = res_sst["government"]["tax_revenue"]
        cpi_sst = res_sst["metrics"]["cpi"]
        
        # GST tax collection should be higher than SST
        self.assertGreater(tax_gst, tax_sst)
        # CPI should have a +2.0 inflation shock under GST
        self.assertGreater(cpi_gst, cpi_sst)

    def test_currency_peg_and_reserves_drain(self):
        # Peg Ringgit to 3.80 when market rate forces want it weak
        # We simulate this by setting Fed rate high to trigger MYR weakness
        self.engine.state["external"]["fed_rate"] = 7.0
        policies_peg = {
            "opr": 2.00,  # low local OPR makes MYR weak
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "blanket",
            "development_expenditure": 22.0,
            "foreign_labor_policy": "balanced",
            "tax_regime": "sst",
            "epf_withdrawal_policy": "none",
            "exchange_rate_policy": "pegged_3.80",
            "east_malaysia_allocation": 4.0
        }
        res_peg = self.engine.step(policies_peg)
        
        # Exchange rate must be locked at 3.80
        self.assertEqual(res_peg["metrics"]["myr_usd"], 3.80)
        # Foreign Reserves should have drained
        self.assertLess(res_peg["metrics"]["foreign_reserves"], 115.0)

    def test_east_malaysia_poverty(self):
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
            "east_malaysia_allocation": 10.0  # high allocation
        }
        res = self.engine.step(policies)
        
        # East Malaysia poverty should have decreased from 14.5%
        self.assertLess(res["metrics"]["east_malaysia_poverty"], 14.5)

    def test_brain_drain(self):
        # High brain drain driven by weak exchange rate
        self.engine.state["metrics"]["myr_usd"] = 4.90
        policies = {
            "opr": 2.00,
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "blanket",
            "development_expenditure": 22.0,
            "foreign_labor_policy": "balanced",
            "tax_regime": "gst",  # GST triggers +1.0 drain
            "epf_withdrawal_policy": "none",
            "exchange_rate_policy": "floating",
            "east_malaysia_allocation": 4.0
        }
        res = self.engine.step(policies)
        
        # Brain drain should be higher than baseline 3.0
        self.assertGreater(res["metrics"]["brain_drain_index"], 3.0)

if __name__ == '__main__':
    unittest.main()
