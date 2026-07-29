def draw_horizontal_bar(val: float, max_val: float = 100.0, width: int = 30) -> str:
    """
    Returns a horizontal ASCII bar representing a value.
    Example: [████████████████████            ]
    """
    percent = max(0.0, min(1.0, val / max_val))
    filled_length = int(width * percent)
    bar = "█" * filled_length + " " * (width - filled_length)
    return f"[{bar}] {val:.1f}%"

def render_history_trend(history: list, metric_key: str, label: str, max_val: float = 100.0):
    """
    Prints a sequence of horizontal bars representing the trend of a metric over historical turns.
    """
    if not history:
        print("No historical data available yet.")
        return
        
    print(f"\n--- Historical Trend: {label} ---")
    
    for idx, snapshot in enumerate(history):
        q = snapshot["quarter"]
        # Access metric inside nested dictionary structure
        val = snapshot["metrics"][metric_key]
        bar_str = draw_horizontal_bar(val, max_val)
        print(f"  Q{q:<2}: {bar_str}")
    print("---------------------------------")
