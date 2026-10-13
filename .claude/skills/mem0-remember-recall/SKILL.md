---
name: mem0-remember-recall
description: Use the SkilledDragon mem0 minilab to add, search, and delete local OSS memories via uv CLI or MCP (keyless FastEmbed + FAISS by default).
---

# mem0 remember / recall (SkilledDragon minilab)

This repo wraps **mem0ai 2.2.1** as an open-source active memory layer. Default path is **keyless** (`infer=false`): FastEmbed + FAISS + Ollama config stub (LLM not called when infer is false).

## CLI (validated JSON only)

```bash
export MEM0_TELEMETRY=False
uv run memory-bakeoff remember --json '{"content":"Prefers dark mode","user_id":"alice","infer":false}'
uv run memory-bakeoff recall --json '{"query":"theme preference","user_id":"alice","top_k":5}'
uv run memory-bakeoff forget --json '{"memory_id":"<id from add results>"}'
```

## MCP

Start the Bun stdio server from `mcp/` (tools: `remember`, `recall`, `forget`, `scorecard_path`). It spawns `uv run memory-bakeoff …` with JSON argv — no shell string composition.

## Notes

- Not comparable to Meta Muse Wonder vendor benchmarks; this is the SkilledDragon lab harness only.
- Optional LLM extraction requires `OPENAI_API_KEY` or `GEMINI_API_KEY` and `infer=true`.
