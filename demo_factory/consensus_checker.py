"""
CONSENSUS CHECKER — Models Cross-Check Each Other
===================================================
No ground truth needed. Instead of comparing to a "correct answer,"
we check how often models AGREE with each other.

Logic:
- If 2 out of 3 models say "spam" and 1 says "not spam" 
  → majority = spam, the 1 model is flagged as an outlier
- Agreement rate = how often a model matches the majority vote
- A model with LOW agreement rate is likely making more mistakes
  (assuming most models tend to get things right most of the time)

This becomes your "accuracy proxy" when you have no ground truth.
"""

import pandas as pd
import ast
from collections import Counter


def extract_label(output_str, label_field: str = "classification") -> str:
    """
    Extract the predicted label from the model's JSON output string.

    IMPORTANT: Not all models follow the exact field name requested in
    the prompt. E.g. we ask for "classification" but qwen-32b sometimes
    returns "label" instead — same value, different key. This function
    checks a list of common alternate field names before giving up.
    """
    # Common alternate names models substitute for the requested field
    possible_fields = [
        label_field,       # the field name we actually asked for
        "label",
        "classification",
        "class",
        "category",
        "result",
        "sentiment",
        "answer",
    ]

    # Accept already-parsed dicts too
    if isinstance(output_str, dict):
        for field in possible_fields:
            if field in output_str and output_str[field]:
                return str(output_str[field]).lower().strip().rstrip('.')

    try:
        parsed = ast.literal_eval(output_str)
        for field in possible_fields:
            if field in parsed and parsed[field]:
                return str(parsed[field]).lower().strip().rstrip('.')
    except Exception:
        pass

    # Fallback: regex search across all possible field names
    import re
    for field in possible_fields:
        pattern = rf"['\"]{field}['\"]\s*:\s*['\"]([^'\"]+)['\"]"
        match = re.search(pattern, output_str, re.IGNORECASE)
        if match:
            return match.group(1).lower().strip().rstrip('.')

    return "PARSE_ERROR"


def build_consensus_table(csv_path: str, label_field: str = "classification") -> pd.DataFrame:
    """
    Reads the results CSV and builds a wide table:
    one row per sample, one column per model, showing each model's answer.

    Example output:
        sample_id | llama-70b | llama-8b | qwen-32b | majority | agreement
        1         | spam      | spam     | spam     | spam     | 3/3
        2         | spam      | not spam | spam     | spam     | 2/3
    """
    df = pd.read_csv(csv_path)
    df["predicted"] = df["output"].apply(lambda x: extract_label(x, label_field))

    # Pivot: one row per sample, one column per model
    pivot = df.pivot(index="sample_id", columns="model", values="predicted")

    # For each sample, find majority vote across all models
    def get_majority(row):
        votes = Counter(row.dropna())
        if not votes:
            return "NO_VALID_VOTES", 0
        majority_label, count = votes.most_common(1)[0]
        total = len(row.dropna())
        return majority_label, f"{count}/{total}"

    results = pivot.apply(get_majority, axis=1)
    pivot["majority"]   = results.apply(lambda x: x[0])
    pivot["agreement"]  = results.apply(lambda x: x[1])

    return pivot


def calculate_model_agreement_rates(consensus_table: pd.DataFrame) -> pd.DataFrame:
    """
    For each model, calculate: what % of the time did THIS model's
    answer match the majority vote?

    A model with a LOW agreement rate is likely the one making mistakes
    (assuming most models get things right most of the time — the
    "wisdom of crowds" assumption).
    """
    model_columns = [
        col for col in consensus_table.columns
        if col not in ["majority", "agreement"]
    ]

    agreement_rates = {}
    for model in model_columns:
        # Exclude PARSE_ERROR / empty values from denominator
        valid_mask = consensus_table[model].apply(lambda x: x not in [None, "", "PARSE_ERROR"])
        valid_total = int(valid_mask.sum())
        matches = int(((consensus_table[model] == consensus_table["majority"]) & valid_mask).sum())
        agreement_rates[model] = round((matches / valid_total) * 100, 1) if valid_total > 0 else 0

    result_df = pd.DataFrame(
        list(agreement_rates.items()),
        columns=["model", "agreement_rate_pct"]
    ).sort_values("agreement_rate_pct", ascending=False)

    return result_df


def find_disagreement_cases(consensus_table: pd.DataFrame) -> pd.DataFrame:
    """
    Returns only the samples where models DISAGREED (agreement < total models).
    These are your "interesting" cases worth manually reviewing —
    instead of reviewing all 20 samples, you only need to check
    the ones where models disagreed.
    """
    model_columns = [
        col for col in consensus_table.columns
        if col not in ["majority", "agreement"]
    ]
    n_models = len(model_columns)

    def is_disagreement(agreement_str):
        matched, total = agreement_str.split("/")
        return int(matched) < int(total)

    disagreements = consensus_table[
        consensus_table["agreement"].apply(is_disagreement)
    ]
    return disagreements


def full_consensus_report(csv_path: str, label_field: str = "classification"):
    """
    Runs the complete consensus analysis and prints a full report.
    This is your main function — call this one.
    """
    print("=" * 60)
    print("  CROSS-MODEL CONSENSUS REPORT")
    print("  (No ground truth used — models verify each other)")
    print("=" * 60)

    consensus_table = build_consensus_table(csv_path, label_field)

    print("\n📊 Full consensus table:")
    print(consensus_table.to_string())

    agreement_rates = calculate_model_agreement_rates(consensus_table)
    print("\n📈 Agreement rate per model (higher = more trustworthy):")
    print(agreement_rates.to_string(index=False))

    disagreements = find_disagreement_cases(consensus_table)
    print(f"\n⚠️  {len(disagreements)} sample(s) where models disagreed:")
    if len(disagreements) > 0:
        print(disagreements.to_string())
        print(f"\n   👉 Manually verify ONLY these {len(disagreements)} samples")
        print(f"      instead of all {len(consensus_table)} — saves time!")
    else:
        print("   ✅ Perfect agreement across all models on all samples!")

    # The recommendation
    most_trusted = agreement_rates.iloc[0]
    print(f"\n📌 RECOMMENDATION:")
    print(f"   Most consistent with group consensus: {most_trusted['model']} "
          f"({most_trusted['agreement_rate_pct']}% agreement rate)")
    print(f"   ⚠️  Note: High agreement ≠ guaranteed correct — it means")
    print(f"      this model agrees with the majority most often.")

    # Save outputs
    consensus_table.to_csv("results/consensus_table.csv")
    agreement_rates.to_csv("results/agreement_rates.csv", index=False)
    print(f"\n💾 Saved:")
    print(f"   - results/consensus_table.csv")
    print(f"   - results/agreement_rates.csv")

    return consensus_table, agreement_rates, disagreements


if __name__ == "__main__":
    # Change label_field to match your task:
    # "classification" for spam, "label" for urgent/not urgent, etc.
    full_consensus_report(
        csv_path="results/day04_results.csv",
        label_field="classification"
    )