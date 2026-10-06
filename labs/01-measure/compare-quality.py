#!/usr/bin/env python3
"""Ask both quantizations the same question and save their actual answers."""
from __future__ import annotations

import argparse
import pathlib
import sys
import time

import httpx

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "lib"))
import labkit

DEFAULT_PROMPT = (
    "Respond in exactly three short lines, without an introduction, headings "
    "or LaTeX. A request emits its first token at 200 ms and its "
    "last token at 1200 ms after the request starts, with 21 output tokens in "
    "total. Calculate TTFT, average TPOT, and decode tokens/second. Show the "
    "formulas briefly, one metric per line."
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--port", type=int, default=8099)
    args = parser.parse_args()
    active = labkit.load_active()
    results = []
    for role in ("primary", "compare"):
        model = labkit.repo_root() / active[f"{role}_model"]
        quant = active[f"{role}_quant"]
        with labkit.serve_bg(str(model), port=args.port) as base:
            start = time.perf_counter()
            response = httpx.post(
                f"{base}/v1/chat/completions",
                json={"model": "local", "messages": [
                    {"role": "user", "content": args.prompt}],
                    "temperature": 0.0, "seed": 42, "max_tokens": 200},
                timeout=300.0,
            )
            response.raise_for_status()
            body = response.json()
            answer = body["choices"][0]["message"]["content"]
            if not answer or not answer.strip():
                labkit.die(f"Empty answer from {quant}; inspect the server log.")
            result = {"quant": quant, "model_file": model.name,
                      "answer": answer.strip(),
                      "elapsed_ms": round((time.perf_counter() - start) * 1000, 1),
                      "finish_reason": body["choices"][0].get("finish_reason"),
                      "usage": body.get("usage"), "timings": body.get("timings")}
            results.append(result)
            print(f"\n=== {quant} ===\n{result['answer']}", flush=True)

    sections = "\n\n".join(
        f"## {r['quant']}\n\n{r['answer']}\n\n"
        f"Elapsed: {r['elapsed_ms']} ms; finish reason: `{r['finish_reason']}`."
        for r in results
    )
    settings = {"threads": labkit.threads(), "ngl": labkit.n_gpu_layers(),
                "ctx": labkit.n_ctx(), "temperature": 0.0,
                "seed": 42, "max_tokens": 200}
    report = (
        "# Quantization answer comparison\n\n"
        f"Same prompt and generation settings for both variants: `{settings}`.\n\n"
        f"## Prompt\n\n{args.prompt}\n\n{sections}\n\n"
        "## Reference calculation\n\n"
        "For the default prompt: TTFT = 200 ms; TPOT = (1200 - 200) / "
        "(21 - 1) = 50 ms/token; decode rate = 1000 / 50 = 20 tokens/s. "
        "This is one quality check; it cannot establish overall model quality.\n"
    )
    # A custom prompt must not inherit the default prompt's reference calculation.
    if args.prompt != DEFAULT_PROMPT:
        report = report.split("## Reference calculation")[0]
    path = labkit.write_report("01-quality-comparison.md", report,
                               {"prompt": args.prompt, "settings": settings,
                                "results": results})
    print(f"\nSaved {path.relative_to(labkit.repo_root())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
