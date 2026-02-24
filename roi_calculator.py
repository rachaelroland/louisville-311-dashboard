#!/usr/bin/env python3
"""
311 AI Assistant - ROI Calculator
Calculates cost savings and ROI for prospective cities
"""

def calculate_roi(
    population,
    daily_calls=None,
    avg_handle_time_minutes=6,
    cost_per_call=5,
    agent_hourly_rate=25,
    deflection_rate=0.35,
    our_monthly_price=4000
):
    """
    Calculate ROI for a city implementing 311 AI Assistant

    Args:
        population: City population
        daily_calls: Average 311 calls per day (if None, estimate from population)
        avg_handle_time_minutes: Average time per call in minutes
        cost_per_call: Fully-loaded cost per call (agent time + overhead)
        agent_hourly_rate: Average agent hourly wage
        deflection_rate: % of calls expected to be deflected by AI (0.0-1.0)
        our_monthly_price: Monthly subscription price

    Returns:
        dict with detailed ROI calculations
    """

    # Estimate daily calls from population if not provided
    if daily_calls is None:
        # Industry rule of thumb: ~0.06-0.08% of population calls 311 per day
        # Mid-size city (100K-300K): 0.07%
        # Large city (300K+): 0.06%
        # Small city (<100K): 0.08%
        if population >= 300000:
            daily_calls = int(population * 0.0006)
        elif population >= 100000:
            daily_calls = int(population * 0.0007)
        else:
            daily_calls = int(population * 0.0008)

    # Calculate current state
    annual_calls = daily_calls * 365
    total_call_time_hours = (annual_calls * avg_handle_time_minutes) / 60
    agent_labor_cost = total_call_time_hours * agent_hourly_rate
    fully_loaded_cost = annual_calls * cost_per_call

    # Calculate with AI deflection
    calls_deflected = int(annual_calls * deflection_rate)
    calls_remaining = annual_calls - calls_deflected

    # Savings
    agent_time_saved_hours = (calls_deflected * avg_handle_time_minutes) / 60
    agent_cost_saved = agent_time_saved_hours * agent_hourly_rate
    total_cost_saved = calls_deflected * cost_per_call

    # Our cost
    our_annual_cost = our_monthly_price * 12

    # Net savings
    net_annual_savings = total_cost_saved - our_annual_cost

    # ROI
    roi_percentage = (net_annual_savings / our_annual_cost) * 100 if our_annual_cost > 0 else 0

    # Payback period (months)
    monthly_savings = total_cost_saved / 12
    payback_months = our_annual_cost / monthly_savings if monthly_savings > 0 else float('inf')

    return {
        # Inputs
        'population': population,
        'daily_calls': daily_calls,
        'avg_handle_time_minutes': avg_handle_time_minutes,
        'cost_per_call': cost_per_call,
        'agent_hourly_rate': agent_hourly_rate,
        'deflection_rate': deflection_rate,
        'our_monthly_price': our_monthly_price,

        # Current state
        'annual_calls': annual_calls,
        'total_call_time_hours': int(total_call_time_hours),
        'agent_labor_cost': int(agent_labor_cost),
        'fully_loaded_cost': int(fully_loaded_cost),

        # With AI
        'calls_deflected_per_day': int(calls_deflected / 365),
        'calls_deflected_per_year': calls_deflected,
        'calls_remaining': calls_remaining,
        'agent_time_saved_hours': int(agent_time_saved_hours),
        'agent_cost_saved': int(agent_cost_saved),
        'total_cost_saved': int(total_cost_saved),

        # Financial analysis
        'our_annual_cost': our_annual_cost,
        'net_annual_savings': int(net_annual_savings),
        'roi_percentage': round(roi_percentage, 1),
        'payback_months': round(payback_months, 1),

        # Equivalent metrics
        'fte_saved': round(agent_time_saved_hours / 2080, 2),  # 2080 hrs = 1 FTE year
        'monthly_savings': int(monthly_savings),
    }


