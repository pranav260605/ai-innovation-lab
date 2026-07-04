\# Day 01 — First API Call



\## What I built

\- Connected to the Groq API using the OpenAI Python SDK.

\- Made my first LLM API call using the Llama 3.3 70B model.

\- Got a structured JSON response back and successfully parsed it into readable data.



\## What I observed

\- The response time from the API(Llama 3.3 70B) was incredibly fast.

\- The AI returned perfect JSON, but wrapped it in decorative Markdown backticks (` ```json `), which caused a parsing error. 



\## What I learned

\- \*\*Why JSON is needed:\*\* JSON acts like organized stat boxes so the computer can easily read and extract specific data instead of guessing through a messy paragraph.

\- \*\*The JSON Error:\*\* The strict Python parser crashed because it tried to read the decorative Markdown "box" instead of the actual JSON data inside it.

\- \*\*The Fix:\*\* We rectified this by writing a command to strip away the Markdown formatting by using this code line (`clean\_text = text.replace...`) before asking Python to parse it.



\## Questions for tomorrow

\- How do I run this across 4 models automatically?

\- How do I measure latency accurately?

