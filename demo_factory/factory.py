import argparse, time
from planner import generate_plan, save_plan, display_plan
from runner import run
from html_generator import generate_html
from readme_generator import generate_readme

def main(problem):
    print(f"\n🏭 DEMO FACTORY starting for:")
    print(f"   '{problem}'\n")

    # Step 1: Plan
    plan = generate_plan(problem)
    if "error" in plan:
        print("❌ Planning failed. Stopping.")
        return
    display_plan(plan)
    save_plan(plan, "experiments/latest_plan.json")

    # Step 2: Run benchmark
    time.sleep(2)
    run("experiments/latest_plan.json")

    # Step 3: Generate dashboard
    recommendation = generate_html(
        "results/day04_results.csv", plan
    )

    # Step 4: Generate README
    generate_readme(plan, recommendation)

    print(f"\n✅ DONE! Open output/dashboard.html in your browser.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem", required=True)
    args = parser.parse_args()
    main(args.problem)