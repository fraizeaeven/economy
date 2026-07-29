# 🛠️ 04 — Technical Constraints & Simulation Engine Blueprint

> **This document defines the technical constraints, mathematical formulas, and simulation state transitions for the Malaysian Economy Text Simulator (METS).**

---

## 1. Mathematical Formulas (Simulation Engine Logic)

Every quarter, the engine updates the economic state. Below are the equations governing the state transition:

### 1.1 Gross Domestic Product (GDP)
GDP is modeled using the expenditure approach:

$$\text{GDP} = C + I + G + (X - M)$$

Where:
- **Consumption ($C$)**: Driven by household disposable income.
  $$C = C_{B40} + C_{M40} + C_{T20}$$
  - $C_{\text{segment}} = \text{Disposable Income}_{\text{segment}} \times \text{MPC}_{\text{segment}}$
  - Marginal Propensity to Consume ($\text{MPC}$): $\text{MPC}_{B40} = 0.90$, $\text{MPC}_{M40} = 0.75$, $\text{MPC}_{T20} = 0.50$.
- **Investment ($I$)**: Driven by interest rates (OPR) and corporate profitability.
  $$I = I_{\text{base}} \times (1 - 0.05 \times (\text{OPR} - \text{OPR}_{\text{base}})) + (\text{SME Profit} \times 0.2)$$
- **Government Spending ($G$)**:
  $$G = \text{Operating Expenditure} + \text{Development Expenditure}$$
- **Net Exports ($X - M$)**:
  - Exports ($X$) depend on Ringgit strength (higher Ringgit = lower exports) and global demand.
  - Imports ($M$) depend on domestic consumption and Ringgit strength (higher Ringgit = cheaper imports = higher imports volume).

### 1.2 Household Income & Commitments
For each segment (B40, M40, T20):

$$\text{Gross Income} = \text{Salary} + \text{Govt Handouts (STR)} + \text{Interest on Savings}$$
$$\text{Commitments} = \text{Utilities} + \text{Debt Service (Loans)}$$

- **Utilities**: Fixed cost baseline, adjusted by inflation.
- **Debt Service**: Highly dynamic and linked to OPR:
  $$\text{Debt Service} = \text{Debt Service}_{\text{base}} \times \left(1 + \beta \times (\text{OPR} - \text{OPR}_{\text{base}})\right)$$
  - $\beta$ (OPR sensitivity coefficient): B40 = `0.2`, M40 = `0.6` (high variable home/car loans), T20 = `0.3`.
- **Disposable Income**:
  $$\text{Disposable Income} = \text{Gross Income} - \text{Commitments} - \text{Income Tax}$$

### 1.3 Corporate / SME Profitability & Employment
- **SME Revenue**: Depends directly on local consumption ($C$).
- **SME Expenses**: Salary paid to B40/M40, commercial loans (OPR-sensitive), utilities, and taxes.
- **Employment Decisions**:
  - If SME Profit $\ge$ threshold, they maintain or increase hiring (Unemployment rate decreases by 0.1% per quarter).
  - If SME Profit < 0, they lay off workers (Unemployment rate increases by 0.2% per quarter).
  - B40 and M40 segments lose salary proportional to the unemployment rate.

### 1.4 Inflation (CPI)
Inflation is driven by three main channels:
1. **Demand-Pull Inflation**: Rises when consumption growth exceeds 5%.
2. **Cost-Push Inflation**: Spikes if global commodity prices (Brent crude, palm oil) rise, or if fuel subsidies are rationalized.
3. **Imported Inflation**: Decreases when the Ringgit strengthens:
   $$\text{Imported Inflation} \propto (\text{MYR/USD} - \text{MYR/USD}_{\text{base}})$$

---

## 2. Python State Schema

The simulation state will be managed in a nested Python dictionary:

```python
state = {
    "quarter": 1,
    "metrics": {
        "gdp": 450.0,             # RM Billion
        "gdp_growth": 4.2,        # %
        "opr": 3.00,              # %
        "cpi": 2.5,               # % (Inflation)
        "myr_usd": 4.40,          # Exchange rate
        "unemployment_rate": 3.5, # %
        "public_satisfaction": 60.0, # %
        "national_debt": 1200.0,  # RM Billion
        "debt_to_gdp": 64.0       # %
    },
    "households": {
        "b40": {
            "households": 3.2,    # Million
            "salary": 3500.0,     # RM/month avg
            "str_aid": 150.0,     # RM/month avg
            "commitments": {
                "utilities": 150.0,
                "debt_service": 800.0 # mostly small loans
            },
            "savings": 200.0      # RM avg
        },
        "m40": {
            "households": 3.2,
            "salary": 7500.0,
            "commitments": {
                "utilities": 400.0,
                "debt_service": 2500.0 # housing + car
            },
            "savings": 2000.0
        },
        "t20": {
            "households": 1.6,
            "salary": 18000.0,
            "commitments": {
                "utilities": 1000.0,
                "debt_service": 4000.0
            },
            "savings": 50000.0
        }
    },
    "government": {
        "tax_revenue": 80.0,      # RM Billion
        "operating_exp": 75.0,    # RM Billion
        "dev_exp": 22.0,          # RM Billion
        "subsidy_policy": "blanket" # or "targeted"
    },
    "sme": {
        "revenue": 120.0,
        "loan_payment": 20.0,
        "profit": 15.0
    },
    "external": {
        "brent_crude": 80.0,      # USD/barrel
        "fed_rate": 5.25          # %
    }
}
```
