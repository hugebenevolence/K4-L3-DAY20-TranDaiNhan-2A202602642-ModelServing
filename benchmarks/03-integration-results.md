# 03 - Integrate: RAG pipeline run

Host `Windows-AMD64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 2.0 | 2708.7 | 2710.8 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.0 | 2669.4 | 2669.5 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.1 | 2624.8 | 2624.9 |

Mean per stage (ms): embed **0.0** · retrieve **0.7** ·
llm **2667.6** · total **2668.4**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Goodput@SLO counts only the requests per second that met the TTFT and TPOT targets. Throughput at saturation ignores SLOs.

**What problem does PagedAttention actually solve?**

> PagedAttention stores the KV cache in non-contiguous pages, removing the internal fragmentation that wasted most GPU memory.

**When does splitting prefill and decode help?**

> Splitting prefill and decode helps because prefill is compute-bound and decode is memory-bandwidth-bound.


## Thành phần thật và stub

N16 là localhost (stub cho hạ tầng cloud); N17 là danh sách tài liệu trong bộ nhớ (stub cho data pipeline); N18 là `TOY_DOCS` (stub cho lakehouse); N19 là keyword overlap (stub cho vector index/features). N20 dùng `llama-server` thật qua OpenAI-compatible HTTP. `embed=0,0 ms` vì không gọi embedding endpoint trong base run. Ba truy vấn đều trả lời cùng context được in trong bảng; LLM chiếm 2667,6/2668,4 ms, gần 100% thời gian client quan sát. Để giảm tổng latency 2×, cần xử lý giai đoạn LLM hoặc overhead HTTP/server trước; tối ưu keyword retrieval vài phần mười mili giây không đủ.
