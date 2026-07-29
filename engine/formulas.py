"""
Macroeconomic formulas and transmission mechanism calculations for METS.
Contains pure functions with no side effects.
"""

def calculate_debt_service(base_debt_service: float, opr: float, base_opr: float, sensitivity: float) -> float:
    """
    Computes updated loan commitments for households or businesses based on OPR shifts.
    OPR increase -> Debt service increase (floating-rate loans).
    """
    # Sensitivity determines how much of the rate change transmits to the borrower.
    rate_diff = (opr - base_opr) / 100.0  # convert percentage points to fraction
    multiplier = 1.0 + (sensitivity * rate_diff * 100.0)
    # Ensure debt service doesn't drop below 50% of base value
    return max(base_debt_service * 0.5, base_debt_service * multiplier)

def calculate_consumption(disposable_income: float, mpc: float) -> float:
    """
    Computes consumption based on disposable income and Marginal Propensity to Consume (MPC).
    """
    return max(0.0, disposable_income * mpc)

def calculate_exchange_rate(
    base_rate: float, 
    local_rate: float, 
    us_rate: float, 
    brent_price: float, 
    base_brent: float = 80.0
) -> float:
    """
    Computes the MYR/USD exchange rate.
    Key drivers:
    1. Interest rate differential (local OPR vs US Fed Funds Rate).
    2. Brent crude oil price (Malaysia is a net exporter).
    """
    # Interest rate differential: local - US. If local rate is higher, MYR strengthens (MYR/USD drops).
    # Baseline differential is 3.00 - 5.25 = -2.25.
    rate_diff = local_rate - us_rate
    base_diff = -2.25
    diff_change = rate_diff - base_diff
    
    # 1% rate differential change shifts MYR by 0.08 points.
    rate_effect = -0.08 * diff_change
    
    # Brent crude price: oil price increase strengthens MYR.
    # $10 change in oil price shifts MYR by 0.03 points.
    oil_change = brent_price - base_brent
    oil_effect = -0.003 * oil_change
    
    myr_usd = base_rate + rate_effect + oil_effect
    
    # Hard bounds for stability (3.80 is old peg, 5.00 is historic low)
    return round(clamp(myr_usd, 3.80, 5.00), 3)

def calculate_inflation(
    consumption_growth: float, 
    myr_change: float, 
    subsidy_policy: str, 
    prev_subsidy_policy: str
) -> float:
    """
    Computes inflation rate (CPI %).
    Drivers:
    1. Base inflation (2.0%).
    2. Demand-pull (rapid consumption growth).
    3. Imported inflation (MYR depreciation).
    4. Policy shock (Subsidy rationalization to targeted).
    """
    inflation = 2.0  # Base inflation is 2.0%
    
    # 1. Demand-pull: if consumption grows faster than 4% quarterly, add to CPI
    if consumption_growth > 0.04:
        inflation += (consumption_growth - 0.04) * 30.0
        
    # 2. Imported inflation: Ringgit weakening (MYR/USD increases) raises import costs
    # E.g. MYR depreciating from 4.40 to 4.60 (+0.20 change) -> +1.5% CPI
    if myr_change > 0:
        inflation += myr_change * 7.5
    elif myr_change < 0:
        # Appreciation cools down inflation
        inflation += myr_change * 3.5
        
    # 3. Subsidy policy shock: switching from blanket to targeted adds +1.8% temporary shock
    if prev_subsidy_policy == "blanket" and subsidy_policy == "targeted":
        inflation += 1.8
    elif prev_subsidy_policy == "targeted" and subsidy_policy == "blanket":
        # Returning to blanket subsidization cools CPI down
        inflation -= 1.0
        
    return round(max(-1.5, inflation), 2)

def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(val, max_val))
