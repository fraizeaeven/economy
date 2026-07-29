import os
import json
from engine.formulas import clamp
from engine.sub_household import step_households
from engine.sub_business import step_business
from engine.sub_finance import step_finance
from engine.sub_government import step_government

class EconomyEngine:
    """
    Central Orchestrator of the Malaysian Economy Text Simulator (METS).
    Initializes the state structure, coordinates sequential execution of sub-engines,
    handles state archiving (history), checking game state, saving, and loading.
    """
    def __init__(self):
        self.state = self.get_default_state()
        self.history = []

    def get_default_state(self) -> dict:
        """
        Builds the baseline Q1 state dictionary.
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
                "tourism_revenue": 10.0,    # Quarterly Tourism export earnings (RM Billion)
                "ron95_price": 2.05,        # Retail petrol price (RM/Litre)
                "diesel_price": 2.15,       # Retail diesel price (RM/Litre)
                "gini": 0.390               # Income inequality index (Gini Coefficient)
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
                "east_malaysia_allocation": 4.0, # RM Billion
                "petrol_subsidy_regime": "blanket", # "blanket", "targeted_b40", "rationalized"
                "diesel_subsidy_regime": "blanket", # "blanket", "targeted_fleet", "rationalized"
                "electricity_tariff_policy": "subsidized" # "subsidized", "targeted_t20", "market_rate"
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
            },
            "sectors": {
                "services": {
                    "gdp_contrib": 270.0,       # RM Billion (60% of GDP)
                    "exports": 20.0,
                    "imports": 15.0,
                    "growth_rate": 4.5
                },
                "manufacturing": {
                    "gdp_contrib": 103.5,       # RM Billion (23% of GDP)
                    "exports": 90.0,
                    "imports": 75.0,
                    "growth_rate": 3.8
                },
                "agriculture": {
                    "gdp_contrib": 31.5,        # RM Billion (7% of GDP)
                    "exports": 15.0,
                    "imports": 22.0,
                    "growth_rate": 1.2
                },
                "mining": {
                    "gdp_contrib": 27.0,        # RM Billion (6% of GDP)
                    "exports": 25.0,
                    "imports": 10.0,
                    "growth_rate": -0.5
                },
                "construction": {
                    "gdp_contrib": 18.0,        # RM Billion (4% of GDP)
                    "exports": 2.0,
                    "imports": 5.0,
                    "growth_rate": 2.5
                }
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
        
        petrol_regime = policies.get("petrol_subsidy_regime", prev_govt.get("petrol_subsidy_regime", "blanket"))
        if petrol_regime not in ["blanket", "targeted_b40", "rationalized"]:
            petrol_regime = "blanket"
            
        diesel_regime = policies.get("diesel_subsidy_regime", prev_govt.get("diesel_subsidy_regime", "blanket"))
        if diesel_regime not in ["blanket", "targeted_fleet", "rationalized"]:
            diesel_regime = "blanket"
            
        electricity_tariff = policies.get("electricity_tariff_policy", prev_govt.get("electricity_tariff_policy", "subsidized"))
        if electricity_tariff not in ["subsidized", "targeted_t20", "market_rate"]:
            electricity_tariff = "subsidized"
            
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
        
        # Calculate RON95 and Diesel prices
        brent_crude = self.state["external"]["brent_crude"]
        if petrol_regime == "rationalized":
            ron95_price = 2.05 + 0.02 * (brent_crude - 80.0)
        else:
            ron95_price = 2.05
            
        if diesel_regime == "rationalized":
            diesel_price = 3.35
        elif diesel_regime == "targeted_fleet":
            diesel_price = 3.35  # retail price is 3.35, fleet card is 2.15
        else:
            diesel_price = 2.15
            
        self.state["metrics"]["ron95_price"] = round(ron95_price, 2)
        self.state["metrics"]["diesel_price"] = round(diesel_price, 2)
        
        # 3. Apply Government Subsidy Policy Shifts
        operating_exp = 75.0
        b40_str_monthly = 150.0
        m40_str_monthly = 0.0
        
        if subsidy_policy == "targeted":
            operating_exp = 60.0  # saving 15 Billion OPEX
            b40_str_monthly = 280.0  # higher direct financial aid
            m40_str_monthly = 80.0
            
        # 4. Exchange Rate and Unemployment parameters
        prev_myr = prev_metrics["myr_usd"]
        unemployment = prev_metrics["unemployment_rate"]
        job_factor = 1.0 - ((unemployment - 3.5) / 100.0 * 2.0)
        
        # Talent flight brain drain factor (pre-computed based on previous state satisfaction)
        prev_satisfaction = prev_metrics["public_satisfaction"]
        
        # Estimate brain drain index beforehand (or use the one matching final exchange rate)
        # To avoid circularity, we calculate exchange rate first.
        brent_crude = self.state["external"]["brent_crude"]
        fed_rate = self.state["external"]["fed_rate"]
        
        # 5. Call Finance sub-engine to compute FX and Investments
        # We need temporary variables from step_finance
        (
            myr_usd,
            myr_change,
            foreign_reserves,
            brain_drain,
            brain_drain_suppression,
            fdi,
            ddi,
            investment,
            tourism_revenue,
            banking_health
        ) = step_finance(
            self.state,
            opr,
            fed_rate,
            brent_crude,
            ex_rate_policy,
            tax_regime,
            self.state["sme"]["profit"],
            prev_metrics.get("epf_pool", 750.0),
            epf_policy,
            corp_tax_rate,
            labor_policy,
            unemployment
        )
        
        # 6. Call Household sub-engine to update salaries, commitments and get total consumption
        self.state["households"]["b40"]["str_aid"] = b40_str_monthly
        self.state["households"]["m40"]["str_aid"] = m40_str_monthly
        
        total_consumption, epf_pool = step_households(
            self.state,
            opr,
            labor_policy,
            b40_wage_factor,
            job_factor,
            brain_drain_suppression,
            epf_policy,
            ron95_price,
            diesel_price,
            electricity_tariff,
            petrol_regime
        )
        
        # 7. Call Business sub-engine to update corporate earnings & unemployment
        sme_revenue, sme_profit, next_unemployment = step_business(
            self.state,
            total_consumption,
            dev_exp,
            opr,
            labor_cost_factor,
            diesel_regime
        )
        
        # Recalculate finance parameters if they depend on the newly computed sme_profit
        # (This resolves the step ordering feedback loops cleanly)
        (
            myr_usd,
            myr_change,
            foreign_reserves,
            brain_drain,
            brain_drain_suppression,
            fdi,
            ddi,
            investment,
            tourism_revenue,
            banking_health
        ) = step_finance(
            self.state,
            opr,
            fed_rate,
            brent_crude,
            ex_rate_policy,
            tax_regime,
            sme_profit,
            epf_pool,
            epf_policy,
            corp_tax_rate,
            labor_policy,
            next_unemployment
        )
        
        # 8. Call Government sub-engine for taxes, regional gap and national indicators
        prev_gdp = prev_metrics["gdp"]
        (
            gdp,
            gdp_growth,
            cpi,
            national_debt,
            debt_to_gdp,
            satisfaction,
            poverty_rate,
            family_health,
            sme_health,
            utilities_health,
            govt_health,
            east_malaysia_poverty,
            gini
        ) = step_government(
            self.state,
            total_consumption,
            myr_change,
            current_snapshot,
            prev_gdp,
            fdi,
            ddi,
            investment,
            tourism_revenue,
            myr_usd,
            next_unemployment,
            sme_profit,
            sme_revenue,
            foreign_reserves,
            epf_pool,
            
            sst_rate,
            corp_tax_rate,
            subsidy_policy,
            dev_exp,
            tax_regime,
            epf_policy,
            ex_rate_policy,
            east_malaysia_allocation,
            labor_policy,
            
            operating_exp,
            b40_str_monthly,
            m40_str_monthly,
            
            petrol_regime,
            diesel_regime,
            electricity_tariff
        )
        
        # 9. Finalize state variables
        self.state["quarter"] += 1
        self.state["metrics"] = {
            "gdp": round(gdp, 2),
            "gdp_growth": round(gdp_growth, 2),
            "opr": round(opr, 2),
            "cpi": round(cpi, 2),
            "myr_usd": round(myr_usd, 3),
            "unemployment_rate": round(next_unemployment, 2),
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
            "tourism_revenue": round(tourism_revenue, 2),
            "ron95_price": round(ron95_price, 2),
            "diesel_price": round(diesel_price, 2),
            "gini": round(gini, 3)
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
            if metrics["debt_to_gdp"] <= 75.0 and metrics["public_satisfaction"] >= 50.0:
                self.state["external"]["election_status"] = f"RE-ELECTED! You have successfully completed Term {term} and won the general election. Citizens have granted you a mandate for Term {term + 1}!"
            else:
                return True, f"ELECTION_LOSS: You survived Term {term} (Quarters {q-20} to {q-1}), but failed to meet the election criteria (Debt-to-GDP < 75% and Public Approval > 50%). You lost the general election!"
                
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

    def forecast_metrics(self) -> dict:
        """
        Fits a linear regression model y = mx + c to the history of:
        - gdp
        - debt_to_gdp
        - public_satisfaction
        - cpi
        
        Returns a dictionary containing the m, c coefficients, equations,
        and predictions for the next 4 quarters.
        """
        temp_history = list(self.history)
        # Always include the current state as the final data point
        temp_history.append({
            "quarter": self.state["quarter"],
            "metrics": dict(self.state["metrics"])
        })
        
        N = len(temp_history)
        x = [q["quarter"] for q in temp_history]
        
        results = {}
        target_keys = ["gdp", "debt_to_gdp", "public_satisfaction", "cpi"]
        
        for key in target_keys:
            y = [q["metrics"][key] for q in temp_history]
            
            # Simple linear regression formula
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xx = sum(xi * xi for xi in x)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            
            denominator = (N * sum_xx - sum_x * sum_x)
            if abs(denominator) < 1e-6:
                m = 0.0
                c = sum_y / N
            else:
                m = (N * sum_xy - sum_x * sum_y) / denominator
                c = (sum_y - m * sum_x) / N
                
            # Forecast next 4 quarters
            current_q = self.state["quarter"]
            forecasts = []
            for i in range(1, 5):
                proj_q = current_q + i
                val = m * proj_q + c
                if key == "public_satisfaction":
                    val = max(0.0, min(100.0, val))
                elif key == "cpi":
                    val = max(-5.0, val)
                forecasts.append((proj_q, round(val, 2)))
                
            results[key] = {
                "m": round(m, 4),
                "c": round(c, 4),
                "equation": f"y = {m:.4f}x + {c:.4f}",
                "forecasts": forecasts
            }
            
        return results
