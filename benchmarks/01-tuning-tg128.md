# 01 - Tune: thread-count sweep

Model `gemma-4-E2B-it-UD-Q4_K_XL.gguf` · host `Windows-AMD64` · llama.cpp `b10488`
CPU: **6 physical · 12 logical** cores · `ngl=99` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 81.0 | 100% |
| 3 | 79.4 | 98% |
| 6 | 80.1 | 99% |
| 12 | 79.6 | 98% |
| 24 | 79.2 | 98% |

**Best**: `-t 1` at 81.0 tok/s
**Slowest tested**: `-t 24` at 79.2 tok/s (1.02x spread)
**Against the physical-core default** (`-t 6`, 80.1 tok/s): 1.01x

Use this in your run:

```bash
LAB_N_THREADS=1 make bench
```

## Giải thích đường cong

`-t 1` đạt 81,05 tok/s và `-t 6` đạt 80,12 tok/s: lợi thế chỉ 1,01×. Toàn bộ dải 1–24 threads nằm trong khoảng 79,16–81,05 tok/s, nên chưa có một điểm gãy rõ ràng. Lệnh dùng `-ngl 99` và GPU CUDA thực sự được nhận diện; decode chủ yếu chạy trên GPU, vì vậy tăng CPU threads không tăng năng lực tính toán chính. Chênh lệch khoảng 1–2% cũng có thể là nhiễu đo; không nên xem `-t 1` là tối ưu chắc chắn nếu chưa lặp thêm.
