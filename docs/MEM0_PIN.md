# mem0ai pin (2.2.1)

- **PyPI package:** `mem0ai==2.2.1` (recorded in `pyproject.toml` / `uv.lock`)
- **Upstream:** https://github.com/mem0ai/mem0 (Apache-2.0)
- **README at pin (summary):** Mem0 is an open-source memory layer for personalized AI (multi-level user/session/agent memory). Default cloud stack uses OpenAI LLM + embeddings; self-hosted supports many providers. April 2026 algorithm notes in upstream README describe managed-platform benchmarks — **this minilab does not claim parity** with those or with Meta Muse Wonder; we publish our own harness scorecard under `reports/`.

## Keyless lab stack (this repo)

```python
Memory.from_config({
  "llm": {"provider": "ollama", "config": {...}},
  "embedder": {"provider": "fastembed", "config": {"model": "sentence-transformers/all-MiniLM-L6-v2", "embedding_dims": 384}},
  "vector_store": {"provider": "faiss", "config": {"path": "...", "embedding_model_dims": 384}},
})
# memory.add(..., infer=False)
```

See upstream [Quickstart](https://docs.mem0.ai/quickstart) for full SDK documentation.
