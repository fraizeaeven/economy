# 📜 10 — Sectoral Health & Population Equilibrium (Feature Specification)

> **This document specifies the requirements, equations, and UI design for tracking the health of individual economic sectors, poverty rates, and foreign populations in the simulator.**

---

## 1. Sectoral Health Status Metrics

To evaluate if the population and economy are in a healthy equilibrium, the simulator will track individual **Health Indices (0% to 100%)** for the 5 core sectors:

### 1.1 Family Health Index
- **Goal**: Protect household purchasing power and financial resilience.
- **Indicators**:
  - **Debt Service Ratio (DSR)**: $\text{DSR} = \text{Debt Service} / \text{Gross Income}$. Healthy range $< 35\%$.
  - **Savings Buffer**: $\text{Savings} / \text{Quarterly Commitments}$.
- **Formula**:
  $$\text{Family Health} = 100 - (\text{DSR} \times 150) - \text{Poverty Rate} \times 2 + \text{Savings Factor}$$
  - Segments B40, M40, and T20 will have individual health scores, aggregated into a national Family Health index.

### 1.2 SME / PKS Health Index
- **Goal**: Maintain business viability, promote local employment, and prevent bankruptcies.
- **Formula**:
  $$\text{SME Health} = \text{clamp}\left(50 + (\text{SME Profit} / \text{SME Revenue}) \times 100 - (\text{OPR} - 3.0) \times 10, 0, 100\right)$$
  - Directly drops if corporate tax is too high or OPR raises borrowing costs beyond profitability limits.

### 1.3 Utilities Company Health Index
- **Goal**: Guarantee operational sustainability and reinvestment in national infrastructure (grid, water, fiber).
- **Formula**:
  $$\text{Utilities Health} = \text{clamp}\left(70 + (\text{Total Billing Receipts} - \text{Govt Subsidy Cutbacks}) \times 0.5, 0, 100\right)$$

### 1.4 Banking Health Index
- **Goal**: Ensure liquidity and financial sector stability.
- **Formula**:
  $$\text{Banking Health} = \text{clamp}\left(80 + (\text{Interest Margin Profit}) - (\text{Unemployment} \times 2), 0, 100\right)$$
  - High unemployment triggers non-performing loans (NPLs), dropping banking health.

### 1.5 Government Fiscal Health Index
- **Goal**: Maintain sovereign debt sustainability.
- **Formula**:
  $$\text{Govt Health} = 100 - (\text{Debt-to-GDP} - 55) \times 1.5 + (\text{Fiscal Deficit \%} \times 10)$$

---

## 2. Investment Dynamics (FDI & DDI)

Investment drives long-term GDP capacity and productivity:

- **Foreign Direct Investment (FDI)**:
  - Injected quarterly into Large Corporates.
  - Driven by corporate tax competitiveness (lower tax = higher FDI) and exchange rate stability.
  - Formula:
    $$\text{FDI} = 15.0 \times \left(1.0 - 1.5 \times (\text{Corporate Tax} - 0.24) - 0.2 \times |\text{MYR/USD} - 4.40|\right)$$
- **Domestic Direct Investment (DDI)**:
  - Injected by domestic businesses and banks into local projects.
  - Driven by SME profitability and lower interest rates (OPR).
  - Formula:
    $$\text{DDI} = 25.0 \times \left(1.0 - 0.05 \times (\text{OPR} - 3.00) + 0.1 \times (\text{SME Profit} - 15.0)\right)$$

---

## 3. Poverty & Population Equilibrium

To address the core objective of finding a "healthy spot for the population first", we introduce poverty lines and foreign labor dynamics.

### 3.1 Kadar Kemiskinan (Poverty Rate %)
- The Poverty Line Income (PLI) is set at RM 2,584 per month (adjusted dynamically for CPI inflation).
- Poverty rate is calculated based on B40 gross monthly income (Salary + STR) relative to the PLI:
  $$\text{Poverty Rate} = \text{clamp}\left(5.6\% + \left(\frac{\text{PLI} - \text{B40 Income}}{100}\right) \times 0.5 + (\text{Unemployment} - 3.5) \times 0.8, 1.5\%, 25.0\%\right)$$

### 3.2 Foreign Population Segments
We track three groups in the labor force:
1. **Registered Foreign Workers**: 2.2 Million baseline.
2. **Unregistered Foreign Workers**: 1.2 Million baseline.
3. **Refugees / Asylum Seekers**: 0.2 Million baseline.

#### Policy Lever: Foreign Worker Quota & Levy
The user can adjust a new policy lever: `foreign_labor_policy` (choices: `loose`, `balanced`, `strict`).

| Policy Choice | Economic Effect | Social Effect |
|---|---|---|
| **Loose** (Cheap labor) | Reduces SME costs (increases profits by 10%), suppresses B40 wages (salary drops by 5%). FDI increases. | Lowers Public Satisfaction (-3%) due to social integration concerns. |
| **Balanced** (Current) | Baseline values. | Neutral. |
| **Strict** (Local priority) | Raises SME costs (profits drop by 15%), pushes B40 wages up (salary increases by 10% as locals are hired instead). | Raises Public Satisfaction (+4%). |

---

## 4. UI Dashboard Layout: Sectoral Health Report

When the user types `v` (Sectoral Health), the console displays a dedicated report:

```
=================================================================
             METS SECTORAL HEALTH & POPULATION REPORT
=================================================================
* SECTOR HEALTH STATUS:
  - Family Health:        [████████████████████████      ] 80.0% (HEALTHY)
  - SME / PKS Health:     [████████████████              ] 55.0% (CAUTION)
  - Utilities Health:     [██████████████████████████    ] 88.0% (EXCELLENT)
  - Banking Health:       [██████████████████████        ] 75.0% (HEALTHY)
  - Government Health:    [██████████████████            ] 62.0% (CAUTION)

* POPULATION & SOCIAL EQUILIBRIUM:
  - Poverty Rate:         5.6% (Poverty Line: RM 2,584/month)
  - Avg. B40 Household:   Salary: RM 3,500 | STR Aid: RM 150
  
* LABOR FORCE PROFILE:
  - Registered Workers:   2.20 Million
  - Unregistered Workers: 1.20 Million
  - Refugee Population:   0.20 Million
  - Current Labor Policy: BALANCED

* CAPITAL FORMATION:
  - Foreign Direct Investment (FDI): RM 15.00 Billion
  - Domestic Direct Investment (DDI): RM 25.00 Billion
=================================================================
```
