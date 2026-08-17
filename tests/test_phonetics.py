"""
Unit Tests for Arudi Phonetic Converter (الكتابة العروضية).
"""

import pytest

from pyarud.phonetics import ArudiConverter


@pytest.fixture
def converter():
    return ArudiConverter()


def test_tanween_conversion(converter):
    # كِتَابٌ -> كِتَابُنْ / كتابن (11010)
    arudi, pattern = converter.prepare_text("كِتَابٌ", saturate=False)
    assert arudi.endswith("ن")
    assert pattern == "11010"


def test_shadda_expansion(converter):
    # شَدَّ -> شَدْدَ / شدد (101)
    arudi, pattern = converter.prepare_text("شَدَّ", saturate=False)
    assert "دد" in arudi
    assert pattern == "101"


def test_madda_expansion(converter):
    # آمَنَ -> ءَاْمَنَ (1011)
    arudi, pattern = converter.prepare_text("آمَنَ", saturate=False)
    assert pattern.startswith("101")


def test_solar_lam_assimilation(converter):
    # وَالشَّمْسِ -> وَشْشَمْسِ / وششمس (10101)
    arudi, pattern = converter.prepare_text("وَالشَّمْسِ", saturate=False)
    assert "ل" not in arudi
    assert "شش" in arudi
    # وَ (1) + شْ (0) + شَ (1) + مْ (0) + سِ (1) = 10101
    assert pattern == "10101"


def test_lunar_lam_preservation(converter):
    # وَالْقَمَرِ -> وَلْقَمَرِ / ولقمر (10111)
    arudi, pattern = converter.prepare_text("وَالْقَمَرِ", saturate=False)
    assert "ل" in arudi
    # وَ (1) + لْ (0) + قَ (1) + مَ (1) + رِ (1) = 10111
    assert pattern == "10111"


def test_wasl_between_words(converter):
    # فِي البَيْتِ -> فِلْبَيْتِ
    arudi, pattern = converter.prepare_text("فِي البَيْتِ", saturate=False)
    # فِ (1) + لْ (0) + بَ (1) + يْ (0) + تِ (1) = 10101
    assert pattern == "10101"


def test_classical_word_expansions(converter):
    # هَذَا -> هَاْذَاْ (1010)
    arudi, pattern = converter.prepare_text("هَذَا", saturate=False)
    assert pattern == "1010"

    # لَكِنْ -> لَاْكِنْ (1010)
    arudi2, pattern2 = converter.prepare_text("لَكِنْ", saturate=False)
    assert pattern2 == "1010"


def test_ashba_saturation(converter):
    # قَلَمُ -> قَلَمُو (110) with saturate=True
    arudi_sat, pat_sat = converter.prepare_text("قَلَمُ", saturate=True)
    assert arudi_sat.endswith("و") or arudi_sat.endswith("وْ")
    assert pat_sat.endswith("0")

    arudi_unsat, pat_unsat = converter.prepare_text("قَلَمُ", saturate=False)
    assert pat_unsat.endswith("1")
