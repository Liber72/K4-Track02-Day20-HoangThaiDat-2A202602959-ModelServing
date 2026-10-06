# 03 - Integrate: RAG pipeline run

Host `Windows-AMD64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.8 | 4222.4 | 4223.2 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.1 | 3752.9 | 3753.0 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.1 | 3631.1 | 3631.2 |

Mean per stage (ms): embed **0.0** · retrieve **0.3** ·
llm **3868.8** · total **3869.1**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Goodput@SLO counts only the requests per second that met the TTFT and TPOT targets. Throughput at saturation ignores SLOs.

**What problem does PagedAttention actually solve?**

> PagedAttention stores the KV cache in non-contiguous pages, removing the internal fragmentation that wasted most GPU memory.

**When does splitting prefill and decode help?**

> Splitting prefill and decode helps because prefill is compute-bound and decode is memory-bandwidth-bound.


## Which N16-N19 pieces are real

| Day | Trạng thái | Thành phần thực sự sử dụng |
|---|---|---|
| N16 Cloud/IaC | stub | Chạy localhost; không triển khai cloud hoặc IaC |
| N17 Data pipeline | stub | Danh sách `TOY_DOCS` trong bộ nhớ |
| N18 Lakehouse | stub | Dữ liệu mẫu trong Python; không có Delta/Iceberg |
| N19 Vector + features | stub | Keyword overlap; không gọi embedding model hoặc vector index N19 |
| N20 Serving | real | Gửi request đến `llama-server` qua HTTP |

Stage LLM chiếm xấp xỉ 100%: trung bình 3868,8 ms trên tổng 3869,1 ms.
Điều này phù hợp với việc retrieval chỉ tìm từ khoá trong vài tài liệu mẫu
(0,3 ms), còn embedding không chạy (0,0 ms). Kết quả này không đại diện cho
pipeline có embedding và vector database thật.

Nếu cần giảm latency 2×, tôi sẽ xử lý **stage gọi LLM**, trước hết kiểm tra
chi phí kết nối HTTP. Phép thử `/health` trước đó ghi 2125,9 ms với `localhost`
và 61,1 ms với `127.0.0.1` (`03-http-health-check.json`). Mỗi địa chỉ chỉ đo một
lần, nên đây là gợi ý chẩn đoán, chưa chứng minh pipeline sẽ nhanh hơn 2×.
Trong lần pipeline mới, server báo prefill + decode khoảng 2094,9 / 1699,9 /
1577,9 ms cho ba query, thấp hơn thời gian stage LLM tương ứng; phần chênh
không thể quy hết cho DNS hoặc kết nối nếu chưa đo riêng. Tôi sẽ thử IPv4 trực
tiếp hoặc tái sử dụng HTTP client, đo lại cùng ba query, rồi đánh giá prefill,
decode và giới hạn output. Tối ưu retrieval 0,3 ms không thể giảm tổng gần
3,9 giây xuống một nửa. Chưa thực hiện phép so sánh before/after này.
