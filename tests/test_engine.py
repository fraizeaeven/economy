import unittest
import os
import tempfile
from engine.main_engine import EconomyEngine

class TestEconomyEngine(unittest.TestCase):
    def setUp(self):
        self.engine = EconomyEngine()

    def test_default_state_initialization(self):
        state = self.engine.state
        self.assertEqual(state["quarter"], 1)
        self.assertEqual(state["metrics"]["opr"], 3.00)
        self.assertEqual(state["metrics"]["gdp"], 450.0)
        self.assertEqual(state["government"]["subsidy_policy"], "blanket")

    def test_engine_step_transition(self):
        policies = {
            "opr": 3.00,
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "blanket",
            "development_expenditure": 22.0
        }
        next_state = self.engine.step(policies)
        
        # Quarter should increment to 2
        self.assertEqual(next_state["quarter"], 2)
        # History should have exactly 1 record
        self.assertEqual(len(self.engine.history), 1)
        self.assertEqual(self.engine.history[0]["quarter"], 1)

    def test_opr_policy_impact(self):
        # Raise OPR to 4.5%
        policies = {
            "opr": 4.50,
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "blanket",
            "development_expenditure": 22.0
        }
        next_state = self.engine.step(policies)
        
        # M40 commitments on debt service should rise (baseline is 2500)
        m40_debt = next_state["households"]["m40"]["commitments"]["debt_service"]
        self.assertGreater(m40_debt, 2500.0)

    def test_targeted_subsidy_policy(self):
        # Change subsidy regime to targeted
        policies = {
            "opr": 3.00,
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "targeted",
            "development_expenditure": 22.0
        }
        next_state = self.engine.step(policies)
        
        # Operating exp should be reduced to 60.0 (blanket baseline is 75.0)
        self.assertEqual(next_state["government"]["operating_exp"], 60.0)
        # B40 STR aid monthly should increase to 280.0
        self.assertEqual(next_state["households"]["b40"]["str_aid"], 280.0)

    def test_save_and_load_state(self):
        # Take a step, save state, make another step, then reload and verify it rolled back
        policies = {
            "opr": 3.00,
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "blanket",
            "development_expenditure": 22.0
        }
        self.engine.step(policies)
        
        # Create temp file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "mets_test_save.json")
        
        try:
            # Save
            save_success = self.engine.save_state(temp_path)
            self.assertTrue(save_success)
            
            # Change state by taking another step
            self.engine.step(policies)
            self.assertEqual(self.engine.state["quarter"], 3)
            
            # Load
            load_success = self.engine.load_state(temp_path)
            self.assertTrue(load_success)
            
            # Verify restored to Q2
            self.assertEqual(self.engine.state["quarter"], 2)
            self.assertEqual(len(self.engine.history), 1)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == '__main__':
    unittest.main()
