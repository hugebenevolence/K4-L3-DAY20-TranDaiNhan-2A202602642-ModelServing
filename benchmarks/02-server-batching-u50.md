# 02 - Continuous batching under load (u50)

Host `Windows-AMD64` · `--parallel 4` · 15 samples over
60s at 2.0s intervals · raw CSV: `02-server-metrics-u50.csv`

| Gauge | Peak observed |
|:--|--:|
| `n_busy_slots_per_decode` (avg/decode) | 3.96 of 4 slots (99%) |
| `requests_processing` | 4 |
| `requests_deferred` | 45 |
| `kv_cache_usage_ratio` | n/a — not exported by llama.cpp `b10488` |
| `tokens_predicted_total` (final) | 15855 |

Highest sampled value was **3.96 of 4** slots. Note this gauge is llama.cpp's *average* busy slots per decode step, so the number below is the highest average we sampled, not an instantaneous maximum batch width. A peak near 1 means
requests were served one at a time -- either the load was too light to overlap, or
they arrived too far apart. A peak approaching `--parallel` means the scheduler was
genuinely packing concurrent requests into shared decode steps.
`requests_deferred` went above zero: more requests arrived than there were slots, so some waited. That wait is the queue time in your P95.

## Quan sát batching

Peak `n_busy_slots_per_decode` được lấy mẫu là 3,96/4, `requests_processing` đạt 4 và `requests_deferred` đạt 45. Little's Law cho 40,5 request đang ở trong hệ thống tại 50 users; phần vượt 4 slot đang chờ, không phải batch rộng 40,5. Gauge của server đo trực tiếp số slot decode; con số Little's Law bao gồm cả hàng đợi và là ước lượng từ request đã hoàn thành. Hai phép đo vì thế bổ sung cho nhau.
