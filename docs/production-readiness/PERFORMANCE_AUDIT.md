# Performance and Reliability Audit

Performance score: 52/100.

## Measurements

- Local Streamlit server ready: approximately 9.6 seconds.
- Three deterministic STEM operations: 2.75 seconds, 3/3 validated.
- Out-of-scope retrieval: 35 ms, zero hits.
- Cold Chroma readiness: 21.48 seconds for eight records.
- Benchmark traced peak memory: approximately 103 MiB.
- Concurrent health probe: 25/25 HTTP 200 in 3.83 seconds.
- Local seven-scenario browser/axe matrix: approximately one minute.
- Public browser content: failed to render within 120 seconds in Chromium, Firefox, and WebKit.

## Applied controls

- ZIP cache is limited to eight entries with a one-hour TTL.
- OpenAI calls use a 90-second timeout and at most two SDK retries.
- Uploads are limited to 50 MB and identified by SHA-256.
- Out-of-scope lessons bypass Chroma initialization.
- Chroma outages return explicit warnings and zero evidence rather than crashing or fabricating.

## Missing evidence

- Live lesson generation latency, request count, token use, and cost.
- Long-lesson nine-adaptation p50/p95/p99.
- Export ZIP/DOCX/PDF timings at realistic sizes.
- Multi-user Streamlit session memory and CPU.
- Rate-limit storms, cancellation, worker restarts, storage contention, and disaster recovery.
- Mobile hardware rendering and network throttling.

Live AI benchmarks were correctly deferred because orchestration and curriculum gates failed first.
