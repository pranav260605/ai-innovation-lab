"""
TEST THE PLANNER
================
Run: python demo_factory/test_planner.py

Tests the Planner with 3 different problem types.
Saves 3 JSON plans to experiments/ folder.
"""

import time
from planner import generate_plan, save_plan, display_plan

# --- 3 DIFFERENT PROBLEMS TO TEST ---
# Each should produce a DIFFERENT task_type in the plan.
# Problem 1 → classification
# Problem 2 → extraction
# Problem 3 → summarisation
problems = [
    "Can AI classify whether customer support emails are urgent or not?",
    "Can AI extract payment terms from supplier contracts?",
    "Which AI model best summarises medical discharge reports?",
]

# --- MAIN ---
def main():
    print("=" * 55)
    print("  PLANNER TEST — 3 Problems, 3 JSON Plans")
    print("=" * 55)

    all_plans = []

    for i, problem in enumerate(problems, 1):
        print(f"\n{'─' * 55}")
        print(f"  TEST {i} of {len(problems)}")

        # Generate the plan
        plan = generate_plan(problem)

        # Display it in readable format
        display_plan(plan)

        # Save to its own JSON file
        save_plan(plan, f"experiments/plan_test_{i}.json")

        all_plans.append(plan)

        # Wait between calls — same pattern as Day 2
        if i < len(problems):
            print(f"\n   Waiting 3 seconds before next plan...")
            time.sleep(3)

    # --- SUMMARY ---
    print(f"\n{'=' * 55}")
    print(f"  SUMMARY")
    print(f"{'=' * 55}")

    for i, plan in enumerate(all_plans, 1):
        if "error" not in plan:
            print(f"  Plan {i}: {plan.get('task_type', 'N/A')} "
                  f"→ {', '.join(plan.get('models_to_test', []))}")
        else:
            print(f"  Plan {i}: ❌ Failed — {plan['error']}")

    print(f"\n✅ All plans saved to experiments/")
    print(f"   Open plan_test_1.json in VS Code and check the structure.")
    print(f"\nQuestions to answer in day03.md:")
    print(f"  - Did all 3 plans have different task_type?")
    print(f"  - Did suggested_prompt always contain {{input}}?")
    print(f"  - Did the Planner always pick exactly 3 models?")
    print(f"  - Did JSON parse cleanly all 3 times?")


if __name__ == "__main__":
    main()