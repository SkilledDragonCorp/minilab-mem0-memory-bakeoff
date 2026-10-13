"""Benchmark runner: latency + recall@k; writes Memory Scorecard."""

from __future__ import annotations

import json
import statistics
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from memory_bakeoff.config import MEM0AI_VERSION, llm_api_key_present
from memory_bakeoff.schemas import BenchRunInput, RecallInput, RememberInput
from memory_bakeoff.store import MemoryStore

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
DEFAULT_FIXTURE = FIXTURES_DIR / "persona_corpus.jsonl"
REPORTS_DIR = REPO_ROOT / "reports"


@dataclass
class MemoryRow:
    persona_id: str
    memory: str
    row_id: str


@dataclass
class QueryRow:
    persona_id: str
    query: str
    relevant_row_ids: list[str]


def load_fixture(path: Path) -> tuple[list[MemoryRow], list[QueryRow]]:
    memories: list[MemoryRow] = []
    queries: list[QueryRow] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("type") == "query":
                queries.append(
                    QueryRow(
                        persona_id=row["persona_id"],
                        query=row["query"],
                        relevant_row_ids=list(row["relevant_row_ids"]),
                    )
                )
            else:
                memories.append(
                    MemoryRow(
                        persona_id=row["persona_id"],
                        memory=row["memory"],
                        row_id=row["row_id"],
                    )
                )
    return memories, queries


def recall_at_k(retrieved_ids: list[str], relevant: set[str], k: int) -> float:
    top = retrieved_ids[:k]
    hits = sum(1 for rid in top if rid in relevant)
    return hits / len(relevant) if relevant else 0.0


def run_bench(payload: BenchRunInput, storage_path: Path) -> dict[str, Any]:
    fixture = Path(payload.fixture_path) if payload.fixture_path else DEFAULT_FIXTURE
    try:
        fixture_label = str(fixture.resolve().relative_to(REPO_ROOT.resolve()))
    except ValueError:
        fixture_label = str(fixture)
    memories, queries = load_fixture(fixture)

    store = MemoryStore(storage_path=storage_path, mode="keyless")
    row_id_to_memory_id: dict[str, str] = {}
    add_latencies: list[float] = []
    try:
        for mem in memories:
            t0 = time.perf_counter()
            result = store.remember(
                RememberInput(content=mem.memory, user_id=mem.persona_id, infer=False)
            )
            add_latencies.append(time.perf_counter() - t0)
            for item in result.get("results", []):
                row_id_to_memory_id[mem.row_id] = str(item["id"])

        search_latencies: list[float] = []
        recall_scores: list[float] = []
        for q in queries:
            t0 = time.perf_counter()
            recalled = store.recall(
                RecallInput(query=q.query, user_id=q.persona_id, top_k=payload.top_k)
            )
            search_latencies.append(time.perf_counter() - t0)
            retrieved_memory_ids = [str(r["id"]) for r in recalled.get("results", [])]
            memory_id_to_row = {mid: rid for rid, mid in row_id_to_memory_id.items()}
            retrieved_row_ids = [
                memory_id_to_row[mid] for mid in retrieved_memory_ids if mid in memory_id_to_row
            ]
            relevant = set(q.relevant_row_ids)
            recall_scores.append(recall_at_k(retrieved_row_ids, relevant, payload.top_k))

        llm_bench: dict[str, Any] | None = None
        if payload.include_llm_bench:
            if not llm_api_key_present():
                llm_bench = {"skipped": True, "reason": "No OPENAI_API_KEY or GEMINI_API_KEY"}
            else:
                llm_store = MemoryStore(storage_path=storage_path / "llm_bench", mode="llm")
                try:
                    t0 = time.perf_counter()
                    llm_store.remember(
                        RememberInput(
                            content="Lab persona notes they prefer window seats on flights.",
                            user_id="bench_llm_user",
                            infer=True,
                        )
                    )
                    llm_add_s = time.perf_counter() - t0
                    t0 = time.perf_counter()
                    llm_store.recall(
                        RecallInput(
                            query="Where does the user like to sit on planes?",
                            user_id="bench_llm_user",
                            top_k=3,
                        )
                    )
                    llm_search_s = time.perf_counter() - t0
                    llm_bench = {
                        "skipped": False,
                        "add_latency_s": llm_add_s,
                        "search_latency_s": llm_search_s,
                        "note": (
                            "SkilledDragon lab harness only — "
                            "not comparable to Muse Wonder vendor benchmarks."
                        ),
                    }
                finally:
                    llm_store.close()
    finally:
        store.close()

    summary: dict[str, Any] = {
        "harness_label": payload.label,
        "generated_at": datetime.now(UTC).isoformat(),
        "mem0ai_version": MEM0AI_VERSION,
        "fixture": fixture_label,
        "memories_ingested": len(memories),
        "queries_evaluated": len(queries),
        "top_k": payload.top_k,
        "latency": {
            "add_ms": {
                "p50": _pct_ms(add_latencies, 50),
                "p95": _pct_ms(add_latencies, 95),
                "mean": _mean_ms(add_latencies),
            },
            "search_ms": {
                "p50": _pct_ms(search_latencies, 50),
                "p95": _pct_ms(search_latencies, 95),
                "mean": _mean_ms(search_latencies),
            },
        },
        "recall_at_k": {
            "k": payload.top_k,
            "mean": statistics.mean(recall_scores) if recall_scores else 0.0,
            "per_query": recall_scores,
        },
        "llm_bench": llm_bench,
        "disclaimer": (
            "Scores reflect the SkilledDragon minilab harness on mem0ai OSS "
            f"{MEM0AI_VERSION}. They are not parity claims vs Meta Muse Wonder vendor benchmarks."
        ),
    }
    return summary


