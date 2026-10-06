# Reflection — Day 20 Model Serving

**Họ Tên:** Trần Đại Nhân
**MSSV:** 2A202602642
**Cohort:** A20-K4 (suy từ tên repo K4; cần người nộp xác nhận)
**Ngày submit dự kiến:** 2026-10-06 (UTC+7)

## 1. Hardware & runtime

| Mục | Giá trị đo/kiểm tra |
|:--|:--|
| OS | Windows 11 AMD64 |
| CPU | AMD Ryzen 5 5600H with Radeon Graphics |
| Cores | 6 physical / 12 logical |
| CPU extensions | Script Windows không probe extension; không dùng kết quả AVX để kết luận |
| RAM | 13,9 GiB |
| Accelerator | NVIDIA GeForce RTX 3050 Laptop GPU, 4096 MiB; CUDA được `llama.cpp` nhận diện |
| Runtime | llama.cpp b10488, `llama-b10488-bin-win-cuda-12.4-x64.zip` |
| Model | Gemma 4 E2B, `LAB_MODEL=gemma4-e2b` |
| Quantization | UD-Q4_K_XL chính; UD-Q2_K_XL đối chiếu |
| Nơi chạy | Máy Windows local trong `hardware.json` |

**Setup story:** Tải prebuilt CUDA runtime và hai GGUF, không build từ source. PowerShell cần `PYTHONIOENCODING=utf-8` để in ký tự Unicode. Port 8080 đã bị ứng dụng khác chiếm nên lượt serve/load dùng `LAB_SERVER_PORT=18080`. Script ghi Markdown trên Windows ban đầu dùng CP1252; đã sửa `labkit.write_report` sang UTF-8 và chuyển báo cáo đã sinh, giữ nguyên số liệu.

## 2. Đo lường

Mỗi quantization gồm 10 request thành công sau một warm-up. Số dưới đây từ `benchmarks/01-quickstart-results.json` của lượt bench cuối.

