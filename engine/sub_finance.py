import json
from engine.formulas import calculate_exchange_rate, clamp

def step_finance(
    state: dict,
    opr: float,
    fed_rate: float,
    brent_crude: float,
    ex_rate_policy: str,
    tax_regime: str,
    sme_profit: float,
    epf_pool: float,
    epf_policy: str,
    corp_tax_rate: float,
    labor_policy: str,
    unemployment: float,
    t20_tax_rate: float = 0.16
) -> tuple[float, float, float, float, float, float, float, float, float, float]:
    """
    Transition function for exchange rates, reserves, investments, brain drain, tourism, and banking health.
    Returns (myr_usd, myr_change, foreign_reserves, brain_drain, brain_drain_suppression, fdi, ddi, investment, tourism_revenue, banking_health).
    """
    prev_metrics = state["metrics"]
    prev_myr = prev_metrics["myr_usd"]
    prev_satisfaction = prev_metrics["public_satisfaction"]
    
    # 1. Exchange Rate & Reserves calculation
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
    
    # 2. Brain Drain Index & Suppression Factor
    brain_drain = 3.0 + 1.5 * (myr_usd - 4.40) - 0.1 * (prev_satisfaction - 60.0)
    if tax_regime == "gst":
        brain_drain += 1.0
    if t20_tax_rate > 0.25:
        brain_drain += (t20_tax_rate - 0.25) * 50.0
    brain_drain = clamp(brain_drain, 1.0, 10.0)
    brain_drain_suppression = 1.0 - (max(0.0, brain_drain - 5.0) / 5.0) * 0.08
    
    # 3. Calculate FDI & DDI (Foreign & Domestic Investment)
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
    
    # 4. Tourism Revenue calculation
    tourism_revenue = 10.0 * (1.0 + 0.15 * (myr_usd - 4.40) - (0.05 if labor_policy == "strict" else 0.0))
    
    # 5. Banking Health index
    banking_health = 80.0 + (opr - 3.00) * 5.0 - (unemployment - 3.5) * 4.0
    banking_health = clamp(banking_health, 0.0, 100.0)
    
    return (
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
    )
