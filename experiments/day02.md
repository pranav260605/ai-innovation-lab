# Day 2: Multi-Model Benchmarking

* **Fixed Hidden Encoding Bugs:** I learned how to spot and fix UTF-16 file encoding errors that corrupt `.env` files, ensuring my API keys load securely without crashing the script.
* **Built a Multi-Client Architecture:** I set up dual API clients (Groq and NVIDIA) and structured my models into a Python dictionary list, allowing me to easily swap and route requests to different AIs.
* **Engineered Bulletproof JSON Parsing:** I used regex and bracket-hunting (`{` and `}`) to automatically strip away DeepSeek's `<think>` tags and Qwen's conversational filler so my code never breaks on extraction.
* **Mastered Precision Benchmarking:** I locked my API calls to `temperature=0` for fair testing and used `time.perf_counter()` to track true, sub-second hardware latency for each model.
* **Automated Data Collection:** I created a loop that respects API rate limits (`time.sleep()`), gracefully catches server-side 503 errors, and formats the final results into a clean Pandas table and CSV file.