from __future__ import annotations

from pathlib import Path

from memory_bakeoff.bench import load_fixture, run_bench
from memory_bakeoff.schemas import BenchRunInput


def test_fixture_loads():
    root = Path(__file__).resolve().parents[1]
    fixture = root / "src/memory_bakeoff/fixtures/persona_corpus.jsonl"
    memories, queries = load_fixture(fixture)
    assert len(memories) >= 6
    assert len(queries) >= 3


def test_bench_run_mock_store(tmp_path, monkeypatch):  # type: ignore[no-untyped-def]
    import memory_bakeoff.config as cfg_module
    from mem0.embeddings.mock import MockEmbeddings
    from mem0.utils.factory import EmbedderFactory

    original = EmbedderFactory.create

    def patched_create(provider_name: str, config, vector_config=None):  # type: ignore[no-untyped-def]
        if provider_name == "fastembed":
            return MockEmbeddings()
        return original(provider_name, config, vector_config)

    def mock_keyless(path, **kwargs):  # type: ignore[no-untyped-def]
        cfg = cfg_module.keyless_memory_config(path, **kwargs)
        cfg["embedder"]["config"]["embedding_dims"] = 10
        cfg["vector_store"]["config"]["embedding_model_dims"] = 10
        return cfg

    monkeypatch.setattr(EmbedderFactory, "create", patched_create)
    monkeypatch.setattr("memory_bakeoff.store.keyless_memory_config", mock_keyless)
    summary = run_bench(BenchRunInput(top_k=3), tmp_path / "bench")
    assert summary["memories_ingested"] > 0
    assert summary["recall_at_k"]["mean"] >= 0.0
