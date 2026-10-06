# 02 - Serve: load test + saturation reading

Host `Windows-AMD64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=6` ·
`ngl=0`

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 36 | 0.62 | 12000 | 19000 | 21000 | 7.8 | 0.0% |
| 50 | 27 | 0.45 | 29000 | 54000 | 60000 | 12.7 | 0.0% |

*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were
really in flight, regardless of how many users locust simulated. It counts queued requests
too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not
utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **0.73x** (15% of linear) |
| P95 latency | **2.84x** |
| Effective concurrency at 50 users | 12.7 vs `--parallel 4` slots (occupancy/slot ratio 3.18) |

**Saturated.** Throughput delivered only 0.73x for 5x the offered load, and effective concurrency (12.7) is at or above all 4 decode slots. Saturation sets in somewhere at or below 50 users; the load you added beyond that point became queue time rather than throughput.

Throughput moved 0.73x while P95 moved 2.84x. That gap is the goodput argument: past saturation you buy throughput by spending latency, and if your SLO is a P95 target then the requests you added are no longer being served within it. (This lab does not fix an SLO number for you -- pick one in your write-up and state how much goodput you keep at it.)

## Your reading

Ở 50 users, hệ thống có dấu hiệu bão hoà: tăng users 5× nhưng RPS giảm từ
0,618 xuống 0,452 (0,73×), trong khi P95 tăng từ 19 lên 54 giây (2,84×).
Effective concurrency ước tính là 12,7, vượt 4 slot; ở 10 users cũng đã là 7,8.
Hai mức tải chưa xác định được chính xác ngưỡng bắt đầu bão hoà. Users của Locust
không phải tốc độ request đầu vào độc lập; đây là phép thử với số client đồng thời
khác nhau, có cả prompt ngắn và dài.

Tôi chọn **SLO minh hoạ P95 E2E ≤ 40 giây**: 10 users đạt, 50 users không đạt,
dựa trên các request đã hoàn tất trong hai lần chạy 60 giây. Có 36 và 27 request
hoàn tất, đều 0 lỗi; điều đó không có nghĩa mọi request của 50 users hoàn thành
hoặc đạt SLO. Chưa đo TTFT/TPOT theo request nên chưa tính được goodput theo hai
metric đó; thống kê tổng hợp cũng chưa cho số request ở 50 users đạt E2E ≤ 40 giây
để tính goodput chính xác. Ước tính Little's Law chỉ mang tính mô tả trong cửa sổ
ngắn này, chưa chứng minh hệ thống đã ở trạng thái ổn định.

Tôi ưu tiên **giới hạn request đồng thời trước server** để giảm thời gian chờ,
chấp nhận ít request được nhận cùng lúc. Lần đo cũ có 4 request xử lý và tối đa
46 request chờ trong `submission/evidence/07-batching.log`, hỗ trợ cơ chế queueing.
Tuy nhiên, CSV metrics mới là các mẫu đứng yên sau tải, nên không dùng nó để
chứng minh queue của lần load mới hoặc tách chính xác queue time và compute time.
Chưa thử knob này và chưa đo goodput sau thay đổi; tôi không tăng `--parallel`
ngay vì tăng slot có thể gây thêm tranh chấp CPU/bộ nhớ.
