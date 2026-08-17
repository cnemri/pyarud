# PyArud (بَيَارُوض)

**PyArud** is a deterministic, high-performance, **zero-dependency** Python engine for Arabic Prosody (*علم العروض والقافية*). It provides mathematically sound meter identification across all 16 classical Arabic meters (*البحور الستة عشر*) and their sub-meter variations (*التام، المجزوء، المشطور، المنهوك، المخلع*), foot-by-foot phonetic scansion, exact Zihaf & 'Ilah diagnosis, and rhyme (*القافية*) analysis.

[![PyPI](https://img.shields.io/pypi/v/pyarud)](https://pypi.org/project/pyarud/)
[![License](https://img.shields.io/github/license/cnemri/pyarud)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)]()

---

## ✨ Features

- **🚀 Zero External Dependencies**: 100% pure Python standard library. Completely independent from `pyarabic` or any heavy external packages.
- **⚡ Extreme Throughput**:
  - Phonetic Arudi Conversion: **>22,000 hemistichs/second** ($0.045\text{ ms/op}$)
  - Full Multi-Meter Verse Scansion: **>3,000 verses/second** ($0.325\text{ ms/op}$)
- **🎯 100% Deterministic Disambiguation**: Formal metric grammar engine resolving notoriously tricky classical overlaps (e.g. *Kamel vs Rajaz*, *Wafer vs Hazaj*, *Mukhalla' al-Basit*, *Saree*, and single-shatr meters).
- **🎼 Full 16-Meter Coverage**: Comprehensive support for all 16 Farahidian meters and variations (*Tam, Majzoo, Mashtoor, Manhook, Mukhalla'*).
- **🔬 Granular Foot Scansion**: Precise foot-by-foot status (`ok`, `broken`, `missing`, `extra_bits`), identifying exact Zihafat (*القبض، الخبن، الطي، الكف، العصب، الإضمار، الخبل، الشكل*) and 'Ilal (*القطع، القصر، الحذف، التذييل، التسبيغ، الكسف، الوقف*).
- **📜 Complete Qafiyah Analysis**: Identifies Rawi (*الروي*), Wasl (*الوصل*), Khuruj (*الخروج*), Ridf (*الردف*), Ta'sees (*التأسيس*), and classical rhyme movement classifications (*المقيدة والمطلقة*).
- **🛡️ 100% Type Safe & Modern**: Strict type annotations with `mypy` and modern Python dataclass models.

---

## 🚀 Installation

Requires Python 3.10+.

```bash
pip install pyarud
```

---

## ⚡ Quick Start

```python
from pyarud import ArudhProcessor

processor = ArudhProcessor()

# 1. Analyze a classical verse (Sadr & Ajuz)
verse = ("أَخِي جَاوَزَ الظَّالِمُونَ الْمَدَى", "فَحَقَّ الْجِهَادُ وَحَقَّ الْفِدَا")
analysis = processor.analyze_verse(*verse)

print(f"Meter: {analysis.meter_name_ar} ({analysis.meter_key})")
print(f"Score: {analysis.score}")
print(f"Arudi Pattern: {analysis.sadr.pattern}  |  {analysis.ajuz.pattern}")

# Foot-by-foot breakdown
for foot in analysis.sadr.feet:
    print(f"  [{foot.status.upper()}] {foot.tafeela_name_ar} ({foot.pattern}) - {foot.zihaf_name_ar}")

# Rhyme (Qafiyah)
if analysis.qafiyah:
    print(f"Rawi: {analysis.qafiyah.rawi_char}")
```

### Analyzing Complete Poems

```python
verses = [
    ("قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيبٍ وَمَنْزِلِ", "بِسِقْطِ اللِّوَى بَيْنَ الدَّخُولِ فَحَوْمَلِ"),
    ("فَتُوضِحَ فَالْمِقْرَاةِ لَمْ يَعْفُ رَسْمُهَا", "لِمَا نَسَجَتْهَا مِنْ جَنُوبٍ وَشَمْأَلِ"),
]

poem_report = processor.analyze_poem(verses)
print(f"Global Meter: {poem_report.meter_name_ar}")
print(f"Dominant Rawi: {poem_report.dominant_rawi}")
print(f"Average Confidence: {poem_report.average_score:.2%}")
```

---

## 📊 Benchmark & Accuracy

Benchmarked on **25 authentic classical poems (76 verses)** across all 16 meters from [Al-Diwan](https://www.aldiwan.net/):

| Metric | Result |
|---|---|
| **Classification Accuracy (16 Buhur)** | **100.0% (76 / 76 verses)** |
| **Phonetic Conversion Speed** | **22,101 hemistichs / sec** |
| **Verse Analysis Speed** | **3,078 verses / sec** |
| **External Runtime Dependencies** | **0 (Zero)** |

---

## 🛠️ Testing & Development

```bash
# Clone repository
git clone https://github.com/cnemri/pyarud.git
cd pyarud

# Run complete test suite (63 unit & benchmark tests)
uv run pytest

# Check code formatting & types
uv run ruff check .
uv run mypy pyarud
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

