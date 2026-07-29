import unittest
from engine.engine import EconomyEngine
from engine.events import trigger_event, EVENTS

class TestEvents(unittest.TestCase):
    def setUp(self):
        self.engine = EconomyEngine()

    def test_fed_rate_hike_event(self):
        state = self.engine.state
        trigger_event("FED_RATE_HIKE", state)
        self.assertEqual(state["external"]["fed_rate"], 6.25)
        self.assertIn("US Fed Funds Rate Hike", state["external"]["shock_event"])

    def test_oil_price_crash(self):
        state = self.engine.state
        trigger_event("BRENT_OIL_CRASH", state)
        self.assertEqual(state["external"]["brent_crude"], 50.0)

    def test_east_coast_floods_expenditure_boost(self):
        state = self.engine.state
        base_exp = state["government"]["operating_exp"]  # 75.0
        trigger_event("FLOODS_EAST_COAST", state)
        self.assertEqual(state["government"]["operating_exp"], base_exp + 5.0)

if __name__ == '__main__':
    unittest.main()
