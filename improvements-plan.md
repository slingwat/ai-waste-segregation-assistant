# AI Waste Segregation Assistant — Improvements Plan

## Overview

Five targeted improvement areas applied to the existing Flask + Gemini architecture.
No new dependencies, no architectural change. All changes stay within:
- `app.py` (backend logic, prompt, Gemini call)
- `templates/index.html` (UI markup, inline JS)
- `static/style.css` (visual styles)

The work is split into five independent sub-tasks that can be implemented and reviewed one at a time.

---

## Sub-Task 1 — Fix the Gemini model name and switch to structured JSON output

**Status:** [x] done

### Intent
The app currently uses `"gemini-3.6-flash"` (line 53 of `app.py`), which is not a real model name and causes every analysis request to fail at runtime. At the same time, the AI response is plain text that is parsed by regex, so any deviation from the exact 5-field format breaks the UI. This sub-task fixes both problems together by:
1. Correcting the model name to `"gemini-2.0-flash"`.
2. Switching the Gemini call to use a JSON response schema so the response is always machine-parseable, regardless of how the model phrases its output.

### Expected Outcomes
- Every analysis request returns a valid HTTP 200 with a structured JSON body.
- The backend returns a flat JSON object with exactly five keys: `item`, `category`, `reason`, `disposal`, `confidence`.
- The frontend receives a reliable data structure instead of raw text, eliminating the regex parser in `formatResult()`.
- The Gemini prompt is updated to match the new schema contract.

### Todo List
1. In `app.py`, change `model="gemini-3.6-flash"` to `model="gemini-2.0-flash"`.
2. Define a `response_schema` dict (or Pydantic model) with five string fields matching the existing labels: `item`, `category`, `reason`, `disposal`, `confidence`.
3. Pass `config={"response_mime_type": "application/json", "response_schema": <schema>}` to `client.models.generate_content()`.
4. Update the prompt text in `app.py` to describe the fields as a JSON object rather than labelled lines; keep the same content constraints (no hallucination, express uncertainty, recommend local guidelines).
5. Parse `response.text` as JSON in `analyze()` and pass the parsed dict to `jsonify()` under a `result` key — so the frontend receives `{ result: { item, category, reason, disposal, confidence } }`.
6. In `index.html`, replace the `formatResult(text)` regex function with a `renderResult(data)` function that reads the five named keys from the object.

### Relevant Context
- `app.py` lines 52–63: Gemini call and `contents` list.
- `app.py` lines 31–49: Prompt string to update.
- `app.py` line 53: Model name to fix.
- `index.html` lines 299–323: `formatResult()` to replace.
- `index.html` line 265: Call site `formatResult(data.result)` to update.

---

## Sub-Task 2 — Colour-coded category badge and structured result layout

**Status:** [x] done

### Intent
The current result panel is a single block of text with bolded labels. After Sub-Task 1 switches to structured JSON output, each field is available as a discrete value. This sub-task uses those values to render a visually distinct result card: a prominent colour-coded badge showing the waste category at the top, followed by clean labelled rows for the remaining four fields.

The five categories each get a distinct colour that communicates meaning at a glance (e.g., green for organic, blue for recyclable, orange for hazardous).

### Expected Outcomes
- The result section shows a colour-coded pill/badge as the first visible element after analysis.
- Category badge colours follow a fixed mapping:
  - Wet/Organic → green (`#2e7d32`)
  - Dry/Recyclable → blue (`#1565c0`)
  - E-Waste → purple (`#6a1b9a`)
  - Hazardous → orange/red (`#bf360c`)
  - Other → grey (`#546e7a`)
- Below the badge: Item, Reason, Disposal, and Confidence are shown as individual labelled rows.
- Confidence level is visually differentiated (e.g., bold green for High, amber for Medium, red for Low).
- The existing `.analysis` CSS class is replaced or augmented with `.result-card`, `.category-badge`, `.result-row`, and `.confidence-tag` classes.

### Todo List
1. After Sub-Task 1 is complete, update `renderResult(data)` in `index.html` to build the new HTML structure: badge first, then rows.
2. Add a `getCategoryColor(category)` helper in the inline JS that maps category string → CSS colour value.
3. Add a `getConfidenceClass(confidence)` helper that maps `"High"` / `"Medium"` / `"Low"` → a CSS class.
4. Add `.category-badge`, `.result-row`, `.result-label`, `.result-value`, and `.confidence-tag` classes to `style.css`, using the colour mapping above.
5. Remove or replace the old `.analysis` block styling in `style.css` with the new class definitions.
6. Ensure the mobile breakpoint (`@media (max-width: 700px)`) still applies sensibly to the new layout.

