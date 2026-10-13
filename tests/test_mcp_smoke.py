from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_mcp_builds():
    subprocess.run(
        ["bun", "install"],
        cwd=REPO / "mcp",
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["bun", "run", "typecheck"],
        cwd=REPO / "mcp",
        check=True,
        capture_output=True,
        text=True,
    )


def test_cli_scorecard_path():
    proc = subprocess.run(
        ["uv", "run", "memory-bakeoff", "scorecard-path"],
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "MEM0_TELEMETRY": "False"},
    )
    data = json.loads(proc.stdout)
    assert "scorecard_md" in data
