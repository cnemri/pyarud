import pytest

from pyarud.processor import ArudhProcessor


@pytest.fixture
def processor():
    return ArudhProcessor()


# --- Standard Meters (Al-Buhur Al-Sittah 'Ashar) ---


def test_mutakarib(processor):
    sadr = "أَخِي جَاوَزَ الظَّالِمُونَ الْمَدَى"
    ajuz = "فَحَقَّ الْجِهَادُ وَحَقَّ الْفِدَا"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "mutakareb"


def test_tawil(processor):
    sadr = "طَوِيلٌ لَهُ دُونَ الْبُحُورِ فَضَائِلُ"
    ajuz = "فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِلُنْ"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "taweel"


def test_basit(processor):
    sadr = "إِنَّ الْبَسِيطَ لَدَيْهِ يُبْسَطُ الْأَمَلُ"
    ajuz = "مُسْتَفْعِلُنْ فَاعِلُنْ مُسْتَفْعِلُنْ فَعِلُنْ"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "baseet"


def test_kamil(processor):
    sadr = "كَمُلَ الْجَمَالُ مِنَ الْبُحُورِ الْكَامِلُ"
    ajuz = "مُتَفَاعِلُنْ مُتَفَاعِلُنْ مُتَفَاعِلُنْ"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "kamel"


def test_wafir(processor):
    sadr = "بُحُورُ الشِّعْرِ وَافِرُهَا جَمِيلُ"
    ajuz = "مُفَاعَلَتُنْ مُفَاعَلَتُنْ فَعُولُنْ"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "wafer"


def test_rajaz(processor):
    sadr = "فِي أَبْحُرِ الْأَرْجَازِ بَحْرٌ يَسْهُلُ"
    ajuz = "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "rajaz"


def test_khafif(processor):
    sadr = "يَا خَفِيفاً خَفَّتْ بِهِ الْحَرَكَاتُ"
    ajuz = "فَاعِلَاتُنْ مُسْتَفْعِ لُنْ فَاعِلَاتُنْ"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "khafeef"


def test_ramal(processor):
    sadr = "رَمَلُ الْأَبْحُرِ يَرْوِيهِ الثِّقَاتُ"
    ajuz = "فَاعِلَاتُنْ فَاعِلَاتُنْ فَاعِلَاتُنْ"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "ramal"


def test_hazaj(processor):
    sadr = "عَلَى الْأَهْزَاجِ تَسْهِيلُ"
    ajuz = "مَفَاعِيلُنْ مَفَاعِيلُ"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "hazaj"


def test_saree(processor):
    # Using the mnemonic pattern
    sadr = "بَحْرٌ سَرِيعٌ مَا لَهُ سَاحِلُ"
    ajuz = "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ فَاعِلُنْ"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "saree"


def test_munsareh(processor):
    sadr = "مُنْسَرِحٌ فِيهِ يُضْرَبُ الْمَثَلُ"
    ajuz = "مُسْتَفْعِلُنْ مَفْعُولَاتُ مُفْتَعِلُنْ"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "munsareh"


def test_madeed(processor):
    sadr = "لِمَدِيدِ الشِّعْرِ عِنْدِي صِفَاتُ"
    ajuz = "فَاعِلَاتُنْ فَاعِلُنْ فَاعِلَاتُنْ"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "madeed"


def test_mudhare(processor):
    sadr = "تَعَدَّ مَعَ الْعَوَاقِلْ"
    ajuz = "مَفَاعِيلُ فَاعِ لَاتُنْ"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "mudhare"


def test_muqtadheb(processor):
    sadr = "اقْتَضِبْ كَمَا سَأَلُوا"
    ajuz = "مَفْعُولَاتُ مُفْتَعِلُنْ"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "muqtadheb"


def test_mujtath(processor):
    sadr = "إِنْ جُثَّتِ الْحَرَكَاتُ"
    ajuz = "مُسْتَفْعِ لُنْ فَاعِلَاتُنْ"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "mujtath"


def test_mutadarak(processor):
    sadr = "حَرَكَاتُ الْمُحْدَثِ تَنْتَقِلُ"
    ajuz = "فَعِلُنْ فَعِلُنْ فَعِلُنْ فَعِلُ"
    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "mutadarak"


# --- Variations & Edge Cases ---


def test_kamil_majzoo(processor):
    # Majzoo Kamil: Muta'fa'ilun Muta'fa'ilun (2 feet instead of 3)
    sadr = "يَا صَاحِبِي لَا تَسْأَلَنّ"
    ajuz = "عَنْ هَالِكٍ كَيْفَ هَلَكْ"  # Example variation
    # Note: We need a valid Majzoo example. Using a standard textbook example:
    # "وَإِذَا افْتَقَرْتَ فَلَا تَكُنْ ... مُتَخَشِّعًا وَتَجَمَّلِ"
    sadr = "وَإِذَا افْتَقَرْتَ فَلَا تَكُنْ"
    ajuz = "مُتَخَشِّعًا وَتَجَمَّلِ"

    result = processor.process_poem([(sadr, ajuz)])
    assert result["meter"] == "kamel"  # Usually returns the main Bahr name


def test_broken_verse(processor):
    sadr = "أَخِي جَاوَزَ الظَّالِمُونَ الْمَدَى"
    ajuz = "وَهَذَا كَلامٌ ثَقِيلٌ جِدًّا"  # Broken
    result = processor.process_poem([(sadr, ajuz)])

    # Depending on implementation, it might return a low score match or no match
    # If it returns a match, the score should be significantly lower than a perfect match.
    # For now, we just check that it doesn't crash and returns *something*.
    assert result is not None
    if "score" in result:
        assert result["score"] < 1.0
