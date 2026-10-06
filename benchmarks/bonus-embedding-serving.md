# Bonus C9 — embedding serving regime

Gemma 4 E2B UD-Q4_K_XL was run as a real `llama-server` embedding endpoint with mean pooling (`/v1/embeddings`, port 18081). The client ran `bonus/serving-regimes/embedding-serving.py`; full console output is `bonus-embedding-raw.txt`. This reuses a **chat** model, so retrieval quality is only a demonstration.

| Batch texts | Request latency (ms) | Throughput (texts/s) |
|--:|--:|--:|
| 1 | 2202.7 | 0.5 |
| 2 | 2403.7 | 0.8 |
| 4 | 2245.0 | 1.8 |
| 8 | 2438.4 | 3.3 |
| 16 | 2511.9 | 6.4 |

Across these single calls, batch 16 returned 16× as many vectors for only 1.14× the latency of batch 1; the reported throughput rose from 0.5 to 6.4 texts/s. This is a prefill-only workload that benefits from grouping inputs, unlike autoregressive chat where sequences enter and leave continuously. The top match for the query about an embedding decode loop was the relevant document (cosine 0.844), but an unrelated RadixAttention text ranked second (0.785). A dedicated embedding model and larger relevance evaluation would be needed for retrieval in production.
