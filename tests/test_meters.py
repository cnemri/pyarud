import pytest

from pyarud.processor import ArudhProcessor


@pytest.fixture
def processor():
    return ArudhProcessor()


# --- 1. Standard Meters (Detection) ---


def test_standard_meters(processor):
    examples = [
        ("taweel", "طَوِيلٌ لَهُ دُونَ البُحُورِ فَضَائِلُ", "فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِلُ"),
        ("madeed", "لِمَدِيدِ الشِّعْرِ عِنْدِي صِفَاتُ", "فَاعِلَاتُنْ فَاعِلُنْ فَاعِلَاتُ"),
        ("baseet", "إِنَّ البَسِيطَ لَدَيهِ يُبْسَطُ الأَمَلُ", "مُسْتَفْعِلُنْ فَاعِلُنْ مُسْتَفْعِلُنْ فَعِلُ"),
        ("wafer", "بُحُورُ الشِّعْرِ وَافِرُهَا جَمِيلُ", "مُفَاعَلَتُنْ مُفَاعَلَتُنْ فَعُولُ"),
        ("kamel", "كَمُلَ الجَمَالُ مِنَ البُحُورِ الكَامِلُ", "مُتَفَاعِلُنْ مُتَفَاعِلُنْ مُتَفَاعِلُ"),
        ("hazaj", "عَلَى الأَهْزَاجِ تَسْهِيلُ", "مَفَاعِيلُنْ مَفَاعِيلُ"),
        ("rajaz", "فِي أَبْحُرِ الأَرْجَازِ بَحْرٌ يَسْهُلُ", "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ مُسْتَفْعِلُ"),
        ("ramal", "رَمَلُ الأَبْحُرِ تَرْوِيهِ الثِّقَاتُ", "فَاعِلَاتُنْ فَاعِلَاتُنْ فَاعِلَاتُ"),
        ("saree", "بَحْرٌ سَرِيعٌ مَا لَهُ سَاحِلُ", "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ فَاعِلُ"),
        ("munsareh", "مُنْسَرِحٌ فِيهِ يُضْرَبُ المَثَلُ", "مُسْتَفْعِلُنْ مَفْعُولَاتُ مُفْتَعِلُ"),
        ("khafeef", "يَا خَفِيفاً خَفَّتْ بِهِ الحَرَكَاتُ", "فَاعِلَاتُنْ مُسْتَفْعِلُنْ فَاعِلَاتُ"),
        ("mudhare", "تُعَدُّ المُضَارِعَاتُ", "مَفَاعِيلُ فَاعِلَاتُ"),
        ("muqtadheb", "اِقْتَضِبْ كَمَا سَأَلُوا", "مَفْعُولَاتُ مُفْتَعِلُ"),
        ("mujtath", "إِنْ جُثَّتِ الحَرَكَاتُ", "مُسْتَفْعِلُنْ فَاعِلَاتُ"),
        ("mutakareb", "عَنِ المُتَقَارِبِ قَالَ الخَلِيلُ", "فَعُولُنْ فَعُولُنْ فَعُولُنْ فَعُولُ"),
        ("mutadarak", "حَرَكَاتُ المُحْدَثِ تَنْتَقِلُ", "فَعِلُنْ فَعِلُنْ فَعِلُنْ فَعِلُ"),
    ]

    for meter, sadr, ajuz in examples:
        result = processor.process_poem([(sadr, ajuz)])
        assert result["meter"] == meter, f"Failed to detect {meter}"
        assert result["verses"][0]["score"] >= 0.95, f"Low score for {meter}"


# --- 2. Forced Analysis & Granular Debugging ---


def test_forced_meter_broken_ajuz(processor):
    # Mutakarib: Fa'ulun (11010) x4
    # Ajuz broken: وَهَذَا كَلامٌ ثَقِيلٌ جِدًّا
    sadr = "أَخِي جَاوَزَ الظَّالِمُونَ الْمَدَى"
    ajuz = "وَهَذَا كَلامٌ ثَقِيلٌ جِدًّا"

    result = processor.process_poem([(sadr, ajuz)], meter_name="mutakareb")

    assert result["meter"] == "mutakareb"
    verse = result["verses"][0]

    # Sadr should be perfect
    assert verse["sadr_analysis"][0]["status"] == "ok"
    assert verse["sadr_analysis"][1]["status"] == "ok"

    # Ajuz has issues
    ajuz_feet = verse["ajuz_analysis"]

    # "Wa ha-dha" (11010) -> Matches Fa'ulun -> OK
    assert ajuz_feet[0]["status"] == "ok"

    # "Ka-la-mun" (11010) -> Matches Fa'ulun -> OK
    assert ajuz_feet[1]["status"] == "ok"

    # "Tha-qee-lun" (11010) -> Matches Fa'ulun -> OK
    assert ajuz_feet[2]["status"] == "ok"

    # "Jid-da" (1010) has extra bits and does not match standard 110/11010 foot -> broken
    assert ajuz_feet[3]["status"] == "broken"
    assert verse["is_valid"] is False


def test_forced_meter_valid_zihaf(processor):
    # Kamil with Idmar (Mustaf'ilun instead of Mutafa'ilun)
    # "Kamula Al-Jamalu..." is perfect Kamil.
    # Let's try one with Idmar.
    # Verse: "مُسْتَفْعِلُنْ مُتَفَاعِلُنْ مُسْتَفْعِلُنْ" (Valid Kamil)
    # This looks like Rajaz but if we force Kamil, it should be valid.

    # Text corresponding to Mustaf'ilun Mutafa'ilun Mustaf'ilun
    sadr = "يَا صَاحِبِي قِفْ وَاسْتَمِعْ قَوْلِي لَكَا"
    # Ya sa-hi-bi (Mustaf'ilun) - Qif was-ta-mi (Mustaf'ilun) - Qaw-li la-ka (Mustaf'ilun)
    # Wait, this is pure Rajaz. But Idmar makes it valid Kamil.

    result = processor.process_poem([(sadr, "")], meter_name="kamel")

    assert result["meter"] == "kamel"
    feet = result["verses"][0]["sadr_analysis"]

    # All feet should be OK because Idmar is valid in Kamil
    assert all(f["status"] == "ok" for f in feet)


# --- 3. Single Shatr Support ---


def test_single_shatr(processor):
    sadr = "أَخِي جَاوَزَ الظَّالِمُونَ الْمَدَى"
    # Pass empty string for Ajuz
    result = processor.process_poem([(sadr, "")])

    assert result["meter"] == "mutakareb"
    assert result["verses"][0]["ajuz_analysis"] is None


# --- 4. Ambiguity Resolution (Priority) ---


def test_ambiguity_priority(processor):
    # Saree vs Munsareh vs Baseet
    # Using the mnemonic which is structurally Saree
    sadr = "بَحْرٌ سَرِيعٌ مَا لَهُ سَاحِلُ"
    ajuz = "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ فَاعِلُنْ"

    result = processor.process_poem([(sadr, ajuz)])
    # Should pick Saree due to priority/structure
    assert result["meter"] == "saree"
