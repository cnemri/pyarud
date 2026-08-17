# Cookbook: Common Recipes

This section contains practical code snippets for common tasks with **PyArud v1.0.0**.

## 1. Analyzing a Poem File (Sadr | Ajuz)

If you have a file `poems.txt` where each line is formatted as `Sadr | Ajuz`:

```python
from pyarud import ArudhProcessor, format_poem_report

processor = ArudhProcessor()
verses = []

with open("poems.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if "|" in line:
            parts = line.split("|")
            verses.append((parts[0].strip(), parts[1].strip()))

analysis = processor.analyze_poem(verses)
print(format_poem_report(analysis))
```

---

## 2. Filtering Poems by Specific Meter

To filter a large collection for a specific meter (e.g. Al-Wafer):

```python
from pyarud import ArudhProcessor

processor = ArudhProcessor()
all_verses = [
    ("سَأَتْرُكُ حُبَّكم مِنْ غَيْرِ بُغْضٍ", "وَلَكِنْ كَثْرَةُ الشُّرَكَاءِ فِيهِ"),
    ("إِذَا غَامَرْتَ فِي شَرَفٍ مَرُومِ", "فَلَا تَقْنَعْ بِمَا دُونَ النُّجُومِ"),
]

wafir_verses = []
for sadr, ajuz in all_verses:
    res = processor.analyze_verse(sadr, ajuz)
    if res.meter_key == "wafer":
        wafir_verses.append((sadr, ajuz))

print(f"Found {len(wafir_verses)} Wafir verses.")
```

---

## 3. Extracting Rhyme and Rawi Details

```python
from pyarud.qafiyah import QafiyahAnalyzer

analyzer = QafiyahAnalyzer()

ajuz = "فَلَا تَقْنَعْ بِمَا دُونَ النُّجُومِ"
q = analyzer.analyze(ajuz)

print("Qafiyah Substring:", q.qafiyah_text)      # جُومِ
print("Rawi Letter:", q.rawi)                   # م
print("Rawi Movement:", q.rawi_movement)         # كسرة
print("Rhyme Form:", q.rhyme_form)               # مكسورة (مطلقة)
print("Rhyme Category:", q.rhyme_type)           # المتواتر
```

---

## 4. Converting Text to Arudi Phonetics & Binary Patterns

```python
from pyarud import ArudiConverter

converter = ArudiConverter()
text = "عَلَى قَدْرِ أَهْلِ العَزْمِ تَأْتِي العَزَائِمُ"

arudi_text, pattern = converter.prepare_text(text)
print("Arudi:", arudi_text)  # عَلَا قَدْرِ أَهْلِ لْعَزْمِ تَأْتِ لْعَزَائِمُو
print("Pattern:", pattern)   # 11010110101011010110110
```

---

## 5. Single-Hemistich Scansion (Mashtoor / Manhook)

For poetic forms or educational exercises analyzing a single hemistich:

```python
from pyarud import ArudhProcessor

processor = ArudhProcessor()
shatr = "يَا دَارَ مَيَّةَ بِالعَلْيَاءِ فَالسَّنَدِ"

res = processor.analyze_verse(shatr, "")
print("Meter:", res.meter_name_ar)
print("Sadr Arudi:", res.sadr.arudi_text)
```
