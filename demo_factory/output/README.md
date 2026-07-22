## Overview
This AI benchmark evaluates the ability of various models to detect spam emails through a classification task. The goal is to determine the most effective model for this specific use case.

## How to Run
To replicate the results, run the benchmark using the provided models: llama-70b, llama-8b, and qwen-32b. The task involves classifying email samples as spam or not spam.

## Results
The benchmark tested 20 email samples using the three models. The results showed that all 20 samples had model disagreement, indicating that manual review is necessary. The average latency and JSON success rates for each model were recorded.

## Recommendation
Based on the results, we recommend using the llama-8b model for spam email detection. It achieved a 95.0% consensus agreement with an average latency of 288ms and a 100.0% JSON success rate. While all samples had model disagreement, the llama-8b model demonstrated the best performance overall, making it the most suitable choice for this task. Manual review of the samples is still advised due to the model disagreement.