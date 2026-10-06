# 01 - Measure: latency baseline

Model `Gemma 4 E2B` · host `Windows-AMD64` · llama.cpp `b10488`
Settings: `threads=6` `ngl=99` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `UD-Q4_K_XL` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 3644 | 70 / 223 | 12.9 / 13.0 | 888 / 1035 / 1035 | 77.4 |
| UD-Q2_K_XL | 2.24 | 4576 | 65 / 212 | 13.0 / 13.3 | 883 / 1024 / 1024 | 77.0 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` and `UD-Q4_K_XL` decode within 2% of each other here, for 0.73 GB difference on disk.

## Quan sát trên máy này

Q2 tiết kiệm 0,73 GiB nhưng decode 77,0 tok/s so với Q4 77,4 tok/s; mức chênh 0,5% rất nhỏ với 10 mẫu mỗi bản. Cùng một bộ 5 câu hỏi ở `bonus-quality-q4.json` và `bonus-quality-q2.json`, cả hai đều hiểu sai TTFT/TPOT khi thiếu ngữ cảnh; riêng Q2 còn mô tả các trang KV của PagedAttention là *contiguous*. Vì RAM/VRAM hiện đủ và Q2 không cho lợi thế tốc độ đo được, tôi chọn Q4. Đây là kiểm tra chất lượng nhỏ, không phải đánh giá accuracy tổng quát.
