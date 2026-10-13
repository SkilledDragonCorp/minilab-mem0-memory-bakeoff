"""CLI entrypoint for memory-bakeoff (also invoked by MCP server)."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from memory_bakeoff.bench import run_bench, scorecard_paths, write_scorecard
from memory_bakeoff.config import default_storage_root, ensure_telemetry_env
from memory_bakeoff.schemas import BenchRunInput, ForgetInput, RecallInput, RememberInput
from memory_bakeoff.store import MemoryStore, json_response


def _load_json_arg(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("JSON payload must be an object")
    return data


def cmd_remember(args: argparse.Namespace) -> None:
    payload = RememberInput.model_validate(_load_json_arg(args.json))
    store = MemoryStore(storage_path=Path(args.data_dir) if args.data_dir else None)
    try:
        print(json_response(store.remember(payload)))
    finally:
        store.close()


def cmd_recall(args: argparse.Namespace) -> None:
    payload = RecallInput.model_validate(_load_json_arg(args.json))
    store = MemoryStore(storage_path=Path(args.data_dir) if args.data_dir else None)
    try:
        print(json_response(store.recall(payload)))
    finally:
        store.close()


def cmd_forget(args: argparse.Namespace) -> None:
    payload = ForgetInput.model_validate(_load_json_arg(args.json))
    store = MemoryStore(storage_path=Path(args.data_dir) if args.data_dir else None)
    try:
        print(json_response(store.forget(payload)))
    finally:
        store.close()


def cmd_bench_run(args: argparse.Namespace) -> None:
    payload = BenchRunInput.model_validate(_load_json_arg(args.json) if args.json else {})
    storage = Path(args.data_dir) if args.data_dir else Path(tempfile.mkdtemp(prefix="mem0-bench-"))
    summary = run_bench(payload, storage)
    md_path, json_path = write_scorecard(summary)
    out = {**summary, "scorecard_md": str(md_path), "scorecard_json": str(json_path)}
    print(json_response(out))


def cmd_scorecard_path(_args: argparse.Namespace) -> None:
    print(json_response(scorecard_paths()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="memory-bakeoff")
    parser.add_argument(
        "--data-dir",
        default=str(default_storage_root()),
        help="Mem0 local storage path (default: MEMORY_BAKEOFF_DATA or .data/mem0)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name, handler in [
        ("remember", cmd_remember),
        ("recall", cmd_recall),
        ("forget", cmd_forget),
    ]:
        p = sub.add_parser(name)
        p.add_argument("--json", required=True, help="JSON payload")
        p.set_defaults(func=handler)

    bench = sub.add_parser("bench")
    bench_sub = bench.add_subparsers(dest="bench_cmd", required=True)
    run_p = bench_sub.add_parser("run")
    run_p.add_argument("--json", default="{}", help="BenchRunInput JSON")
    run_p.set_defaults(func=cmd_bench_run)

    sc = sub.add_parser("scorecard-path")
    sc.set_defaults(func=cmd_scorecard_path)
    return parser


def main() -> None:
    ensure_telemetry_env()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
