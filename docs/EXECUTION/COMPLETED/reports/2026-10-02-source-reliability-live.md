# Live source reliability baseline — 2026-10-02

## Scope and method

Ran `python3 scripts/source_reliability.py --runs 3 --limit 20 --categories technology,business,world,science --country VN --output /tmp/source-reliability.json` against Google News RSS over the real outbound network. The probe made exactly 12 category requests (three attempts for each category), fetching up to 20 items per request. This was a read-only RSS and extraction check; it did not use a production database, an LLM, or Telegram.

The runner's requested `python` executable was unavailable in this environment, so the identical script and arguments were executed with `python3` (Python 3.12.3). All 12 requests completed successfully; the run produced 240 fetched items total.

## Results

| Source | Category | RSS transport | Extraction | Trigger metric and fallback |
|---|---|---:|---:|---|
| Google News RSS (VN) | technology | 3/3 (100%, healthy) | 0/60 (0%, fallback target) | `content_extraction_rate` below 75%; try Readability-lxml before Playwright |
| Google News RSS (VN) | business | 3/3 (100%, healthy) | 0/60 (0%, fallback target) | `content_extraction_rate` below 75%; try Readability-lxml before Playwright |
| Google News RSS (VN) | world | 3/3 (100%, healthy) | 0/60 (0%, fallback target) | `content_extraction_rate` below 75%; try Readability-lxml before Playwright |
| Google News RSS (VN) | science | 3/3 (100%, healthy) | 0/60 (0%, fallback target) | `content_extraction_rate` below 75%; try Readability-lxml before Playwright |
| **Overall** | **12 category requests** | **12/12 (100%, healthy)** | **0/240 (0%, fallback target)** | **Content extraction is the fallback trigger for all four categories.** |

Health bands follow the probe thresholds: healthy at 95% or higher, warning at 75–94.99%, and fallback target below 75%. There were no transport failures and no per-attempt network-unverifiable outcomes. The aggregate average latency was 7,601.75 ms per category request.

## Evidence

The sanitized machine-readable evidence, including all 12 per-attempt outcomes, counts, latencies, aggregate rates, bands, and fallback targets, is in [2026-10-02-source-reliability-live.json](2026-10-02-source-reliability-live.json). Transport success means the RSS request returned parsed items; extraction success means fetched articles had nonempty extracted content.
