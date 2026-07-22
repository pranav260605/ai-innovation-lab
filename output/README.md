## Overview
This AI benchmark evaluates the ability of various models to detect spam emails through a classification task. The goal is to determine the most effective model for this specific use case.

## How to Run
To replicate the results, run the benchmark with the following models: llama-70b, llama-8b, and qwen-32b. The task involves classifying email samples as spam or not spam.

## Results
The benchmark tested the three models on a set of email samples. The results showed that:
- llama-70b achieved 95.0% consensus agreement
- The average latency for llama-70b was 388ms
- JSON success rate for llama-70b was 100.0%
- 5 out of 20 samples had model disagreement, indicating a need for manual review

## Recommendation
Based on the results, we recommend using the **llama-70b** model for spam email detection. Its high consensus agreement and low latency make it the most suitable choice for this task. However, it is worth noting that 25% of the samples (5 out of 20) had model disagreement, suggesting that manual review of these cases is necessary to ensure accuracy.