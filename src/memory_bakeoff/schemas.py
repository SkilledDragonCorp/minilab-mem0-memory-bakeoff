"""Validated CLI / MCP payloads."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class RememberInput(BaseModel):
    content: str = Field(..., min_length=1, max_length=32_000)
    user_id: str = Field(..., min_length=1, max_length=256)
    agent_id: str | None = Field(default=None, max_length=256)
    run_id: str | None = Field(default=None, max_length=256)
    infer: bool = False
    metadata: dict[str, Any] | None = None


class RecallInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=8_000)
    user_id: str = Field(..., min_length=1, max_length=256)
    top_k: int = Field(default=5, ge=1, le=50)
    agent_id: str | None = Field(default=None, max_length=256)
    run_id: str | None = Field(default=None, max_length=256)


class ForgetInput(BaseModel):
    memory_id: str = Field(..., min_length=1, max_length=128)

    @field_validator("memory_id")
    @classmethod
    def no_shell_metacharacters(cls, v: str) -> str:
        if any(c in v for c in ";&|`$"):
            raise ValueError("memory_id contains invalid characters")
        return v


class BenchRunInput(BaseModel):
    fixture_path: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    include_llm_bench: bool = False
    label: str = Field(default="skilleddragon-lab-harness", max_length=128)