def _mean_ms(samples: list[float]) -> float:
    return statistics.mean(samples) * 1000 if samples else 0.0


def _pct_ms(samples: list[float], pct: float) -> float:
    if not samples:
        return 0.0
    ordered = sorted(samples)
    idx = max(0, min(len(ordered) - 1, int(round((pct / 100) * (len(ordered) - 1)))))
    return ordered[idx] * 1000


def write_scorecard(summary: dict[str, Any], reports_dir: Path | None = None) -> tuple[Path, Path]:
    out_dir = reports_dir or REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "scorecard.json"
    md_path = out_dir / "scorecard.md"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lat = summary["latency"]
    rec = summary["recall_at_k"]
    add_ms = lat["add_ms"]
    search_ms = lat["search_ms"]
    md = f"""# Mem0 Memory Scorecard (SkilledDragon Lab Harness)

> **Disclaimer:** {summary["disclaimer"]}

| Field | Value |
| --- | --- |
| Generated (UTC) | {summary["generated_at"]} |
| mem0ai pin | `{summary["mem0ai_version"]}` |
| Harness label | `{summary["harness_label"]}` |
| Memories ingested | {summary["memories_ingested"]} |
| Queries evaluated | {summary["queries_evaluated"]} |
| top_k | {summary["top_k"]} |

## Latency (this lab run)

| Operation | p50 (ms) | p95 (ms) | mean (ms) |
| --- | ---: | ---: | ---: |
| add | {add_ms["p50"]:.2f} | {add_ms["p95"]:.2f} | {add_ms["mean"]:.2f} |
| search | {search_ms["p50"]:.2f} | {search_ms["p95"]:.2f} | {search_ms["mean"]:.2f} |

## Recall@{summary["top_k"]} (fixture persona corpus)

**Mean recall@{summary["top_k"]}:** {rec["mean"]:.3f}

Per-query scores: `{rec["per_query"]}`

## Optional LLM bench

```json
{json.dumps(summary.get("llm_bench"), indent=2)}
```

Built by [SkilledDragon LLC](https://skilleddragon.com) — OSS memory evaluation minilab.
"""
    md_path.write_text(md, encoding="utf-8")
    return md_path, json_path


def scorecard_paths(reports_dir: Path | None = None) -> dict[str, str]:
    out_dir = reports_dir or REPORTS_DIR
    return {
        "scorecard_md": str(out_dir / "scorecard.md"),
        "scorecard_json": str(out_dir / "scorecard.json"),
    }
