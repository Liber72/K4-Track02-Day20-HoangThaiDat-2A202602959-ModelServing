# Reflection — Day 20 Lab (Personal Report)

> **Họ Tên:** Hoàng Thái Đạt
> **MSSV:** 2A202602959
> **Cohort:** 4
> **Ngày submit:** 06/10/2026

Số liệu là kết quả trên laptop của tôi. Baseline và tuning giữ các lần đo đã lưu;
serving và pipeline dùng báo cáo mới nhất hiện có. Bằng chứng batching của lần
chạy trước được ghi riêng, không ghép thành số đo của lần load mới.

## 1. Hardware & runtime *(rubric 1, 2 — 10 điểm)*

- **OS:** Windows 10 (AMD64)
- **CPU:** AMD Ryzen 5 5600H with Radeon Graphics
- **Cores:** 6 physical / 12 logical
- **CPU extensions:** Theo thông tin tôi ghi nhận: MMX(+), SSE, SSE2, SSE3, SSSE3,
  SSE4.1, SSE4.2, SSE4A, x86-64, AMD-V, AES, AVX, AVX2, FMA3 và SHA.
  Danh sách này không phải kết quả đo của `hardware.json`.
- **RAM:** 15,4 GB
- **Accelerator:** NVIDIA GeForce RTX 3050 Ti Laptop GPU, 4096 MiB.
  Các số đo base bên dưới chạy CPU với `ngl=0`.
- **llama.cpp asset:** Prebuilt b10488 Windows x64; executable trong `runtime/b10488/`.
- **Model:** Gemma 4 E2B
- **Quantization:** UD-Q4_K_XL (primary) + UD-Q2_K_XL (compare)
- **Chạy ở đâu:** Laptop local của tôi.
- **Cấu hình serving:** 6 threads, `--parallel 4`, `ctx=2048`, `ngl=0`.

**Setup story (≤ 80 chữ):**

Runtime ban đầu không thấy CUDA vì ZIP thư viện bị tải thiếu/hỏng. Tôi chạy CPU
với `ngl=0` để hoàn thành base, sửa encoding UTF-8, probe RAM và kiểm tra đường
dẫn Git trên Windows. Sau đó tải lại DLL CUDA 12.4 cho b10488; runtime đã nhận GPU.
Chưa chạy bonus GPU, nên chưa có số đo CUDA để so sánh.

Bằng chứng sửa CUDA: `submission/evidence/09-cuda-repair.json`. Nguyên nhân mạng
không ổn định chỉ là giả thuyết; chưa xác minh được lý do archive bị tải thiếu.

## 2. Đo lường *(rubric 3, 4, 5 — 20 điểm)*

Nguồn: `benchmarks/01-quickstart-results.md` và JSON tương ứng. Mỗi quantization
hoàn tất 10/10 request; warm-up bị loại. CPU 6 threads, `ngl=0`, `ctx=2048`,
giới hạn output 64 token.

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|---|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 5510 | 311 / 369 | 60.5 / 62.5 | 4083 / 4203 / 4203 | 16.5 |
| UD-Q2_K_XL | 2.24 | 4852 | 507 / 615 | 51.5 / 54.4 | 3740 / 4041 / 4041 | 19.4 |

**Quan sát (≤ 60 chữ):**

2-bit decode nhanh hơn khoảng 18%, nhỏ hơn 0,73 GB, nhưng TTFT P50 tăng
311 → 507 ms. Cùng câu hỏi TTFT/TPOT, cả hai đều sai; một câu chưa đủ đánh giá
chất lượng tổng thể. Tôi giữ 4-bit mặc định vì chưa đủ bằng chứng để đổi chỉ
dựa vào tốc độ.

Phép thử chất lượng và câu trả lời thực tế nằm trong
`benchmarks/01-quality-comparison.md`; không suy rộng từ một câu hỏi thành
kết luận 4-bit hoặc 2-bit tốt hơn về chất lượng tổng thể.

## 3. Serving under load *(rubric 8, 9, 10 — 20 điểm)*

Nguồn: `benchmarks/02-server-results.json`, hai file `locust-*_stats.csv` và
báo cáo Markdown. Đây là hai lần chạy 60 giây, cùng server 4-bit trên CPU.

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|--:|--:|--:|--:|--:|--:|--:|--:|
| 10 | 36 | 0.62 | 12000 | 19000 | 21000 | 7.8 | 0.0% |
| 50 | 27 | 0.45 | 29000 | 54000 | 60000 | 12.7 | 0.0% |

