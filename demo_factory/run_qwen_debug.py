import os, json, runpy

base_dir = os.path.dirname(__file__)
samples_path = os.path.join(base_dir, "samples.json")
with open(samples_path) as f:
    samples = json.load(f)

# Load runner.py as a module dict (avoids package import issues)
runner_mod = runpy.run_path(os.path.join(base_dir, "runner.py"))
call_model = runner_mod["call_model"]
wrap_for_json = runner_mod["wrap_for_json"]

print("Running qwen-32b on first 3 samples (raw + parsed):\n")
for i, sample in enumerate(samples[:3], start=1):
    prompt = wrap_for_json(f"Classify the following email as spam or not spam: {sample}", "classification")
    result = call_model("qwen-32b", prompt)
    print(f"--- Sample {i} ---")
    print("Sample text:\n", sample)
    print("\nRAW OUTPUT:\n", result.get("output"))
    print("\nPARSED:\n", result.get("parsed"))
    print()
