# 01 - Measure: latency baseline

Model `Gemma 4 E2B` · host `Windows-AMD64` · llama.cpp `b10488`
Settings: `threads=6` `ngl=0` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `UD-Q4_K_XL` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 5510 | 311 / 369 | 60.5 / 62.5 | 4083 / 4203 / 4203 | 16.5 |
| UD-Q2_K_XL | 2.24 | 4852 | 507 / 615 | 51.5 / 54.4 | 3740 / 4041 / 4041 | 19.4 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` decodes **1.18x faster** than `UD-Q4_K_XL` here, for 0.73 GB less on disk.

## Your observation

2-bit decode nhanh hơn khoảng 18% (19,4 so với 16,5 token/s), nhỏ hơn 0,73 GB,
nhưng TTFT P50 tăng từ 311 lên 507 ms. Trong phép thử cùng câu hỏi tính TTFT/TPOT,
cả hai bản đều tính sai (`01-quality-comparison.md`). Một câu chưa đủ kết luận
chất lượng tổng thể; tôi giữ 4-bit mặc định, chưa đổi chỉ vì tốc độ.
