"""
PLANNER MODULE — The Brain of Demo Factory
==========================================
Input : A client problem statement (string)
Output: A JSON experiment plan (dict)

Uses ONLY Groq models — proven working from Day 2.
"""

import os, json, re, time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- THE PHONE (same single client as Day 2) ---
groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Adding nvidia_client back
nvidia_client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)

# UPDATE AVAILABLE_MODELS — replace deepseek-r1 with your actual model
AVAILABLE_MODELS = [
    {
        "name":  "llama-70b",
        "model": "llama-3.3-70b-versatile",
        "client": groq_client,
        "note":  "Most accurate · 2648ms · Complex tasks"
    },
    {
        "name":  "llama-8b",
        "model": "llama-3.1-8b-instant",
        "client": groq_client,
        "note":  "Fastest · 320ms · Simple tasks"
    },
    {
        "name":  "qwen-32b",
        "model": "qwen/qwen3-32b",
        "client": groq_client,
        "note":  "Detailed reasoning · 2215ms"
    },
    {
        "name":  "deepseek-v4",
        "model": "deepseek-ai/deepseek-v4-flash",
        "client": nvidia_client,
        "note":  "NVIDIA · DeepSeek V4 · 12854ms"
    },
]

# --- EXACT clean_json FROM DAY 2 (no changes) ---
def clean_json(text: str) -> dict:
    """
    Extracts and parses JSON from text, completely ignoring markdown backticks,
    thinking tags, and any conversational filler words.
    (Your battle-tested function from Day 2)
    """
    # 1. Strip out thinking/thought blocks
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"<thought>.*?</thought>", "", cleaned, flags=re.DOTALL)

    # 2. Find the mathematical boundaries of the JSON object
    start_idx = cleaned.find("{")
    end_idx   = cleaned.rfind("}")

    # 3. If no brackets found, not JSON
    if start_idx == -1 or end_idx == -1 or start_idx > end_idx:
        return {"error": "No valid JSON object found in response", "raw": text[:200]}

    # 4. Slice out exactly the JSON block
    json_str = cleaned[start_idx:end_idx + 1]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {e}", "raw": text[:200]}


# --- THE PLANNER FUNCTION ---
def generate_plan(problem_statement: str) -> dict:
    """
    Takes any client problem statement.
    Returns a complete JSON experiment plan.

    Example:
        plan = generate_plan("Can AI summarise medical reports?")
        print(plan["task_type"])        # "summarisation"
        print(plan["suggested_prompt"]) # "Summarise this report in..."
    """

    # NOTE: Double curly brackets {{ }} in f-strings
    # Single { } = Python variable
    # Double {{ }} = literal curly bracket in the output string
    meta_prompt = f"""
You are an AI experimentation expert working in a rapid innovation team.

A client has asked: "{problem_statement}"

Your job is to design a quick benchmark experiment to answer this.

You have these 4 models available (choose 3 for the experiment):
- llama-70b    → most accurate, 2.6s response, use for complex tasks
- llama-8b     → fastest (0.3s), use for simple tasks only
- qwen-32b     → good at detailed explanations, 2.2s response
- deepseek-v4  → deep V4 reasoning via NVIDIA, very slow (12.8s), use sparingly

Return ONLY a valid JSON object with EXACTLY these fields:

{{
  "task_type": "one of: classification, extraction, summarisation, generation, sql, qa",
  "models_to_test": ["pick exactly 3 from: llama-70b, llama-8b, qwen-32b, deepseek-v4"],
  "suggested_prompt": "the exact prompt to send each model — use {{{{input}}}} as placeholder for the test sample",
  "metrics": ["pick from: json_valid, accuracy, latency_ms, coherence"],
  "n_samples": 20,
  "rationale": "one sentence explaining your model and metric choices"
}}

Rules:
- suggested_prompt MUST contain the placeholder {{{{input}}}}
- Pick models that match the task complexity
- Return NOTHING outside the JSON object
"""

    print(f"\n📋 Generating plan for: '{problem_statement}'")
    print(f"   Thinking...", end="", flush=True)

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Best quality for planning
            messages=[{"role": "user", "content": meta_prompt}],
            temperature=0,   # Same plan every run
            max_tokens=600
        )

        raw_text = response.choices[0].message.content
        plan     = clean_json(raw_text)

        if "error" in plan:
            print(f" ✗ JSON parse failed")
            print(f"   Raw: {plan.get('raw', '')}")
            return plan

        # Add metadata
        plan["problem_statement"]      = problem_statement
        plan["model_used_for_planning"] = "llama-3.3-70b-versatile"

        print(f" ✓ Done!")
        return plan

    except Exception as e:
        print(f" ✗ API Error: {e}")
        return {"error": str(e)}


# --- SAVE PLAN ---
def save_plan(plan: dict, path: str = "experiments/plan.json"):
    os.makedirs("experiments", exist_ok=True)
    with open(path, "w") as f:
        json.dump(plan, f, indent=2)
    print(f"   💾 Saved → {path}")


# --- DISPLAY PLAN ---
def display_plan(plan: dict):
    print("\n" + "=" * 55)
    print("  EXPERIMENT PLAN")
    print("=" * 55)

    if "error" in plan:
        print(f"  ❌ Error: {plan['error']}")
        return

    print(f"  Problem   : {plan.get('problem_statement', 'N/A')}")
    print(f"  Task type : {plan.get('task_type', 'N/A')}")
    print(f"  Models    : {', '.join(plan.get('models_to_test', []))}")
    print(f"  Metrics   : {', '.join(plan.get('metrics', []))}")
    print(f"  Samples   : {plan.get('n_samples', 'N/A')}")
    print(f"  Rationale : {plan.get('rationale', 'N/A')}")
    print(f"\n  Prompt template:")
    print(f"  {plan.get('suggested_prompt', 'N/A')}")
    print("=" * 55)