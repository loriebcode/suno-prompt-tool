"""
prompt_logic.py

Core logic for building and validating Suno AI music prompts, following
a specific set of songwriting standards:
  - Prompts must stay under 1,000 characters
  - No real artist names allowed (Suno/AI music tools generally prohibit
    referencing real artists, to avoid style-cloning a specific person)
  - Vocal direction should specify a vocal type (e.g. contralto)
  - Vocals should be described as upfront/dry/prominent in the mix, with
    instruments sitting behind them

This module is pure logic (no web code), so it can be tested and reused
independently — same architecture pattern as the other two projects in
this portfolio.
"""

import re
from dataclasses import dataclass, field
from typing import List


MAX_PROMPT_LENGTH = 1000

# A short list of well-known artist names to flag if they appear in a
# prompt. This is intentionally NOT exhaustive — it's a helpful safety
# net, not a guarantee. Users should always double check manually too.
# Kept lowercase for case-insensitive matching.
COMMON_ARTIST_NAMES = [
    "beyonce", "beyoncé", "rihanna", "drake", "the weeknd", "weeknd",
    "adele", "taylor swift", "ariana grande", "sza", "burna boy",
    "wizkid", "davido", "tems", "chris brown", "usher", "alicia keys",
    "mariah carey", "whitney houston", "michael jackson", "prince",
    "stevie wonder", "frank ocean", "kendrick lamar", "jay-z", "jay z",
    "kanye", "ye", "billie eilish", "dua lipa", "bruno mars",
]

VOCAL_TYPES = [
    "soprano", "mezzo-soprano", "mezzo soprano", "contralto", "alto",
    "tenor", "baritone", "bass",
]

# Keywords that indicate vocals should sit forward in the mix
# (upfront/dry/prominent). Matched independently — the prompt just needs
# the word "vocal(s)" to appear reasonably near one of these descriptors,
# since songwriters phrase this many different ways
# ("vocals upfront and dry", "upfront, dry vocal delivery", etc).
UPFRONT_VOCAL_KEYWORDS = ["upfront", "up front", "dry", "prominent", "forward", "clear and present"]

# Keywords indicating instruments should sit behind/support the vocal.
INSTRUMENTS_BEHIND_KEYWORDS = [
    "behind the vocal", "behind the lead", "sit back", "sitting behind",
    "recede", "subdued instrumental", "background", "supportive not competing",
    "instruments behind",
]


@dataclass
class ValidationIssue:
    severity: str  # "error" or "warning"
    message: str


@dataclass
class ValidationResult:
    is_valid: bool
    character_count: int
    issues: List[ValidationIssue] = field(default_factory=list)


def find_artist_names(prompt: str) -> List[str]:
    """Return any known artist names found in the prompt (case-insensitive)."""
    prompt_lower = prompt.lower()
    found = []
    for artist in COMMON_ARTIST_NAMES:
        # Use word-boundary-ish matching so "ye" doesn't match inside other words
        pattern = r"\b" + re.escape(artist) + r"\b"
        if re.search(pattern, prompt_lower):
            found.append(artist)
    return found


def has_vocal_type(prompt: str) -> bool:
    prompt_lower = prompt.lower()
    return any(vt in prompt_lower for vt in VOCAL_TYPES)


def has_upfront_vocal_direction(prompt: str) -> bool:
    """
    Check whether the prompt directs vocals to sit forward in the mix.
    Looks for an upfront-style keyword (upfront, dry, prominent, forward)
    appearing reasonably close to the word "vocal"/"vocals", since
    songwriters phrase this many different ways.
    """
    prompt_lower = prompt.lower()
    if "vocal" not in prompt_lower:
        return False

    for keyword in UPFRONT_VOCAL_KEYWORDS:
        if keyword in prompt_lower:
            # Check proximity: is this keyword within ~40 characters of
            # the word "vocal"? This avoids false positives where the
            # keyword describes something unrelated elsewhere in the prompt.
            for match in re.finditer(re.escape(keyword), prompt_lower):
                vocal_positions = [m.start() for m in re.finditer("vocal", prompt_lower)]
                if any(abs(match.start() - vp) <= 40 for vp in vocal_positions):
                    return True
    return False


def has_instruments_behind_direction(prompt: str) -> bool:
    prompt_lower = prompt.lower()
    return any(keyword in prompt_lower for keyword in INSTRUMENTS_BEHIND_KEYWORDS)


