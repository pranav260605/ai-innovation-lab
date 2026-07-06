import os
import time
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd

load_dotenv() #this opens my .env file to get my secret passwords

# --- STEP 1: THE PHONES (Clients) ---
groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

nvidia_client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)

# --- This is something like my phone book(my models list) ---
# --- STEP 2: THE PHONEBOOK (Models List) ---
MODELS = [
    {
        "name":   "Llama-70B",
        "client": groq_client,
        "model":  "llama-3.3-70b-versatile",
        "note":   "Meta · Best quality"
    },
    {
        "name":   "Llama-8B",
        "client": groq_client,
        "model":  "llama-3.1-8b-instant",
        "note":   "Meta · Fastest"
    },
    {
        "name":   "Qwen-3-32B",
        "client": groq_client,
        "model":  "qwen/qwen3-32b",
        "note":   "Alibaba · Advanced Reasoning"
    },
    {
        "name":   "DeepSeek-V4",
        "client": nvidia_client,
        "model":  "deepseek-ai/deepseek-v4-flash",
        "note":   "NVIDIA · DeepSeek V4 Reasoning"
    },
]

import json
import re

# --- the adv.json clearer ---
def clean_json(text: str) -> dict:
    """
    Extracts and parses JSON from text, completely ignoring markdown backticks,
    thinking tags, and any conversational filler words at the beginning or end.
    """
    # 1. Strip out any potential thinking or thought blocks
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"<thought>.*?</thought>", "", cleaned, flags=re.DOTALL)
    
    # 2. Find the mathematical boundaries of the JSON object
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    
    # 3. If there are no brackets, it's definitely not JSON
    if start_idx == -1 or end_idx == -1 or start_idx > end_idx:
        return {"error": "No valid JSON object found in response", "raw": text[:200]}
        
    # 4. Slice out exactly the JSON block and ignore everything else
    json_str = cleaned[start_idx:end_idx + 1]
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {e}", "raw": text[:200]}
    
    # --- STEP 4: THE BENCHMARKING ENGINE ---
def call_model(model_config: dict, prompt: str) -> dict:
    """
    Call one model, measure how fast it replies, and clean the JSON.
    """
    print(f"  → Calling {model_config['name']}...", end="", flush=True)
    
    # 1. Start the high-precision stopwatch
    start = time.perf_counter()
    
    try:
        # 2. Make the API call using the specific client for this model
        response = model_config["client"].chat.completions.create(
            model=model_config["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=0,      # Lock in the most logical, non-random answer
            max_tokens=500      # Give DeepSeek enough room to <think>
        )
        
        # 3. Stop the stopwatch
        end = time.perf_counter()
        
        raw_text = response.choices[0].message.content
        latency_ms = round((end - start) * 1000)
        tokens = response.usage.total_tokens
        
        # 4. Clean and parse the response
        parsed = clean_json(raw_text)
        
        print(f" ✓ {latency_ms}ms | {tokens} tokens")
        
        return {
            "model":      model_config["name"],
            "latency_ms": latency_ms,
            "tokens":     tokens,
            "parsed":     parsed,
            "error":      parsed.get("error")
        }
        
    except Exception as e:
        # If the API crashes (e.g., network issue), catch it without crashing the script
        print(f" ✗ ERROR: {e}")
        return {
            "model":      model_config["name"],
            "latency_ms": 0,
            "tokens":     0,
            "parsed":     {},
            "error":      str(e)
        }
        
        # --- STEP 5: THE TEST PROMPT ---
# We are asking all 4 models to do the exact same job: Sentiment Classification.
PROMPT = """Classify the sentiment of this customer review.
Return ONLY valid JSON with these exact fields:
- sentiment: exactly "positive" or "negative" or "neutral"
- confidence: a number between 0.0 and 1.0
- reason: one sentence explaining your classification

Review: "The product arrived on time but the packaging was damaged.
The item itself works perfectly though."
"""

# --- STEP 6: AUTOMATION LOOP ---
def run_all_models(prompt: str) -> list:
    """Run the prompt across all models in the phonebook and respect rate limits."""
    results = []
    for i, model_config in enumerate(MODELS):
        result = call_model(model_config, prompt)
        results.append(result)
        
        # Pause for 2 seconds to avoid Groq/NVIDIA rate limits
        if i < len(MODELS) - 1:
            time.sleep(2)
            
    return results

# --- STEP 7: BUILD THE TABLE ---
def build_table(results: list) -> pd.DataFrame:
    """Convert raw results into a clean pandas DataFrame."""
    rows = []
    for r in results:
        parsed = r["parsed"]
        rows.append({
            "Model":       r["model"],
            "Latency(ms)": r["latency_ms"],
            "Tokens":      r["tokens"],
            "Sentiment":   parsed.get("sentiment", "PARSE_ERROR"),
            "Confidence":  parsed.get("confidence", "N/A"),
            "Reason":      parsed.get("reason", r.get("error", "N/A")),
            "JSON_OK":     "✓" if not r["error"] else "✗",
        })
    return pd.DataFrame(rows)

# --- STEP 8: SAVE TO CSV ---
def save_csv(df: pd.DataFrame, path: str = "results/day02_results.csv"):
    os.makedirs("results", exist_ok=True)
    df.to_csv(path, index=False)
    print(f"\n  💾 Saved to {path}")

# --- MAIN EXECUTION ---
def main():
    print("=" * 60)
    print("  DAY 2 — 4 Models, 1 Prompt, Full Comparison")
    print("=" * 60)
    print("\nRunning sentiment classification across 4 models...\n")

    results = run_all_models(PROMPT)
    df      = build_table(results)

    print("\n" + "=" * 60)
    print("  COMPARISON TABLE")
    print("=" * 60)
    print(df.to_string(index=False))

    save_csv(df)

if __name__ == "__main__":
    main()