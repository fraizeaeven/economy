# 📜 08 — Class Signatures & Engine Contracts (API Contract)

> **This document defines the class interfaces, methods, parameters, and return types of the core simulation components.**

---

## 1. EconomyEngine Class Signature (`engine/engine.py`)

The main orchestrator class that manages state.

```python
class EconomyEngine:
    def __init__(self, state_preset: dict = None):
        """
        Initializes the simulation state. If state_preset is provided,
        restores state from it, otherwise loads default Malaysian starting state.
        """
        self.state = {}
        self.history = []  # List of past states for trend tracking
        self.active_events = []
        
    def step(self, policies: dict) -> dict:
        """
        Runs a single transition step of 1 quarter:
        1. Applies any active/scheduled events.
        2. Applies user policies.
        3. Invokes math formulas to compute the next state.
        4. Saves state to history.
        5. Returns the updated state.
        """
        pass
        
    def get_kpis(self) -> dict:
        """
        Returns a simplified dictionary of the 6 core KPIs for reporting.
        """
        pass

    def check_game_status(self) -> tuple[bool, str]:
        """
        Checks if the simulation has ended:
        - Return: (is_over, reason_string)
        - Loss scenarios: Debt/GDP > 80%, Public Satisfaction < 20%.
        - Win scenario: Reaching Q20 with Debt < 65% and Public Satisfaction > 50%.
        """
        pass

    def save_state(self, filepath: str) -> bool:
        """Saves current state and history to a JSON file."""
        pass

    def load_state(self, filepath: str) -> bool:
        """Loads state and history from a JSON file."""
        pass
```

---

## 2. Policy Input Schema

The `step()` function expects a `policies` dictionary matching the following schema:

```json
{
  "opr": 3.00,                      // float: Overnight Policy Rate (1.50 to 6.00)
  "sst_rate": 0.06,                 // float: Sales & Service Tax rate (0.04 to 0.10)
  "corporate_tax": 0.24,            // float: Corporate tax rate (0.20 to 0.30)
  "subsidy_regime": "blanket",      // string: "blanket" or "targeted"
  "development_expenditure": 22.0    // float: RM Billion (10.0 to 50.0)
}
```

---

## 3. Pure Formulas Module (`engine/formulas.py`)

Pure mathematical calculations utilized by the Engine:

```python
def calculate_consumption(disposable_income: dict, mpc: dict) -> dict:
    """
    Computes consumption per household segment.
    """
    pass

def calculate_debt_service(base_debt: float, opr: float, base_opr: float, sensitivity: float) -> float:
    """
    Computes updated household loan repayment commitments based on OPR shifts.
    """
    pass

def calculate_exchange_rate(myr_base: float, local_rate: float, us_rate: float, brent_price: float) -> float:
    """
    Computes the MYR/USD exchange rate based on interest rate differentials and oil prices.
    """
    pass

def calculate_inflation(consumption_growth: float, myr_change: float, subsidy_change: float) -> float:
    """
    Computes quarterly CPI inflation rate.
    """
    pass
```