- **Số users tăng:** 5×; đây không phải phép đo arrival rate tăng chính xác 5×.
- **Throughput 50/10 users:** 0,73×, tính từ RPS chưa làm tròn.
- **P95 50/10 users:** 2,84× (54 / 19).
- **Effective concurrency ở 50 users:** 12,7 so với 4 slot; occupancy/slot ≈ 3,18.
  Đây là ước tính RPS × latency trung bình, không phải utilisation hay queue count.

**Batching:** CSV metrics mới ghi cao nhất 3,80/4, processing = 0, deferred = 0,
token counter giữ nguyên 7618 ở cả 15 mẫu. Timestamp và screenshot cho thấy
metrics được lấy sau khi load-50 đã kết thúc. Vì vậy không dùng CSV này để
khẳng định server đang bận 95% hoặc không có queue trong lần load mới.

**Bằng chứng batching trước đó:** `submission/evidence/07-batching.log` ghi
busy-slots cao nhất lấy mẫu 3,91/4, processing đạt 4, deferred đạt 46 và token
counter tăng. Đây là lần đo trước có tải đồng thời, tách biệt với bảng mới.
Cần đo lại metrics chồng với load nếu muốn có CSV mới đúng yêu cầu rubric 9.

**SLO minh hoạ đã chọn:** P95 E2E ≤ 40 giây. 10 users đạt (19 giây);
50 users không đạt (54 giây), trên các request đã hoàn tất. Không có số đo
TTFT/TPOT theo request trong load test này. Chưa tính được goodput chính xác
cho 50 users từ thống kê tổng hợp; không đồng nhất RPS với goodput. 0 lỗi trên
request hoàn tất không có nghĩa mọi request phát ra đều hoàn thành trước khi dừng.

**Saturation reading (≤ 80 chữ):**

Ở 50 users có dấu hiệu bão hoà: RPS giảm 0,73×, P95 tăng 19 → 54 giây.
Concurrency 12,7 vượt 4 slot; chưa biết chính xác ngưỡng bắt đầu. Log cũ xác
nhận queue, CSV mới không đo dưới tải. Tôi ưu tiên giới hạn request đồng thời
để giảm chờ, chấp nhận nhận ít request hơn. Chưa đo tác dụng hoặc goodput
sau thay đổi.

Cửa sổ đo ngắn, ít request và prompt có độ dài khác nhau; chưa tách riêng
queue time/compute time hoặc chứng minh trạng thái ổn định. Nhận xét này là
dấu hiệu từ dữ liệu, không kết luận nguyên nhân duy nhất làm RPS giảm.

## 4. Integration *(rubric 12, 13 — 15 điểm)*

Nguồn: `benchmarks/03-integration-results.md` và JSON tương ứng.

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | Localhost, không triển khai cloud/IaC | stub |
| N17 Data pipeline | Danh sách `TOY_DOCS` trong bộ nhớ | stub |
| N18 Lakehouse | Dữ liệu mẫu trong Python, không có Delta/Iceberg | stub |
| N19 Vector + features | Keyword overlap; không gọi embedding server hoặc vector index N19 | stub |
| N20 Serving | `llama-server` qua HTTP | real |

**Latency split (mean của 3 query):**

- embed: 0.0 ms — không gọi embedding model.
- retrieve: 0.3 ms.
- llm: 3868.8 ms — gồm thời gian gọi HTTP và inference.
- total: 3869.1 ms.
- **Stage chiếm nhiều nhất:** llm, xấp xỉ 100%.

**Reflection (≤ 60 chữ):**

LLM chiếm gần 100%, phù hợp với retrieval mẫu chỉ 0,3 ms. Tôi ưu tiên kiểm tra
kết nối HTTP rồi đo lại prefill/decode. Phép thử health trước đó gợi ý dùng
IPv4 trực tiếp, nhưng mỗi địa chỉ chỉ đo một lần. Chưa chứng minh giảm 2×;
tối ưu retrieval không đủ.

Phép thử health: localhost 2125,9 ms, IPv4 trực tiếp 61,1 ms, lưu tại
`benchmarks/03-http-health-check.json`. Đây là chẩn đoán riêng, không phải
benchmark inference hay kết quả tối ưu pipeline. Pipeline đã chạy hết ba query
và trả về context; không tuyên bố đây là tích hợp N19 thật.

## 5. The single change that mattered most *(rubric 11 — 10 điểm)*

**Change:** So sánh hạ `-t 24` xuống `-t 6` trong thread sweep trên CPU,
cùng model UD-Q4_K_XL và metric `tg128`. Đây là hai cấu hình trong thí nghiệm;
cấu hình mặc định ban đầu vốn đã là 6 threads.

