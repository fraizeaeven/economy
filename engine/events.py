import random

def _apply_fed_hike(state):
    state["external"]["fed_rate"] = 6.25
    state["external"]["shock_event"] = "US Fed Funds Rate Hike (+100 bps)"

def _apply_oil_crash(state):
    state["external"]["brent_crude"] = 50.0
    state["external"]["shock_event"] = "Brent Crude Price Crash ($50/barrel)"

def _apply_oil_boom(state):
    state["external"]["brent_crude"] = 105.0
    state["external"]["shock_event"] = "Brent Crude Price Boom ($105/barrel)"

def _apply_floods(state):
    # Operating exp in state will be altered before calculations
    state["government"]["operating_exp"] += 5.0  # emergency spending
    state["metrics"]["unemployment_rate"] = min(10.0, state["metrics"]["unemployment_rate"] + 0.3)
    state["metrics"]["public_satisfaction"] = max(0.0, state["metrics"]["public_satisfaction"] - 3.0)
    state["external"]["shock_event"] = "East Coast Floods (Emergency spending & supply disruptions)"

def _apply_payrise(state):
    state["government"]["operating_exp"] += 3.0
    state["households"]["m40"]["salary_base"] += 200.0
    state["metrics"]["public_satisfaction"] = min(100.0, state["metrics"]["public_satisfaction"] + 5.0)
    state["external"]["shock_event"] = "Civil Servant Salary Raise (+RM200 base for M40)"

EVENTS = {
    "FED_RATE_HIKE": {
        "name": "US Fed Funds Rate Hike",
        "description": "The US Federal Reserve aggressively raises interest rates to 6.25%, triggering currency capital outflows and putting depreciation pressure on the Ringgit.",
        "modifier": _apply_fed_hike
    },
    "BRENT_OIL_CRASH": {
        "name": "Brent Crude Price Crash",
        "description": "Oversupply spikes causing Brent Crude to drop to $50/barrel. This weakens Malaysia's trade surplus and oil tax base.",
        "modifier": _apply_oil_crash
    },
    "OIL_BOOM": {
        "name": "Brent Crude Price Boom",
        "description": "Geopolitical supply constraints drive Brent Crude up to $105/barrel, raising export revenues and strengthening the Ringgit.",
        "modifier": _apply_oil_boom
    },
    "FLOODS_EAST_COAST": {
        "name": "East Coast Floods",
        "description": "Heavy monsoon rains submerge coastal farmlands. Domestic transport routes block and emergency relief funds activate.",
        "modifier": _apply_floods
    },
    "CIVIL_SERVANT_PAYRISE": {
        "name": "Civil Servant Salary Raise",
        "description": "In response to inflation concerns, the administration adjusts public sector salaries. Government expenditure increases, boosting public morale.",
        "modifier": _apply_payrise
    }
}

def trigger_event(event_key: str, state: dict) -> dict:
    """
    Applies the specific event modifiers directly to the simulation state.
    """
    if event_key in EVENTS:
        EVENTS[event_key]["modifier"](state)
    return state

def get_random_event(probability: float = 0.35) -> str | None:
    """
    Randomly chooses a shock event based on a probability threshold.
    """
    if random.random() < probability:
        return random.choice(list(EVENTS.keys()))
    return None
