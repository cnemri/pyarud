"""
Backward-compatibility shim for pyarud.arabic -> pyarud.core.arabic.
"""

from .core.arabic import (
    is_haraka,
    is_moon_letter,
    is_shadda,
    is_sukun,
    is_sun_letter,
    is_tanween,
    normalize_ligatures,
    normalize_orthography,
    strip_punctuation,
    strip_tashkeel,
    strip_tatweel,
)

__all__ = [
    "strip_tashkeel",
    "strip_tatweel",
    "strip_punctuation",
    "normalize_ligatures",
    "normalize_orthography",
    "is_sun_letter",
    "is_moon_letter",
    "is_haraka",
    "is_tanween",
    "is_shadda",
    "is_sukun",
]
