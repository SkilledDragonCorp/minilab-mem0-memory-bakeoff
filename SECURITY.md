# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 0.1.x (main) | Yes |

## Reporting a vulnerability

Email **security@skilleddragon.com** with reproduction steps and impact. Do not open public issues for sensitive reports.

## Minilab practices

- Secrets only via environment variables (see `.env.example`); never commit `.env`.
- CLI and MCP inputs validated with Pydantic / Zod schemas.
- Pre-commit and CI run **gitleaks** (`gitleaks git --redact --exit-code 1`).
- Dependency audits: `pip-audit` and `bun audit` (CI fails on high severity).
- Telemetry disabled in CI via `MEM0_TELEMETRY=False`.

## Upstream

Memory core: [mem0ai/mem0](https://github.com/mem0ai/mem0) (Apache-2.0). Report core SDK issues upstream when appropriate.
