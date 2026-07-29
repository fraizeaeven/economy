import unittest
from engine.formulas import (
    calculate_debt_service,
    calculate_consumption,
    calculate_exchange_rate,
    calculate_inflation
)

class TestFormulas(unittest.TestCase):
    def test_debt_service_baseline(self):
        # When OPR equals baseline, debt service should remain unchanged
        result = calculate_debt_service(2500.0, 3.00, 3.00, 0.6)
        self.assertEqual(result, 2500.0)

    def test_debt_service_increase(self):
        # OPR hike (from 3.00 to 4.00) raises debt service
        # diff = 1.0, sensitivity = 0.6 => multiplier = 1.6 => 2500 * 1.6 = 4000
        result = calculate_debt_service(2500.0, 4.00, 3.00, 0.6)
        self.assertEqual(result, 4000.0)

    def test_consumption(self):
        # B40 with 90% MPC
        self.assertEqual(calculate_consumption(5000.0, 0.90), 4500.0)
        # Negative income results in zero consumption
        self.assertEqual(calculate_consumption(-100.0, 0.90), 0.0)

    def test_exchange_rate_baseline(self):
        # At baseline, rate should match base rate
        result = calculate_exchange_rate(4.40, 3.00, 5.25, 80.0)
        self.assertEqual(result, 4.40)

    def test_exchange_rate_oil_spike(self):
        # Brent oil price spikes to 90.0 (+10 USD) -> Ringgit strengthens (MYR/USD drops)
        # oil_effect = -0.003 * 10 = -0.03 => rate = 4.40 - 0.03 = 4.37
        result = calculate_exchange_rate(4.40, 3.00, 5.25, 90.0)
        self.assertEqual(result, 4.37)

    def test_inflation_baseline(self):
        result = calculate_inflation(0.02, 0.0, "blanket", "blanket")
        self.assertEqual(result, 2.0)

    def test_inflation_subsidy_shock(self):
        # Switching from blanket to targeted adds +1.8% inflation shock
        result = calculate_inflation(0.02, 0.0, "targeted", "blanket")
        self.assertEqual(result, 3.8)

if __name__ == '__main__':
    unittest.main()
