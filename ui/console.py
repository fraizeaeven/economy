import sys

# ANSI color codes
CLR_HEADER = "\033[95m"
CLR_CYAN = "\033[96m"
CLR_GREEN = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_RED = "\033[91m"
CLR_RESET = "\033[0m"
CLR_BOLD = "\033[1m"

def print_separator(char="=", length=65):
    print(CLR_CYAN + char * length + CLR_RESET)

def color_value(val, threshold_high, threshold_low=None, invert=False):
    """
    Returns colored string based on threshold conditions.
    invert=True: high is bad (e.g. inflation, debt), low is good.
    invert=False: high is good (e.g. growth, satisfaction), low is bad.
    """
    if invert:
        if val >= threshold_high:
            return f"{CLR_RED}{val}{CLR_RESET}"
        if threshold_low is not None and val <= threshold_low:
            return f"{CLR_GREEN}{val}{CLR_RESET}"
        return f"{CLR_YELLOW}{val}{CLR_RESET}"
    else:
        if val >= threshold_high:
            return f"{CLR_GREEN}{val}{CLR_RESET}"
        if threshold_low is not None and val <= threshold_low:
            return f"{CLR_RED}{val}{CLR_RESET}"
        return f"{CLR_YELLOW}{val}{CLR_RESET}"

def print_dashboard(state: dict):
    q = state["quarter"]
    metrics = state["metrics"]
    govt = state["government"]
    sme = state["sme"]
    households = state["households"]
    external = state["external"]
    
    print_separator()
    print(f"{CLR_BOLD}{CLR_HEADER}       MALAYSIAN ECONOMY STATUS TRACKER (METS) - QUARTER {q}/20{CLR_RESET}")
    print_separator("-")
    
    # Active shock event banner
    shock = external.get("shock_event")
    if shock:
        print(f"{CLR_BOLD}{CLR_RED}⚠️ SHOCK ALERT: {shock}{CLR_RESET}")
        print_separator("-")
        
    # Section 1: Macro Aggregates
    print(f"{CLR_BOLD}1. MACROECONOMIC METRICS{CLR_RESET}")
    
    gdp_str = f"RM {metrics['gdp']:.1f} Billion"
    gdp_growth_str = color_value(metrics["gdp_growth"], 4.5, 3.5) + "%"
    opr_str = f"{metrics['opr']:.2f}%"
    cpi_str = color_value(metrics["cpi"], 3.5, 1.5, invert=True) + "%"
    myr_str = color_value(metrics["myr_usd"], 4.60, 4.30, invert=True) + " MYR/USD"
    unemployment_str = color_value(metrics["unemployment_rate"], 4.5, 3.3, invert=True) + "%"
    
    print(f"  * GDP (Quarterly):  {gdp_str:<22} * GDP Growth (Ann.): {gdp_growth_str}")
    print(f"  * Overnight Policy: {opr_str:<22} * Inflation (CPI):   {cpi_str}")
    print(f"  * Ringgit (MYR):    {myr_str:<22} * Unemployment:      {unemployment_str}")
    
    print_separator("-")
    
    # Section 2: Fiscal & Government Status
    print(f"{CLR_BOLD}2. GOVERNMENT FISCAL ACCOUNT{CLR_RESET}")
    tax_rev = govt["tax_revenue"]
    opex = govt["operating_exp"]
    devex = govt["dev_exp"]
    subsidy = govt["subsidy_policy"].upper()
    
    debt_val = metrics["national_debt"]
    debt_gdp = metrics["debt_to_gdp"]
    debt_gdp_colored = color_value(debt_gdp, 75.0, 60.0, invert=True) + "%"
    
    balance = tax_rev - (opex + devex)
    balance_colored = (CLR_GREEN if balance >= 0 else CLR_RED) + f"RM {balance:.2f} Billion" + CLR_RESET
    
    print(f"  * Tax Revenues:     RM {tax_rev:.2f} Billion    * Operating Exp:     RM {opex:.2f} Billion")
    print(f"  * Development Exp:  RM {devex:.2f} Billion    * Fiscal Balance:    {balance_colored}")
    print(f"  * National Debt:    RM {debt_val:.1f} Billion   * Debt-to-GDP:       {debt_gdp_colored}")
    print(f"  * Subsidy Policy:   {CLR_BOLD}{subsidy}{CLR_RESET}")
    
    print_separator("-")
    
    # Section 3: Household Micro Flows
    print(f"{CLR_BOLD}3. HOUSEHOLD SEGMENTS (Income, Commitments & Savings){CLR_RESET}")
    for name, key in [("B40 (Bottom 40%)", "b40"), ("M40 (Middle 40%)", "m40"), ("T20 (Top 20%)", "t20")]:
        seg = households[key]
        utils = seg["commitments"]["utilities"]
        debt = seg["commitments"]["debt_service"]
        aid = seg.get("str_aid", 0.0)
        
        # Monthly gross
        gross = seg["salary"] + aid
        savings = seg["savings"]
        
        print(f"  {CLR_BOLD}* {name}{CLR_RESET}")
        print(f"    - Avg Monthly Salary: RM {seg['salary']:.2f}  | Direct Aid (STR): RM {aid:.2f}")
        print(f"    - Monthly Debt Pay:   RM {debt:.2f}    | Utilities Bill:   RM {utils:.2f}")
        print(f"    - Accum. Savings:     RM {savings:.2f} Billion")
        
    print_separator("-")
    
    # Section 4: SME & External Factors
    print(f"{CLR_BOLD}4. CORPORATE/SME & EXTERNAL DRIVERS{CLR_RESET}")
    sme_profit = sme["profit"]
    sme_profit_colored = (CLR_GREEN if sme_profit >= 0 else CLR_RED) + f"RM {sme_profit:.2f} Billion" + CLR_RESET
    print(f"  * SME Profitability: {sme_profit_colored:<22} * Brent Crude Oil:   ${external['brent_crude']:.1f}/barrel")
    print(f"  * SME Loan Payments: RM {sme['loan_payment']:.2f} Billion   * US Fed Funds Rate: {external['fed_rate']:.2f}%")
    
    print_separator("-")
    
    # Section 5: Public Approval & Gini Index
    approval_val = metrics["public_satisfaction"]
    approval_bar = color_value(approval_val, 60.0, 40.0) + "%"
    
    gini_val = metrics.get("gini", 0.390)
    gini_color = CLR_GREEN if gini_val <= 0.390 else (CLR_YELLOW if gini_val <= 0.420 else CLR_RED)
    gini_colored = f"{gini_color}{gini_val:.3f}{CLR_RESET}"
    
    print(f"{CLR_BOLD}PUBLIC SATISFACTION INDEX: {approval_bar:<20} | GINI COEFFICIENT (INEQUALITY): {gini_colored}{CLR_RESET}")
    print_separator()

