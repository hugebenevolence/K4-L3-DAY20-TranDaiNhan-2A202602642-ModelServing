"""Run the same five deterministic questions against a served quantization."""
import argparse
import json
from pathlib import Path

import httpx


QUESTIONS = [
    "Define TTFT and TPOT in one sentence each.",
    "Why can 2-bit quantization use less memory but fail to decode faster?",
    "Explain what PagedAttention stores in pages and why.",
    "What does goodput at a latency SLO count?",
    "When does continuous batching admit a new request?",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    rows = []
    for question in QUESTIONS:
        response = httpx.post(
            f"{args.base_url}/v1/chat/completions",
            json={"model": "local", "messages": [{"role": "user", "content": question}],
                  "max_tokens": 128, "temperature": 0},
            timeout=120,
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
        rows.append({"question": question, "answer": answer})
        print(f"Q: {question}\nA: {answer}\n")
    output = Path("benchmarks") / f"bonus-quality-{args.label}.json"
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
