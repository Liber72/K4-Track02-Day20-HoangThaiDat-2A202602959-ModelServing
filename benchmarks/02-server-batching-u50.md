# 02 - Continuous batching under load (u50)

Host `Windows-AMD64` · `--parallel 4` · 15 samples over
60s at 2.0s intervals · raw CSV: `02-server-metrics-u50.csv`

| Gauge | Peak observed |
|:--|--:|
| `n_busy_slots_per_decode` (avg/decode) | 3.80 of 4 slots (95%) |
| `requests_processing` | 0 |
| `requests_deferred` | 0 |
| `kv_cache_usage_ratio` | n/a — not exported by llama.cpp `b10488` |
| `tokens_predicted_total` (final) | 7618 |

Highest sampled value was **3.80 of 4** slots. Note this gauge is llama.cpp's *average* busy slots per decode step, so the number below is the highest average we sampled, not an instantaneous maximum batch width. A peak near 1 means
requests were served one at a time -- either the load was too light to overlap, or
they arrived too far apart. A peak approaching `--parallel` means the scheduler was
genuinely packing concurrent requests into shared decode steps.
`requests_deferred` stayed at zero during this sampling window. This alone does
not show that every request found a free slot during the load test.

## Observation

Giá trị lớn nhất lấy mẫu là **3,80 trên 4 slot**, khác effective concurrency
**12,7** ở 50 users. `n_busy_slots_per_decode` là số slot bận trung bình trên
các bước decode, không phải số request đang xử lý tại thời điểm scrape.
Little's Law ở phía client tính RPS × latency trung bình, gồm cả thời gian chờ.
Vì khác đại lượng và cửa sổ đo, không lấy 12,7 − 3,80 để kết luận có chính xác
8,9 request trong queue. Khi đánh giá batching, tôi dùng metric trực tiếp của
server; khi đánh giá latency người dùng, tôi dùng Locust cùng giới hạn mẫu.

**Giới hạn của CSV mới:** cả 15 mẫu đều giữ `n_busy_slots_per_decode=3.80205`,
`tokens_predicted_total=7618`, `n_decode_total=2051`, `requests_processing=0`
và `requests_deferred=0`. Các timestamp trải từ khoảng **20:43:55 đến 20:44:52
(UTC+7)**, sau khi load-50 trong screenshot `05-locust-50.png` kết thúc lúc
**20:39:50**. Đây là số trung bình còn lưu sau tải, không phải quan sát peak
batching đang diễn ra dưới lần load mới. Khoảng cách scrape thực tế xấp xỉ
4 giây vì còn thời gian HTTP; 2 giây trong đầu báo cáo là khoảng nghỉ cấu hình.

**Bằng chứng lần chạy trước:** log thật `submission/evidence/07-batching.log`
ghi số token tăng từ 1495 lên 3381, processing đạt 4, deferred đạt 46 và
giá trị busy-slots cao nhất lấy mẫu đạt **3,91/4**. Log này hỗ trợ việc đã có
batching và queue dưới tải ở lần chạy trước; không gán các số đó cho CSV hoặc
load test mới. Để có bộ CSV mới đo đúng yêu cầu rubric 9, cần chạy `metrics`
chồng thời gian với `load-50` rồi cập nhật nhận xét theo kết quả thực tế.
