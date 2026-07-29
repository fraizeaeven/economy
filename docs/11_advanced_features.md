# 📜 11 — Advanced Economic Features (GST, EPF, Pegging, Brain Drain, East Malaysia)

> **This document drafts the specifications, variables, and formulas for 5 advanced key features to enhance the macroeconomic realism of the Malaysian Economy Text Simulator (METS).**

---

## 1. Feature 1: EPF / KWSP Retirement Fund & Withdrawal Policy
- **Concept**: Modeling retirement savings and the trade-offs of early retirement withdrawals (e.g., historical i-Sinar/i-Lestari).
- **Mechanics**:
  - Employee contributions (11%) and Employer contributions (13%) are deducted from salaries and added to the **EPF National Fund Pool**.
  - **EPF Fund Capital** directly drives Domestic Direct Investment (DDI) capacity: DDI increases proportional to EPF fund growth.
  - **Policy Lever**: `epf_withdrawal_policy` (choices: `none`, `targeted`, `unrestricted`).
    - `none`: EPF funds grow steadily. Family Health Index increases due to long-term financial security.
    - `targeted` / `unrestricted`: Instantly transfers RM 5.0B to RM 15.0B from EPF savings directly to B40/M40 disposable income. This spikes short-term Consumption ($C$) and Public Satisfaction (+10%), but reduces EPF Capital (dropping DDI by 15%) and degrades Family Health Index (-15%) due to depleted retirement savings.

---

## 2. Feature 2: Ringgit Exchange Policy (Pegged vs Floating) & Foreign Reserves
- **Concept**: Modeling exchange rate regimes (fixed pegs vs managed floats) and central bank reserves.
- **Mechanics**:
  - **Foreign Reserves**: Starts at USD 115 Billion.
  - **Policy Lever**: `exchange_rate_policy` (choices: `floating`, `pegged_4.00`, `pegged_3.80`).
    - `floating`: Exchange rate is determined by the `calculate_exchange_rate` formula. Foreign reserves fluctuate slightly based on trade balances.
    - `pegged_X`: Ringgit is locked at the pegged rate (e.g., 3.80 or 4.00 MYR/USD).
  - **Reserve Drain**: If market forces pull the market exchange rate away from the peg, Bank Negara must defend the peg.
    - If market rate is weaker than peg, Bank Negara sells USD reserves to buy MYR:
      $$\text{Reserves Change} = -2.5 \times (\text{Market Rate} - \text{Peg Rate}) \text{ USD Billion/quarter}$$
    - If Foreign Reserves fall below **USD 10 Billion**, a currency default crisis is triggered, resulting in an instant `GAME OVER`.

---

## 3. Feature 3: Tax Reform (SST vs GST / Broad-Based Consumption Tax)
- **Concept**: The fiscal and social trade-offs of Sales and Services Tax (SST) versus Goods and Services Tax (GST).
- **Policy Lever**: `tax_regime` (choices: `sst`, `gst`).
- **Mechanics**:
  - `sst`: Selective tax. Baseline rate 6%. Only applied to 40% of consumption. Low tax revenue, but neutral CPI inflation impact and higher public satisfaction.
  - `gst`: Broad-based value-added tax. Rate fixed at 6% (or adjustable). Applied to 90% of consumption.
    - **Fiscal Effect**: Generates **+45%** higher tax revenue compared to SST at the same rate, accelerating debt reduction.
    - **Inflation Effect**: Triggers a one-off CPI inflation spike of **+2.0%** in the quarter of implementation.
    - **Social Effect**: Lowers B40 disposable income and public satisfaction (-8% approval shock) due to higher cost of basic goods.

---

## 4. Feature 4: Regional Development (East Malaysia Gap) & Tourism Sector
- **Concept**: Modeling infrastructure development disparities in Sabah and Sarawak, and the impact of the tourism sector.
- **Policy Lever**: `east_malaysia_allocation` (Min 2.0B, Max 15.0B, Default 4.0B - allocated from Development Expenditure).
- **Mechanics**:
  - Sabah and Sarawak start with a poverty rate of `14.5%`.
  - Increasing allocations to East Malaysia reduces the East Malaysia poverty rate and increases overall Public Satisfaction (+1.5% per extra Billion).
  - However, East Malaysian projects have a lower short-term GDP multiplier (0.8x) compared to West Malaysian infrastructure (1.2x) due to logistical distances.
  - **Tourism Sector**: Generates quarterly service export revenue:
    $$\text{Tourism Revenue} = 10.0 \times \left(1.0 + 0.1 \times (\text{MYR/USD} - 4.40) - (\text{Foreign Labor strictness penalty})\right)$$

---

## 5. Feature 5: Talent Flight (Brain Drain Index)
- **Concept**: Modeling skilled workforce migration to high-wage regions (e.g., Singapore) and its impact on productivity.
- **Metrics**: **Brain Drain Index (0.0 to 10.0)**. Starts at `3.0`.
- **Drivers**:
  - Increases if exchange rate MYR is weak (exchange rate index increases).
  - Increases if public satisfaction is low, or if corporate/personal income tax is too high.
  - Formula:
    $$\text{Brain Drain Index} = \text{clamp}(3.0 + 1.5 \times (\text{MYR/USD} - 4.40) - 0.1 \times (\text{Satisfaction} - 60), 1.0, 10.0)$$
- **Economic Feedback Loop**:
  - High Brain Drain ($> 5.0$) suppressed T20 and M40 average salary base by up to **8%** over time due to shortage of high-skilled labor.
  - High Brain Drain reduces FDI inflows by **15%** (MNCs avoid markets with labor deficits) and reduces SME productivity (costs increase).
