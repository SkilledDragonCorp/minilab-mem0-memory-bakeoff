"""MemoryStore wrapper around mem0ai Memory client."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mem0 import Memory  # type: ignore[import-untyped]

from memory_bakeoff.config import default_storage_root, keyless_memory_config, llm_memory_config
from memory_bakeoff.schemas import ForgetInput, RecallInput, RememberInput


class MemoryStore:
    def __init__(
        self,
        storage_path: Path | None = None,
        *,
        mode: str = "keyless",
        config_override: dict[str, Any] | None = None,
    ) -> None:
        root = storage_path or default_storage_root()
        root.mkdir(parents=True, exist_ok=True)
        self.storage_path = root
        if config_override is not None:
            config: dict[str, Any] = config_override
        elif mode == "llm":
            llm_cfg = llm_memory_config(root)
            if llm_cfg is None:
                raise RuntimeError("LLM mode requires OPENAI_API_KEY or GEMINI_API_KEY")
            config = llm_cfg
        else:
            config = keyless_memory_config(root)
        self._memory = Memory.from_config(config)

    def remember(self, payload: RememberInput) -> dict[str, Any]:
        result: dict[str, Any] = self._memory.add(
            payload.content,
            user_id=payload.user_id,
            agent_id=payload.agent_id,
            run_id=payload.run_id,
            metadata=payload.metadata,
            infer=payload.infer,
        )
        return result

    def recall(self, payload: RecallInput) -> dict[str, Any]:
        filters: dict[str, str] = {"user_id": payload.user_id}
        if payload.agent_id:
            filters["agent_id"] = payload.agent_id
        if payload.run_id:
            filters["run_id"] = payload.run_id
        searched: dict[str, Any] = self._memory.search(
            query=payload.query, filters=filters, top_k=payload.top_k
        )
        return searched

    def forget(self, payload: ForgetInput) -> dict[str, Any]:
        self._memory.delete(payload.memory_id)
        return {"deleted": payload.memory_id}

    def close(self) -> None:
        self._memory.close()


def json_response(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)
