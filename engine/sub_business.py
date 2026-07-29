import json
from engine.formulas import calculate_debt_service

def step_business(
    state: dict,
    total_consumption: float,
    dev_exp: float,
    opr: float,
    labor_cost_factor: float,
    diesel_regime: str
) -> tuple[float, float, float]:
    """
    Transition function for the Corporate/SME segment.
    Updates SME revenue, loan payment, profit, and unemployment rate.
    Returns (sme_revenue, sme_profit, unemployment_rate).
    """
    # SME revenue driven by consumption, development projects, exports
    sme_revenue = (total_consumption * 2.5 * 0.45) + 12.0 + (dev_exp * 0.35)
    # SME loan payments affected by OPR (sensitivity = 0.5, base = 20B)
    sme_loan_payment = calculate_debt_service(20.0, opr, 3.00, 0.5)
    
    # SME costs = Wages (approx 45 Billion * labor policy cost factor) + Utilities (5 Billion) + Loan payments
    base_operational_costs = 45.0 * labor_cost_factor
    if diesel_regime == "rationalized":
        base_operational_costs *= 1.08  # 8% operational/logistics spike
        
    sme_costs = base_operational_costs + 5.0 + sme_loan_payment
    sme_profit = max(-10.0, sme_revenue - sme_costs)
    
    state["sme"] = {
        "revenue": round(sme_revenue, 2),
        "loan_payment": round(sme_loan_payment, 2),
        "profit": round(sme_profit, 2)
    }
    
    # Unemployment impact from SME profitability
    prev_unemployment = state["metrics"]["unemployment_rate"]
    if sme_profit > 10.0:
        unemployment = max(3.0, prev_unemployment - 0.1)
    elif sme_profit < 2.0:
        unemployment = min(10.0, prev_unemployment + 0.2)
    else:
        unemployment = prev_unemployment
        
    return sme_revenue, sme_profit, unemployment
