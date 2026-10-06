# 02 - Serve: load test + saturation reading

Host `Windows-AMD64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=6` ·
`ngl=99`

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 155 | 2.61 | 2700 | 4500 | 5100 | 7.5 | 0.0% |
| 50 | 144 | 2.43 | 19000 | 20000 | 21000 | 40.5 | 0.0% |

*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were
really in flight, regardless of how many users locust simulated. It counts queued requests
too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not
utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **0.93x** (19% of linear) |
| P95 latency | **4.44x** |
| Effective concurrency at 50 users | 40.5 vs `--parallel 4` slots (occupancy/slot ratio 10.13) |

**Saturated.** Throughput delivered only 0.93x for 5x the offered load, and effective concurrency (40.5) is at or above all 4 decode slots. Saturation sets in somewhere at or below 50 users; the load you added beyond that point became queue time rather than throughput.

Throughput moved 0.93x while P95 moved 4.44x. That gap is the goodput argument: past saturation you buy throughput by spending latency, and if your SLO is a P95 target then the requests you added are no longer being served within it. (This lab does not fix an SLO number for you -- pick one in your write-up and state how much goodput you keep at it.)

## Đọc điểm bão hòa

Ở 10 users, effective concurrency 7,5 đã vượt 4 slot, nên hàng đợi có thể xuất hiện ngay tại mức tải này; hai mốc 10 và 50 chưa đủ để xác định chính xác điểm gãy thấp hơn 10. Từ 10 lên 50 users, RPS giảm từ 2,61 xuống 2,43 trong khi P95 tăng 4,44×, tới 20 giây. Mẫu metrics đồng thời ghi 3,96/4 slot bận và tối đa 45 request deferred. Với mục tiêu P95 ≤ 5 giây, lượt 10 users đạt, lượt 50 users không đạt. Tôi sẽ giới hạn tải đầu vào hoặc tăng năng lực phục vụ trước khi tăng thêm concurrency; chỉ tăng `--parallel` khi đo lại cho thấy GPU còn headroom.
