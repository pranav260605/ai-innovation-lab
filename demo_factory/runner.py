import os, json, re, time, argparse
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- SAME CLIENTS AS DAY 2 ---
groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
nvidia_client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)

# --- MODEL REGISTRY ---
MODEL_REGISTRY = {
    "llama-70b":    (groq_client,   "llama-3.3-70b-versatile"),
    "llama-8b":     (groq_client,   "llama-3.1-8b-instant"),
    "qwen-32b":     (groq_client,   "qwen/qwen3-32b"),
    "deepseek-v4":  (nvidia_client, "deepseek-ai/deepseek-v4-flash"),
}

# --- EXACT clean_json FROM DAY 2 ---
def clean_json(text):
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"<thought>.*?</thought>", "", cleaned, flags=re.DOTALL)
    start = cleaned.find("{")
    end   = cleaned.rfind("}")
    if start == -1 or end == -1 or start > end:
        return {"error": "No JSON found", "raw": text[:200]}
    try:
        return json.loads(cleaned[start:end+1])
    except json.JSONDecodeError as e:
        return {"error": str(e), "raw": text[:200]}

# --- CALL ONE MODEL ON ONE SAMPLE ---
# --- CALL ONE MODEL ON ONE SAMPLE ---
def call_model(model_key, prompt):
    client, model_name = MODEL_REGISTRY[model_key]
    start = time.perf_counter()
    try:
        # Define the arguments for the API call
        kwargs = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 800
        }
        
        # Enforce JSON mode for Groq models to prevent prose
        if client == groq_client:
            kwargs["response_format"] = {"type": "json_object"}

        r = client.chat.completions.create(**kwargs)
        
        end      = time.perf_counter()
        raw      = r.choices[0].message.content
        parsed   = clean_json(raw)
        return {
            "latency_ms": round((end - start) * 1000),
            "tokens":     r.usage.total_tokens,
            "output":     raw,
            "parsed":     parsed,
            "json_valid": "✓" if "error" not in parsed else "✗"
        }
    except Exception as e:
        return {
            "latency_ms": 0, "tokens": 0,
            "output": "",   "parsed": {},
            "json_valid": "✗"
        }
def wrap_for_json(task_prompt, task_type):
    """Safety net — forces JSON. The bypass has been removed."""
    
    if task_type == "classification":
        schema = '{"label": "...", "confidence": 0.0-1.0}'
    elif task_type == "extraction":
        schema = '{"extracted_fields": {...}, "confidence": 0.0-1.0}'
    else:
        schema = '{"result": "...", "confidence": 0.0-1.0}'

    return f"""{task_prompt}

IMPORTANT: Return ONLY valid JSON. No explanation, no markdown.
Format exactly like this: {schema}"""
# --- RUNNER CORE ---
def run(plan_path):
    # Load plan
    with open(plan_path) as f:
        plan = json.load(f)

    # Load samples
    samples_path = os.path.join(
        os.path.dirname(__file__), "samples.json"
    )
    with open(samples_path) as f:
        samples = json.load(f)

    prompt_template = plan["suggested_prompt"]
    models          = plan["models_to_test"]
    total_calls     = len(samples) * len(models)

    print(f"\n🚀 Runner starting")
    print(f"   Plan     : {plan['task_type']}")
    print(f"   Models   : {', '.join(models)}")
    print(f"   Samples  : {len(samples)}")
    print(f"   Total    : {total_calls} API calls\n")

    rows    = []
    call_no = 0

    for model_key in models:
        print(f"  [{model_key}]")
        for i, sample in enumerate(samples):
            call_no += 1

            # ⚠ KEY LINE — use .replace() not .format()
            filled = prompt_template.replace("{{input}}", sample)
            filled = wrap_for_json(filled, plan["task_type"])
            result = call_model(model_key, filled)

            if model_key == "qwen-32b":
                print(f"    RAW qwen output: {result['parsed']}")

            rows.append({
                "model":      model_key,
                "sample_id":  i + 1,
                "sample":     sample[:60] + "...",
                "latency_ms": result["latency_ms"],
                "tokens":     result["tokens"],
                "json_valid": result["json_valid"],
                "output": str(result["parsed"]),   # no truncation — needed for consensus checking
            })

            print(f"    Sample {i+1:02d}/{len(samples)} "
                  f"{result['json_valid']} "
                  f"{result['latency_ms']}ms")

            time.sleep(2)

    # Save CSV
    df = pd.DataFrame(rows)
    os.makedirs("results", exist_ok=True)
    out = "results/day04_results.csv"
    df.to_csv(out, index=False)

    # Summary
    print(f"\n{'='*50}")
    print(f"  SUMMARY")
    print(f"{'='*50}")
    summary = df.groupby("model").agg(
        avg_latency=("latency_ms", "mean"),
        json_ok    =("json_valid", lambda x: (x=="✓").sum())
    ).reset_index()
    print(summary.to_string(index=False))
    print(f"\n  💾 Saved → {out}")
    print(f"  ✅ {total_calls} calls complete")

# --- RUN ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", default="experiments/plan_test_1.json")
    args = parser.parse_args()
    run(args.plan)