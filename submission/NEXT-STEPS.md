# Các bước còn lại — Day 20

Reflection đã được cập nhật theo baseline/tuning đã lưu và báo cáo load/RAG mới
nhất. Thông tin cá nhân đã điền; hiện có 7 screenshot thật. Các lựa chọn giữ nguyên:
Gemma 4 E2B 4-bit, CPU 6 threads, 4 slot, RAG mẫu; so sánh 24 → 6 threads;
SLO minh hoạ P95 E2E ≤ 40 giây; đề xuất giới hạn request đồng thời, chưa thử knob.

## 1. Đọc lại nhận xét và bằng chứng

Các câu hỏi bắt buộc trong báo cáo baseline, tuning, load và integration đã có
câu trả lời. Báo cáo batching đã sửa để phân biệt số trung bình trên decode với
effective concurrency của client.

Khi bắt đầu cập nhật, hai mục chưa điền nằm trong
`benchmarks/02-server-results.md` và `benchmarks/03-integration-results.md`;
đã trả lời cả hai. Quét lại toàn bộ 63 file văn bản của repo, gồm file bị Git
bỏ qua (trừ runtime, môi trường ảo, Git và dependency), tìm thấy 24 chỗ còn
nhắc marker hoặc mẫu trả lời; không có mục chưa trả lời trong báo cáo kết quả.

Các câu hỏi còn hiển thị trong mã sinh báo cáo base và nơi đã trả lời:

| Vị trí câu hỏi mẫu | Báo cáo đã trả lời |
|---|---|
| `labs/01-measure/benchmark.py:218` | `benchmarks/01-quickstart-results.md` — Your observation |
| `labs/01-measure/tune.py:107` | `benchmarks/01-tuning-tg128.md` — Your explanation |
| `labs/02-serve/load-report.py:187` | `benchmarks/02-server-results.md` — Your reading |
| `labs/02-serve/record-metrics.py:142` | `benchmarks/02-server-batching-u50.md` — Observation |
| `labs/03-integrate/pipeline.py:219` | `benchmarks/03-integration-results.md` — Which N16-N19 pieces are real |

Các câu hỏi mẫu bonus còn ở `bonus/compare-builds.py:178`,
`bonus/mlx/compare-mlx-vs-llama-cpp.py:240`, `bonus/sweeps/batch-size-sweep.py:74`,
`bonus/sweeps/ctx-len-sweep.py:116`, `bonus/sweeps/gpu-offload-sweep.py:81`
và `bonus/sweeps/quant-sweep.py:138`. Chưa chạy các phép đo bonus nên chưa có
báo cáo/kết quả để trả lời các câu hỏi này. Đây là phần tùy chọn.

Các chỗ còn lại là hướng dẫn trong `cloud/Day20-lab.ipynb`, `docs/GUIDE.md`,
`docs/CLOUD.md`, `docs/SUBMISSION.md`, `docs/RUBRIC.md`, `docs/bonus/README.md`,
`docs/bonus/01-build-from-source.md`; chuỗi kiểm tra trong `scripts/verify.py`
và đoạn mô tả này. Đây là template/quy định, không phải bài trả lời còn thiếu.
Chạy lại script sinh báo cáo sẽ tạo lại placeholder, cần điền lại theo số đo mới.

Theo `docs/RULES.md` §3, cần hiểu và tự giải thích được các nhận xét trước khi nộp.

## 2. Bằng chứng batching cần lưu ý

CSV metrics mới được lấy khoảng 20:43:55–20:44:52, sau khi load-50 mới kết thúc
lúc 20:39:50. Cả 15 mẫu có processing/deferred bằng 0 và token counter không đổi.
Nó không chứng minh batching đang diễn ra trong lần load mới.

Log cũ `submission/evidence/07-batching.log` vẫn có bằng chứng dưới tải:
processing 4, deferred tới 46, busy-slots tới 3,91 và token counter tăng.
Các báo cáo đã ghi rõ đây là lần chạy trước, không gán cho lần load mới.

Để có CSV mới đúng yêu cầu rubric 9, dùng ba terminal trong thư mục repo:
server đang chạy ở terminal 1; terminal 2 chạy `.\lab.ps1 load-50`; ngay khi
Locust đang tăng users, terminal 3 chạy `.\lab.ps1 metrics`.
Không bật thêm server trên cùng port. Sau đó chạy `.\lab.ps1 load-report`,
cập nhật nhận xét/Reflection theo số liệu mới và chụp lại ảnh load-50 tương ứng.
Đây là bước cần làm nếu muốn thay bằng chứng cũ bằng bộ đo mới đồng nhất.

## 3. Git và nộp bài

Verifier đã xác nhận Reflection không còn placeholder bắt buộc. Lần kiểm tra
hiện tại còn 10 lỗi do các file kết quả, manifest/hardware và ảnh chưa được đưa
vào Git. Chưa stage, commit hoặc push trong lần cập nhật tài liệu này.

Sau khi kiểm tra báo cáo/bằng chứng, stage đúng file, chạy `.\lab.ps1 verify`,
commit và push. Không đưa weights, runtime hoặc secrets vào Git.
Repo cần đúng tên mẫu `K4-L3-DAY20-HoVaTen-MSSV-ModelServing`, public và URL
phải được nộp vào VinUni LMS theo hạn của lớp.

## 4. CUDA và bonus

CUDA đã được sửa và runtime nhận GPU. Base giữ `ngl=0`; chưa chạy bonus.
Khi làm bonus, đo GPU offload sweep thật và báo cáo before/after riêng;
không tính kết quả tuning CPU của base thành kết quả bonus.