def prompt_float(prompt_text, min_val, max_val, default_val):
    while True:
        try:
            line = input(f"{prompt_text} [{default_val}]: ").strip()
            if not line:
                return default_val
            val = float(line)
            if min_val <= val <= max_val:
                return val
            print(f"{CLR_RED}Value must be between {min_val} and {max_val}.{CLR_RESET}")
        except ValueError:
            print(f"{CLR_RED}Please enter a valid number.{CLR_RESET}")

def prompt_choice(prompt_text, choices, default_val):
    choices_str = "/".join(choices)
    while True:
        line = input(f"{prompt_text} ({choices_str}) [{default_val}]: ").strip().lower()
        if not line:
            return default_val
        if line in choices:
            return line
        print(f"{CLR_RED}Please select one of the following: {choices_str}{CLR_RESET}")

def draw_bar(val: float, max_val: float = 100.0, width: int = 25) -> str:
    percent = max(0.0, min(1.0, val / max_val))
    filled = int(width * percent)
    bar = "█" * filled + " " * (width - filled)
    
    if val >= 75.0:
        color = CLR_GREEN
    elif val <= 45.0:
        color = CLR_RED
    else:
        color = CLR_YELLOW
        
    return f"[{color}{bar}{CLR_RESET}] {val:.1f}%"

