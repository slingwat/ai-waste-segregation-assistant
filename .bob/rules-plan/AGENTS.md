# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Architectural Constraints (Non-Obvious Only)

- **Stateless by design**: Flask holds no state between requests. The Gemini client is a module-level singleton (`client = genai.Client(...)` at import time) — it is safe to reuse across requests because the SDK is stateless.
- **Prompt schema is the integration contract**: The only contract between backend and frontend is the 5-field plain-text format. Switching to structured JSON output (`response_schema`) would be the highest-impact refactor — it would decouple the prompt from `formatResult()` and make output reliable.
- **Single-file architecture is load-bearing**: There is no package structure, no blueprints, no service layer. Any feature that adds a second route or a helper function can stay in `app.py` without architectural change up to ~150 lines.
- **No persistence layer**: There is no database, no session, no cache. Each `/analyze` POST is fully independent. Adding history or user sessions would require introducing a storage backend (e.g., SQLite + Flask-Session) as a greenfield addition.
- **`venv/` contains Python 3.14**: This is a pre-release Python version. Some packages may have compatibility issues. Do not assume standard CPython 3.11/3.12 behaviour.
- **No rate limiting or auth**: The `/analyze` endpoint is open. Any deployment plan must account for API quota exhaustion and cost exposure from unauthenticated access.
