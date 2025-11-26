# Welcome to PyArud (بيعروض)

**PyArud** is a robust Python library for Arabic prosody (Arud) analysis. It detects poetic meters, analyzes verses foot-by-foot, and identifies variations (Zihaf) and defects (Ellah).

## Why PyArud?

Arabic prosody is complex. A single meter can have dozens of valid variations (Zihaf) and obligatory endings (Ellah). Most tools give a simple "Pass/Fail" or struggle with common variations.

**PyArud is designed for precision:**
- **It doesn't just guess:** It uses a deterministic, exhaustive map of valid meter variations.
- **It explains itself:** Instead of just saying "Invalid", it tells you *exactly* which foot broke the rhythm.
- **It handles the edge cases:** From *Idmar* in Kamil to *Batr* in Mutakarib, the library supports deep prosodic rules.

## Features

- **Smart Meter Detection**: Automatically identifies the 16 Khalil meters (Buhur), differentiating between similar rhythms (e.g., Rajaz vs. Kamil).
- **Granular Analysis**: Breaks down every verse into its component feet (Tafila), validating each one individually.
- **Defect Diagnosis**: Explicitly flags:
    - `broken`: Text that violates the meter.
    - `missing`: Feet that are absent from the line.
    - `extra_bits`: Syllables that overflow the meter.
- **Arudi Conversion**: Built-in text processing to handle Arabic diacritics, silent letters (e.g., Solar Lam), and phonetic pronunciation.

## Installation

```bash
pip install pyarud
```

## Quick Start

```python
from pyarud.processor import ArudhProcessor

processor = ArudhProcessor()
verse = [("أَخِي جَاوَزَ الظَّالِمُونَ الْمَدَى", "فَحَقَّ الْجِهَادُ وَحَقَّ الْفِدَا")]

result = processor.process_poem(verse)
print(f"Detected Meter: {result['meter']}")
```
