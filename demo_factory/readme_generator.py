import os
from planner import groq_client  # reuse existing client

def generate_readme(plan, recommendation, output_path="output/README.md"):
    prompt = f"""Write a professional GitHub README for this AI benchmark:

Problem: {plan.get('problem_statement')}
Task type: {plan.get('task_type')}
Models tested: {', '.join(plan.get('models_to_test', []))}
Recommendation: {recommendation}

Include sections: ## Overview, ## How to Run, ## Results, ## Recommendation
Keep it under 250 words. Be specific with the numbers given."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )

    readme_text = response.choices[0].message.content

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(readme_text)

    print(f"  📝 README saved → {output_path}")
    return readme_text