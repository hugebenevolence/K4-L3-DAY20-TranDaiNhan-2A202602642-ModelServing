# Bonus - Quantization sweep (Gemma 4 E2B, Unsloth Dynamic ladder)

Host `Windows-AMD64` · llama.cpp `b10488` ·
`threads=6` `ngl=99` · metric `tg128`

| Quantization | Size (GiB) | tg128 (tok/s) | vs UD-Q4_K_XL | tok/s per GiB |
|:--|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 80.6 | 1.00x | 27.1 |
| UD-Q2_K_XL | 2.24 | 77.7 | 0.96x | 34.7 |

The file-size reduction alone did not improve decode throughput here: Q2 is
smaller yet slower in this run. Memory traffic, dequantization work, and GPU
kernel choice can all affect that result; this sweep did not isolate them.
The "tok/s per GiB" column is a storage-efficiency ratio, not a direct measure
of memory bandwidth. Quality was checked separately on five identical prompts
per quantization in `bonus-quality.md`.

## Kết quả chọn quantization

Q4 đạt 80,61 tok/s, Q2 đạt 77,68 tok/s với cùng `tg128`, `threads=6`, `ngl=99`; chuyển Q2 → Q4 nhanh hơn 1,04× dù file lớn hơn 0,73 GiB. Tôi chọn Q4 trên máy có 13,9 GiB RAM và RTX 3050 4 GiB vì Q2 không mang lại tốc độ, còn câu trả lời PagedAttention trong bộ 5 câu kiểm tra mắc lỗi “contiguous”. Cả hai bản đều sai TTFT/TPOT trong câu hỏi thiếu ngữ cảnh, nên không xem Q4 là chính xác tuyệt đối. Xem `bonus-quality-q*.json`.
