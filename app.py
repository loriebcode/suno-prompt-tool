"""
app.py

Flask web application for the Suno Prompt Builder & Validator.

Two modes on one page:
  - Build: turn genre/BPM/key/mood inputs into a draft prompt
  - Validate: check any prompt (built here or pasted in) against the
    songwriting standards (length, no artist names, vocal direction)

The actual logic lives in prompt_logic.py — this file just connects a
web form to that logic, same pattern as the other two projects.
"""

from flask import Flask, render_template, request
from prompt_logic import build_prompt, validate_prompt, MAX_PROMPT_LENGTH

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        prompt_text="",
        result=None,
        max_length=MAX_PROMPT_LENGTH,
        form_values={},
    )


@app.route("/build", methods=["POST"])
def build():
    """Build a draft prompt from structured inputs, then validate it."""
    form_values = {
        "genre": request.form.get("genre", "").strip(),
        "bpm": request.form.get("bpm", "").strip(),
        "key": request.form.get("key", "").strip(),
        "mood": request.form.get("mood", "").strip(),
        "vocal_type": request.form.get("vocal_type", "contralto").strip(),
        "extra_notes": request.form.get("extra_notes", "").strip(),
    }

    try:
        bpm_value = float(form_values["bpm"]) if form_values["bpm"] else 0
        prompt_text = build_prompt(
            genre=form_values["genre"] or "R&B",
            bpm=bpm_value or 100,
            key=form_values["key"] or "C major",
            mood=form_values["mood"],
            vocal_type=form_values["vocal_type"] or "contralto",
            extra_notes=form_values["extra_notes"],
        )
        result = validate_prompt(prompt_text)
    except (ValueError, TypeError) as e:
        prompt_text = ""
        result = None

    return render_template(
        "index.html",
        prompt_text=prompt_text,
        result=result,
        max_length=MAX_PROMPT_LENGTH,
        form_values=form_values,
    )


@app.route("/validate", methods=["POST"])
def validate():
    """Validate a prompt the user pasted in directly."""
    prompt_text = request.form.get("prompt_text", "")
    result = validate_prompt(prompt_text)

    return render_template(
        "index.html",
        prompt_text=prompt_text,
        result=result,
        max_length=MAX_PROMPT_LENGTH,
        form_values={},
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
