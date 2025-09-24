"""
run_example.py

Run QA analysis on call transcripts.
- Use `--call call3` to analyze a single call.
- Use `--model gpt-4o` to pick a specific model.
- Defaults to gpt-4o-mini if not specified.
"""

import os
import argparse
from qa_agent import analyze_transcript

BASE_DIR = os.path.dirname(__file__)
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_transcripts")


def print_report(result: dict, model: str):
    """Pretty-print analysis results as a mini report."""
    print("=" * 60)
    print(f"Call ID: {result.get('call_id')}")
    print(f"Model: {model}")
    print("-" * 60)
    print(f"Outcome: {result.get('classification')}")
    print()
    print("Summary:")
    print(f"  {result.get('summary')}")
    print()
    print("Improvement Suggestions:")
    if isinstance(result.get("improvements"), list):
        for i, suggestion in enumerate(result["improvements"], start=1):
            print(f"  {i}. {suggestion}")
    else:
        print(f"  {result.get('improvements')}")
    print("=" * 60)
    print()


def main():
    parser = argparse.ArgumentParser(description="QA Voice Agent Analysis")
    parser.add_argument("--call", type=str, help="Which call to analyze (e.g., call1, call2, call3)")
    parser.add_argument("--model", type=str, default="gpt-4o-mini",
                        help="Which model to use (default: gpt-4o-mini). Examples: gpt-4o, gpt-4.5-preview")
    args = parser.parse_args()

    model = args.model
    call_id = args.call

    if call_id:
        path = os.path.join(SAMPLE_DIR, f"{call_id}.txt")
        if not os.path.exists(path):
            print(f"Transcript not found: {path}")
            return
        with open(path, "r", encoding="utf-8") as f:
            transcript = f.read()
        result = analyze_transcript(transcript, call_id=call_id, model=model)
        print_report(result, model)
    else:
        print(f"Analyzing all transcripts with {model}...\n")
        for filename in sorted(os.listdir(SAMPLE_DIR)):
            if filename.endswith(".txt"):
                call_id = filename.replace(".txt", "")
                with open(os.path.join(SAMPLE_DIR, filename), "r", encoding="utf-8") as f:
                    transcript = f.read()
                result = analyze_transcript(transcript, call_id=call_id, model=model)
                print_report(result, model)


if __name__ == "__main__":
    main()
