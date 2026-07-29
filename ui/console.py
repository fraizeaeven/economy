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
    
    # Section 5: Public Approval
    approval_val = metrics["public_satisfaction"]
    approval_bar = color_value(approval_val, 60.0, 40.0) + "%"
    print(f"{CLR_BOLD}PUBLIC SATISFACTION INDEX: {approval_bar}{CLR_RESET}")
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