| Quantization | Size (GiB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|:--|:--|:--|--:|
| UD-Q4_K_XL | 2,97 | 3644 | 70 / 223 | 12,9 / 13,0 | 888 / 1035 / 1035 | 77,4 |
| UD-Q2_K_XL | 2,24 | 4576 | 65 / 212 | 13,0 / 13,3 | 883 / 1024 / 1024 | 77,0 |

**Quan sát:** Q2 nhỏ hơn 0,73 GiB nhưng decode chậm hơn khoảng 0,5% trong bench và 3,6% trong sweep `tg128`; không có speedup đáng tin cậy. Hai bản đều trả lời sai TTFT/TPOT khi thiếu context, còn Q2 mắc thêm lỗi “contiguous” ở câu PagedAttention. Với bộ 5 câu nhỏ này và RAM hiện có, chọn Q4. Xem `benchmarks/bonus-quality.md`.

## 3. Serving under load

Hai lượt Locust chạy 60 giây mỗi lượt, cùng model UD-Q4_K_XL và `--parallel 4`.

| Users | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|--:|--:|--:|--:|--:|--:|--:|
| 10 | 2,61 | 2700 | 4500 | 5100 | 7,5 | 0 |
| 50 | 2,43 | 19000 | 20000 | 21000 | 40,5 | 0 |

- Offered load tăng 5×; throughput thực đạt **0,93×**.
- P95 tăng **4,44×**.
- Peak `llamacpp:n_busy_slots_per_decode` lấy mẫu dưới 50 users: **3,96/4** slots; `requests_deferred` peak **45**.

**Saturation reading:** Ở 10 users, Little's Law cho 7,5 request trong hệ thống, đã vượt 4 slot; hai mốc đo chưa xác định chính xác điểm gãy dưới 10. Đến 50 users, RPS không tăng nhưng P95 tăng 4,44× và 45 request bị deferred: thời gian thêm chủ yếu là chờ hàng đợi. Với SLO P95 ≤ 5 giây, lượt 10 users đạt còn 50 users thất bại. Giới hạn/admission control cho tải quá khả năng phục vụ sẽ bảo vệ goodput theo SLO; thay đổi slot cần được đo lại cùng SLO.

## 4. Integration

| Day | Piece | Real hay stub? |
|:--|:--|:--|
| N16 Cloud/IaC | Localhost | Stub cho cloud/IaC |
| N17 Data pipeline | Danh sách tài liệu trong bộ nhớ | Stub |
| N18 Lakehouse | `TOY_DOCS` | Stub |
| N19 Vector + features | Keyword overlap | Stub; không có vector index/feature store |
| N20 Serving | `llama-server` OpenAI-compatible | Real |

Ba query chạy hết và in provenance (`goodput`, `paged`, `disagg` đứng đầu tương ứng). Mean latency từ `benchmarks/03-integration-results.json`:

- embed: **0,0 ms** (không gọi embedding endpoint trong base run)
- retrieve: **0,7 ms**
- llm: **2667,6 ms**
- total: **2668,4 ms**
- stage lớn nhất: **llm, gần 100%** total

**Reflection:** LLM/HTTP áp đảo trên corpus đồ chơi; tối ưu keyword retrieval không thể giảm total 2×. Cần đo tiếp phần server và chi phí request client trước khi chọn cách giảm decode/prefill. Truy vấn có context ngắn ở đây, nên kết quả không đại diện cho RAG dài hoặc embedding model thật.

## 5. The single change that mattered most

**Change:** tăng `--parallel` từ 1 lên 4 trên cùng UD-Q4_K_XL, 10 Locust users, 60 giây, cùng task mix và token budget. Raw CSV: `benchmarks/locust-p1-u10_stats.csv` và `benchmarks/locust-10_stats.csv`.

```text
before:  1,29 RPS; P95 8400 ms (--parallel 1)
after:   2,61 RPS; P95 4500 ms (--parallel 4)
speedup: 2,02× RPS; P95 giảm 1,87×
```

Một slot chỉ decode một sequence tại một thời điểm. Bốn slot cho scheduler ghép các sequence đang hoạt động vào những bước decode chung và nhận request mới khi slot rảnh. Số token/giây của từng request có thể thay đổi, nhưng tổng throughput tăng và hàng đợi ngắn hơn ở cùng 10 users; vì thế P95 giảm từ 8,4 xuống 4,5 giây. Mẫu 50 users đo riêng cho thấy peak 3,96/4 slot bận, xác nhận scheduler có dùng nhiều slot.

Theo sweep thread, `-t 1` và `-t 6` chỉ khác 1,01× (81,05 so với 80,12 tok/s). CUDA đang offload 99 layers, nên thay CPU threads không tác động rõ đến nút thắt chính. Kết quả slot là thay đổi lớn hơn trong các phép đo ở đây. Do prompt trong Locust chọn ngẫu nhiên, tỷ số 2,02× chỉ áp dụng cho hai lượt 60 giây này; cần lặp lại nếu dùng để chọn cấu hình production.

## 6. Bonus

Đã làm **B2** quantization sweep, **B3** speedup từ sweep, **B4/C5** kiểm tra chất lượng 5 prompt trên Q4/Q2, và **B5/C9** embedding serving thật. Xem `benchmarks/bonus-quant-sweep.md`, `bonus-quality.md`, `bonus-embedding-serving.md`.

```text
before:  Q2 77,68 tok/s, 2,24 GiB
after:   Q4 80,61 tok/s, 2,97 GiB
speedup: Q4 nhanh hơn 1,04× trên phép đo tg128
```

Q2 nhỏ hơn nhưng không nhanh hơn trên RTX 3050 này; kích thước file không quyết định tốc độ khi định dạng dequantization và phần cứng cũng tham gia. C5 bộc lộ một lỗi nội dung cụ thể của Q2 về PagedAttention, đồng thời cả hai bản sai định nghĩa TTFT/TPOT nếu hỏi thiếu context. C9 đo batch embedding 1→16: throughput 0,5→6,4 texts/s khi latency request chỉ tăng 2202,7→2511,9 ms; đây là prefill theo batch, không phải vòng decode chat. Bộ thử C9 dùng chat model làm embedder nên chỉ là minh họa regime.

## 7. Điều bất ngờ

Q2 dùng ít bộ nhớ hơn nhưng không cải thiện decode; thay `--parallel` có tác động rõ hơn thay CPU thread count khi model offload GPU.

## 8. Self-check

- [x] Hardware, manifest, bench/tune/load/metrics/pipeline reports có số đo thật
- [x] 5 screenshots chụp từ terminal và CSV Locust thật
- [x] Model weights và runtime binary không được commit
- [ ] Người nộp đọc lại phần lập luận, xác nhận cohort và ngày submit
- [ ] Push public repo và nộp URL lên LMS

## 9. Khai báo sử dụng AI

OpenAI Codex hỗ trợ đọc yêu cầu, chạy script, xử lý lỗi port/mã hóa, tạo ảnh chụp terminal, tổng hợp số đo và soạn **bản nháp** phân tích. Không dùng AI tạo số liệu hay ảnh giả. Người nộp cần đọc, hiểu, sửa theo nhận định của mình và xác nhận nội dung trước khi nộp.
