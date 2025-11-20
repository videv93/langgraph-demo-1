#!/usr/bin/env python3
"""YTC Trading Assistant CLI - Interactive interface for YTC trading methodology."""

import os
import sys
from dotenv import load_dotenv
from src.agent.utils.ytc_assistant import YTCTradingAssistant

# Load environment variables
load_dotenv()


def print_header():
    """Print CLI header."""
    print("\n" + "=" * 80)
    print("YTC Trading Assistant - Powered by Pinecone")
    print("Interactive YTC Trading Methodology Guidance")
    print("=" * 80 + "\n")


def print_menu():
    """Print main menu."""
    print("\nCommands:")
    print("  1. Ask about YTC method")
    print("  2. Get pattern analysis")
    print("  3. Get entry rules")
    print("  4. Get Fibonacci strategy")
    print("  5. Get stop loss guidance")
    print("  6. Get risk management rules")
    print("  7. Validate a setup")
    print("  help - Show this menu")
    print("  exit - Quit the program\n")


def query_ytc_method(assistant: YTCTradingAssistant):
    """Interactive YTC method query."""
    print("\n📚 Query YTC Trading Method")
    question = input("Enter your question: ").strip()

    if question:
        print("\n🔄 Getting response from YTC Assistant...\n")
        response = assistant.query_ytc_method(question)
        print(f"✅ Response:\n{response}\n")


def pattern_analysis(assistant: YTCTradingAssistant):
    """Get pattern analysis."""
    print("\n🎯 Pattern Analysis")
    pattern = input("Enter pattern type (3_swing_trap, pullback, breakout, etc.): ").strip()
    trend = input("Enter trend (uptrend, downtrend, sideways): ").strip()

    price_data = {}
    try:
        price_data["current_price"] = float(input("Enter current price: "))
        price_data["recent_high"] = float(input("Enter recent high: "))
        price_data["recent_low"] = float(input("Enter recent low: "))
    except ValueError:
        print("❌ Invalid price input")
        return

    print("\n🔄 Analyzing pattern...\n")
    response = assistant.get_pattern_analysis(pattern, trend, price_data)
    print(f"✅ Analysis:\n{response}\n")


def entry_rules(assistant: YTCTradingAssistant):
    """Get entry rules."""
    print("\n📋 Entry Rules")
    setup_type = input("Enter setup type (pullback, 3-swing-trap, etc.): ").strip()
    direction = input("Enter direction (long, short): ").strip()

    print("\n🔄 Retrieving entry rules...\n")
    response = assistant.get_entry_rules(setup_type, direction)
    print(f"✅ Entry Rules:\n{response}\n")


def fibonacci_strategy(assistant: YTCTradingAssistant):
    """Get Fibonacci strategy."""
    print("\n📊 Fibonacci Retracement Strategy")
    print("🔄 Retrieving strategy...\n")
    response = assistant.get_fibonacci_strategy()
    print(f"✅ Strategy:\n{response}\n")


def stop_loss_guidance(assistant: YTCTradingAssistant):
    """Get stop loss guidance."""
    print("\n🛑 Stop Loss Guidance")
    setup_type = input("Enter setup type: ").strip()

    try:
        entry_price = float(input("Enter entry price: "))
    except ValueError:
        print("❌ Invalid entry price")
        return

    structure = {}
    try:
        structure["support"] = float(input("Enter support level: "))
        structure["resistance"] = float(input("Enter resistance level: "))
    except ValueError:
        print("❌ Invalid structure levels")
        return

    print("\n🔄 Getting stop loss guidance...\n")
    response = assistant.get_stop_loss_guidance(setup_type, entry_price, structure)
    print(f"✅ Stop Loss Guidance:\n{response}\n")


def risk_management(assistant: YTCTradingAssistant):
    """Get risk management rules."""
    print("\n💰 Risk Management Rules")
    print("🔄 Retrieving rules...\n")
    response = assistant.get_risk_management_rules()
    print(f"✅ Risk Management:\n{response}\n")


def validate_setup(assistant: YTCTradingAssistant):
    """Validate a trading setup."""
    print("\n✔️  Setup Validation")
    setup_data = {}

    setup_data["pattern_type"] = input("Enter pattern type: ").strip()
    setup_data["trend"] = input("Enter trend (uptrend/downtrend): ").strip()

    try:
        setup_data["entry_price"] = float(input("Enter entry price: "))
        setup_data["stop_loss"] = float(input("Enter stop loss: "))
    except ValueError:
        print("❌ Invalid prices")
        return

    # Get target prices
    targets_str = input("Enter targets (comma-separated): ").strip()
    setup_data["targets"] = [float(t.strip()) for t in targets_str.split(",") if t.strip()]

    # Get supporting factors
    factors_str = input("Enter supporting factors (comma-separated): ").strip()
    setup_data["supporting_factors"] = [f.strip() for f in factors_str.split(",") if f.strip()]

    print("\n🔄 Validating setup...\n")
    result = assistant.validate_setup(setup_data)

    print(f"✅ Validation Result:")
    print(f"   Validated: {'Yes ✓' if result['validated'] else 'No ✗'}")
    print(f"\n   Analysis:\n{result['analysis']}\n")


def main():
    """Main CLI loop."""
    print_header()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set in .env file")
        print("Please add your OpenAI API key to continue.")
        sys.exit(1)

    print("🚀 Initializing YTC Trading Assistant...\n")
    assistant = YTCTradingAssistant()

    if not assistant.client:
        print("❌ Failed to initialize assistant")
        sys.exit(1)

    print("✅ Assistant ready!\n")
    print_menu()

    while True:
        try:
            choice = input("Enter command (or 'help' for menu): ").strip().lower()

            if choice == "exit" or choice == "q":
                print("\n👋 Goodbye!\n")
                break

            elif choice == "help":
                print_menu()

            elif choice == "1":
                query_ytc_method(assistant)

            elif choice == "2":
                pattern_analysis(assistant)

            elif choice == "3":
                entry_rules(assistant)

            elif choice == "4":
                fibonacci_strategy(assistant)

            elif choice == "5":
                stop_loss_guidance(assistant)

            elif choice == "6":
                risk_management(assistant)

            elif choice == "7":
                validate_setup(assistant)

            else:
                print(f"❓ Unknown command: '{choice}'. Type 'help' for menu.")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
