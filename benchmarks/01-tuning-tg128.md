# 01 - Tune: thread-count sweep

Model `gemma-4-E2B-it-UD-Q4_K_XL.gguf` · host `Windows-AMD64` · llama.cpp `b10488`
CPU: **6 physical · 12 logical** cores · `ngl=0` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 9.3 | 56% |
| 3 | 16.5 | 100% |
| 6 | 16.5 | 100% |
| 12 | 13.3 | 80% |
| 24 | 11.1 | 67% |

**Best**: `-t 6` at 16.5 tok/s
**Slowest tested**: `-t 1` at 9.3 tok/s (1.78x spread)
**Against the physical-core default** (`-t 6`, 16.5 tok/s): 1.00x

Use this in your run:

```bash
LAB_N_THREADS=6 make bench
```

## Your explanation

Curve gần như phẳng ở 3–6 threads: số gốc là 16,49 và 16,53 token/s, chênh
khoảng 0,24%; hai lần lặp mỗi điểm chưa đủ để khẳng định 6 luôn tốt hơn 3.
Ở 12 và 24 threads, tốc độ giảm xuống 13,30 và 11,13 token/s.

Máy có 6 core vật lý. Logical threads chia sẻ tài nguyên core; 24 threads còn
vượt số logical core. Decode phải đọc trọng số liên tục, nên thêm threads có thể
tăng tranh chấp băng thông bộ nhớ và chi phí lập lịch mà không tăng tài nguyên
tương ứng. Đây là giải thích phù hợp với curve, chưa phải kết quả đo riêng
bandwidth, cache hay context switch.

So sánh hai cấu hình trong thí nghiệm: 24 → 6 threads đạt 16,53 / 11,13 = 1,49×.
Cấu hình mặc định vốn đã là 6 threads, nên tuning không tăng tốc so với mặc định
(1,00×); không trình bày 24 threads như cấu hình ban đầu của hệ thống.
