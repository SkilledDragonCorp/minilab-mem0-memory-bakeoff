# minilab-mem0-memory-bakeoff

SkilledDragon minilab proving **[mem0ai](https://github.com/mem0ai/mem0) 2.2.1** works as an open-source **Active Memory** layer (post–Meta Muse Wonder, Oct 12 2026). This harness adds/search/deletes memories, exposes MCP tools, and publishes a **Memory Scorecard**.

> **Hedge:** All comparisons are **SkilledDragon lab harness** results on OSS mem0 — **not** parity with Muse Wonder or Mem0 managed-platform vendor benchmarks.

## What we built

| Layer | Stack |
| --- | --- |
| Memory core | Python 3.12+ via [uv](https://docs.astral.sh/uv/), `mem0ai==2.2.1` |
| Keyless path | `Memory.from_config` → Ollama LLM stub, **FastEmbed**, **FAISS**, `add(..., infer=False)` |
| CLI | `memory-bakeoff` (remember / recall / forget / bench / scorecard-path) |
| MCP | Bun + TypeScript stdio server (`mcp/`) → spawns `uv run memory-bakeoff` with JSON argv |
| Skills | `.claude/skills/mem0-remember-recall`, `mem0-scorecard` |

Pin notes: [docs/MEM0_PIN.md](docs/MEM0_PIN.md). Upstream skill check recorded in [skills-lock.json](skills-lock.json).

## Setup

```bash
# Python
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --extra dev
cp .env.example .env

# MCP (Node >= 24)
nvm use   # .nvmrc → 24
cd mcp && bun install && bun run typecheck
```

## Tutorial

```bash
export MEM0_TELEMETRY=False

# Add + search (keyless)
uv run memory-bakeoff remember --json '{"content":"Alex prefers espresso","user_id":"alex","infer":false}'
uv run memory-bakeoff recall --json '{"query":"coffee preference","user_id":"alex","top_k":3}'

# Benchmark + scorecard
uv run memory-bakeoff bench run --json '{"top_k":5,"include_llm_bench":false}'
cat reports/scorecard.md
```

## Test results (local, Oct 13 2026)

```bash
export MEM0_TELEMETRY=False
uv run pytest tests -q
# 6 passed in ~5s

uv run ruff check src tests && uv run mypy src/memory_bakeoff
cd mcp && bun run typecheck
```

Sample scorecard metrics from this repo (`reports/scorecard.md`):

- Mean **recall@5**: **1.000** on fixture persona corpus (9 memories / 9 queries)
- Add latency p50: **~6 ms**; search p50: **~4 ms** (local FAISS + MiniLM, lab hardware)

## Using these skills in Claude Code and Cursor

Skills live **only** under `.claude/skills/`:

- `mem0-remember-recall` — CLI/MCP remember, recall, forget
- `mem0-scorecard` — run bench and read `reports/scorecard.md`

Copy or symlink into your agent skills path per vendor docs. Upstream Mem0 reference skill hash: see `skills-lock.json`.

## MCP

```json
{
  "mcpServers": {
    "mem0-memory-bakeoff": {
      "command": "bun",
      "args": ["run", "src/index.ts"],
      "cwd": "/path/to/minilab-mem0-memory-bakeoff/mcp",
      "env": { "MEM0_TELEMETRY": "False" }
    }
  }
}
```

Tools: `remember`, `recall`, `forget`, `scorecard_path`.

## API keys (optional)

| Variable | Purpose |
| --- | --- |
| `MEM0_TELEMETRY` | Set `False` in lab/CI (default in `.env.example`) |
| `MEMORY_BAKEOFF_DATA` | Local FAISS path (default `.data/mem0`) |
| `OPENAI_API_KEY` | Optional LLM bench + infer=true |
| `GEMINI_API_KEY` | Optional LLM bench (alternative) |
| `OLLAMA_*` / `FASTEMBED_MODEL` | Keyless stack tuning |

LLM benchmark runs only when `OPENAI_API_KEY` or `GEMINI_API_KEY` is set; otherwise skipped cleanly.

## Limitations

- OSS mem0 ≠ Mem0 Cloud proprietary algorithm scores in upstream README.
- FAISS path disables hybrid BM25 unless you switch vector store (e.g. local Qdrant).
- FastEmbed downloads models on first run; CI caches Hugging Face under `.cache/huggingface`.
- Muse Wonder / vendor benchmarks are **out of scope** for claims from this repo.

## Security

See [SECURITY.md](SECURITY.md). Gitleaks + dependency audits run in CI.

---

Built by **SkilledDragon LLC** — [skilleddragon.com](https://skilleddragon.com)
