import json
from engine.formulas import calculate_inflation, clamp

def step_government(
    state: dict,
    total_consumption: float,
    myr_change: float,
    current_snapshot: dict,
    prev_gdp: float,
    fdi: float,
    ddi: float,
    investment: float,
    tourism_revenue: float,
    myr_usd: float,
    unemployment: float,
    sme_profit: float,
    sme_revenue: float,
    foreign_reserves: float,
    epf_pool: float,
    
    # Policy variables
    sst_rate: float,
    corp_tax_rate: float,
    subsidy_policy: str,
    dev_exp: float,
    tax_regime: str,
    epf_policy: str,
    ex_rate_policy: str,
    east_malaysia_allocation: float,
    labor_policy: str,
    
    # OPEX & STR
    operating_exp: float,
    b40_str_monthly: float,
    m40_str_monthly: float,
    
    # New Fuel and Electricity Regimes
    petrol_regime: str,
    diesel_regime: str,
    electricity_tariff: str
) -> tuple[float, float, float, float, float, float, float, float, float, float, float, float]:
    """
    Transition function for the Government / Fiscal & Social segment.
    Updates government spending, tax revenue, East Malaysia poverty, CPI, satisfaction, poverty rate, health indexes.
    Returns (gdp, gdp_growth, cpi, national_debt, debt_to_gdp, satisfaction, poverty_rate, family_health, sme_health, utilities_health, govt_health, east_malaysia_poverty).
    """
    households = state["households"]
    prev_metrics = current_snapshot["metrics"]
    prev_govt = current_snapshot["government"]
    
    # 1. STR cost allocation
    b40_str_cost = (b40_str_monthly * households["b40"]["households"] * 3) / 1000.0
    m40_str_cost = (m40_str_monthly * households["m40"]["households"] * 3) / 1000.0
    total_str_cost = b40_str_cost + m40_str_cost
    
    # 2. Fuel Subsidy Cost & Savings
    # Baseline opex of 75.0/60.0 includes 5.5B blanket fuel subsidies (4.0B RON95, 1.5B Diesel)
    petrol_bill = 4.0 if petrol_regime == "blanket" else (1.5 if petrol_regime == "targeted_b40" else 0.0)
    diesel_bill = 1.5 if diesel_regime == "blanket" else (0.5 if diesel_regime == "targeted_fleet" else 0.0)
    
    actual_fuel_cost = petrol_bill + diesel_bill
    opex_savings = 5.5 - actual_fuel_cost
    
    # Adjusted operating expenditure
    effective_operating_exp = max(30.0, operating_exp - opex_savings)
    
    # 3. Taxes collected (GST vs SST)
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
    
    # Government spending
    total_govt_spending = effective_operating_exp + dev_exp + total_str_cost
    fiscal_deficit = total_tax_revenue - total_govt_spending
    
    state["government"] = {
        "tax_revenue": round(total_tax_revenue, 2),
        "operating_exp": round(effective_operating_exp, 2),
        "dev_exp": round(dev_exp, 2),
        "subsidy_policy": subsidy_policy,
        "tax_regime": tax_regime,
        "epf_withdrawal_policy": epf_policy,
        "exchange_rate_policy": ex_rate_policy,
        "east_malaysia_allocation": east_malaysia_allocation,
        "petrol_subsidy_regime": petrol_regime,
        "diesel_subsidy_regime": diesel_regime,
        "electricity_tariff_policy": electricity_tariff
    }
    
    # 4. Regional development effective multiplier
    dev_exp_effective = (dev_exp - east_malaysia_allocation) * 1.2 + (east_malaysia_allocation * 0.8)
    
    # 5. Dynamic Industry Sectors (GDP, Exports, Imports)
    ex_factor = (myr_usd - 4.40)
    prev_sectors = current_snapshot.get("sectors", {})
    
    # 5.1 Services (Wholesale, Retail, Financials, Tourism)
    consumption_ratio = (total_consumption * 2.5) / 200.0
    tourism_ratio = tourism_revenue / 10.0
    serv_gdp = 270.0 * (0.90 * consumption_ratio + 0.10 * tourism_ratio)
    serv_exports = 20.0 * (0.50 * (1.0 + 0.10 * ex_factor) + 0.50 * tourism_ratio)
    serv_imports = 15.0 * (1.0 - 0.05 * ex_factor)
    
    # 5.2 Manufacturing (E&E, Semiconductors, Petrochemicals)
    mfg_gdp = 103.5 * (0.50 * (fdi / 15.0) + 0.50 * (1.0 + 0.15 * ex_factor))
    mfg_exports = 90.0 * (0.50 * (fdi / 15.0) + 0.50 * (1.0 + 0.20 * ex_factor))
    mfg_imports = 75.0 * (0.50 * (fdi / 15.0) + 0.50 * (1.0 - 0.10 * ex_factor))
    
    # 5.3 Agriculture & Commodities (Palm Oil, Rubber, smallholders)
    agri_mult = 1.05 if labor_policy == "loose" else (0.92 if labor_policy == "strict" else 1.0)
    agri_gdp = 31.5 * (1.0 + 0.04 * (state["external"]["brent_crude"] - 80.0) / 80.0) * agri_mult
    agri_exports = 15.0 * (1.0 + 0.08 * (state["external"]["brent_crude"] - 80.0) / 80.0) * agri_mult
    agri_imports = 22.0 * (1.0 - 0.05 * ex_factor)
    
    # 5.4 Mining & Petroleum (PETRONAS crude extraction, LNG)
    mine_gdp = 27.0 * (state["external"]["brent_crude"] / 80.0)
    mine_exports = 25.0 * (state["external"]["brent_crude"] / 80.0)
    mine_imports = 10.0 * (1.0 - 0.05 * ex_factor)
    
    # 5.5 Construction (DeveX infrastructure, property development)
    const_gdp = 18.0 * (dev_exp_effective / 22.0)
    const_exports = 2.0 * (dev_exp_effective / 22.0)
    const_imports = 5.0 * (dev_exp_effective / 22.0) * (1.0 - 0.05 * ex_factor)
    
    # Save sector snapshot details
    state["sectors"] = {
        "services": {
            "gdp_contrib": round(serv_gdp, 2),
            "exports": round(serv_exports, 2),
            "imports": round(serv_imports, 2),
            "growth_rate": round(((serv_gdp - prev_sectors.get("services", {}).get("gdp_contrib", 261.0)) / prev_sectors.get("services", {}).get("gdp_contrib", 261.0)) * 4.0 * 100.0, 2)
        },
        "manufacturing": {
            "gdp_contrib": round(mfg_gdp, 2),
            "exports": round(mfg_exports, 2),
            "imports": round(mfg_imports, 2),
            "growth_rate": round(((mfg_gdp - prev_sectors.get("manufacturing", {}).get("gdp_contrib", 103.5)) / prev_sectors.get("manufacturing", {}).get("gdp_contrib", 103.5)) * 4.0 * 100.0, 2)
        },
        "agriculture": {
            "gdp_contrib": round(agri_gdp, 2),
            "exports": round(agri_exports, 2),
            "imports": round(agri_imports, 2),
            "growth_rate": round(((agri_gdp - prev_sectors.get("agriculture", {}).get("gdp_contrib", 31.5)) / prev_sectors.get("agriculture", {}).get("gdp_contrib", 31.5)) * 4.0 * 100.0, 2)
        },
        "mining": {
            "gdp_contrib": round(mine_gdp, 2),
            "exports": round(mine_exports, 2),
            "imports": round(mine_imports, 2),
            "growth_rate": round(((mine_gdp - prev_sectors.get("mining", {}).get("gdp_contrib", 27.0)) / prev_sectors.get("mining", {}).get("gdp_contrib", 27.0)) * 4.0 * 100.0, 2)
        },
        "construction": {
            "gdp_contrib": round(const_gdp, 2),
            "exports": round(const_exports, 2),
            "imports": round(const_imports, 2),
            "growth_rate": round(((const_gdp - prev_sectors.get("construction", {}).get("gdp_contrib", 18.0)) / prev_sectors.get("construction", {}).get("gdp_contrib", 18.0)) * 4.0 * 100.0, 2)
        }
    }
    
    # 6. Aggregate GDP expenditure & Trade Balance
    gdp = serv_gdp + mfg_gdp + agri_gdp + mine_gdp + const_gdp
    exports = serv_exports + mfg_exports + agri_exports + mine_exports + const_exports
    imports = serv_imports + mfg_imports + agri_imports + mine_imports + const_imports
    net_exports = exports - imports
    
    # GDP Growth Rate
    gdp_growth = ((gdp - prev_gdp) / prev_gdp) * 4.0 * 100.0  # Annualized quarterly growth
    
    # Inflation CPI (DOSM Weighted Basket)
    # CPI = 0.30*Food + 0.15*Transport + 0.23*Utility + 0.32*Core
    cpi_base = 1.5 + myr_change * 4.0
    
    prev_consumption = sum(current_snapshot["households"][k]["salary"] * current_snapshot["households"][k]["households"] * 3 / 1000.0 for k in ["b40", "m40", "t20"])
    consumption_growth = (total_consumption - prev_consumption) / prev_gdp if prev_gdp > 0 else 0.02
    
    # 1. Food: driven by consumption growth and labor tightness
    food_inf = cpi_base + consumption_growth * 1.5
    if labor_policy == "strict":
        food_inf += 0.5
        
    # 2. Transport: driven by Petrol (RON95) and Diesel prices
    ron95_mult = state["metrics"].get("ron95_price", 2.05) / 2.05
    diesel_mult = state["metrics"].get("diesel_price", 2.15) / 2.15
    transport_inf = cpi_base + (ron95_mult - 1.0) * 15.0 + (diesel_mult - 1.0) * 5.0
    
    # 3. Housing & Utilities: driven by tariff policy and interest rates (OPR)
    util_inf = cpi_base + 0.10 * (state["metrics"]["opr"] - 3.00)
    if electricity_tariff == "market_rate":
        util_inf += 4.0
    elif electricity_tariff == "targeted_t20":
        util_inf += 1.5
        
    # 4. Core goods: driven by consumption growth and GST tax shocks
    core_inf = cpi_base + consumption_growth * 2.0
    if tax_regime == "gst":
        core_inf += 1.5
        
    cpi = 0.30 * food_inf + 0.15 * transport_inf + 0.23 * util_inf + 0.32 * core_inf
    
    # One-off policy adjustment spikes
    if prev_govt.get("tax_regime", "sst") == "sst" and tax_regime == "gst":
        cpi += 2.0
    elif prev_govt.get("tax_regime", "sst") == "gst" and tax_regime == "sst":
        cpi -= 1.0
        
    if prev_govt.get("petrol_subsidy_regime", "blanket") != "rationalized" and petrol_regime == "rationalized":
        cpi += 1.2
        
    if prev_govt.get("diesel_subsidy_regime", "blanket") != "rationalized" and diesel_regime == "rationalized":
        cpi += 0.8
        
    cpi = max(-2.0, cpi)
    
    # Gini Coefficient Calculation (DOSM Inequality Metric)
    inc_b40 = (households["b40"]["salary"] + households["b40"]["str_aid"]) * households["b40"]["households"]
    inc_m40 = (households["m40"]["salary"] + households["m40"]["str_aid"]) * households["m40"]["households"]
    inc_t20 = (households["t20"]["salary"] + households["t20"]["str_aid"]) * households["t20"]["households"]
    inc_total = inc_b40 + inc_m40 + inc_t20
    
    s1 = inc_b40 / inc_total if inc_total > 0 else 0.18
    s2 = (inc_b40 + inc_m40) / inc_total if inc_total > 0 else 0.55
    gini = 1.0 - (0.80 * s1 + 0.60 * s2 + 0.20)
    
    # East Malaysia Poverty adjustment
    em_poverty_change = -0.3 * (east_malaysia_allocation - 4.0) - 0.2
    east_malaysia_poverty = clamp(prev_metrics.get("east_malaysia_poverty", 14.5) + em_poverty_change, 2.0, 25.0)
    
    # National Debt
    national_debt = prev_metrics["national_debt"] - fiscal_deficit
    debt_to_gdp = (national_debt / (gdp * 4.0)) * 100.0
    
    # 7. Public Satisfaction Index calculation
    satisfaction = prev_metrics["public_satisfaction"]
    
    # Negative factors
    if cpi > 3.0:
        satisfaction -= (cpi - 3.0) * 2.5
    if unemployment > 3.5:
        satisfaction -= (unemployment - 3.5) * 4.0
    if sst_rate > 0.06 and tax_regime == "sst":
        satisfaction -= (sst_rate - 0.06) * 150.0
        
    # Positive factors
    if gdp_growth > 4.5:
        satisfaction += (gdp_growth - 4.5) * 1.5
    if subsidy_policy == "blanket":
        satisfaction += 1.0
    else:
        satisfaction -= 2.0
        
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
        
    # Petrol & Diesel subsidy removal backlash
    if petrol_regime == "rationalized":
        satisfaction -= 5.0
    elif petrol_regime == "targeted_b40":
        satisfaction -= 2.0
        
    if diesel_regime == "rationalized":
        satisfaction -= 3.0
        
    # Electricity price hike backlash
    if electricity_tariff == "market_rate":
        satisfaction -= 4.0
        
    # Gini backlash
    satisfaction -= (gini - 0.390) * 100.0
    
    # Reserves insecurity check
    if foreign_reserves < 30.0:
        satisfaction -= (30.0 - foreign_reserves) * 0.5
        
    satisfaction = clamp(satisfaction, 0.0, 100.0)
    
    # Poverty Line Income adjusted for inflation
    pli = 2584.0 * (cpi / 2.5)
    b40_income = households["b40"]["salary"] + households["b40"]["str_aid"]
    poverty_rate = 5.6 + ((pli - b40_income) / 100.0) * 0.5 + (unemployment - 3.5) * 0.8
    poverty_rate = clamp(poverty_rate, 1.5, 25.0)
    
    # Sectoral Health Indices
    avg_dsr = ((households["b40"]["commitments"]["debt_service"] / households["b40"]["salary"]) + 
               (households["m40"]["commitments"]["debt_service"] / households["m40"]["salary"])) / 2.0
    epf_penalty = 15.0 if epf_policy == "unrestricted" else (7.0 if epf_policy == "targeted" else 0.0)
    family_health = 100.0 - (avg_dsr * 150.0) - (poverty_rate * 2.0) + (households["m40"]["savings"] * 0.2) - epf_penalty
    family_health = clamp(family_health, 0.0, 100.0)
    
    sme_health = 50.0 + (sme_profit / sme_revenue) * 100.0 - (state["metrics"]["opr"] - 3.00) * 10.0
    if labor_policy == "loose":
        sme_health += 5.0
    elif labor_policy == "strict":
        sme_health -= 5.0
    sme_health = clamp(sme_health, 0.0, 100.0)
    
    h_bills = sum(((households[k]["commitments"]["utilities"]) * households[k]["households"] * 3) / 1000.0 for k in ["b40", "m40", "t20"])
    billing_receipts = h_bills + 5.0
    utilities_health = 70.0 + (billing_receipts - 15.0) * 5.0 - (10.0 if subsidy_policy == "targeted" else 0.0)
    utilities_health = clamp(utilities_health, 0.0, 100.0)
    
    govt_health = 100.0 - (debt_to_gdp - 55.0) * 1.5 + (fiscal_deficit / gdp) * 10.0
    govt_health = clamp(govt_health, 0.0, 100.0)
    
    return (
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
    )
