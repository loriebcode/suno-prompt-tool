# Prompt Booth — Suno Prompt Builder & Validator

A web app that builds and checks AI music prompts (for tools like Suno)
against a specific set of songwriting standards, so every prompt is
ready to use without second-guessing it.

Built by [Lorie B](https://soundbetter.com/profiles/726133-lorie-b) / AI Girl LLC.

## What it does

**Build mode**
Turn structured inputs (genre, BPM, key, mood, vocal type, production
notes) into a draft prompt that already follows the standards below.

**Validate mode**
Paste any prompt — built here or written by hand — and check it against:
- **Length** — must stay under 1,000 characters (Suno's practical limit)
- **No artist names** — flags real artist names so you describe the
  *sound*, not a specific person's style
- **Vocal type** — checks that a vocal type (e.g. contralto) is specified
- **Vocal placement** — checks that vocals are directed to sit upfront
  and dry in the mix
- **Instrument placement** — checks that instruments are directed to sit
  behind the vocal, not competing with it

Each check is either an **error** (must fix — length and artist names)
or a **warning** (should consider — the vocal/instrument direction
checks), since those are strong recommendations rather than hard
platform rules.

## Why I built this

As a songwriter who writes Suno prompts regularly, I follow the same
rules every time — no artist names, vocals upfront and dry, contralto
direction, length under 1,000 characters — but doing that check by hand
is easy to mess up under a tight character count. This tool also rounds
out a 3-project coding portfolio, alongside a Flask web app (royalty
split calculator) and a Python CLI tool (BPM & key reference), to show
range across different problem types and interaction styles.

## Tech stack

- **Python 3** — core build/validation logic
- **Flask** — web framework
- **HTML / CSS / vanilla JS** — frontend, no frameworks
- **Tests** — 14 tests covering length checks, artist-name detection,
  vocal direction detection, and the prompt builder itself

## Running it locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py

# 3. Open in your browser
# http://localhost:5001
```

## Running the tests

```bash
python test_prompt_logic.py
```

All 14 tests should pass.

## Project structure

```
suno-prompt-tool/
├── app.py                  # Flask routes
├── prompt_logic.py          # Pure Python build/validate logic (no web code)
├── test_prompt_logic.py     # Tests for the logic
├── templates/
│   └── index.html           # The web page (build + validate panels)
├── static/
│   ├── style.css
│   └── script.js              # Tab switching between modes
└── requirements.txt
```

## A note on the artist-name check

The built-in artist name list is intentionally a helpful safety net, not
an exhaustive or guaranteed filter — it only catches the names in its
list. Always give a prompt a final manual read before using it.

## Possible future additions

- A larger, more comprehensive artist-name list (or a flagging API)
- Save/export prompt history
- Genre-specific prompt templates (R&B, Afrobeats, Afro Soul presets)
