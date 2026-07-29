import unittest
from engine.engine import EconomyEngine

class TestIntegration(unittest.TestCase):
    def test_full_20_quarter_simulation_loop(self):
        engine = EconomyEngine()
        
        # Consistent baseline policies
        policies = {
            "opr": 3.00,
            "sst_rate": 0.06,
            "corporate_tax": 0.24,
            "subsidy_regime": "blanket",
            "development_expenditure": 22.0
        }
        
        # Run 20 quarters
        for q in range(1, 21):
            state = engine.step(policies)
            
            # Check constraints
            self.assertEqual(state["quarter"], q + 1)
            
            # Verify GDP is positive
            self.assertGreater(state["metrics"]["gdp"], 0)
            
            # Verify inflation is a valid float
            self.assertIsInstance(state["metrics"]["cpi"], float)
            
            # Verify exchange rate is within bounds
            self.assertTrue(3.80 <= state["metrics"]["myr_usd"] <= 5.00)
            
            # Verify unemployment is within bounds
            self.assertTrue(3.0 <= state["metrics"]["unemployment_rate"] <= 10.0)
            
            # Verify satisfaction index is clamped
            self.assertTrue(0.0 <= state["metrics"]["public_satisfaction"] <= 100.0)

        # Check ending state
        is_over, reason = engine.check_game_status()
        self.assertTrue(is_over)
        self.assertIn("VICTORY" in reason or "GAME_OVER" in reason or "DEBT_CRISIS" in reason or "CIVIL_UNREST" in reason, [True])

if __name__ == '__main__':
    unittest.main()
