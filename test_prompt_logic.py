"""
test_prompt_logic.py

Tests for the Suno prompt builder/validator logic in prompt_logic.py.

Run with:
    python -m pytest test_prompt_logic.py -v

Or, without pytest installed:
    python test_prompt_logic.py
"""

from prompt_logic import (
    build_prompt,
    find_artist_names,
    has_instruments_behind_direction,
    has_upfront_vocal_direction,
    has_vocal_type,
    validate_prompt,
    MAX_PROMPT_LENGTH,
)


def test_empty_prompt_is_invalid():
    result = validate_prompt("")
    assert result.is_valid is False
    assert any("empty" in i.message.lower() for i in result.issues)


def test_prompt_over_length_limit_is_invalid():
    long_prompt = "A" * (MAX_PROMPT_LENGTH + 50)
    result = validate_prompt(long_prompt)
    assert result.is_valid is False
    assert result.character_count == MAX_PROMPT_LENGTH + 50
    assert any("over the" in i.message for i in result.issues)


def test_prompt_under_length_limit_has_no_length_error():
    short_prompt = "Short test prompt with contralto vocals upfront and dry, instruments behind."
    result = validate_prompt(short_prompt)
    length_errors = [i for i in result.issues if "character" in i.message.lower() and i.severity == "error"]
    assert length_errors == []


def test_artist_name_detected_case_insensitive():
    prompt = "Make it sound like BEYONCE with big vocals."
    found = find_artist_names(prompt)
    assert "beyonce" in found


def test_artist_name_not_falsely_detected():
    """Make sure normal words don't trigger false positives
    (e.g. 'ye' as an artist name shouldn't match inside other words)."""
    prompt = "A bright, eye-catching melody with layered harmonies."
    found = find_artist_names(prompt)
    assert found == []


def test_clean_prompt_with_no_artist_names():
    prompt = "Afrobeats track, contralto vocals upfront and dry, instruments behind the vocal."
    found = find_artist_names(prompt)
    assert found == []


def test_has_vocal_type_detects_contralto():
    assert has_vocal_type("Smooth contralto vocals over a slow groove.") is True


def test_has_vocal_type_false_when_missing():
    assert has_vocal_type("Smooth vocals over a slow groove.") is False


def test_upfront_vocal_direction_detected():
    prompt = "contralto vocals, upfront and dry in the mix, prominent and clear"
    assert has_upfront_vocal_direction(prompt) is True


def test_upfront_vocal_direction_false_when_missing():
    prompt = "contralto vocals over a chill beat"
    assert has_upfront_vocal_direction(prompt) is False


def test_instruments_behind_direction_detected():
    prompt = "instruments sitting behind the vocal, supportive not competing"
    assert has_instruments_behind_direction(prompt) is True


def test_build_prompt_includes_all_required_elements():
    prompt = build_prompt(
        genre="R&B",
        bpm=100,
        key="C major",
        vocal_type="contralto",
    )
    assert "contralto" in prompt.lower()
    assert "100" in prompt
    assert "c major" in prompt.lower()
    assert len(prompt) <= MAX_PROMPT_LENGTH


def test_build_prompt_passes_its_own_validation():
    """A freshly built prompt (with no artist names, proper vocal
    direction) should pass validation cleanly with no warnings."""
    prompt = build_prompt(
        genre="Afro Soul R&B",
        bpm=104,
        key="F minor",
        mood="moody",
        vocal_type="contralto",
    )
    result = validate_prompt(prompt)
    assert result.is_valid is True
    assert result.issues == []


def test_build_prompt_truncates_if_extra_notes_too_long():
    huge_notes = "x" * 2000
    prompt = build_prompt(
        genre="R&B", bpm=100, key="C major", extra_notes=huge_notes
    )
    assert len(prompt) <= MAX_PROMPT_LENGTH


if __name__ == "__main__":
    test_functions = [
        test_empty_prompt_is_invalid,
        test_prompt_over_length_limit_is_invalid,
        test_prompt_under_length_limit_has_no_length_error,
        test_artist_name_detected_case_insensitive,
        test_artist_name_not_falsely_detected,
        test_clean_prompt_with_no_artist_names,
        test_has_vocal_type_detects_contralto,
        test_has_vocal_type_false_when_missing,
        test_upfront_vocal_direction_detected,
        test_upfront_vocal_direction_false_when_missing,
        test_instruments_behind_direction_detected,
        test_build_prompt_includes_all_required_elements,
        test_build_prompt_passes_its_own_validation,
        test_build_prompt_truncates_if_extra_notes_too_long,
    ]

    passed = 0
    for test_func in test_functions:
        try:
            test_func()
            print(f"PASSED: {test_func.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAILED: {test_func.__name__} — {e}")

    print(f"\n{passed}/{len(test_functions)} tests passed")
