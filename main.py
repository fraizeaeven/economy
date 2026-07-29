import os
import sys
from engine.main_engine import EconomyEngine
from engine.events import get_random_event, trigger_event, EVENTS
from ui.console import (
    print_dashboard,
    prompt_float,
    prompt_choice,
    print_separator,
    print_sectoral_health,
    print_forecasting_report,
    print_sectoral_gdp,
    CLR_GREEN,
    CLR_RED,
    CLR_YELLOW,
    CLR_CYAN,
    CLR_RESET,
    CLR_BOLD
)
from ui.charts import render_history_trend

SAVE_FILE = "mets_save.json"

def print_intro():
    print_separator("=")
    print(f"{CLR_BOLD}{CLR_GREEN}   MALAYSIAN ECONOMY SIMULATOR: THE SOVEREIGN ORCHESTRATOR{CLR_RESET}")
    print_separator("=")
    print("Welcome, Minister of Finance and Governor of Bank Negara Malaysia.")
    print("You have been appointed to steer the economic ship of Malaysia.")
    print("Your mandate is to guide the country through a 5-year cycle (20 Quarters).")
    print("\nRules & Victory Conditions:")
    print(f"  1. {CLR_BOLD}Debt Sustainability{CLR_RESET}: Keep National Debt-to-GDP below {CLR_RED}80.0%{CLR_RESET}. (Target: <75.0%)")
    print(f"  2. {CLR_BOLD}Public Mandate{CLR_RESET}: Keep Public Satisfaction above {CLR_RED}20.0%{CLR_RESET}. (Target: >50.0% at Q20)")
    print("  3. Balances are delicate: raising OPR cools inflation but hurts GDP growth.")
    print("     Rationalizing subsidies saves budget but causes inflation and public anger.")
    print_separator("=")
    input("Press Enter to begin...")

def show_help():
    print_separator("-")
    print(f"{CLR_BOLD}COMMAND HELP:{CLR_RESET}")
    print("  When prompted for OPR or policy inputs, you can enter:")
    print(f"    * {CLR_BOLD}t{CLR_RESET} - View historical trend charts (ASCII visualizers)")
    print(f"    * {CLR_BOLD}v{CLR_RESET} - View Sectoral Health, Poverty, and Foreign Population report")
    print(f"    * {CLR_BOLD}i{CLR_RESET} - View DOSM Industry Sectoral Report (employment & trade)")
    print(f"    * {CLR_BOLD}p{CLR_RESET} - View Macroeconomic Projections (y = mx + c linear forecasting)")
    print(f"    * {CLR_BOLD}s{CLR_RESET} - Save current game state to file")
    print(f"    * {CLR_BOLD}l{CLR_RESET} - Load previous game state from file")
    print(f"    * {CLR_BOLD}h{CLR_RESET} - Show this help menu")
    print(f"    * {CLR_BOLD}q{CLR_RESET} - Exit the simulation")
    print_separator("-")

