# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Documentation Context (Non-Obvious Only)

- **No docs folder**: All project knowledge lives in `app.py`, `templates/index.html`, and `static/style.css`. There is no README, wiki, or docstrings.
- **"EcoAI" is the product name**: The nav logo reads "♻️ EcoAI". Internally the project directory is `ai-waste-segregation`. Both names refer to the same thing.
- **SDG 12 framing is intentional**: The footer references "SDG 12 — Responsible Consumption and Production". This is not decorative — it is the stated mission of the internship project and should be preserved in any UI changes.
- **No tests exist**: There is no test suite, no test directory, and no CI. Behavioural claims cannot be verified programmatically.
- **The model name in code is incorrect**: `"gemini-3.6-flash"` in `app.py` is not a real model — any documentation of the app's AI capabilities should note this needs to be corrected before the app works.
