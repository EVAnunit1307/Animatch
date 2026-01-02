"""
Starter for a LangChain-based matcher summarizer.

What to do next (you own this):
- Pick your LLM provider/model (e.g., OpenAI GPT-4o-mini).
- Install deps when ready: `pip install langchain langchain-openai` (or other provider).
- Wire this script to your matcher functions (extract_landmarks, landmarks_to_features,
  match_characters, explain_match) to produce a summary.

Suggested flow to implement:
1) Load image bytes.
2) Run extract_landmarks -> landmarks_to_features -> match_characters; attach reasons via explain_match.
3) Pass `{matches, quality}` into a simple LangChain prompt and print the summary.

This file intentionally contains no LangChain code yet so you can learn/implement it step by step.
"""


def main():
    print("TODO: implement LangChain summarizer here.")


if __name__ == "__main__":
    main()
