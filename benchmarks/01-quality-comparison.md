# Quantization answer comparison

Same prompt and generation settings for both variants: `{'threads': 6, 'ngl': 0, 'ctx': 2048, 'temperature': 0.0, 'seed': 42, 'max_tokens': 200}`.

## Prompt

Respond in exactly three short lines, without an introduction, headings or LaTeX. A request emits its first token at 200 ms and its last token at 1200 ms after the request starts, with 21 output tokens in total. Calculate TTFT, average TPOT, and decode tokens/second. Show the formulas briefly, one metric per line.

## UD-Q4_K_XL

TTFT = 1000 ms
Average TPOT = 500 ms
Decode tokens/second = 21

Elapsed: 2371.5 ms; finish reason: `stop`.

## UD-Q2_K_XL

TTFT = 1000ms - 200ms = 800ms
Average TPOT = (1200ms - 200ms) / 1000ms = 1000ms
Decode tokens/sec = 21 tokens / 1000ms = 21 tokens/sec

Elapsed: 5878.8 ms; finish reason: `stop`.

## Reference calculation

For the default prompt: TTFT = 200 ms; TPOT = (1200 - 200) / (21 - 1) = 50 ms/token; decode rate = 1000 / 50 = 20 tokens/s. This is one quality check; it cannot establish overall model quality.
