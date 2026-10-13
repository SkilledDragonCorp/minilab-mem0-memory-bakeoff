from __future__ import annotations

from pathlib import Path

import pytest
from mem0.embeddings.mock import MockEmbeddings
from mem0.utils.factory import EmbedderFactory

from memory_bakeoff.config import keyless_memory_config
from memory_bakeoff.store import MemoryStore


@pytest.fixture
def mock_embedder_memory_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> MemoryStore:
    """Keyless config with MockEmbeddings — no network or model download."""

    original = EmbedderFactory.create

    def patched_create(provider_name: str, config, vector_config=None):  # type: ignore[no-untyped-def]
        if provider_name == "fastembed":
            return MockEmbeddings()
        return original(provider_name, config, vector_config)

    monkeypatch.setattr(EmbedderFactory, "create", patched_create)
    cfg = keyless_memory_config(tmp_path)
    cfg["vector_store"]["config"]["embedding_model_dims"] = 10
    return MemoryStore(storage_path=tmp_path, config_override=cfg)
