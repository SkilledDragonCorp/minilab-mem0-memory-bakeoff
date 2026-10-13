from __future__ import annotations

from memory_bakeoff.schemas import ForgetInput, RecallInput, RememberInput


def test_remember_recall_forget_round_trip(mock_embedder_memory_store):  # type: ignore[no-untyped-def]
    store = mock_embedder_memory_store
    added = store.remember(
        RememberInput(content="User prefers dark mode", user_id="u1", infer=False)
    )
    memory_id = added["results"][0]["id"]
    recalled = store.recall(RecallInput(query="dark mode", user_id="u1", top_k=3))
    assert recalled["results"]
    assert any(r["id"] == memory_id for r in recalled["results"])
    store.forget(ForgetInput(memory_id=memory_id))
    after = store.recall(RecallInput(query="dark mode", user_id="u1", top_k=3))
    assert not any(r["id"] == memory_id for r in after.get("results", []))