def print_sectoral_health(state: dict):
    metrics = state["metrics"]
    households = state["households"]
    external = state["external"]
    govt = state["government"]
    
    print_separator("=")
    print(f"{CLR_BOLD}{CLR_HEADER}             METS SECTORAL HEALTH & POPULATION REPORT{CLR_RESET}")
    print_separator("=")
    
    print(f"{CLR_BOLD}* SECTOR HEALTH STATUS:{CLR_RESET}")
    print(f"  - Family Health Index:    {draw_bar(metrics['family_health'])}")
    print(f"  - SME / PKS Health Index: {draw_bar(metrics['sme_health'])}")
    print(f"  - Utilities Health Index: {draw_bar(metrics['utilities_health'])}")
    print(f"  - Banking Health Index:   {draw_bar(metrics['banking_health'])}")
    print(f"  - Government Health:      {draw_bar(metrics['govt_health'])}")
    
    print_separator("-")
    
    print(f"{CLR_BOLD}* POPULATION & SOCIAL EQUILIBRIUM:{CLR_RESET}")
    pli_val = 2584.0 * (metrics["cpi"] / 2.5)
    print(f"  - Poverty Rate (National): {CLR_YELLOW}{metrics['poverty_rate']:.2f}%{CLR_RESET} (Poverty Line: RM {pli_val:.2f}/month)")
    print(f"  - East Malaysia Poverty:  {CLR_RED if metrics.get('east_malaysia_poverty', 14.5) > 10.0 else CLR_GREEN}{metrics.get('east_malaysia_poverty', 14.5):.2f}%{CLR_RESET} (Sabah & Sarawak)")
    print(f"  - B40 Monthly Income:     RM {households['b40']['salary'] + households['b40']['str_aid']:.2f} (Gaji: RM {households['b40']['salary']:.2f} | STR: RM {households['b40']['str_aid']:.2f})")
    
    # Brain Drain Index
    bd_idx = metrics.get("brain_drain_index", 3.0)
    bd_color = CLR_RED if bd_idx > 5.0 else (CLR_YELLOW if bd_idx > 3.5 else CLR_GREEN)
    print(f"  - Brain Drain Index:      {bd_color}{bd_idx:.2f} / 10.0{CLR_RESET} " + (f"{CLR_RED}(HIGH TALENT FLIGHT!){CLR_RESET}" if bd_idx > 5.0 else ""))
    
    print_separator("-")
    
    print(f"{CLR_BOLD}* LIQUIDITY, RESERVES & FUND POOLS:{CLR_RESET}")
    reserves_val = metrics.get("foreign_reserves", 115.0)
    res_color = CLR_RED if reserves_val < 30.0 else (CLR_YELLOW if reserves_val < 75.0 else CLR_GREEN)
    
    print(f"  - BNM Foreign Reserves:   {res_color}USD {reserves_val:.2f} Billion{CLR_RESET} (Peg Guard limit: > USD 10.0B)")
    print(f"  - EPF (KWSP) Fund Pool:   {CLR_GREEN}RM {metrics.get('epf_pool', 750.0):.2f} Billion{CLR_RESET} (Withdrawal: {govt.get('epf_withdrawal_policy', 'none').upper()})")
    print(f"  - Exchange Rate Regime:   {CLR_BOLD}{govt.get('exchange_rate_policy', 'floating').upper()}{CLR_RESET}")
    print(f"  - Electricity Tariff:     {CLR_BOLD}{govt.get('electricity_tariff_policy', 'subsidized').upper()}{CLR_RESET}")
    
    print_separator("-")
    
    print(f"{CLR_BOLD}* DOMESTIC FUEL SUBSIDIES & PRICING:{CLR_RESET}")
    print(f"  - Petrol RON95 Price:     {CLR_GREEN}RM {metrics.get('ron95_price', 2.05):.2f} / Litre{CLR_RESET} (Regime: {govt.get('petrol_subsidy_regime', 'blanket').upper()})")
    print(f"  - Diesel Price:           {CLR_GREEN}RM {metrics.get('diesel_price', 2.15):.2f} / Litre{CLR_RESET} (Regime: {govt.get('diesel_subsidy_regime', 'blanket').upper()})")
    
    print_separator("-")
    
    print(f"{CLR_BOLD}* LABOR & EXTERNAL PROFILE:{CLR_RESET}")
    reg_fw = external.get("registered_foreign_workers", 2.2)
    unreg_fw = external.get("unregistered_foreign_workers", 1.2)
    refugees = external.get("refugees", 0.2)
    policy = external.get("foreign_labor_policy", "balanced").upper()
    
    print(f"  - Registered Workers:     {reg_fw:.2f} Million")
    print(f"  - Unregistered Workers:   {unreg_fw:.2f} Million")
    print(f"  - Refugee Population:     {refugees:.2f} Million")
    print(f"  - Labor / Border Policy:  {CLR_BOLD}{policy}{CLR_RESET}")
    
    print_separator("-")
    
    print(f"{CLR_BOLD}* CAPITAL INVESTMENT & TRADE (QUARTERLY):{CLR_RESET}")
    print(f"  - Foreign Direct Investment (FDI): RM {metrics['fdi']:.2f} Billion | Domestic (DDI): RM {metrics['ddi']:.2f} Billion")
    print(f"  - Tourism Service Exports:         RM {metrics.get('tourism_revenue', 10.0):.2f} Billion")
    print_separator()

