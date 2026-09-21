# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Stack

- Python 3.14, Flask 3.1, `google-genai` 2.19 (Gemini SDK)
- Single-page app: `app.py` (backend) + `templates/index.html` (UI + JS) + `static/style.css`
- Virtual environment at `venv/` using Python 3.14

## Running the App

```bash
source venv/bin/activate
GEMINI_API_KEY=<your_key> python app.py
```

There is no `requirements.txt`. Dependencies live only in `venv/`. If you add a package, install it into `venv/` and document it here.

## Critical Gotchas

- **Model name**: [`app.py:53`](app.py:53) uses `"gemini-3.6-flash"` — this is **not a real model name** and will cause a runtime API error. The correct names are `"gemini-1.5-flash"` or `"gemini-2.0-flash"`.
- **API key**: `os.environ.get("GEMINI_API_KEY")` returns `None` silently if unset — the app starts fine but every `/analyze` call fails with a cryptic SDK error.
- **Image handling**: Images are read entirely into memory (`image.read()`), base64-encoded, and sent inline to Gemini. Nothing is ever written to disk. Do not add file-save logic unless intentional.
- **No `MAX_CONTENT_LENGTH`**: Flask has no upload size cap configured. Large images will be accepted and forwarded to Gemini.

## AI Prompt Contract

The prompt in [`app.py:31–49`](app.py:31) enforces a strict 5-field plain-text schema:

```
Item: ...
Category: <Wet/Organic | Dry/Recyclable | E-Waste | Hazardous | Other>
Reason: ...
Disposal: ...
Confidence: <High | Medium | Low>
```

The frontend `formatResult()` in [`templates/index.html:299`](templates/index.html:299) parses this by regex (bold labels, `\n` → `<br>`). If the prompt or schema changes, `formatResult()` must be updated in sync — there is no structured JSON output mode.

## Code Style

- No linter or formatter config exists (no `pyproject.toml`, `.flake8`, `black.toml`, etc.)
- Follow the existing style: 4-space Python indent, single blank line between top-level functions, no type annotations.
- JS in `index.html` uses `async/await` with `fetch`; no bundler, no TypeScript, no npm.
- CSS uses plain hex colours from a fixed green palette (`#269447` primary, `#f4f8f5` background). Do not introduce CSS variables or external frameworks.

## Testing

There is no test suite. No `pytest`, `unittest`, or test directory exists.
