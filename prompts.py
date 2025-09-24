"""
prompts.py
Prompt templates for QA analysis of customer support transcripts.
"""

# Prompt 1 – Summarize
SUMMARY_PROMPT = """You are a QA assistant. Summarize the following customer support call.
Focus on:
- The customer’s intent
- The AI agent’s actions
- Whether the issue was resolved or escalated

Transcript:
{transcript}
"""

# Prompt 2 – Classification
CLASSIFICATION_PROMPT = """Based on this summary, classify the call outcome into ONE of the following:
- Automated – Successful
- Automated – Partially Successful
- Escalated – Partially Successful
- Escalated – Unsuccessful

Summary:
{summary}

Answer with ONLY the classification text.
"""

# Prompt 3 – Improvement suggestions
IMPROVEMENT_PROMPT = """You are a QA reviewer. Based on the call summary and classification, suggest
2–3 concrete improvements for the AI agent’s behavior.

Summary:
{summary}

Classification:
{classification}

Write clear bullet points.
"""
