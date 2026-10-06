# Bonus measurement — decode slots at 10 users

Gemma 4 E2B UD-Q4_K_XL · llama.cpp b10488 CUDA · `threads=6`, `ctx=2048`, `ngl=99`. Both Locust runs lasted 60 seconds with the same 80/20 short/RAG task mix and token budgets. Raw results: `locust-p1-u10_stats.csv` and `locust-10_stats.csv`.

| `--parallel` | Requests | RPS | P95 (ms) | Failures |
|--:|--:|--:|--:|--:|
| 1 | 76 | 1.29 | 8400 | 0 |
| 4 | 155 | 2.61 | 4500 | 0 |

Changing 1 → 4 slots delivered **2.02× RPS** and reduced P95 by **1.87×** (8400/4500). The scheduler can keep several sequences in the same decode step; the u50 metrics separately observed 3.96/4 busy slots. With a P95 ≤ 5 s objective, the one-slot run failed and the four-slot run passed at 10 users. Prompt selection is random, so the exact ratios have run-to-run uncertainty; the shared model, hardware, duration and load shape make the direction meaningful.
