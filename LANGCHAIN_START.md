# LangChain Starter (Skeleton Only)

This repo already has the matcher logic. When you’re ready to add LangChain, follow these steps:

1) Install deps (pick your provider):
   - Base: `pip install langchain`
   - OpenAI example: `pip install langchain-openai`
   - Set your API key in env (e.g., `OPENAI_API_KEY`).

2) Use the starter script: `scripts/lc_match_summarizer.py`
   - Load an image (bytes).
   - Run your existing pipeline:
     - `extract_landmarks` -> `landmarks_to_features` -> `match_characters`
     - Attach `reasons` via `explain_match`
   - Feed `{matches, quality}` into a simple LangChain prompt and print the summary.

3) Keep it simple:
   - One LLM (low temperature) to summarize matches and note quality flags.
   - No agents/tool-chains needed at first.

File intentionally left as guidance only; no LangChain code is included so you can implement it step by step.
