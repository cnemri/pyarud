"""
Unit Tests for Qafiyah and Rhyme Analyzer (علم القافية).
"""

import pytest

from pyarud.qafiyah import QafiyahAnalyzer


@pytest.fixture
def analyzer():
    return QafiyahAnalyzer()


def test_qafiyah_rawi_detection(analyzer):
    # البيت: "وَالسَيفُ وَالرُمحُ وَالقِرطاسُ وَالقَلَمُ" -> الروي هو الميم
    q = analyzer.analyze("وَالسَّيْفُ وَالرُّمْحُ وَالقِرْطَاسُ وَالقَلَمُ")
    assert q.rawi == "م"
    assert q.rawi_haraka == "damma"
    assert q.rhyme_classification == "muqayyadah" or q.rhyme_classification == "mutlaqah"


def test_qafiyah_muqayyadah(analyzer):
    # قافية مقيدة بساكن
    q = analyzer.analyze("إِذَا الْغَيْثُ هَمَلْ", is_muqayyad=True)
    assert q.rawi == "ل"
    assert q.rhyme_classification == "muqayyadah"


def test_qafiyah_wasl(analyzer):
    # الهاء وصلا: "كَأَنَّهُ حَبُّ فُلْفُلِهِ" -> الروي اللام والوصل الهاء
    q = analyzer.analyze("كَأَنَّهُ حَبُّ فُلْفُلِهِ")
    assert q.rawi == "ل"
    assert q.wasl == "ه"


def test_qafiyah_ridf(analyzer):
    # ردف بياء قبل الروي مباشرة: "وَأَيُّ بَنِي آدَمٍ سَعِيدُ" -> الروي الدال، والردف هو الياء
    q = analyzer.analyze("وَأَيُّ بَنِي آدَمٍ سَعِيدُ")
    assert q.rawi == "د"
    assert q.ridf == "ي"


def test_qafiyah_tasees_and_dakhil(analyzer):
    # تأسيس بالألف ودخيل: "لِمَدِيدِ الشِّعْرِ عِنْدِي صِفَاتُ" / "فَضَائِلُ" -> الروي اللام، التأسيس الألف، الدخيل الهمزة
    q = analyzer.analyze("طَوِيلٌ لَهُ دُونَ البُحُورِ فَضَائِلُ")
    assert q.rawi == "ل"
    assert q.tasees == "ا"
    assert q.dakhil == "ئ"


def test_qafiyah_rhythmic_types(analyzer):
    # المتدارك / المتواتر
    q1 = analyzer.analyze("مِنْ خَبَرِ المَحْبُوبَةِ الصَّائِمِ")
    assert q1.qafiyah_type_en in ["Al-Mutawatir", "Al-Mutadarak", "Al-Mutarakib", "Al-Mutakawis", "Al-Mutaradif"]
    assert q1.qafiyah_type_ar != ""