```text
before:  11.13 token/s tại 24 threads
after:   16.53 token/s tại 6 threads
speedup: 1.49× (16.53 / 11.13)
```

**Tại sao nó work:**

Từ 3 lên 6 threads, tốc độ chỉ tăng từ 16,49 lên 16,53 token/s, gần như plateau.
Khi tăng lên 12 hoặc 24, tốc độ giảm. Máy chỉ có 6 core vật lý; các logical
thread chia sẻ tài nguyên core, còn 24 threads vượt cả số logical core.
Decode đọc trọng số liên tục, nên thêm threads có thể tăng tranh chấp băng
thông bộ nhớ và chi phí lập lịch thay vì tăng khả năng xử lý tương ứng.

Giảm từ cấu hình thử 24 xuống 6 threads đạt 1,49×, phù hợp với cách giải thích
trên. Tôi chưa đo riêng memory bandwidth, cache hay context switch nên đây là
suy luận từ curve, không phải chứng minh một nguyên nhân duy nhất. So với mặc
định 6 threads, tuning không tạo thêm speedup (1,00×); hai lần lặp mỗi điểm
cũng chưa đủ kết luận chênh lệch nhỏ giữa 3 và 6 là ổn định.

Nguồn: `benchmarks/01-tuning-tg128.json` và báo cáo Markdown tương ứng.

## 6. Bonus *(optional — tối đa 10 điểm)*

**Chưa thực hiện bonus.** Đã sửa CUDA và xác nhận runtime nhận GPU, nhưng chưa
chạy GPU offload sweep hoặc phép so sánh before/after CUDA. Không dùng kết quả
thread sweep của base để nhận điểm bonus; chưa có số liệu bonus để báo cáo.

## 7. Điều làm tôi chú ý nhất *(optional)*

Tăng threads vượt số core vật lý làm decode chậm hơn trong thí nghiệm này.
Mặc định 6 threads vốn đã đạt điểm tốt nhất của sweep, nên kết quả 1,49× là so
sánh với cấu hình thử 24 threads, không phải tăng tốc so với mặc định.

## 8. Self-check trước khi push

- [ ] `hardware.json` committed.
- [ ] `models/active.json` committed.
- [ ] `benchmarks/01-quickstart-results.md` committed.
- [ ] `benchmarks/01-tuning-tg128.md` committed.
- [ ] `benchmarks/02-server-results.md` committed.
- [ ] Bằng chứng batching dưới tải và CSV/báo cáo được đưa vào commit.
- [ ] `benchmarks/locust-10_stats.csv` + `locust-50_stats.csv` committed.
- [ ] `benchmarks/03-integration-results.md` committed.
- [x] Các section bắt buộc trong báo cáo `benchmarks/*.md` đã có nhận xét.
- [x] Có 7 ảnh thật trong `submission/screenshots/`, gồm 5 mục bắt buộc.
- [ ] Screenshots đã được commit.
- [ ] `make verify` hoặc `.\lab.ps1 verify` → exit 0.
- [ ] Repo tên đúng mẫu `K4-L3-DAY20-HoVaTen-MSSV-ModelServing`.
- [ ] Repo GitHub ở chế độ public.
- [ ] Đã push và paste public URL vào VinUni LMS đúng hạn.
- [ ] Kiểm tra commit cuối không chứa weights, runtime hoặc secrets.

Mapping ảnh: `01-hardware-probe.png` → hardware; `02-bench.png` → baseline;
`03a_serve.png` + `03b_smoke.png` → server và smoke; `04-locust-10.png` +
`05-locust-50.png` → load test; `08-pipeline.png` → integration.
Các ô committed/push để trống vì cập nhật tài liệu không đồng nghĩa đã commit
hoặc nộp bài. Đọc lại lập luận và kiểm tra bằng chứng batching trước khi nộp.

## 9. Khai báo sử dụng AI *(xem docs/RULES.md §3)*

Sử dụng Codex để đọc hướng dẫn, hỗ trợ chạy script lab, sửa encoding và đường
dẫn Git trên Windows, sửa probe RAM, thêm phép thử cùng câu hỏi cho hai
quantization, sửa CUDA và tổng hợp số đo thật. Codex hỗ trợ soạn/cập nhật nhận
xét từ tài liệu và các lựa chọn đã trao đổi: giữ 4-bit, so sánh 24 → 6 threads,
SLO P95 E2E ≤ 40 giây và đề xuất giới hạn request đồng thời. Bản thảo cần được
tôi đọc lại và hiểu để giải thích; không tạo số liệu hoặc screenshot giả.