def print_forecasting_report(forecast_data: dict):
    """
    Prints a forecasting dashboard displaying the fitted linear equations (y = mx + c)
    and quarterly predictions for the next 4 quarters.
    """
    print_separator()
    print(f"{CLR_BOLD}{CLR_GREEN}========================================================================{CLR_RESET}")
    print(f"{CLR_BOLD}       METS MACROECONOMIC FORECASTING REPORT (LINEAR REGRESSION){CLR_RESET}")
    print(f"{CLR_BOLD}{CLR_GREEN}========================================================================{CLR_RESET}")
    print(f"Projecting outcomes for the next 4 quarters using fitted linear trend lines:")
    print("  Model: y = mx + c  (y: metric value, x: quarter index)")
    print_separator("-")
    
    friendly_names = {
        "gdp": "Gross Domestic Product (GDP - RM Billion)",
        "debt_to_gdp": "National Debt-to-GDP Ratio (%)",
        "public_satisfaction": "Public Satisfaction Index (%)",
        "cpi": "Consumer Price Index Inflation (%)"
    }
    
    for key, data in forecast_data.items():
        name = friendly_names.get(key, key)
        equation = data["equation"]
        m = data["m"]
        c = data["c"]
        
        print(f"\n{CLR_BOLD}* {name}:{CLR_RESET}")
        print(f"  Linear Formula: {CLR_YELLOW}{equation}{CLR_RESET}  (Slope m: {m:+.4f} | Intercept c: {c:.4f})")
        print("  Projections:")
        
        for q, val in data["forecasts"]:
            alert = ""
            if key == "debt_to_gdp" and val >= 80.0:
                alert = f" {CLR_RED}[CRITICAL DEBT SHOCK WARNING!]{CLR_RESET}"
            elif key == "debt_to_gdp" and val >= 70.0:
                alert = f" {CLR_YELLOW}[DEBT WARNING]{CLR_RESET}"
            elif key == "public_satisfaction" and val <= 20.0:
                alert = f" {CLR_RED}[CRITICAL CIVIL UNREST WARNING!]{CLR_RESET}"
            elif key == "public_satisfaction" and val <= 35.0:
                alert = f" {CLR_YELLOW}[LOW APPROVAL WARNING]{CLR_RESET}"
            elif key == "cpi" and val >= 4.0:
                alert = f" {CLR_RED}[HIGH INFLATION WARNING]{CLR_RESET}"
                
            print(f"    - Quarter {q:<3}: {val:.2f}{alert}")
            
    print_separator("-")
    print("Disclaimer: Projections assume no policy shifts or external shocks occur.")
    print_separator()

