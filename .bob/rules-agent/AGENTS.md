# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Coding Rules (Non-Obvious Only)

- **Model name is wrong**: `app.py:53` uses `"gemini-3.6-flash"` which does not exist. Fix to `"gemini-1.5-flash"` or `"gemini-2.0-flash"` before any live testing.
- **Image → Gemini pipeline is memory-only**: `image.read()` → `base64.b64encode()` → `inline_data`. Never introduce disk writes into this path without adding cleanup logic.
- **Prompt and `formatResult()` are tightly coupled**: The plain-text 5-field schema in `app.py` is parsed by raw regex in `index.html`. Any prompt schema change requires a matching JS update — there is no structured output contract.
- **No file validation on `/analyze`**: Backend only checks `"image" in request.files` and `filename != ""`. It does not validate MIME type, file signature, or size. Add `flask.request.content_length` and `image.mimetype` checks if exposing publicly.
- **Single entry point**: All backend logic is in `app.py`. Do not split into modules unless the file grows significantly — the project is intentionally minimal.
- **No `requirements.txt`**: Adding a dependency means `pip install <pkg>` into `venv/` only. Update `AGENTS.md` with the package name and version.
