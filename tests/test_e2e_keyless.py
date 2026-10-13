from __future__ import annotations

import pytest

from memory_bakeoff.schemas import RecallInput, RememberInput
from memory_bakeoff.store import MemoryStore


@pytest.mark.e2e
def test_keyless_add_search(tmp_path):  # type: ignore[no-untyped-def]
    store = MemoryStore(storage_path=tmp_path / "e2e", mode="keyless")
    try:
        store.remember(
            RememberInput(content="Casey drinks oat milk lattes.", user_id="casey", infer=False)
        )
        result = store.recall(
            RecallInput(query="What milk does Casey prefer?", user_id="casey", top_k=3)
        )
        assert result["results"]
        assert "oat" in result["results"][0]["memory"].lower()
    finally:
        store.close()
