"""
Unit Tests for Zero-Dependency Arabic Text Normalization and Utilities.
"""

from pyarud.arabic import (
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


def test_strip_tashkeel():
    text = "بِسْمِ اللَّـهِ الرَّحْمَـٰنِ الرَّحِيمِ"
    clean = strip_tashkeel(text)
    assert "ِ" not in clean
    assert "ّ" not in clean
    assert "ْ" not in clean
    assert "َ" not in clean
    assert "ـ" in clean or "بسم" in clean


def test_strip_tatweel():
    text = "شِــــعْــــرٌ"
    clean = strip_tatweel(text)
    assert "ـ" not in clean
    assert clean == "شِعْرٌ"


def test_strip_punctuation():
    text = "«قَالَ الشَّاعِرُ: هَلْ غَادَرَ الشُّعَرَاءُ؟!»"
    clean = strip_punctuation(text)
    assert "«" not in clean
    assert "»" not in clean
    assert ":" not in clean
    assert "؟" not in clean
    assert "!" not in clean
    assert clean == "قَالَ الشَّاعِرُ هَلْ غَادَرَ الشُّعَرَاءُ"


def test_normalize_orthography():
    text = "أحمد وإبراهيم مع آمنة والفتى"
    norm = normalize_orthography(text, normalize_alef=True, normalize_maksura=True)
    assert "أ" not in norm
    assert "إ" not in norm
    assert "آ" not in norm
    assert "ى" not in norm
    assert norm == "احمد وابراهيم مع امنة والفتا"


def test_normalize_ligatures():
    # Test ligature normalization (e.g. \ufefb -> \u0644\u0627)
    text = "\ufefb"
    norm = normalize_ligatures(text)
    assert norm == "لا"


def test_letter_classifiers():
    assert is_sun_letter("ت")
    assert is_sun_letter("ش")
    assert is_sun_letter("ن")
    assert not is_sun_letter("ق")
    assert not is_sun_letter("ب")

    assert is_moon_letter("ق")
    assert is_moon_letter("ب")
    assert is_moon_letter("ع")
    assert not is_moon_letter("ش")

    assert is_haraka("َ")
    assert is_haraka("ُ")
    assert is_haraka("ِ")
    assert not is_haraka("ً")

    assert is_tanween("ً")
    assert is_tanween("ٌ")
    assert is_tanween("ٍ")
    assert not is_tanween("َ")

    assert is_shadda("ّ")
    assert is_sukun("ْ")