def validate_prompt(prompt: str) -> ValidationResult:
    """
    Run a Suno prompt against the songwriting standards and return a
    ValidationResult listing any errors (must fix) or warnings (should
    consider fixing).
    """
    issues: List[ValidationIssue] = []
    char_count = len(prompt)

    if char_count == 0:
        issues.append(ValidationIssue("error", "Prompt is empty."))
    elif char_count > MAX_PROMPT_LENGTH:
        over_by = char_count - MAX_PROMPT_LENGTH
        issues.append(
            ValidationIssue(
                "error",
                f"Prompt is {char_count} characters — {over_by} over the "
                f"{MAX_PROMPT_LENGTH} character limit. Trim it down.",
            )
        )

    artist_hits = find_artist_names(prompt)
    if artist_hits:
        names = ", ".join(sorted(set(artist_hits)))
        issues.append(
            ValidationIssue(
                "error",
                f"Prompt may reference a real artist name: {names}. "
                f"Remove artist references and describe the style/sound instead.",
            )
        )

    if char_count > 0 and not has_vocal_type(prompt):
        issues.append(
            ValidationIssue(
                "warning",
                "No vocal type detected (e.g. 'contralto'). Consider adding "
                "one for clearer vocal direction.",
            )
        )

    if char_count > 0 and not has_upfront_vocal_direction(prompt):
        issues.append(
            ValidationIssue(
                "warning",
                "Prompt doesn't clearly say vocals should be upfront/dry/"
                "prominent. Consider adding that direction.",
            )
        )

    if char_count > 0 and not has_instruments_behind_direction(prompt):
        issues.append(
            ValidationIssue(
                "warning",
                "Prompt doesn't clearly say instruments should sit behind "
                "the vocal. Consider adding that direction.",
            )
        )

    has_errors = any(i.severity == "error" for i in issues)

    return ValidationResult(
        is_valid=not has_errors,
        character_count=char_count,
        issues=issues,
    )


def build_prompt(
    genre: str,
    bpm: float,
    key: str,
    mood: str = "",
    vocal_type: str = "contralto",
    extra_notes: str = "",
) -> str:
    """
    Build a starting-point Suno prompt from structured inputs, already
    following the songwriting standards (vocal type, upfront/dry vocals,
    instruments behind, no artist names).

    This is a draft generator, not a final answer — the user should
    review and refine the output, then run it back through
    validate_prompt() before using it.
    """
    parts = []

    genre_clause = genre.strip()
    if mood.strip():
        genre_clause += f", {mood.strip()} mood"
    parts.append(genre_clause)

    parts.append(f"{bpm:g} BPM")
    parts.append(f"key of {key.strip()}")

    parts.append(
        f"{vocal_type.strip()} vocals, upfront and dry in the mix, "
        f"prominent and clear"
    )
    parts.append("instruments sitting behind the vocal, supportive not competing")

    if extra_notes.strip():
        parts.append(extra_notes.strip())

    prompt = ". ".join(p.strip().rstrip(".") for p in parts if p.strip()) + "."

    # Defensive trim in case extra_notes pushed it over the limit
    if len(prompt) > MAX_PROMPT_LENGTH:
        prompt = prompt[: MAX_PROMPT_LENGTH - 3].rstrip() + "..."

    return prompt


if __name__ == "__main__":
    # Quick manual test when running this file directly
    draft = build_prompt(
        genre="Afro Soul R&B with Arabic fusion elements",
        bpm=104,
        key="F minor",
        mood="moody, sensual",
        vocal_type="contralto",
        extra_notes="warm analog production, subtle hand percussion",
    )
    print("Generated draft prompt:")
    print(draft)
    print(f"\nCharacter count: {len(draft)}")

    print("\nValidation result:")
    result = validate_prompt(draft)
    print(f"Valid: {result.is_valid}")
    for issue in result.issues:
        print(f"  [{issue.severity.upper()}] {issue.message}")

    print("\n--- Testing a prompt with an artist name ---")
    bad_prompt = "Make this sound like Beyonce with contralto vocals, upfront and dry, instruments behind."
    bad_result = validate_prompt(bad_prompt)
    print(f"Valid: {bad_result.is_valid}")
    for issue in bad_result.issues:
        print(f"  [{issue.severity.upper()}] {issue.message}")
