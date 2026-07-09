## Overview
This AI benchmark evaluates the ability of various models to detect spam emails through classification tasks. The goal is to determine the most effective model in terms of accuracy and latency.

## How to Run
To reproduce the results, run the benchmarking script with the following models: llama-70b, llama-8b, and qwen-32b. The script will test each model's ability to classify emails as spam or not.

## Results
The benchmarking results are as follows:
- llama-70b: Not recommended due to lower performance
- llama-8b: 100.0% JSON success rate with an average latency of 251ms
- qwen-32b: Not recommended due to lower performance

## Recommendation
Based on the results, we recommend using the **llama-8b** model for spam email detection. It achieved a **100.0%** JSON success rate with an average latency of **251ms**, making it the most efficient and accurate model tested. Its high accuracy and low latency make it suitable for real-time spam email detection applications.