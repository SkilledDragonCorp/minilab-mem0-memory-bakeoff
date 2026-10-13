# Security Policy

This is a **SkilledDragon educational minilab**, not a production product. It is published so people can try a small, keyed-off demo. We do **not** maintain these repos on a regular schedule and we do **not** operate a vulnerability response program for them.

## Contact

General questions: **hello@skilleddragon.com**  
Do not use a dedicated security mailbox for this repo — none exists.

## If you find an issue

- Prefer reporting **upstream** when the issue is in [mem0ai/mem0](https://github.com/mem0ai/mem0) or other dependencies.
- For something specific to this minilab’s wrapper scripts, you may email hello@skilleddragon.com. There is **no SLA**, and we may not patch or reply quickly.
- Do not expect private coordinated disclosure or paid bounty handling here.

## Minilab hygiene (what this repo does)

- Secrets only via environment variables (see `.env.example`); never commit `.env`.
- CLI and MCP inputs validated with Pydantic / Zod schemas.
- Pre-commit and CI run **gitleaks**.
- Dependency audits run in CI when configured.
- Telemetry disabled in CI via `MEM0_TELEMETRY=False`.

Use at your own risk. Pin versions, review the code, and treat this as sample material.