def print_sectoral_gdp(state: dict):
    """
    Renders the Industry Sectors dashboard, detailing GDP shares, exports/imports,
    and employment splits per household segment.
    """
    sectors = state.get("sectors", {})
    metrics = state["metrics"]
    total_gdp = metrics["gdp"]
    
    print_separator()
    print(f"{CLR_BOLD}{CLR_CYAN}========================================================================{CLR_RESET}")
    print(f"{CLR_BOLD}                 DOSM MALAYSIAN INDUSTRY SECTORAL REPORT{CLR_RESET}")
    print(f"{CLR_BOLD}{CLR_CYAN}========================================================================{CLR_RESET}")
    print(f"Total National GDP: RM {total_gdp:.2f} Billion")
    print_separator("-")
    
    industry_profiles = {
        "services": {
            "name": "Services (Wholesale, Retail, Finance, Tourism, Utilities)",
            "sme_concentration": "High (70% Micro/SMEs weight)",
            "desc": "Primary driver of domestic consumption and tertiary job market.",
            "b40": 40, "m40": 50, "t20": 65
        },
        "manufacturing": {
            "name": "Manufacturing (E&E, Semiconductor, Petrochemical)",
            "sme_concentration": "Low-Medium (20% SME weight, dominated by MNCs)",
            "desc": "Engine of global exports and FDI capital accumulation.",
            "b40": 10, "m40": 30, "t20": 15
        },
        "agriculture": {
            "name": "Agriculture & Commodities (Palm Oil, Rubber, Paddy)",
            "sme_concentration": "High (50% SME smallholders weight)",
            "desc": "Commodity trade anchor, net food imports contributor.",
            "b40": 30, "m40": 0, "t20": 5
        },
        "mining": {
            "name": "Mining & Petroleum (PETRONAS crude extraction, LNG)",
            "sme_concentration": "Very Low (5% SME weight, capital-intensive corps)",
            "desc": "Sovereign dividend source, highly sensitive to oil shock spikes.",
            "b40": 0, "m40": 15, "t20": 15
        },
        "construction": {
            "name": "Construction (Infrastructure & Real Estate developments)",
            "sme_concentration": "High (60% SME subcontractors weight)",
            "desc": "Fuses public devex to employment, sensitive to interest rates.",
            "b40": 20, "m40": 5, "t20": 0
        }
    }
    
    for key, data in sectors.items():
        profile = industry_profiles.get(key, {})
        gdp_contrib = data["gdp_contrib"]
        gdp_pct = (gdp_contrib / total_gdp) * 100.0 if total_gdp > 0 else 0.0
        g_rate = data.get("growth_rate", 0.0)
        
        g_color = CLR_GREEN if g_rate >= 0 else CLR_RED
        g_rate_str = f"{g_color}{g_rate:+.2f}%{CLR_RESET}"
        
        print(f"\n{CLR_BOLD}* {profile.get('name', key.upper())}:{CLR_RESET}")
        print(f"  - GDP Contribution:  RM {gdp_contrib:.2f} Billion ({gdp_pct:.2f}% of total GDP)")
        print(f"  - Sector Growth:      {g_rate_str} (Annualized)")
        print(f"  - Trade Volume:       Exports: RM {data['exports']:.2f}B | Imports: RM {data['imports']:.2f}B")
        print(f"  - SME Concentration:  {profile.get('sme_concentration')}")
        print(f"  - Role / Impact:      {profile.get('desc')}")
        print(f"  - Segment Workers:    {CLR_BOLD}B40:{CLR_RESET} {profile.get('b40')}% | {CLR_BOLD}M40:{CLR_RESET} {profile.get('m40')}% | {CLR_BOLD}T20:{CLR_RESET} {profile.get('t20')}%")
        
    print_separator("-")
    print("Source: DOSM Structural Indicators Simulation. Re-evaluates each Quarter.")
    print_separator()

