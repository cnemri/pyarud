# Quick Start

This guide will get you analyzing Arabic poetry with **PyArud v1.0.0** in under 5 minutes.

## 1. Single Verse Analysis

The most direct way to analyze a verse is with `analyze_verse()`:

```python
from pyarud import ArudhProcessor, format_verse_report

processor = ArudhProcessor()

sadr = "إِذَا غَامَرْتَ فِي شَرَفٍ مَرُومِ"
ajuz = "فَلَا تَقْنَعْ بِمَا دُونَ النُّجُومِ"

# Returns a strongly-typed VerseAnalysis object
verse_analysis = processor.analyze_verse(sadr, ajuz)

# Print a rich formatted report
print(format_verse_report(verse_analysis))
```

### Direct Attribute Access

You can access all prosodic and rhyme properties directly:

```python
print("Bahr Key:", verse_analysis.meter_key)          # 'taweel'
print("Bahr Arabic:", verse_analysis.meter_name_ar)   # 'الطويل'
print("Accuracy Score:", verse_analysis.score)        # 1.0

# Sadr details
print("Sadr Arudi Text:", verse_analysis.sadr.arudi_text)
print("Sadr Pattern:", verse_analysis.sadr.pattern)
for foot in verse_analysis.sadr.feet:
    print(f"  Foot: {foot.foot_name} | Status: {foot.status} | Defect: {foot.defect_name}")

# Qafiyah & Rhyme details
q = verse_analysis.qafiyah
print(f"Rawi: {q.rawi} ({q.rhyme_form})")
print(f"Rhyme Pattern: {q.pattern} ({q.rhyme_type})")
```

---

## 2. Multi-Verse Poem Analysis

To analyze an entire poem, use `analyze_poem()`:

```python
from pyarud import ArudhProcessor, format_poem_report

processor = ArudhProcessor()

poem = [
    ("إِذَا غَامَرْتَ فِي شَرَفٍ مَرُومِ", "فَلَا تَقْنَعْ بِمَا دُونَ النُّجُومِ"),
    ("فَطَعْمُ المَوْتِ فِي أَمْرٍ حَقِيرٍ", "كَطَعْمِ المَوْتِ فِي أَمْرٍ عَظِيمِ"),
    ("يَرَى الجُبَنَاءُ أَنَّ العَجْزَ عَقْلٌ", "وَتِلْكَ خَدِيعَةُ الطَّبْعِ اللَّئِيمِ"),
]

poem_analysis = processor.analyze_poem(poem)
print(format_poem_report(poem_analysis))

print("Dominant Meter:", poem_analysis.meter_name_ar)
print("Average Score:", poem_analysis.average_score)
print(f"Total Verses: {len(poem_analysis.verses)}")
```

---

## 3. Extracting Phonetic & Binary Patterns

If you only need phonetic transcription or binary prosodic patterns (`1` = Mutaharrik, `0` = Sakin):

```python
from pyarud import ArudiConverter

converter = ArudiConverter()

arudi_text, pattern = converter.prepare_text("مُسْتَفْعِلُنْ مَفْعُولَاتُ")
print("Arudi Text:", arudi_text)  # مُسْتَفْعِلُنْ مَفْعُولَاتُ
print("Binary Pattern:", pattern) # 1010110101010
```

---

## 4. Dictionary Serialization (Legacy & JSON Support)

If you need a plain Python `dict` or JSON-serializable object:

```python
# Convert any analysis to dict
data = verse_analysis.to_dict()
# Or use legacy process_poem
legacy_dict = processor.process_poem([("سَأَتْرُكُ حُبَّكم مِنْ غَيْرِ بُغْضٍ", "وَلَكِنْ كَثْرَةُ الشُّرَكَاءِ فِيهِ")])
```
