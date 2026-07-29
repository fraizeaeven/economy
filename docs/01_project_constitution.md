# 📜 01 — Project Constitution

> **This document defines the immutable identity, strategic direction, and non-negotiable design principles of the Malaysian Economy Text Simulator (METS). It is the highest-authority reference in the entire documentation chain.**

---

## 1. Project Identity

**Product Name**: Malaysian Economy Text Simulator (METS)  
**Tagline**: *"Steer the nation through fiscal and monetary winds."*  
**Classification**: Text-Based Turn-Based Macroeconomic Simulation Engine

### What It Is

METS is a lightweight, turn-based interactive simulation application. The user assumes the role of the National Economic Council, holding control over both **Fiscal Policy** (Ministry of Finance) and **Monetary Policy** (Bank Negara Malaysia). The simulation progresses quarter-by-quarter (or year-by-year), presenting the user with macroeconomic events, global shocks, and policy choices. The goal is to balance economic growth, currency strength, price stability, and public satisfaction while keeping national debt sustainable.

### What It Is NOT

- This is **not** a predictive economic forecasting tool. It is an educational and interactive simulator based on simplified macroeconomic formulas and historical relationships.
- This is **not** a real-time game. It is strictly turn-based (quarters or years) to allow thoughtful policy formulation.

---

## 2. Core Simulation Loop

The engine operates on a feedback loop of policies, macroeconomic metrics, and external events:

```
[Start Quarter]
      ↓
[Display Current Metrics & Global Shocks (e.g., Oil Price spike, Fed rate hikes)]
      ↓
[Policy Decision Input (Adjust OPR, Tax Rates, Budget Allocations, Subsidies)]
      ↓
[Run Economic Model (Recalculate GDP, CPI, MYR, Debt, Satisfaction)]
      ↓
[Display Quarterly Results & Impact Feed]
      ↓
[Check Win/Loss Conditions]
```

---

## 3. Design Constitution

### 3.1 Macroeconomic Realism (Non-Negotiable)
- **Interest Rate Transmission**: Raising the OPR (Overnight Policy Rate) must strengthen the Ringgit (MYR) and cool inflation, but drag down GDP growth.
- **Fiscal-Monetary Balance**: Heavy government spending boosts GDP in the short term but increases fiscal deficit, national debt, and can trigger rating downgrades if debt-to-GDP exceeds limits.
- **Subsidy Dynamics**: High subsidies (e.g., fuel subsidy) reduce inflation (CPI) and boost public satisfaction, but increase government operating expenditure. Rationalizing subsidies frees up fiscal space but spikes CPI and lowers public satisfaction.
- **External Dependencies**: Malaysia is a small open economy. External variables like Brent crude oil prices, US Federal Reserve interest rates, and China GDP growth must influence domestic economic indicators.

### 3.2 Visual & Interface Standards
- **High-Signal Terminal/Text UI**: Clear, structured dashboard readouts.
- **Liquid Glass Theme (Web/HTML Variant)**: If packaged as a web UI later, it should use dark modes with high-contrast color-coded indicators (green for positive, yellow for warning, red for critical).
- **Responsive Text Layout**: Adaptable layout that displays clean tables and cards in standard terminal viewports or basic web containers.

---

## 4. Key Performance Indicators (KPIs)

The user is evaluated on 6 core pillars:

1. **GDP Growth Rate (%)**: Target range `+4.0%` to `+5.5%`.
2. **Inflation Rate (CPI %)**: Target range `+2.0%` to `+3.0%`.
3. **National Debt-to-GDP (%)**: Statutory ceiling limit of `65.0%`.
4. **Ringgit Exchange Rate (MYR/USD)**: Stable range `4.20` to `4.60`.
5. **Fiscal Balance (% of GDP)**: Deficit target `< -3.5%`.
6. **Public Satisfaction Index (%)**: Target `> 50%` (drops if inflation is high or tax is too high).

---

## 5. Success Metrics (Project Level)

- Simulation runs smoothly without syntax errors or mathematical divergence (e.g., infinite inflation or negative GDP).
- User can play a full 5-year cycle (20 quarters) to completion.
- Clear win/loss states based on debt crisis (loss) or election victory (win).
