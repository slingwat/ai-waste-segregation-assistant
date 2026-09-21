from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
import os
import base64
import json

app = Flask(__name__)

# Connect to Gemini
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Maximum accepted image size (10 MB)
MAX_IMAGE_BYTES = 10 * 1024 * 1024

# Structured output schema for Gemini
WASTE_SCHEMA = {
    "type": "object",
    "properties": {
        "item":       {"type": "string"},
        "category":   {"type": "string"},
        "reason":     {"type": "string"},
        "disposal":   {"type": "string"},
        "confidence": {"type": "string"}
    },
    "required": ["item", "category", "reason", "disposal", "confidence"]
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    # --- Input validation ---
    if "image" not in request.files:
        return jsonify({
            "error": "No image was received. Please choose a file and try again.",
            "error_code": "no_file"
        }), 400

    image = request.files["image"]

    if image.filename == "":
        return jsonify({
            "error": "Please select an image file before analyzing.",
            "error_code": "no_file"
        }), 400

    if not image.mimetype.startswith("image/"):
        return jsonify({
            "error": "That file doesn't look like an image. Please upload a JPG, PNG, or WebP.",
            "error_code": "invalid_file"
        }), 400

    image_data = image.read()

    if len(image_data) > MAX_IMAGE_BYTES:
        return jsonify({
            "error": "The image is too large (max 10 MB). Please resize it and try again.",
            "error_code": "file_too_large"
        }), 413

    prompt = """
You are an AI Waste Segregation Assistant.

Analyze the uploaded image and identify the waste item.

Return a JSON object with exactly these five fields:

- item: the identified waste item (string)
- category: exactly one of — Wet/Organic, Dry/Recyclable, E-Waste, Hazardous, or Other
- reason: a short explanation of why this category was chosen
- disposal: a simple, practical disposal recommendation
- confidence: exactly one of — High, Medium, or Low

Important:
- Do not make up information.
- If the image is unclear, set confidence to Low and explain in reason.
- If the item cannot be safely classified, set disposal to "Check local waste-management guidelines."
- Keep all values concise and easy for a non-expert to understand.
"""

    # --- Call Gemini ---
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                {
                    "inline_data": {
                        "mime_type": image.mimetype,
                        "data": base64.b64encode(image_data).decode("utf-8")
                    }
                },
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=WASTE_SCHEMA
            )
        )
    except Exception as e:
        print("GEMINI API ERROR:", e)
        return jsonify({
            "error": "The AI service returned an error. Please wait a moment and try again.",
            "error_code": "ai_error"
        }), 502

    # --- Parse structured response ---
    try:
        result = json.loads(response.text)
    except (json.JSONDecodeError, AttributeError) as e:
        print("PARSE ERROR:", e, "| Raw:", getattr(response, "text", None))
        return jsonify({
            "error": "The AI response was in an unexpected format. Please try again.",
            "error_code": "ai_parse_error"
        }), 502

    return jsonify({"result": result})


if __name__ == "__main__":
    app.run(debug=True)
