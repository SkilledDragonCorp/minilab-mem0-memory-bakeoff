---
name: mem0-scorecard
description: Run the SkilledDragon mem0 memory bakeoff benchmark and read reports/scorecard.md plus scorecard.json (latency, recall@k, lab disclaimer).
---

# mem0 Memory Scorecard

Generate the **Memory Scorecard** for this minilab harness (not Muse Wonder parity).

## Run benchmark

```bash
export MEM0_TELEMETRY=False
uv run memory-bakeoff bench run --json '{"top_k":5,"include_llm_bench":false}'
```

Outputs:

- `reports/scorecard.md` — human-readable summary
- `reports/scorecard.json` — machine-readable metrics

## MCP

Call tool `scorecard_path` to resolve current report paths after a bench run.

## Metrics

- Add/search latency (p50, p95, mean)
- recall@k on `src/memory_bakeoff/fixtures/persona_corpus.jsonl`
- Optional LLM bench when API keys are set (skipped cleanly otherwise)

Every comparison is labeled **SkilledDragon lab harness** on mem0ai OSS 2.2.1.