def run_simulation():
    print_intro()
    engine = EconomyEngine()
    
    while True:
        # Check game win/loss status before starting the quarter
        is_over, reason = engine.check_game_status()
        if is_over:
            print_separator("=")
            print(f"{CLR_BOLD}{CLR_RED}🚨 GAME OVER: SIMULATION ENDED{CLR_RESET}")
            print(f"\n{reason}")
            print_separator("=")
            
            play_again = prompt_choice("Do you want to start a new simulation?", ["y", "n"], "y")
            if play_again == "y":
                engine = EconomyEngine()
                continue
            else:
                print("Thank you for playing METS!")
                sys.exit(0)
                
        # Check and print re-election victory
        election_msg = engine.state["external"].get("election_status")
        if election_msg:
            print_separator("=")
            print(f"{CLR_BOLD}{CLR_GREEN}🎉 ELECTION VICTORY: {election_msg}{CLR_RESET}")
            print_separator("=")
            engine.state["external"]["election_status"] = None
            input("Press Enter to begin your next term...")
            print("\n" * 5)
            
        # 1. Print dashboard
        print_dashboard(engine.state)
        
        # 2. Trigger random macroeconomic events
        # We trigger events starting from Q2 onwards to give user 1 baseline turn
        active_event_key = None
        if engine.state["quarter"] > 1:
            active_event_key = get_random_event(0.35)
            if active_event_key:
                # Apply temporary modifications to state
                trigger_event(active_event_key, engine.state)
                # Redisplay dashboard showing shock alert
                print("\n" * 2)
                print_dashboard(engine.state)
                event_meta = EVENTS[active_event_key]
                print(f"{CLR_BOLD}{CLR_YELLOW}📣 NEWS RELEASES:{CLR_RESET}")
                print(f"  {CLR_BOLD}{event_meta['name']}{CLR_RESET}: {event_meta['description']}")
                print_separator("-")
                
        # 3. Policy Inputs
        print(f"{CLR_BOLD}Formulate policy rules for Q{engine.state['quarter']}:{CLR_RESET}")
        print("  (Type 'h' for help and shortcut commands)")
        
        curr_opr = engine.state["metrics"]["opr"]
        curr_sst = engine.state["government"]["tax_revenue"] # dummy proxy for default values
        
        # We loop until user inputs actual policy numbers (rather than shortcut commands)
        while True:
            raw_input = input(f"  Set Overnight Policy Rate (OPR) (1.50 - 6.00) [{curr_opr:.2f}%]: ").strip().lower()
            
            if raw_input == 'h':
                show_help()
                continue
            elif raw_input == 't':
                render_history_trend(engine.history + [engine.state], "public_satisfaction", "Public Satisfaction")
                render_history_trend(engine.history + [engine.state], "debt_to_gdp", "Debt-to-GDP (%)")
                continue
            elif raw_input == 'v':
                print_sectoral_health(engine.state)
                continue
            elif raw_input == 'i':
                print_sectoral_gdp(engine.state)
                continue
            elif raw_input == 'p':
                forecast_data = engine.forecast_metrics()
                print_forecasting_report(forecast_data)
                continue
            elif raw_input == 's':
                if engine.save_state(SAVE_FILE):
                    print(f"{CLR_GREEN}Game saved successfully to {SAVE_FILE}!{CLR_RESET}")
                else:
                    print(f"{CLR_RED}Failed to save game state.{CLR_RESET}")
                continue
            elif raw_input == 'l':
                if os.path.exists(SAVE_FILE) and engine.load_state(SAVE_FILE):
                    print(f"{CLR_GREEN}Game loaded successfully from {SAVE_FILE}!{CLR_RESET}")
                    # Re-trigger loop with loaded state
                    break
                else:
                    print(f"{CLR_RED}Failed to load game state (Save file may not exist).{CLR_RESET}")
                continue
            elif raw_input == 'q':
                confirm = prompt_choice("Are you sure you want to quit?", ["y", "n"], "n")
                if confirm == "y":
                    print("Exiting simulator. Jumpa lagi!")
                    sys.exit(0)
                continue
            
            # If it's a numeric policy entry, validate and get other inputs
            try:
                if not raw_input:
                    opr_val = curr_opr
                else:
                    opr_val = float(raw_input)
                    if not (1.50 <= opr_val <= 6.00):
                        print(f"{CLR_RED}OPR must be between 1.50 and 6.00.{CLR_RESET}")
                        continue
                
                # Fetch other inputs
                sst_val = prompt_float("  Set SST rate (0% - 15%)", 0.0, 0.15, 0.06)
                corp_tax_val = prompt_float("  Set Corporate Tax rate (10% - 35%)", 0.10, 0.35, 0.24)
                subsidy_regime = prompt_choice("  Set Subsidy Regime", ["blanket", "targeted"], engine.state["government"]["subsidy_policy"])
                devex_val = prompt_float("  Set Development Expenditure (RM Billion)", 10.0, 50.0, engine.state["government"]["dev_exp"])
                labor_policy = prompt_choice("  Set Foreign Labor Policy", ["loose", "balanced", "strict"], engine.state["external"]["foreign_labor_policy"])
                
                # Fetch advanced inputs
                tax_reg = prompt_choice("  Set Tax Regime", ["sst", "gst"], engine.state["government"].get("tax_regime", "sst"))
                epf_withdrawal = prompt_choice("  Set EPF Withdrawal Policy", ["none", "targeted", "unrestricted"], engine.state["government"].get("epf_withdrawal_policy", "none"))
                ex_rate_regime = prompt_choice("  Set Exchange Rate Regime", ["floating", "pegged_4.00", "pegged_3.80"], engine.state["government"].get("exchange_rate_policy", "floating"))
                em_alloc = prompt_float("  Set East Malaysia Infrastructure Allocation (RM Billion)", 2.0, 15.0, engine.state["government"].get("east_malaysia_allocation", 4.0))
                
                # Fetch fuel & tariff inputs
                petrol_reg = prompt_choice("  Set Petrol RON95 Subsidy Regime", ["blanket", "targeted_b40", "rationalized"], engine.state["government"].get("petrol_subsidy_regime", "blanket"))
                diesel_reg = prompt_choice("  Set Diesel Subsidy Regime", ["blanket", "targeted_fleet", "rationalized"], engine.state["government"].get("diesel_subsidy_regime", "blanket"))
                elec_tariff = prompt_choice("  Set Electricity Tariff Policy", ["subsidized", "targeted_t20", "market_rate"], engine.state["government"].get("electricity_tariff_policy", "subsidized"))
                
                # Bundle and execute step
                policies = {
                    "opr": opr_val,
                    "sst_rate": sst_val,
                    "corporate_tax": corp_tax_val,
                    "subsidy_regime": subsidy_regime,
                    "development_expenditure": devex_val,
                    "foreign_labor_policy": labor_policy,
                    "tax_regime": tax_reg,
                    "epf_withdrawal_policy": epf_withdrawal,
                    "exchange_rate_policy": ex_rate_regime,
                    "east_malaysia_allocation": em_alloc,
                    "petrol_subsidy_regime": petrol_reg,
                    "diesel_subsidy_regime": diesel_reg,
                    "electricity_tariff_policy": elec_tariff
                }
                
                # Clear active shock text from state for next turns
                engine.state["external"]["shock_event"] = None
                
                # Execute step
                engine.step(policies)
                break
                
            except ValueError:
                print(f"{CLR_RED}Invalid input. Please enter a valid number or command shortcut.{CLR_RESET}")
                
        print("\n" * 2)

if __name__ == '__main__':
    try:
        run_simulation()
    except KeyboardInterrupt:
        print("\nSimulation aborted. Goodbye!")
        sys.exit(0)
