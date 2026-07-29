# 🔍 02 — Requirement Discovery

> **This document lists the system requirements, functional specifications, and target parameters of the Malaysian Economy Text Simulator (METS).**

---

## 1. Problem Statement & Objectives

Understanding macroeconomic policies is often abstract and complex. Users need an interactive, low-friction environment to see how monetary policy (OPR adjustments) and fiscal policy (taxation, spending, subsidies) interact in a small open economy like Malaysia.

The simulator should:
- Demonstrate trade-offs (e.g., inflation vs. growth, debt vs. public satisfaction).
- Model realistic Malaysian dynamics (dependence on oil prices, palm oil, global interest differentials).
- Provide a responsive text-based interface.

---

## 2. Core Economic Parameters (Starting State)

To reflect the real Malaysia economic baseline:

| Parameter | Starting Value | Description |
|---|---|---|
| **GDP (Nominal)** | RM 450 Billion | Initial quarterly GDP baseline |
| **GDP Growth Rate** | `4.2%` (annualized) | Quarterly annualized growth rate |
| **OPR** | `3.00%` | BNM Overnight Policy Rate |
| **Inflation Rate (CPI)**| `2.5%` | Consumer Price Index annual change |
| **National Debt** | RM 1.2 Trillion | Total federal government debt |
| **Debt-to-GDP** | `64.0%` | Debt as a percentage of annualized GDP |
| **MYR/USD Exchange Rate**| `4.40` | Price of 1 USD in MYR |
| **Fiscal Deficit** | `-4.3%` | Government deficit as % of GDP |
| **US Fed Funds Rate** | `5.25%` | US interest rate (impacts capital flows) |
| **Brent Crude Oil** | `$80` / barrel | Critical commodity export price |
| **Public Satisfaction** | `60%` | Combined metric of tax burden, inflation, and growth |

---

## 3. Functional Requirements

### 3.1 Turn Flow & Game Engine
- The game runs for **20 Quarters** (5 years).
- Each quarter, the engine:
  1. Computes starting parameters and applies scheduled/random macroeconomic events (e.g., US Fed rate hike, Crude Oil price collapse).
  2. Displays the **Macroeconomic Dashboard**.
  3. Prompt the user for policy adjustments.
  4. Runs the simulation step (updates state based on policy transmission formulas).
  5. Displays the quarterly transition report.
  6. Checks fail conditions.

### 3.2 Policy Controls (User Inputs)
Every turn, the user can choose to adjust:
- **Monetary Policy**:
  - `OPR`: Increase/Decrease by multiples of `0.25%` (Limit: `1.50%` to `6.00%`).
- **Fiscal Policy**:
  - `Tax Rate (SST)`: Adjust between `4%` and `10%` (Baseline: `6%`).
  - `Corporate Tax`: Adjust between `20%` and `30%` (Baseline: `24%`).
  - `Fuel Subsidies`: Targeted (low spending, higher inflation) vs. Blanket (high spending, low inflation).
  - `Development Expenditure`: RM Billion allocation per quarter (Baseline: RM 22B).

### 3.3 Event Engine (Shocks)
The engine generates scheduled and random external events:
- **Global Financial Shock**: US Fed hikes rates → capital flight → MYR depreciates → import inflation spikes.
- **Commodity Boom/Bust**: Brent Crude spikes/drops → government oil revenue changes drastically.
- **Domestic Shocks**: Severe flooding → agriculture/tourism GDP drop, relief spending required.
- **Elections**: Occurs at Quarter 20. Public satisfaction determines if the government is re-elected (Satisfaction > 50%).

---

## 4. Technical Constraints

- **Language**: Python 3.10+ (Core game loop, terminal executable).
- **Dependencies**: Zero external dependencies (only standard library: `math`, `random`, `json`).
- **Data Persistence**: Support simple JSON-based save/load game states.
- **Modular Interface**: Engine logic must be separated from UI logic to allow easy migration to a Next.js / FastAPI fullstack web app.
