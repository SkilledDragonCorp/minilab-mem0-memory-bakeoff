"""Mem0 configuration builders for keyless and optional LLM-backed modes."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

MEM0AI_VERSION = "2.2.1"
FASTEMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
FASTEMBED_DIMS = 384


def ensure_telemetry_env() -> None:
    if "MEM0_TELEMETRY" not in os.environ:
        os.environ["MEM0_TELEMETRY"] = "False"


def keyless_memory_config(
    storage_path: str | Path,
    *,
    vector_provider: Literal["faiss", "qdrant"] = "faiss",
) -> dict[str, Any]:
    """Keyless stack: Ollama LLM (unused when infer=False), FastEmbed, local vector store."""
    ensure_telemetry_env()
    path = str(storage_path)
    vector_store: dict[str, Any]
    if vector_provider == "faiss":
        vector_store = {
            "provider": "faiss",
            "config": {
                "path": path,
                "collection_name": "memory_bakeoff",
                "embedding_model_dims": FASTEMBED_DIMS,
            },
        }
    else:
        vector_store = {
            "provider": "qdrant",
            "config": {
                "path": path,
                "collection_name": "memory_bakeoff",
                "embedding_model_dims": FASTEMBED_DIMS,
                "on_disk": True,
            },
        }

    return {
        "llm": {
            "provider": "ollama",
            "config": {
                "model": os.environ.get("OLLAMA_MODEL", "llama3.2:1b"),
                "ollama_base_url": os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            },
        },
        "embedder": {
            "provider": "fastembed",
            "config": {
                "model": os.environ.get("FASTEMBED_MODEL", FASTEMBED_MODEL),
                "embedding_dims": FASTEMBED_DIMS,
            },
        },
        "vector_store": vector_store,
    }


def llm_api_key_present() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY"))


def llm_memory_config(storage_path: str | Path) -> dict[str, Any] | None:
    """Cloud LLM + FastEmbed when an API key is available; otherwise None."""
    if os.environ.get("OPENAI_API_KEY"):
        llm: dict[str, Any] = {
            "provider": "openai",
            "config": {"model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini")},
        }
    elif os.environ.get("GEMINI_API_KEY"):
        llm = {
            "provider": "gemini",
            "config": {"model": os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")},
        }
    else:
        return None

    base = keyless_memory_config(storage_path)
    base["llm"] = llm
    return base


def default_storage_root() -> Path:
    return Path(os.environ.get("MEMORY_BAKEOFF_DATA", ".data/mem0"))
