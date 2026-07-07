# Day 03 — The Planner

## What I built
- planner.py — generate_plan() function using meta-prompting
- test_planner.py — tested on 3 different problem types
- 3 JSON plans saved to experiments/ folder

## Results
- Plan 1: classification → llama-70b, qwen-32b, llama-8b
- Plan 2: extraction → llama-70b, qwen-32b, llama-8b
- Plan 3: summarisation → llama-70b, qwen-32b, deepseek-v4
- All 3 task_types different ✅
- All prompts contain {input} placeholder ✅
- All 3 parsed to clean JSON ✅

## Key concept learned
- Meta-prompting: using an LLM to plan how to use other LLMs
- The Planner uses Llama 70B (most accurate from Day 2)
- temperature=0 means same plan every run — deterministic

## Day 4 Warning
- Prompt placeholder stores as {{input}} in JSON
- Use .replace("{{input}}", sample) in Runner — NOT .format()

## Questions for Day 4
- How does Runner read the plan and run the actual benchmark?
- How does it substitute {{input}} with real test data?