def print_roi_report(results, city_name="Your City"):
    """
    Print a formatted ROI report
    """
    print("=" * 80)
    print(f"311 AI ASSISTANT - ROI ANALYSIS FOR {city_name.upper()}")
    print("=" * 80)
    print()

    print("📊 CURRENT STATE (Without AI)")
    print("-" * 80)
    print(f"  Population:                    {results['population']:,}")
    print(f"  Daily 311 calls:               {results['daily_calls']:,}")
    print(f"  Annual 311 calls:              {results['annual_calls']:,}")
    print(f"  Average handle time:           {results['avg_handle_time_minutes']} minutes")
    print(f"  Cost per call:                 ${results['cost_per_call']:.2f}")
    print()
    print(f"  Total call center hours/year:  {results['total_call_time_hours']:,} hours")
    print(f"  Agent labor cost:              ${results['agent_labor_cost']:,}/year")
    print(f"  Fully-loaded 311 cost:         ${results['fully_loaded_cost']:,}/year")
    print()

    print("🤖 WITH AI ASSISTANT")
    print("-" * 80)
    print(f"  Expected deflection rate:      {results['deflection_rate']*100:.0f}%")
    print(f"  Calls deflected per day:       {results['calls_deflected_per_day']:,}")
    print(f"  Calls deflected per year:      {results['calls_deflected_per_year']:,}")
    print(f"  Calls remaining:               {results['calls_remaining']:,}")
    print()
    print(f"  Agent time saved:              {results['agent_time_saved_hours']:,} hours/year")
    print(f"  Equivalent FTE saved:          {results['fte_saved']} full-time agents")
    print()

    print("💰 FINANCIAL IMPACT")
    print("-" * 80)
    print(f"  Cost savings from deflection:  ${results['total_cost_saved']:,}/year")
    print(f"  AI assistant cost:             ${results['our_annual_cost']:,}/year")
    print(f"                                 (${results['our_monthly_price']:,}/month)")
    print()
    print(f"  ✅ NET ANNUAL SAVINGS:          ${results['net_annual_savings']:,}")
    print(f"  ✅ ROI:                          {results['roi_percentage']:.1f}%")
    print(f"  ✅ PAYBACK PERIOD:               {results['payback_months']:.1f} months")
    print()

    # Assessment
    if results['roi_percentage'] >= 300:
        assessment = "🎉 EXCELLENT - Very strong ROI, easy to justify"
    elif results['roi_percentage'] >= 200:
        assessment = "✅ VERY GOOD - Strong business case"
    elif results['roi_percentage'] >= 100:
        assessment = "✅ GOOD - Positive ROI, recommend proceeding"
    elif results['roi_percentage'] >= 50:
        assessment = "⚠️  MODERATE - Positive but lower ROI"
    else:
        assessment = "❌ WEAK - May need to adjust pricing or deflection assumptions"

    print(f"📈 ASSESSMENT: {assessment}")
    print()

    print("=" * 80)


def print_comparison_table():
    """
    Print ROI comparison across different city sizes
    """
    print("=" * 80)
    print("ROI COMPARISON BY CITY SIZE")
    print("=" * 80)
    print()

    city_scenarios = [
        ("Small City", 75000, 60, 2000),
        ("Medium City", 200000, 140, 4000),
        ("Large City", 600000, 400, 5000),
        ("Major City", 1000000, 650, 8000),
    ]

    print(f"{'City Type':<15} {'Pop':<10} {'Calls/Day':<12} {'Price/Mo':<12} {'Annual Savings':<18} {'ROI':<8} {'Payback'}")
    print("-" * 100)

    for city_type, pop, calls, price in city_scenarios:
        results = calculate_roi(
            population=pop,
            daily_calls=calls,
            our_monthly_price=price,
            deflection_rate=0.35  # Conservative 35%
        )

        print(f"{city_type:<15} {pop:>9,} {calls:>11,} ${price:>10,} ${results['net_annual_savings']:>16,} {results['roi_percentage']:>6.0f}% {results['payback_months']:>6.1f}mo")

    print()
    print("Assumptions: 35% deflection rate, $5 cost/call, 6 min avg handle time")
    print("=" * 80)
    print()


# Example usage
if __name__ == "__main__":
    print()

    # Example 1: Louisville Metro (actual data)
    print("EXAMPLE 1: LOUISVILLE METRO (ACTUAL)")
    print()
    louisville_results = calculate_roi(
        population=617000,
        daily_calls=400,
        avg_handle_time_minutes=6,
        cost_per_call=5,
        agent_hourly_rate=25,
        deflection_rate=0.40,  # We're seeing 40% in Louisville
        our_monthly_price=5000
    )
    print_roi_report(louisville_results, "Louisville Metro, KY")

    print("\n" * 2)

    # Example 2: Lexington (pilot prospect)
    print("EXAMPLE 2: LEXINGTON, KY (PILOT PROSPECT)")
    print()
    lexington_results = calculate_roi(
        population=320000,
        daily_calls=220,  # Estimated
        our_monthly_price=4000  # Professional tier, 50% pilot discount
    )
    print_roi_report(lexington_results, "Lexington-Fayette, KY")

    print("\n" * 2)

    # Example 3: Comparison table
    print_comparison_table()

    # Save results to JSON for use in other tools
    import json
    with open('roi_examples.json', 'w') as f:
        json.dump({
            'louisville': louisville_results,
            'lexington': lexington_results
        }, f, indent=2)

    print("Results saved to roi_examples.json")
    print()
