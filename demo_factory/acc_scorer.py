import pandas as pd
import ast

# Your manual ground-truth labels for the 20 samples
# (you decide urgent/not_urgent by reading each one yourself)
GROUND_TRUTH = {
    1: "urgent",      2: "not_urgent",  3: "urgent",
    4: "not_urgent",  5: "urgent",      6: "not_urgent",
    7: "urgent",      8: "not_urgent",  9: "urgent",
    10: "not_urgent", 11: "urgent",     12: "not_urgent",
    13: "urgent",     14: "not_urgent", 15: "urgent",
    16: "not_urgent", 17: "urgent",     18: "not_urgent",
    19: "urgent",     20: "not_urgent",
}

def score():
    df = pd.read_csv("results/day04_results.csv")

    def extract_label(output_str):
        try:
            parsed = ast.literal_eval(output_str)
            return parsed.get("label", "").lower()
        except:
            return ""

    df["predicted"] = df["output"].apply(extract_label)
    df["actual"]    = df["sample_id"].map(GROUND_TRUTH)
    df["correct"]   = df["predicted"] == df["actual"]

    print("="*50)
    print("  ACCURACY BY MODEL")
    print("="*50)

    summary = df.groupby("model").agg(
        accuracy=("correct", "mean"),
        avg_latency=("latency_ms", "mean"),
        json_success=("json_valid", lambda x: (x=="✓").mean())
    ).reset_index()

    summary["accuracy"] = (summary["accuracy"]*100).round(1)
    summary["json_success"] = (summary["json_success"]*100).round(1)

    print(summary.to_string(index=False))

    # The Anand-style recommendation
    best = summary.sort_values("accuracy", ascending=False).iloc[0]
    fastest = summary.sort_values("avg_latency").iloc[0]

    print(f"\n📌 RECOMMENDATION:")
    print(f"   Most accurate: {best['model']} "
          f"({best['accuracy']}% accuracy)")
    print(f"   Fastest      : {fastest['model']} "
          f"({fastest['avg_latency']:.0f}ms avg)")

    df.to_csv("results/day05_scored.csv", index=False)
    print(f"\n💾 Saved → results/day05_scored.csv")

if __name__ == "__main__":
    score()