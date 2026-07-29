# 🏛️ 06 — Software Architecture

> **This document defines the code structure, file layout, and component boundaries of the Malaysian Economy Text Simulator (METS).**

---

## 1. Directory Structure

To keep the simulator modular and testable, the codebase is split into separated layers:

```
malaysia-economy-status/
│
├── docs/                      # Pre-code planning & documentation
│   ├── 01_project_constitution.md
│   ├── 02_requirement_discovery.md
│   ├── 03_business_analysis.md
│   └── ...
│
├── engine/                    # Core simulation logic
│   ├── __init__.py
│   ├── engine.py              # Main EconomyEngine class
│   ├── formulas.py            # Pure mathematical functions
│   └── events.py              # Macroeconomic shock events
│
├── ui/                        # User interface layer
│   ├── __init__.py
│   ├── console.py             # CLI formatting, tables, color wrappers
│   └── charts.py              # Text-based ASCII visualizers (bar charts)
│
├── tests/                     # Unit & integration tests
│   ├── __init__.py
│   ├── test_engine.py
│   └── test_formulas.py
│
├── .gitignore
├── README.md
├── requirements.txt           # Empty for now (standard library only)
└── main.py                    # Entry point of the simulator
```

---

## 2. Component Design & Responsibilities

### 2.1 Core Simulation Engine (`engine/engine.py`)
- Maintains the overall state dictionary.
- Coordinates calls to `formulas.py` to calculate the next quarter's state.
- Tracks turn counts, checks game over / success states.
- Implements state persistence (`save_game` and `load_game` to JSON).

### 2.2 Mathematical Model (`engine/formulas.py`)
- Set of pure, deterministic functions without side effects.
- Input: Current state dictionary + user policies.
- Output: Incremental state change values (e.g., $\Delta\text{GDP}$, $\Delta\text{CPI}$, $\Delta\text{MYR}$).
- Using pure functions makes testing extremely simple.

### 2.3 Event Shock System (`engine/events.py`)
- Dictionary of predefined events (e.g., "FED_HIKE", "OIL_CRASH").
- Triggers events based on current quarter index or randomly with a probability parameter.
- Applies modifications to current parameters before mathematical calculations run.

### 2.4 User Interface Layer (`ui/console.py` & `ui/charts.py`)
- Takes the current state and renders it nicely in the terminal.
- Uses ANSI color codes for high-signal indicator logs (green/red).
- Renders simple ASCII bar charts for economic metrics (e.g., public satisfaction trend).
- Handles validation of user terminal inputs.
