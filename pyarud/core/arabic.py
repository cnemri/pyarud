"""
Zero-dependency Arabic Text Processing Utilities for PyArud.

Provides high-performance functions for stripping tashkeel, normalizing
ligatures and orthography, and classifying Arabic characters.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Final

from .constants import (
    ALEF,
    ALEF_HAMZA_ABOVE,
    ALEF_HAMZA_BELOW,
    ALEF_MADDA,
    ALEF_MAKSURA,
    ALL_PUNCTUATION,
    DAGGER_ALEF,
    DAMMA,
    FATHA,
    FATHATAN,
    HARAKAT_SET,
    HEH,
    KASRA,
    LETTERS_SET,
    LONG_VOWELS_SET,
    MOON_LETTERS_SET,
    SHADDA,
    SUKUN,
    SUN_LETTERS_SET,
    TANWEEN_SET,
    TASHKEEL_SET,
    TATWEEL,
    TEH_MARBUTA,
    WASLA,
)

# Precompiled translation tables and regexes for maximum performance
_TASHKEEL_NO_SHADDA_TABLE: Final = str.maketrans("", "", "".join(c for c in TASHKEEL_SET if c != SHADDA))
_TASHKEEL_ALL_TABLE: Final = str.maketrans("", "", "".join(TASHKEEL_SET))
_TATWEEL_TABLE: Final = str.maketrans("", "", TATWEEL)
_PUNCTUATION_TABLE: Final = str.maketrans("", "", ALL_PUNCTUATION)

_RE_MULTIPLE_SPACES: Final = re.compile(r"\s+")
_RE_SHADDA_HARAKA_ORDER: Final = re.compile(f"([{FATHA}{DAMMA}{KASRA}{FATHATAN}])([{SHADDA}])")
_RE_ALEF_FATHATAN: Final = re.compile(f"{ALEF}{FATHATAN}")
_RE_ALEF_HARAKA: Final = re.compile(f"{ALEF}[{FATHA}{DAMMA}{KASRA}]")


def strip_tashkeel(text: str, keep_shadda: bool = False) -> str:
    """
    Remove Arabic diacritics (harakat, tanween, sukun, dagger alif, etc.).

    Args:
        text (str): Input Arabic text.
        keep_shadda (bool): If True, preserves the Shadda (gemination mark).

    Returns:
        str: Text with diacritics stripped.
    """
    if not text:
        return ""
    if keep_shadda:
        return text.translate(_TASHKEEL_NO_SHADDA_TABLE)
    return text.translate(_TASHKEEL_ALL_TABLE)


def strip_tatweel(text: str) -> str:
    """Remove Arabic Kashida/Tatweel (ـ) elongation characters."""
    if not text:
        return ""
    return text.translate(_TATWEEL_TABLE)


def strip_punctuation(text: str) -> str:
    """Remove Arabic and Western punctuation marks."""
    if not text:
        return ""
    return text.translate(_PUNCTUATION_TABLE)


def normalize_spaces(text: str) -> str:
    """Collapse consecutive whitespaces into a single space and strip leading/trailing spaces."""
    if not text:
        return ""
    return _RE_MULTIPLE_SPACES.sub(" ", text).strip()


def normalize_ligatures(text: str) -> str:
    """
    Decomposes Lam-Alif Unicode presentation forms and ligatures into standard Arabic letters,
    preserving standard precomposed Arabic characters.
    """
    if not text:
        return ""

    # Map presentation forms and composite ligatures
    ligatures = {
        "\ufefb": "ل" + ALEF,
        "\ufefc": "ل" + ALEF,
        "\ufef7": "ل" + ALEF_HAMZA_ABOVE,
        "\ufef8": "ل" + ALEF_HAMZA_ABOVE,
        "\ufef9": "ل" + ALEF_HAMZA_BELOW,
        "\ufefa": "ل" + ALEF_HAMZA_BELOW,
        "\ufef5": "ل" + ALEF_MADDA,
        "\ufef6": "ل" + ALEF_MADDA,
    }
    for lig, rep in ligatures.items():
        text = text.replace(lig, rep)

    return unicodedata.normalize("NFC", text)


def normalize_orthography(
    text: str,
    normalize_alef: bool = False,
    normalize_maksura: bool = False,
    normalize_teh_marbuta: bool = False,
) -> str:
    """
    Standardize Arabic orthographic anomalies for prosodic analysis:
    1. Replace Wasla (ٱ) with standard Alif (ا).
    2. Normalize Dagger Alif (ٰ) to standard Alif (ا).
    3. Ensure Shadda precedes vowel diacritics.
    4. Remove invalid harakat on standard Alif.
    5. Swap Alif + Tanween Fath to Tanween Fath + Alif for deterministic parsing.
    6. Optionally normalize all Hamzated Alefs (أ, إ, آ, ٱ) to bare Alef (ا).
    7. Optionally normalize Alef Maksura (ى) to Alef (ا).
    8. Optionally normalize Teh Marbuta (ة) to Heh (ه).
    """
    if not text:
        return ""

    # Replace Wasla and Dagger Alif
    text = text.replace(WASLA, ALEF)
    text = text.replace(DAGGER_ALEF, ALEF)

    # Optional broad orthographic normalizations
    if normalize_alef:
        text = text.replace(ALEF_HAMZA_ABOVE, ALEF)
        text = text.replace(ALEF_HAMZA_BELOW, ALEF)
        text = text.replace(ALEF_MADDA, ALEF)

    if normalize_maksura:
        text = text.replace(ALEF_MAKSURA, ALEF)

    if normalize_teh_marbuta:
        text = text.replace(TEH_MARBUTA, HEH)

    # Reorder haraka + shadda to shadda + haraka
    text = _RE_SHADDA_HARAKA_ORDER.sub(r"\2\1", text)

    # Remove harakat improperly placed directly on bare Alif (unless Hamza)
    text = _RE_ALEF_HARAKA.sub(ALEF, text)

    # Normalize Alif + Tanween Fath -> Tanween Fath + Alif
    text = _RE_ALEF_FATHATAN.sub(f"{FATHATAN}{ALEF}", text)

    return text


def is_sun_letter(char: str) -> bool:
    """Check if the given character is a Solar letter (حرف شمسي)."""
    return char in SUN_LETTERS_SET


def is_moon_letter(char: str) -> bool:
    """Check if the given character is a Lunar letter (حرف قمري)."""
    return char in MOON_LETTERS_SET


def is_haraka(char: str) -> bool:
    """Check if the given character is a short vowel (Fatha, Damma, Kasra)."""
    return char in HARAKAT_SET


def is_tanween(char: str) -> bool:
    """Check if the given character is a Tanween diacritic."""
    return char in TANWEEN_SET


def is_shadda(char: str) -> bool:
    """Check if the given character is a Shadda."""
    return char == SHADDA


def is_sukun(char: str) -> bool:
    """Check if the given character is a Sukun."""
    return char == SUKUN


def is_long_vowel(char: str) -> bool:
    """Check if the given character is a long vowel (Alif, Waw, Yeh, Alif Maksura)."""
    return char in LONG_VOWELS_SET


def is_arabic_letter(char: str) -> bool:
    """Check if the character is an Arabic consonant or letter."""
    return char in LETTERS_SET
