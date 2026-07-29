import json
from engine.formulas import calculate_debt_service, calculate_consumption

def step_households(
    state: dict,
    opr: float,
    labor_policy: str,
    b40_wage_factor: float,
    job_factor: float,
    brain_drain_suppression: float,
    epf_policy: str
) -> tuple[float, float]:
    """
    Transition function for the Household segment.
    Updates salaries, commitments, savings, EPF pool and returns total consumption and new EPF pool value.
    """
    households = state["households"]
    
    # 1. Update average salary based on employment & talent flight
    for key in ["b40", "m40", "t20"]:
        segment = households[key]
        factor = job_factor if key != "t20" else 1.0
        wage_factor = b40_wage_factor if key == "b40" else 1.0
        salary_suppression = brain_drain_suppression if key in ["m40", "t20"] else 1.0
        segment["salary"] = round(segment["salary_base"] * factor * wage_factor * salary_suppression, 2)
        
        # Apply OPR updates to debt service
        sensitivity = 0.2 if key == "b40" else (0.6 if key == "m40" else 0.3)
        base_debt = 800.0 if key == "b40" else (2500.0 if key == "m40" else 4000.0)
        segment["commitments"]["debt_service"] = round(
            calculate_debt_service(base_debt, opr, 3.00, sensitivity), 2
        )
        
    # 2. EPF calculations
    # Employee 11% + Employer 13% = 24% of salary
    total_epf_contribution = sum(
        (households[k]["salary"] * households[k]["households"] * 3 * 0.24) / 1000.0
        for k in ["b40", "m40", "t20"]
    )
    
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
        
    prev_epf = state["metrics"].get("epf_pool", 750.0)
    epf_pool = max(0.0, prev_epf + total_epf_contribution - epf_withdrawal_amt)
    
    # 3. Calculate Consumption & update savings
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
        
        total_consumption += consumption
        
        # Update savings
        savings_change = disposable_income - consumption
        segment["savings"] = round(max(0.0, segment["savings"] + savings_change), 2)
        
    return total_consumption, epf_pool
