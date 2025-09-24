"""
qa_agent.py
This module implements the core logic for analysing e-commerce customer
support calls using large language models (LLMs). Prompts live in
`prompts.py` and are passed to a chosen LLM. If no OpenAI API key is
available, a heuristic fallback runs instead.
"""

import os
from dataclasses import dataclass, asdict
from typing import Optional, Dict
from openai import OpenAI, OpenAIError

import prompts

# Load environment variables from .env file if it exists
def _load_env():
    """Load environment variables from .env file if present."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

_load_env()


@dataclass
class CallAnalysis:
    call_id: Optional[str]
    summary: str
    classification: str
    improvements: str


# ---------------------------------------------------------------------
# Safe OpenAI initialization
# ---------------------------------------------------------------------

def _get_client():
    """Return OpenAI client if API key is present, else None."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        return OpenAI(api_key=api_key)
    except OpenAIError:
        return None


client = _get_client()


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _call_openai(prompt: str, model: str = "gpt-4o-mini") -> str:
    """Call OpenAI API with the given prompt text."""
    if client is None:
        raise RuntimeError("WARNING: No valid API key detected. Falling back to heuristics.")
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


def _heuristic_analysis(transcript: str, call_id: Optional[str] = None) -> Dict:
    """Rule-based backup if OpenAI is not available."""
    text = transcript.lower()

    # detect intent
    if "order" in text:
        intent = "Order status"
    elif "return" in text or "refund" in text:
        intent = "Return / Refund"
    elif "membership" in text:
        intent = "Membership"
    elif "size" in text:
        intent = "Product question"
    else:
        intent = "General inquiry"

    # detect escalation / success
    escalated = any(word in text for word in ["transfer", "connect", "escalate"])
    successful = ("thank you" in text or "great" in text or "resolved" in text) and not escalated

    if not escalated and successful:
        outcome = "Automated - Successful"
    elif not escalated:
        outcome = "Automated - Partially Successful"
    elif escalated and successful:
        outcome = "Escalated - Partially Successful"
    else:
        outcome = "Escalated - Unsuccessful"

    improvements = [
        "Provide as much useful info as possible before escalation.",
        "Acknowledge customer frustration and explain escalation clearly.",
    ]

    return {
        "call_id": call_id,
        "summary": f"Heuristic analysis - intent: {intent}, outcome: {outcome}.",
        "classification": outcome,
        "improvements": improvements,
    }


# ---------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------

def analyze_transcript(transcript: str, call_id: Optional[str] = None, model: str = None) -> Dict:
    """
    Analyse a transcript and return dict with summary, classification,
    and improvement suggestions. Uses LLM if available, else heuristics.
    """
    if model is None:
        model = "gpt-4o-mini"

    try:
        # Step 1: summarise
        summary = _call_openai(prompts.SUMMARY_PROMPT.format(transcript=transcript), model=model)

        # Step 2: classify
        classification = _call_openai(
            prompts.CLASSIFICATION_PROMPT.format(summary=summary), model=model
        )

        # Step 3: suggest improvements
        improvements = _call_openai(
            prompts.IMPROVEMENT_PROMPT.format(summary=summary, classification=classification),
            model=model,
        )

        analysis = CallAnalysis(
            call_id=call_id,
            summary=summary,
            classification=classification,
            improvements=improvements,
        )
        return asdict(analysis)

    except Exception as e:
        print(f"WARNING: Falling back to heuristics due to error: {e}")
        return _heuristic_analysis(transcript, call_id=call_id)
