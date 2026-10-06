# Bonus C5 — smallest useful quantization check

Five identical questions were sent to each quantization at `temperature=0`, `max_tokens=128`. Raw prompts and complete returned strings are in `bonus-quality-q4.json` and `bonus-quality-q2.json`; the runner is `bonus/quality-check.py`. This is a small factual spot check, not a general accuracy benchmark.

| Question | Q4 | Q2 |
|:--|:--|:--|
| TTFT / TPOT definitions | Wrong: interprets them as product engagement and purchase | Wrong: interprets them as failure metrics |
| Why 2-bit may fail to speed decode | Starts a broadly relevant explanation; 128-token cap cuts it short | Starts a broadly relevant explanation; 128-token cap cuts it short |
| PagedAttention pages | Identifies K/V data and paging | Says the stored data are “contiguous”, contradicting non-contiguous KV pages |
| Goodput@SLO | Connects successful completions to a latency target | Gives a less specific description of successful completions |
| Continuous batching | Discusses dynamic admission but is verbose | Discusses dynamic admission but is verbose |

The lower Q2 quantization is **0.73 GiB smaller**, yet the `tg128` sweep measured **77.68 tok/s** versus **80.61 tok/s** for Q4. On this machine, Q2 offers neither a decode-speed gain nor a clear quality win. Q4 is the smallest of these two that I would deploy, with a domain-specific eval and retrieval context added before real use. The TTFT failure in both variants shows that quantization alone is not the only quality issue.
