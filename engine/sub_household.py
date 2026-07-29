import json
from engine.formulas import calculate_debt_service, calculate_consumption, clamp

def step_households(
    state: dict,
    opr: float,
    labor_policy: str,
    b40_wage_factor: float,
    job_factor: float,
    brain_drain_suppression: float,
    epf_policy: str,
    ron95_price: float,
    diesel_price: float,
    electricity_tariff: str,
    petrol_regime: str,
    m40_tax_rate: float = 0.04,
    t20_tax_rate: float = 0.16
) -> tuple[float, float]:
    """
    Transition function for the Household segment.
    Updates salaries based on Gov/Private/SME/Micro job sectors shares,
    calculates utility and petrol commitments, EPF pool, and returns total consumption.
    """
    households = state["households"]
    prev_metrics = state["metrics"]
    sme_health = prev_metrics.get("sme_health", 75.0)
    
    # 1. Sector Shares Definitions (Company Type)
    # Shares: [Gov, Private, SME, Micro SME]
    sector_shares = {
        "b40": [0.15, 0.25, 0.35, 0.25],
        "m40": [0.25, 0.45, 0.25, 0.05],
        "t20": [0.15, 0.60, 0.20, 0.05]
    }
    
    # Industrial Sector shares
    industry_shares = {
        "b40": {"services": 0.40, "manufacturing": 0.10, "agriculture": 0.30, "mining": 0.00, "construction": 0.20},
        "m40": {"services": 0.50, "manufacturing": 0.30, "agriculture": 0.00, "mining": 0.15, "construction": 0.05},
        "t20": {"services": 0.65, "manufacturing": 0.15, "agriculture": 0.05, "mining": 0.15, "construction": 0.00}
    }
    
    # Calculate industry-specific GDP multipliers relative to baseline
    prev_sectors = state.get("sectors", {})
    m_serv = prev_sectors.get("services", {}).get("gdp_contrib", 261.0) / 261.0
    m_mfg = prev_sectors.get("manufacturing", {}).get("gdp_contrib", 103.5) / 103.5
    m_agri = prev_sectors.get("agriculture", {}).get("gdp_contrib", 31.5) / 31.5
    m_mine = prev_sectors.get("mining", {}).get("gdp_contrib", 27.0) / 27.0
    m_const = prev_sectors.get("construction", {}).get("gdp_contrib", 18.0) / 18.0
    
    # OPR multiplier on Micro SMEs
    micro_opr_factor = 1.0 - 0.05 * (opr - 3.00)
    # SME health multiplier on SME & Micro SME wages
    sme_profit_factor = 0.8 + 0.2 * (sme_health / 100.0)
    
    # 2. Update Sectoral Salaries & commitments
    for key in ["b40", "m40", "t20"]:
        segment = households[key]
        base = segment["salary_base"]
        
        # Calculate salaries per sector
        w_gov = base
        
        factor = job_factor if key != "t20" else 1.0
        salary_suppression = brain_drain_suppression if key in ["m40", "t20"] else 1.0
        w_priv = base * factor * salary_suppression
        
        wage_factor = b40_wage_factor if key == "b40" else 1.0
        w_sme = base * factor * wage_factor * sme_profit_factor
        
        w_micro = base * factor * wage_factor * sme_profit_factor * micro_opr_factor
        
        c_shares = sector_shares[key]
        weighted_company_salary = (c_shares[0] * w_gov) + (c_shares[1] * w_priv) + (c_shares[2] * w_sme) + (c_shares[3] * w_micro)
        
        # Industry multiplier effect
        ind_share = industry_shares[key]
        industry_multiplier = (
            (ind_share["services"] * m_serv) +
            (ind_share["manufacturing"] * m_mfg) +
            (ind_share["agriculture"] * m_agri) +
            (ind_share["mining"] * m_mine) +
            (ind_share["construction"] * m_const)
        )
        
        segment["salary"] = round(weighted_company_salary * industry_multiplier, 2)
        
        # Apply OPR updates to debt service
        sensitivity = 0.2 if key == "b40" else (0.6 if key == "m40" else 0.3)
        base_debt = 800.0 if key == "b40" else (2500.0 if key == "m40" else 4000.0)
        segment["commitments"]["debt_service"] = round(
            calculate_debt_service(base_debt, opr, 3.00, sensitivity), 2
        )
        
        if petrol_regime == "rationalized":
            p_price = ron95_price
        elif petrol_regime == "targeted_b40":
            p_price = 2.05 if key == "b40" else (2.45 if key == "m40" else 2.85)
        else:
            p_price = 2.05
            
        fuel_litres = 60.0 if key == "b40" else (120.0 if key == "m40" else 200.0)
        segment["commitments"]["fuel"] = round(fuel_litres * p_price, 2)
        
        # Electricity / Utility calculations
        base_utils = 150.0 if key == "b40" else (400.0 if key == "m40" else 1000.0)
        if electricity_tariff == "targeted_t20":
            t_mult = 1.30 if key == "t20" else 1.00
        elif electricity_tariff == "market_rate":
            t_mult = 1.50 if key == "t20" else 1.25
        else:
            t_mult = 1.00
            
        segment["commitments"]["utilities"] = round(base_utils * t_mult, 2)
        
    # 3. EPF calculations
    total_epf_contribution = sum(
        (households[k]["salary"] * households[k]["households"] * 3 * 0.24) / 1000.0
        for k in ["b40", "m40", "t20"]
    )
    
    epf_withdrawal_inject_b40 = 0.0
    epf_withdrawal_inject_m40 = 0.0
    epf_withdrawal_amt = 0.0
    
    # EPF policy is read from parameters
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
    
    # 4. Calculate Consumption & update savings
    total_consumption = 0.0
    
    for key in ["b40", "m40", "t20"]:
        segment = households[key]
        n_households = segment["households"]
        
        withdrawal_inject = epf_withdrawal_inject_b40 if key == "b40" else (epf_withdrawal_inject_m40 if key == "m40" else 0.0)
        monthly_income = segment["salary"] + segment["str_aid"] + withdrawal_inject
        q_gross_income = (monthly_income * n_households * 3) / 1000.0
        
        # personal income tax
        tax_rate = 0.0 if key == "b40" else (m40_tax_rate if key == "m40" else t20_tax_rate)
        personal_tax = q_gross_income * tax_rate
        
        # Total commitments include: utilities + debt_service + fuel
        monthly_commitments = segment["commitments"]["utilities"] + segment["commitments"]["debt_service"] + segment["commitments"].get("fuel", 0.0)
        q_commitments = (monthly_commitments * n_households * 3) / 1000.0
        
        disposable_income = q_gross_income - personal_tax - q_commitments
        consumption = calculate_consumption(disposable_income, segment["mpc"])
        
        total_consumption += consumption
        
        # Update savings
        savings_change = disposable_income - consumption
        segment["savings"] = round(max(0.0, segment["savings"] + savings_change), 2)
        
    return total_consumption, epf_pool