def print_tax_report(state: dict):
    """
    Renders the detailed Tax Structure report including LHDN collections breakdown
    and active rates.
    """
    govt = state.get("government", {})
    total_tax = govt.get("tax_revenue", 0.0)
    
    print_separator()
    print(f"{CLR_BOLD}{CLR_GREEN}========================================================================{CLR_RESET}")
    print(f"{CLR_BOLD}                 LHDN MALAYSIAN TAX STRUCTURE REPORT{CLR_RESET}")
    print(f"{CLR_BOLD}{CLR_GREEN}========================================================================{CLR_RESET}")
    print(f"Total Quarterly Tax Revenue: RM {total_tax:.2f} Billion")
    print_separator("-")
    
    # Active Rates
    tax_reg = govt.get("tax_regime", "sst").upper()
    print(f"{CLR_BOLD}Active Tax Regimes & Policy Rates:{CLR_RESET}")
    print(f"  - Personal Tax Rates:  B40: {CLR_BOLD}0.0%{CLR_RESET} | M40: {govt.get('m40_tax_rate', 0.04)*100:.1f}% | T20: {govt.get('t20_tax_rate', 0.16)*100:.1f}%")
    print(f"  - Business Tax Rates:  SMEs: {govt.get('sme_tax_rate', 0.17)*100:.1f}% | Standard Corp: {state.get('metrics', {}).get('corporate_tax', 0.24)*100:.1f}%")
    if tax_reg == "GST":
        print(f"  - Indirect Tax:        GST System ({govt.get('gst_rate', 0.06)*100:.1f}%)")
    else:
        print(f"  - Indirect Tax:        SST System (Sales: {govt.get('sst_sales_rate', 0.10)*100:.1f}% | Service: {govt.get('sst_service_rate', 0.08)*100:.1f}%)")
    print(f"  - Special/Other Rates: PITA (O&G): {govt.get('pita_rate', 0.38)*100:.1f}% | RPGT (Property): {govt.get('rpgt_rate', 0.05)*100:.1f}% | Import Duties: {govt.get('import_duty_rate', 0.05)*100:.1f}%")
    print_separator("-")
    
    # Collections breakdown
    coll_indirect = govt.get("coll_indirect", 0.0)
    coll_sme = govt.get("coll_sme", 0.0)
    coll_corp = govt.get("coll_corp", 0.0)
    coll_personal = govt.get("coll_personal", 0.0)
    coll_pita = govt.get("coll_pita", 0.0)
    coll_rpgt = govt.get("coll_rpgt", 0.0)
    coll_import_duties = govt.get("coll_import_duties", 0.0)
    coll_non_tax = govt.get("coll_non_tax", 0.0)
    
    print(f"{CLR_BOLD}Quarterly Collections Breakdown (RM Billion):{CLR_RESET}")
    print(f"  * {CLR_BOLD}Direct Taxes:{CLR_RESET}")
    print(f"    - Personal Income Tax:     RM {coll_personal:>6.2f}B  ({(coll_personal/total_tax*100 if total_tax>0 else 0):.1f}%)")
    print(f"    - SME Business Tax:        RM {coll_sme:>6.2f}B  ({(coll_sme/total_tax*100 if total_tax>0 else 0):.1f}%)")
    print(f"    - Corporate Income Tax:    RM {coll_corp:>6.2f}B  ({(coll_corp/total_tax*100 if total_tax>0 else 0):.1f}%)")
    print(f"    - Petroleum Tax (PITA):    RM {coll_pita:>6.2f}B  ({(coll_pita/total_tax*100 if total_tax>0 else 0):.1f}%)")
    print(f"  * {CLR_BOLD}Indirect Taxes:{CLR_RESET}")
    print(f"    - GST/SST Consumption Tax: RM {coll_indirect:>6.2f}B  ({(coll_indirect/total_tax*100 if total_tax>0 else 0):.1f}%)")
    print(f"    - Customs Import Duties:   RM {coll_import_duties:>6.2f}B  ({(coll_import_duties/total_tax*100 if total_tax>0 else 0):.1f}%)")
    print(f"  * {CLR_BOLD}Other Revenues:{CLR_RESET}")
    print(f"    - Real Property Gains Tax: RM {coll_rpgt:>6.2f}B  ({(coll_rpgt/total_tax*100 if total_tax>0 else 0):.1f}%)")
    print(f"    - Non-Tax State Revenue:   RM {coll_non_tax:>6.2f}B  ({(coll_non_tax/total_tax*100 if total_tax>0 else 0):.1f}%)")
    
    print_separator("-")
    print("Source: LHDN & Royal Malaysian Customs Simulation models.")
    print_separator()
