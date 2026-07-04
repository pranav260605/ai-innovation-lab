import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()  # This magically loads your secret key from the .env file

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Test 1: Simple question
print("=== TEST 1: Simple question ===")
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "What is a SQL JOIN? One sentence."}],
    max_tokens=100
)
print(response.choices[0].message.content)

# Test 2: Ask for JSON (structured output)
print("\n=== TEST 2: JSON output ===")
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content":
        """Return ONLY valid JSON (no extra text) with these fields:
        - answer: one sentence explanation of SQL JOIN
        - example: one SQL example
        - difficulty: easy/medium/hard"""}],
    max_tokens=200
)

text = response.choices[0].message.content

# Clean the markdown formatting before reading
clean_text = text.replace("```json\n", "").replace("```json", "").replace("```", "").strip()

try:
    data = json.loads(clean_text)
    print(f"Answer: {data['answer']}")
    print(f"Example: {data['example']}")
    print(f"Difficulty: {data['difficulty']}")
except:
    print("JSON parse failed. Raw response:")
    print(text)

print("\n✅ Day 1 API setup complete! You can now talk to an LLM from Python.")