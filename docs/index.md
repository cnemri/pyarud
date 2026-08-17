# Welcome to PyArud (بيعروض)

**PyArud** is the definitive, zero-dependency Python library for Arabic prosody (العروض) and rhyme (القافية) analysis. It bridges the gap between classical Farahidian prosodic theory and modern computational linguistics.

Whether you are building a digital humanities platform, an Arabic NLP pipeline, a poetry generation model, or studying *Ilm al-Arudh*, PyArud provides an exact, deterministic, and high-performance toolkit.

<div class="grid cards" markdown>

-   :material-feather: **Zero Runtime Dependencies**
    Pure Python 3.12+ with zero external packages. Fast, lightweight, and embeddable anywhere.
    [:arrow_right: Installation](installation.md)

-   :material-scale-balance: **Deterministic Farahidi Engine**
    Exact Dynamic Programming grammar scansion covering all 16 Buhur and their variations.
    [:arrow_right: Explore Meters](meters.md)

-   :material-format-list-checks: **Zihafat, Ilal & Qafiyah**
    Deep foot-by-foot defect detection and full rhyme analysis (Rawi, Wasl, Khuruj, Ridf, Tasees).
    [:arrow_right: Quick Start](quickstart.md)

-   :material-code-json: **Modern Typed Architecture**
    Strictly typed dataclasses (`VerseAnalysis`, `PoemAnalysis`), PEP 561 compliance, and rich formatting.
    [:arrow_right: Architecture](architecture.md)

</div>

## Why PyArud?

Arabic prosody is a rigorous mathematical and linguistic system of permissibility (`Jawaz`) and necessity (`Wujub`).

**PyArud v1.0.0 is different because:**
1.  **Zero Dependencies**: No dependency on `pyarabic` or C-extensions. Pure, robust, Unicode-compliant Arabic orthography and phonetics.
2.  **Deterministic Scansion**: Replaces heuristic/fuzzy matching with Farahidi's dynamic programming grammar rules, accurately handling composite Zihafat and Ilal.
3.  **Complete Rhyme Analysis**: Fully extracts and classifies the Rawi (الروي), Wasl (الوصل), Khuruj (الخروج), Ridf (الردف), Tasees (التأسيس), Dakhil (الدخيل), and rhyme movement (المجرى، التوجيه، النفاذ).
4.  **100% Unseen Benchmark Accuracy**: Tested on 80 authentic classical and modern Arabic poems crawled directly from [Al-Diwan](https://www.aldiwan.net/) across all 16 meters with a 100% pass rate.

## Installation

```bash
pip install pyarud
```

Or with `uv`:

```bash
uv add pyarud
```

## Quick Example

```python
from pyarud import ArudhProcessor, format_verse_report

processor = ArudhProcessor()

# Analyze a verse by Al-Mutanabbi
sadr = "إِذَا غَامَرْتَ فِي شَرَفٍ مَرُومِ"
ajuz = "فَلَا تَقْنَعْ بِمَا دُونَ النُّجُومِ"

analysis = processor.analyze_verse(sadr, ajuz)
print(format_verse_report(analysis))

# Access typed attributes directly:
print("Meter:", analysis.meter_name_ar)       # الطويل
print("Score:", analysis.score)               # 1.0
print("Rawi:", analysis.qafiyah.rawi)         # م
print("Rhyme Form:", analysis.qafiyah.rhyme_form) # مكسورة
```