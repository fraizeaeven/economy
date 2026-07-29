# 📊 03 — Economic Flow & Agent-Based Analysis (Domain Model)

> **This document maps the flow of funds, population segmentation, sectoral interactions, and the transmission mechanisms of policy decisions in the Malaysian Economy Text Simulator (METS).**

---

## 1. Population & Socio-Economic Segmentation

The simulation represents the Malaysian population through **Isi Rumah (Households)** and **Syarikat (Business Enterprises)**, grouped to reflect realistic socio-economic behaviors.

### 1.1 Household Segments (Isi Rumah)
We model 8.0 Million households in Malaysia, divided into three brackets:

| Segment | Proportion | Est. Households | Avg. Monthly Income | Primary Income Source | Commitment Sensitivity |
|---|---|---|---|---|---|
| **B40 (Bottom 40%)** | 40% | 3.2 Million | < RM 5,000 | Wages (SME/PKS), Direct Government Aid (STR) | **High**: Extremely sensitive to inflation (CPI) and interest rates on small loans. Zero savings cushion. |
| **M40 (Middle 40%)** | 40% | 3.2 Million | RM 5,000 - RM 12,000 | Wages (Corporate/Civil Service) | **Medium-High**: Heavy exposure to floating-rate housing and car loans (highly impacted by OPR). |
| **T20 (Top 20%)** | 20% | 1.6 Million | > RM 12,000 | Corporate Wages, Dividends, Business profits | **Low**: High savings cushion, benefits from high bank interest deposit rates. |

### 1.2 Enterprise Segments (Syarikat)
Businesses are split into two categories which drive employment and production:

- **SMEs & PKS (Small-Medium Enterprises)**:
  - Employs **70%** of the domestic workforce (heavily B40 and lower M40).
  - Highly dependent on domestic consumer spending.
  - High debt-to-equity ratio (highly sensitive to interest rate hikes/OPR).
- **Large Corporates & MNCs**:
  - Employs **30%** of the workforce.
  - Export-oriented (benefits from a weaker Ringgit, but hurt by high global raw material imports).
  - Access to diversified funding (less affected by local OPR changes).

---

## 2. Closed-Loop Flow of Funds (Pergerakan Duit)

The economy functions as a circular flow of money between 5 core economic actors:

```
                  ┌──────────────────────────────────────────┐
                  │                KERAJAAN                  │
                  └─────────┬──────────────────────┬─────────┘
             Direct Aid     │                      │   Taxes & Utilities
             & Salaries     │                      │
                            ▼                      ▼
    ┌─────────────────────────┐                  ┌─────────────────────────┐
    │       ISI RUMAH         ├─Consumption─────►│        SYARIKAT         │
    │   (B40, M40, T20)       │◄──Wages/Salary───┤      (SMEs & MNCs)      │
    └──────────┬──────────────┘                  └──────────────┬──────────┘
      Savings  │    ▲                              Savings      │  Loan Payments
      & Loans  │    │ Loan Interest                & Loans      │  & Interest
               ▼    │                                           ▼  
    ┌─────────────────────────┐                  ┌─────────────────────────┐
    │          BANK           │◄──Interbank/OPR──►│    SYARIKAT UTILITI     │
    │   (Commercial Banks)    │                   │   (TNB, Water, Telco)   │
    └─────────────────────────┘                  └─────────────────────────┘
```

### 2.1 The Flow Mechanics

1. **Wages (Syarikat → Isi Rumah)**:
   - Businesses pay monthly salaries to households.
   - SME salaries are volatile, depending on quarterly sales. MNC salaries are stable.
2. **Consumption (Isi Rumah → Syarikat & Utiliti)**:
   - Households spend their disposable income (Income minus Commitments & Taxes) on consumption.
   - Part of consumption goes to basic Utilities (fixed costs paid to Utility Companies).
3. **Commitments (Isi Rumah & Syarikat → Bank)**:
   - Households pay housing and car loans (fixed or variable rate).
   - Companies pay business loans.
   - When **OPR increases**, variable rate loan commitments increase instantly, shrinking household disposable income.
4. **Taxes (Isi Rumah & Syarikat → Kerajaan)**:
   - Households pay Personal Income Tax and SST (sales tax on consumption).
   - Companies pay Corporate Tax.
5. **Government Redistribution (Kerajaan → Isi Rumah & Syarikat)**:
   - Kerajaan uses tax revenue to pay **Direct Financial Aid** (e.g., STR) targeting B40/M40.
   - Kerajaan pays salaries of civil servants (Isi Rumah).
   - Kerajaan provides incentives and grants to SMEs & PKS to stimulate hiring.

---

## 3. Policy Transmission Channels

### 3.1 Monetary Policy: OPR (Bank Negara Malaysia)
OPR is the control lever of money supply and credit cost:

$$\text{OPR} \uparrow \implies \text{Loan Interest Rates} \uparrow \implies \text{Commitments} \uparrow \implies \text{Disposable Income} \downarrow \implies \text{Consumer Spending} \downarrow \implies \text{Inflation} \downarrow$$

- **Ringgit Channel**: Higher OPR attracts foreign capital, strengthening the Ringgit (MYR/USD drops). A stronger MYR reduces the cost of imported goods (cutting import-driven inflation) but makes exports slightly less competitive.
- **Employment Channel**: High OPR raises debt costs for SMEs, leading to hiring freezes or layoffs, which increases unemployment.

### 3.2 Fiscal Policy: Taxation & Expenditure (Ministry of Finance)
Fiscal policy controls government debt and direct redistribution:

- **SST (Sales Tax) / Income Tax**:
  - Higher taxes increase government revenue (reducing deficit/debt growth).
  - However, they directly reduce household disposable income and consumer spending, lowering Public Satisfaction.
- **Operating & Development Expenditure**:
  - High Operating Expenditure (emoluments, blanket subsidies) directly cushions public inflation but runs a high fiscal deficit.
  - Development Expenditure (building infrastructure) injects money directly to Corporates/SMEs, boosting jobs and GDP growth in the medium term.
- **Direct Handouts (STR)**:
  - Directly injected into B40 and lower M40. Since B40 has a high **Marginal Propensity to Consume (MPC)**, almost 100% of STR goes directly back into the economy via local SME purchases.