### Relevant Context
- `index.html` lines 258–267: Existing `.analysis` div — the insertion point.
- `style.css` lines 259–275: Existing `.analysis` styles to replace.
- `style.css` line 373: Mobile breakpoint to update if needed.
- Category strings defined in `app.py` prompt line 39: `Wet/Organic`, `Dry/Recyclable`, `E-Waste`, `Hazardous`, `Other`.

---

## Sub-Task 3 — Specific error messages and "Try Again" button

**Status:** [x] done

### Intent
The current error handling shows one of two generic messages: "No image uploaded." or "Something went wrong while analyzing the image." Users cannot tell whether the failure was a missing API key, a network timeout, an oversized image, or a bad Gemini response. This sub-task introduces distinct error states and a "Try Again" button that re-submits the last image without the user having to re-select it.

### Expected Outcomes
- The backend returns distinct error codes/messages for each failure scenario (see error map below).
- The frontend renders a distinct user-facing message per error code.
- A "🔄 Try Again" button appears on every error state and re-runs `analyzeWaste()` against the already-selected file.
- The "Try Again" button is not shown on the initial placeholder state, only after a failed attempt.

**Error map:**

| Scenario | HTTP Status | `error_code` | User Message |
|---|---|---|---|
| No file in request | 400 | `no_file` | "No image was received. Please choose a file and try again." |
| Empty filename | 400 | `no_file` | "Please select an image file before analyzing." |
| MIME type not image/* | 400 | `invalid_file` | "That file doesn't look like an image. Please upload a JPG, PNG, or WebP." |
| File > 10 MB | 413 | `file_too_large` | "The image is too large (max 10 MB). Please resize it and try again." |
| Gemini API error (SDK exception) | 502 | `ai_error` | "The AI service returned an error. Please wait a moment and try again." |
| JSON parse failure on Gemini response | 502 | `ai_parse_error` | "The AI response was in an unexpected format. Please try again." |
| Unhandled exception | 500 | `server_error` | "Something went wrong on our end. Please try again." |

### Todo List
1. In `app.py`, add a MIME type check after reading `image.mimetype` — reject anything that does not start with `image/`.
2. Add a `MAX_IMAGE_BYTES = 10 * 1024 * 1024` constant and check `len(image_data)` after `image.read()`.
3. Wrap the Gemini SDK call in its own `try/except` block (separate from the outer handler) and return `{"error": "...", "error_code": "ai_error"}`.
4. Wrap `json.loads(response.text)` in a `try/except json.JSONDecodeError` and return `error_code: "ai_parse_error"`.
5. Update all `return jsonify({"error": ...})` calls to also include an `"error_code"` string key.
6. In `index.html`, update the error rendering branch to read `data.error_code` and look up the user-facing message from a JS constant map.
7. In `index.html`, append a "🔄 Try Again" button to every error HTML block; its `onclick` calls `analyzeWaste()` directly.
8. Ensure the "Try Again" path does not require re-selecting the file (the `imageInput` value is still set from the previous selection).

### Relevant Context
- `app.py` lines 19–26: Existing file presence checks.
- `app.py` lines 28–29: `image.read()` call — size check goes here.
- `app.py` lines 52–63: Gemini call — wrap in inner try/except.
- `app.py` lines 69–73: Outer except — change to `error_code: "server_error"`.
- `index.html` lines 243–254: Existing error rendering block to extend.
- `index.html` lines 175–296: `analyzeWaste()` function — "Try Again" calls this directly.

---

## Sub-Task 4 — User experience: drag-and-drop upload and scroll-to-result

**Status:** [x] done

### Intent
Two friction points exist in the current UX:
1. The file selector is a hidden `<input>` triggered by a styled label. There is no drag-and-drop zone, which is the instinctive behaviour on desktop.
2. After clicking Analyze, the result section is below the fold on most screens. The user does not know analysis is complete unless they scroll down.

This sub-task adds a visible drag-and-drop zone over the existing upload area and auto-scrolls to the result section once the AI response arrives.

### Expected Outcomes
- The upload card area accepts files dragged from the desktop; on drop, the file is treated identically to a file-input selection (preview shown, same `imageInput` reference used for the fetch).
- The drag-and-drop zone changes appearance (dashed green border, light green background) while a file is being dragged over it.
- After the Gemini response is rendered (success or error), the page automatically scrolls to the result section.
- No change to the existing click-to-browse behaviour — both paths work.
- The file input's `accept="image/*"` restriction is mirrored on the drop handler (non-image drops are ignored with a brief inline message).

### Todo List
1. In `index.html`, wrap the upload card's interior content (icon, heading, choose button) in a `<div id="drop-zone">`.
2. Add `dragover`, `dragenter`, `dragleave`, and `drop` event listeners on `#drop-zone` in the inline JS.
3. On `drop`: extract `event.dataTransfer.files[0]`, assign it to the `imageInput` via `DataTransfer` object (so `imageInput.files` is set), then call `previewImage()`.
4. Add `.drag-over` CSS class to `style.css` — dashed green border + `#edf5ef` background — applied during `dragenter`/`dragover` and removed on `dragleave`/`drop`.
5. At the end of `analyzeWaste()`, after the result HTML is injected (both success and error paths), call `document.getElementById("result").scrollIntoView({ behavior: "smooth", block: "start" })`.
6. Test that the mobile layout is not negatively affected (drag-and-drop does nothing on touch devices; the upload button still works).

### Relevant Context
- `index.html` lines 41–79: Upload card section — wrap interior here.
- `index.html` lines 146–172: `previewImage()` — called after drag drop.
- `index.html` lines 258–267: Success result injection — add scroll call here.
- `index.html` lines 272–282: Error result injection — add scroll call here.
- `style.css` lines 95–107: `.upload-card` — the drop zone target.

---

## Sub-Task 5 — Responsible AI communication: uncertainty indicators and SDG disclaimer

**Status:** [x] done

### Intent
The app gives AI-generated disposal advice that users may act on in the real world. Two responsible-AI improvements are needed:
1. When the Confidence field is "Low" or "Medium", the UI should display a contextual caution notice recommending the user verify with local waste-management guidelines — rather than just showing the word "Low" in the result.
2. The existing footer disclaimer ("AI-generated guidance should be verified with local waste-management rules.") is 11px and easy to miss. It should also appear inline within the result card itself, directly below the disposal recommendation, so it is seen in context.

These changes do not alter the AI prompt or API call — they are purely presentational enhancements to the result rendering introduced in Sub-Task 2.

### Expected Outcomes
- When `confidence === "Low"` or `confidence === "Medium"`, a yellow/amber caution banner renders inside the result card, containing the text: "⚠️ AI confidence is [level]. Always verify disposal guidance with your local waste-management authority."
- The caution banner does not appear when `confidence === "High"`.
- A small italicised disclaimer ("AI-generated guidance. Verify with local rules.") appears directly below the Disposal field value inside the result card, regardless of confidence level.
- The footer disclaimer remains unchanged (it serves a different audience reading the page before interacting).
- New CSS classes: `.caution-banner` (amber background, amber border) and `.disposal-disclaimer` (small, muted italic).

### Todo List
1. In `renderResult(data)` in `index.html` (added in Sub-Task 2), add a conditional block that renders `.caution-banner` when `data.confidence` is `"Low"` or `"Medium"`.
2. Add the inline `.disposal-disclaimer` element directly after the Disposal row value.
3. Add `.caution-banner` to `style.css`: amber/yellow background (`#fff8e1`), left border `#f9a825`, padding, border-radius matching the card style.
4. Add `.disposal-disclaimer` to `style.css`: `font-size: 12px`, `font-style: italic`, `color: #68736c` (matching existing muted tone).
5. Ensure neither element appears in the loading state or error state — only in the success render path.

### Relevant Context
- `index.html` lines 258–267: Success result injection — this is where `renderResult(data)` is called (established in Sub-Task 2).
- `style.css` line 364: `.disclaimer` — match the existing muted style for `.disposal-disclaimer`.
- `app.py` prompt line 44: `Confidence: <High, Medium, or Low>` — the source of truth for valid values.
- The caution banner copy aligns with the existing footer disclaimer wording on `index.html` line 136.
