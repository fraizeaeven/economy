import json
import os
from engine.formulas import (
    calculate_debt_service,
    calculate_consumption,
    calculate_exchange_rate,
    calculate_inflation,
    clamp
)

class EconomyEngine:
    def __init__(self, state_preset: dict = None):
        """
        Initializes the simulator state. If state_preset is provided,
        loads that state, otherwise initializes the default Malaysian state.
        """
        if state_preset:
            self.state = state_preset
            self.history = state_preset.get("history", [])
        else:
            self.state = self.get_default_state()
            self.history = []
            
        self.active_events = []

    def get_default_state(self) -> dict:
        """
        Returns the initial starting state dictionary of the economy.
        All currency metrics are in RM Billion unless specified otherwise.
        """
        return {
            "quarter": 1,
            "metrics": {
                "gdp": 450.0,               # Quarterly GDP (RM Billion)
                "gdp_growth": 4.2,          # Annualized growth rate (%)
                "opr": 3.00,                # Overnight Policy Rate (%)
                "cpi": 2.5,                 # CPI Inflation rate (%)
                "myr_usd": 4.40,            # Exchange rate (MYR per 1 USD)
                "unemployment_rate": 3.5,   # Unemployment (%)
                "public_satisfaction": 60.0, # Public satisfaction (%)
                "national_debt": 1200.0,    # National Debt (RM Billion)
                "debt_to_gdp": 66.67,       # Debt as % of annualized GDP
                "poverty_rate": 5.6,        # % households below Poverty Line
                "fdi": 15.0,                # Foreign Direct Investment (RM Billion)
                "ddi": 25.0,                # Domestic Direct Investment (RM Billion)
                "family_health": 80.0,      # Family health index (%)
                "sme_health": 75.0,         # SME/PKS health index (%)
                "utilities_health": 85.0,   # Utilities company health index (%)
                "banking_health": 80.0,     # Commercial banks health index (%)
                "govt_health": 78.0,        # Government fiscal health index (%)
                "brain_drain_index": 3.0,   # Talent flight index (0.0 to 10.0)
                "east_malaysia_poverty": 14.5, # Sabah & Sarawak poverty (%)
                "foreign_reserves": 115.0,  # BNM reserves (USD Billion)
                "epf_pool": 750.0,          # KWSP total asset pool (RM Billion)
                "tourism_revenue": 10.0     # Quarterly Tourism export earnings (RM Billion)
            },
            "households": {
                "b40": {
                    "households": 3.2,      # Million households
                    "salary_base": 3500.0,  # Base salary (RM/month)
                    "salary": 3500.0,       # Current salary (RM/month)
                    "str_aid": 150.0,       # Govt direct financial aid (RM/month)
                    "commitments": {
                        "utilities": 150.0,
                        "debt_service": 800.0
                    },
                    "mpc": 0.90,            # Marginal Propensity to Consume
                    "savings": 2.0          # RM Billion (Total segment savings)
                },
                "m40": {
                    "households": 3.2,
                    "salary_base": 7500.0,
                    "salary": 7500.0,
                    "str_aid": 0.0,
                    "commitments": {
                        "utilities": 400.0,
                        "debt_service": 2500.0
                    },
                    "mpc": 0.75,
                    "savings": 20.0
                },
                "t20": {
                    "households": 1.6,
                    "salary_base": 18000.0,
                    "salary": 18000.0,
                    "str_aid": 0.0,
                    "commitments": {
                        "utilities": 1000.0,
                        "debt_service": 4000.0
                    },
                    "mpc": 0.50,
                    "savings": 150.0
                }
            },
            "government": {
                "tax_revenue": 82.5,        # RM Billion
                "operating_exp": 75.0,      # RM Billion
                "dev_exp": 22.0,            # RM Billion
                "subsidy_policy": "blanket", # "blanket" or "targeted"
                "tax_regime": "sst",        # "sst" or "gst"
                "epf_withdrawal_policy": "none", # "none", "targeted", or "unrestricted"
                "exchange_rate_policy": "floating", # "floating", "pegged_4.00", or "pegged_3.80"
                "east_malaysia_allocation": 4.0 # RM Billion
            },
            "sme": {
                "revenue": 120.0,
                "loan_payment": 20.0,       # RM Billion
                "profit": 15.0
            },
            "external": {
                "brent_crude": 80.0,        # USD / barrel
                "fed_rate": 5.25,           # %
                "shock_event": None,        # Event name of the quarter
                "election_status": None,    # Re-election message flag
                "foreign_labor_policy": "balanced", # "loose", "balanced", or "strict"
                "registered_foreign_workers": 2.2,  # Million workers
                "unregistered_foreign_workers": 1.2, # Million workers
                "refugees": 0.2             # Million refugees
            }
        }

    def step(self, policies: dict) -> dict:
        """
        Transitions the economy forward by 1 Quarter.
        """
        # 1. Archive current state to history
        current_snapshot = json.loads(json.dumps(self.state))
        self.history.append(current_snapshot)
        
        # 2. Extract inputs (clamp values to prevent extreme policies)
        opr = clamp(policies.get("opr", 3.00), 1.50, 6.00)
        sst_rate = clamp(policies.get("sst_rate", 0.06), 0.00, 0.15)
        corp_tax_rate = clamp(policies.get("corporate_tax", 0.24), 0.10, 0.35)
        subsidy_policy = policies.get("subsidy_regime", "blanket")
        dev_exp = clamp(policies.get("development_expenditure", 22.0), 10.0, 50.0)
        labor_policy = policies.get("foreign_labor_policy", "balanced")
        if labor_policy not in ["loose", "balanced", "strict"]:
            labor_policy = "balanced"
            
        prev_metrics = self.state["metrics"]
        prev_govt = self.state["government"]
        
        # Advanced policies extraction
        tax_regime = policies.get("tax_regime", prev_govt.get("tax_regime", "sst"))
        if tax_regime not in ["sst", "gst"]:
            tax_regime = "sst"
            
        epf_policy = policies.get("epf_withdrawal_policy", prev_govt.get("epf_withdrawal_policy", "none"))
        if epf_policy not in ["none", "targeted", "unrestricted"]:
            epf_policy = "none"
            
        ex_rate_policy = policies.get("exchange_rate_policy", prev_govt.get("exchange_rate_policy", "floating"))
        if ex_rate_policy not in ["floating", "pegged_4.00", "pegged_3.80"]:
            ex_rate_policy = "floating"
            
        east_malaysia_allocation = clamp(
            policies.get("east_malaysia_allocation", prev_govt.get("east_malaysia_allocation", 4.0)),
            2.0, 15.0
        )
            
        # Update foreign population and cost factors based on policy choice
        if labor_policy == "loose":
            self.state["external"]["registered_foreign_workers"] = 2.5
            self.state["external"]["unregistered_foreign_workers"] = 1.4
            labor_cost_factor = 0.90  # 10% cost reduction for SMEs (cheap labor)
            b40_wage_factor = 0.95    # suppressed local B40 wages
        elif labor_policy == "strict":
            self.state["external"]["registered_foreign_workers"] = 1.8
            self.state["external"]["unregistered_foreign_workers"] = 0.9
            labor_cost_factor = 1.15  # 15% cost increase for SMEs
            b40_wage_factor = 1.10    # boosted B40 wages (priority to locals)
        else:
            self.state["external"]["registered_foreign_workers"] = 2.2
            self.state["external"]["unregistered_foreign_workers"] = 1.2
            labor_cost_factor = 1.0
            b40_wage_factor = 1.0
            
        self.state["external"]["foreign_labor_policy"] = labor_policy
        
        prev_myr = prev_metrics["myr_usd"]
        
        # 3. Update external variables from state (could be altered by events module)
        brent_crude = self.state["external"]["brent_crude"]
        fed_rate = self.state["external"]["fed_rate"]
        
        # 4. Exchange Rate & Reserves calculation
        market_myr_usd = calculate_exchange_rate(4.40, opr, fed_rate, brent_crude)
        
        # Defending pegged currency consumes foreign reserves
        if ex_rate_policy == "pegged_4.00":
            myr_usd = 4.00
            reserves_change = -2.5 * (market_myr_usd - 4.00)
        elif ex_rate_policy == "pegged_3.80":
            myr_usd = 3.80
            reserves_change = -3.5 * (market_myr_usd - 3.80)
        else:
            myr_usd = market_myr_usd
            # float reserves flow
            reserves_change = 0.5 * (prev_metrics.get("fdi", 15.0) + prev_metrics.get("ddi", 25.0) - 40.0) / 10.0
            
        myr_change = myr_usd - prev_myr
        foreign_reserves = max(0.0, prev_metrics.get("foreign_reserves", 115.0) + reserves_change)
        
        # 4.2 Brain Drain Index & Suppression Factor
        prev_satisfaction = prev_metrics["public_satisfaction"]
        brain_drain = 3.0 + 1.5 * (myr_usd - 4.40) - 0.1 * (prev_satisfaction - 60.0)
        if tax_regime == "gst":
            brain_drain += 1.0
        brain_drain = clamp(brain_drain, 1.0, 10.0)
        brain_drain_suppression = 1.0 - (max(0.0, brain_drain - 5.0) / 5.0) * 0.08
        
        # 5. Unemployment impact from SME profitability
        sme_profit = self.state["sme"]["profit"]
        unemployment = prev_metrics["unemployment_rate"]
        if sme_profit > 10.0:
            unemployment = max(3.0, unemployment - 0.1)
        elif sme_profit < 2.0:
            unemployment = min(10.0, unemployment + 0.2)
            
        # 6. Apply Government Subsidy Policy Shifts
        # If targeted, operating expenditure decreases, and STR aid increases for B40/M40
        operating_exp = 75.0
        b40_str_monthly = 150.0
        m40_str_monthly = 0.0
        
        if subsidy_policy == "targeted":
            operating_exp = 60.0  # saving 15 Billion OPEX
            b40_str_monthly = 280.0  # higher direct financial aid
            m40_str_monthly = 80.0
            
        # 7. Update Household Salaries & Commitments (OPR Transmission)
        households = self.state["households"]
        
        # Salary changes based on unemployment
        # baseline unemployment is 3.5%
        job_factor = 1.0 - ((unemployment - 3.5) / 100.0 * 2.0)
        
        # Update each segment
        for key in ["b40", "m40", "t20"]:
            segment = households[key]
            # Update salary based on job factor & foreign worker wage impact
            factor = job_factor if key != "t20" else 1.0
            wage_factor = b40_wage_factor if key == "b40" else 1.0
            salary_suppression = brain_drain_suppression if key in ["m40", "t20"] else 1.0
            segment["salary"] = round(segment["salary_base"] * factor * wage_factor * salary_suppression, 2)
            
            # Apply OPR updates to debt service
            # B40 sensitivity = 0.2, M40 = 0.6, T20 = 0.3
            sensitivity = 0.2 if key == "b40" else (0.6 if key == "m40" else 0.3)
            base_debt = 800.0 if key == "b40" else (2500.0 if key == "m40" else 4000.0)
            segment["commitments"]["debt_service"] = round(
                calculate_debt_service(base_debt, opr, 3.00, sensitivity), 2
            )
            
        households["b40"]["str_aid"] = b40_str_monthly
        households["m40"]["str_aid"] = m40_str_monthly
        
        # EPF caruman calculations
        total_epf_contribution = sum((households[k]["salary"] * households[k]["households"] * 3 * 0.24) / 1000.0 for k in ["b40", "m40", "t20"])
        
        epf_withdrawal_inject_b40 = 0.0
        epf_withdrawal_inject_m40 = 0.0
        epf_withdrawal_amt = 0.0
        
        if epf_policy == "targeted":
            epf_withdrawal_amt = 5.0
            epf_withdrawal_inject_b40 = 3.0 / (households["b40"]["households"] * 3) * 1000.0
            epf_withdrawal_inject_m40 = 2.0 / (households["m40"]["households"] * 3) * 1000.0
        elif epf_policy == "unrestricted":
            epf_withdrawal_amt = 12.0
            epf_withdrawal_inject_b40 = 7.0 / (households["b40"]["households"] * 3) * 1000.0
            epf_withdrawal_inject_m40 = 5.0 / (households["m40"]["households"] * 3) * 1000.0
            
        epf_pool = max(0.0, prev_metrics.get("epf_pool", 750.0) + total_epf_contribution - epf_withdrawal_amt)
        
        # Calculate Household Income, commitments & consumption in RM Billion (Quarterly)
        # formula: Monthly (RM) * households (Million) * 3 (months) / 1000.0
        segment_consumption = {}
        total_consumption = 0.0
        
        for key in ["b40", "m40", "t20"]:
            segment = households[key]
            n_households = segment["households"]
            
            withdrawal_inject = epf_withdrawal_inject_b40 if key == "b40" else (epf_withdrawal_inject_m40 if key == "m40" else 0.0)
            monthly_income = segment["salary"] + segment["str_aid"] + withdrawal_inject
            q_gross_income = (monthly_income * n_households * 3) / 1000.0
            
            # personal income tax
            tax_rate = 0.0 if key == "b40" else (0.04 if key == "m40" else 0.16)
            personal_tax = q_gross_income * tax_rate
            
            q_commitments = ((segment["commitments"]["utilities"] + segment["commitments"]["debt_service"]) * n_households * 3) / 1000.0
            
            disposable_income = q_gross_income - personal_tax - q_commitments
            consumption = calculate_consumption(disposable_income, segment["mpc"])
            
            segment_consumption[key] = consumption
            total_consumption += consumption
            
            # Update savings
            savings_change = disposable_income - consumption
            segment["savings"] = round(max(0.0, segment["savings"] + savings_change), 2)
            
        # 8. SME/PKS Segment Calculations
        # SME revenue driven by consumption, development projects, exports
        sme_revenue = (total_consumption * 2.5 * 0.45) + 12.0 + (dev_exp * 0.35)
        # SME loan payments affected by OPR (sensitivity = 0.5, base = 20B)
        sme_loan_payment = calculate_debt_service(20.0, opr, 3.00, 0.5)
        # SME costs = Wages (approx 45 Billion * labor policy cost factor) + Utilities (5 Billion) + Loan payments
        sme_costs = (45.0 * labor_cost_factor) + 5.0 + sme_loan_payment
        sme_profit = max(-10.0, sme_revenue - sme_costs)
        
        self.state["sme"] = {
            "revenue": round(sme_revenue, 2),
            "loan_payment": round(sme_loan_payment, 2),
            "profit": round(sme_profit, 2)
        }
        
        # 9. Government Balance Sheet
        # STR aid cost in RM Billion (Quarterly)
        b40_str_cost = (b40_str_monthly * households["b40"]["households"] * 3) / 1000.0
        m40_str_cost = (m40_str_monthly * households["m40"]["households"] * 3) / 1000.0
        total_str_cost = b40_str_cost + m40_str_cost
        
        # Taxes collected (GST vs SST)
        if tax_regime == "gst":
            sst_revenue = 0.0
            tax_reg_rev = (total_consumption * 2.5) * 0.90 * 0.06  # 6% GST applied to 90% consumption
        else:
            sst_revenue = (total_consumption * 2.5) * 0.40 * sst_rate  # SST applied to 40% consumption
            tax_reg_rev = sst_revenue
            
        corp_tax_revenue = max(0.0, sme_profit * corp_tax_rate) + 20.0  # 20B base from large corps
        
        # Personal tax collection
        personal_tax_rev = 0.0
        for key in ["b40", "m40", "t20"]:
            segment = households[key]
            rate = 0.0 if key == "b40" else (0.04 if key == "m40" else 0.16)
            personal_tax_rev += ((segment["salary"] + segment["str_aid"]) * segment["households"] * 3 / 1000.0) * rate
            
        total_tax_revenue = tax_reg_rev + corp_tax_revenue + (personal_tax_rev * 2.0) + 38.0  # 38.0B other state income
        
        # Government expenditure
        total_govt_spending = operating_exp + dev_exp + total_str_cost
        fiscal_deficit = total_tax_revenue - total_govt_spending
        
        self.state["government"] = {
            "tax_revenue": round(total_tax_revenue, 2),
            "operating_exp": round(operating_exp, 2),
            "dev_exp": round(dev_exp, 2),
            "subsidy_policy": subsidy_policy,
            "tax_regime": tax_regime,
            "epf_withdrawal_policy": epf_policy,
            "exchange_rate_policy": ex_rate_policy,
            "east_malaysia_allocation": east_malaysia_allocation
        }
        
        # 10. Macroeconomic Aggregate Indicators
        # Calculate FDI & DDI (Foreign & Domestic Investment)
        fdi = max(2.0, 15.0 * (1.0 - 1.5 * (corp_tax_rate - 0.24) - 0.2 * abs(myr_usd - 4.40)))
        
        # DDI is driven by EPF pool size factor (baseline pool 750)
        epf_factor = epf_pool / 750.0
        
        # Apply direct capital reduction penalty to DDI from EPF withdrawals
        epf_withdrawal_penalty = 1.0
        if epf_policy == "targeted":
            epf_withdrawal_penalty = 0.85
        elif epf_policy == "unrestricted":
            epf_withdrawal_penalty = 0.70
            
        ddi = max(5.0, 25.0 * (1.0 - 0.05 * (opr - 3.00) + 0.1 * (sme_profit - 15.0)) * epf_factor * epf_withdrawal_penalty)
        
        # Investment (OPR-sensitive base + Corporate Profit multiplier)
        investment = (ddi + fdi) * 2.5 + max(0.0, sme_profit * 0.25)
        
        # Tourism Revenue calculation
        tourism_revenue = 10.0 * (1.0 + 0.15 * (myr_usd - 4.40) - (0.05 if labor_policy == "strict" else 0.0))
        
        # Net exports (sensitive to exchange rate)
        ex_factor = (myr_usd - 4.40)
        exports = 110.0 * (1.0 + 0.15 * ex_factor) + (brent_crude - 80.0) * 0.3 + tourism_revenue
        imports = 95.0 * (1.0 - 0.10 * ex_factor)
        net_exports = exports - imports
        
        # Regional development effective multiplier
        # EM infrastructure allocation has a 0.8x multiplier, West Malaysia has 1.2x multiplier
        dev_exp_effective = (dev_exp - east_malaysia_allocation) * 1.2 + (east_malaysia_allocation * 0.8)
        
        # GDP expenditure formula
        gdp = (total_consumption * 2.5) + investment + (operating_exp + dev_exp_effective) + net_exports
        
        # GDP Growth Rate
        prev_gdp = prev_metrics["gdp"]
        gdp_growth = ((gdp - prev_gdp) / prev_gdp) * 4.0 * 100.0  # Annualized quarterly growth
        
        # Inflation CPI
        prev_consumption = sum(current_snapshot["households"][k]["salary"] * current_snapshot["households"][k]["households"] * 3 / 1000.0 for k in ["b40", "m40", "t20"])
        consumption_growth = (total_consumption - prev_consumption) / prev_gdp if prev_gdp > 0 else 0.02
        
        cpi = calculate_inflation(
            consumption_growth, 
            myr_change, 
            subsidy_policy, 
            prev_govt["subsidy_policy"]
        )
        
        # Apply GST one-off implementation/rollback inflation shocks
        if prev_govt.get("tax_regime", "sst") == "sst" and tax_regime == "gst":
            cpi += 2.0
        elif prev_govt.get("tax_regime", "sst") == "gst" and tax_regime == "sst":
            cpi -= 1.0
            
        # East Malaysia Poverty adjustment
        em_poverty_change = -0.3 * (east_malaysia_allocation - 4.0) - 0.2
        east_malaysia_poverty = clamp(prev_metrics.get("east_malaysia_poverty", 14.5) + em_poverty_change, 2.0, 25.0)
        
        # National Debt
        national_debt = prev_metrics["national_debt"] - fiscal_deficit
        debt_to_gdp = (national_debt / (gdp * 4.0)) * 100.0
        
        # 11. Public Satisfaction Index calculation
        # Base starts at previous value
        satisfaction = prev_metrics["public_satisfaction"]
        
        # Negative factors
        if cpi > 3.0:
            satisfaction -= (cpi - 3.0) * 2.5  # high inflation drops satisfaction
        if unemployment > 3.5:
            satisfaction -= (unemployment - 3.5) * 4.0  # job losses drop satisfaction
        if sst_rate > 0.06 and tax_regime == "sst":
            satisfaction -= (sst_rate - 0.06) * 150.0  # higher tax rates drops satisfaction
            
        # Positive factors
        if gdp_growth > 4.5:
            satisfaction += (gdp_growth - 4.5) * 1.5
        if subsidy_policy == "blanket":
            satisfaction += 1.0  # people prefer blanket subsidies
        else:
            satisfaction -= 2.0  # fuel subsidy cut backlash
            
        # Direct STR aid boost
        if total_str_cost > 3.0:
            satisfaction += (total_str_cost - 3.0) * 0.5
            
        # GST tax regime backlash
        if tax_regime == "gst":
            satisfaction -= 8.0
            
        # EPF withdrawal boost
        if epf_policy == "targeted":
            satisfaction += 4.0
        elif epf_policy == "unrestricted":
            satisfaction += 10.0
            
        # Reserves insecurity check
        if foreign_reserves < 30.0:
            satisfaction -= (30.0 - foreign_reserves) * 0.5
            
        satisfaction = clamp(satisfaction, 0.0, 100.0)
        
        # 11.2 Poverty Rate Calculation
        pli = 2584.0 * (cpi / 2.5)  # Poverty Line Income adjusted for inflation
        b40_income = households["b40"]["salary"] + households["b40"]["str_aid"]
        poverty_rate = 5.6 + ((pli - b40_income) / 100.0) * 0.5 + (unemployment - 3.5) * 0.8
        poverty_rate = clamp(poverty_rate, 1.5, 25.0)

        # 11.3 Sectoral Health Indices
        # Family Health (penalized by EPF withdrawals)
        avg_dsr = ((households["b40"]["commitments"]["debt_service"] / households["b40"]["salary"]) + 
                   (households["m40"]["commitments"]["debt_service"] / households["m40"]["salary"])) / 2.0
        epf_penalty = 15.0 if epf_policy == "unrestricted" else (7.0 if epf_policy == "targeted" else 0.0)
        family_health = 100.0 - (avg_dsr * 150.0) - (poverty_rate * 2.0) + (households["m40"]["savings"] * 0.2) - epf_penalty
        family_health = clamp(family_health, 0.0, 100.0)

        # SME Health
        sme_health = 50.0 + (sme_profit / sme_revenue) * 100.0 - (opr - 3.00) * 10.0
        if labor_policy == "loose":
            sme_health += 5.0
        elif labor_policy == "strict":
            sme_health -= 5.0
        sme_health = clamp(sme_health, 0.0, 100.0)

        # Utilities Health
        h_bills = sum(((households[k]["commitments"]["utilities"]) * households[k]["households"] * 3) / 1000.0 for k in ["b40", "m40", "t20"])
        billing_receipts = h_bills + 5.0
        utilities_health = 70.0 + (billing_receipts - 15.0) * 5.0 - (10.0 if subsidy_policy == "targeted" else 0.0)
        utilities_health = clamp(utilities_health, 0.0, 100.0)

        # Banking Health
        banking_health = 80.0 + (opr - 3.00) * 5.0 - (unemployment - 3.5) * 4.0
        banking_health = clamp(banking_health, 0.0, 100.0)

        # Government Fiscal Health
        govt_health = 100.0 - (debt_to_gdp - 55.0) * 1.5 + (fiscal_deficit / gdp) * 10.0
        govt_health = clamp(govt_health, 0.0, 100.0)
        
        # 12. Finalize State
        self.state["quarter"] += 1
        self.state["metrics"] = {
            "gdp": round(gdp, 2),
            "gdp_growth": round(gdp_growth, 2),
            "opr": round(opr, 2),
            "cpi": round(cpi, 2),
            "myr_usd": round(myr_usd, 3),
            "unemployment_rate": round(unemployment, 2),
            "public_satisfaction": round(satisfaction, 2),
            "national_debt": round(national_debt, 2),
            "debt_to_gdp": round(debt_to_gdp, 2),
            "poverty_rate": round(poverty_rate, 2),
            "fdi": round(fdi, 2),
            "ddi": round(ddi, 2),
            "family_health": round(family_health, 2),
            "sme_health": round(sme_health, 2),
            "utilities_health": round(utilities_health, 2),
            "banking_health": round(banking_health, 2),
            "govt_health": round(govt_health, 2),
            "brain_drain_index": round(brain_drain, 2),
            "east_malaysia_poverty": round(east_malaysia_poverty, 2),
            "foreign_reserves": round(foreign_reserves, 2),
            "epf_pool": round(epf_pool, 2),
            "tourism_revenue": round(tourism_revenue, 2)
        }
        
        return self.state

    def check_game_status(self) -> tuple[bool, str]:
        """
        Evaluates current metrics for game completion:
        - Win/Re-election: Every 20 quarters, checks if debt_to_gdp < 65% and satisfaction > 50%
        - Loss: Debt-to-GDP > 80%, reserves < 10B, or public satisfaction < 20%
        """
        metrics = self.state["metrics"]
        q = self.state["quarter"]
        
        if metrics["debt_to_gdp"] >= 80.0:
            return True, "DEBT_CRISIS: Malaysia's national debt-to-GDP ratio has exceeded 80%. Sovereign rating downgraded to junk. Economic default declared!"
            
        if metrics["public_satisfaction"] <= 20.0:
            return True, "CIVIL_UNREST: Public satisfaction has plummeted below 20%. Widespread protests and strikes have paralyzed the country. Government dissolved!"
            
        if metrics.get("foreign_reserves", 115.0) < 10.0:
            return True, "RESERVES_DEPLETED: Bank Negara's foreign reserves fell below USD 10 Billion. Sovereign balance sheet collapsed, causing extreme capital flight and currency default!"
            
        # Check election at the end of each 20-quarter cycle (Term)
        # e.g., Q21 (Q20 step just completed), Q41 (Q40 completed), etc.
        if q > 1 and (q - 1) % 20 == 0:
            term = (q - 1) // 20
            if metrics["debt_to_gdp"] <= 65.0 and metrics["public_satisfaction"] >= 50.0:
                self.state["external"]["election_status"] = f"RE-ELECTED! You have successfully completed Term {term} and won the general election. Citizens have granted you a mandate for Term {term + 1}!"
            else:
                return True, f"ELECTION_LOSS: You survived Term {term} (Quarters {q-20} to {q-1}), but failed to meet the election criteria (Debt-to-GDP < 65% and Public Approval > 50%). You lost the general election!"
                
        return False, "ACTIVE"

    def save_state(self, filepath: str) -> bool:
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            data = {
                "state": self.state,
                "history": self.history
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    def load_state(self, filepath: str) -> bool:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.state = data["state"]
            self.history = data["history"]
            return True
        except Exception:
            return False
