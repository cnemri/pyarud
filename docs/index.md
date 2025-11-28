# Welcome to PyArud (بيعروض)

**PyArud** is the definitive Python library for Arabic prosody (Arud) analysis. It bridges the gap between classical prosodic theory and modern computational linguistics.

Whether you are a developer building a poetry app, a researcher analyzing classical corpuses, or a student of *Ilm al-Arudh*, PyArud provides the tools you need.

<div class="grid cards" markdown>

-   :material-book-open-variant: **Deep Theory**
    Learn the science of Arudh, from Al-Khalil's circles to the anatomy of a Watad.
    [:arrow_right: Read the Theory](theory/introduction.md)

-   :material-scale-balance: **The 16 Meters**
    A comprehensive reference for every Bahr, its keys, variations, and allowed modifications.
    [:arrow_right: Explore Meters](meters.md)

-   :material-code-json: **Robust Analysis**
    Detect meters, analyze feet, and identify specific defects (Zihaf & Ellah) with precision.
    [:arrow_right: Quick Start](quickstart.md)

-   :material-hammer-wrench: **Extensible Architecture**
    Built on a modular pipeline that allows you to register custom spellings and extend definitions.
    [:arrow_right: Architecture](architecture.md)

</div>

## Why PyArud?

Arabic prosody is not just about counting syllables. It is a complex system of permissibility (`Jawaz`) and necessity (`Wujub`).

**PyArud is different because:**
1.  **It knows the rules**: It doesn't just regex match. It understands that a `Mustaf'ilun` in Rajaz allows different changes than a `Mustaf'ilun` in Basit.
2.  **It handles the details**: From `Iltiqa al-Sakinayn` (meeting of stills) to `Ashba'` (saturation), the linguistic engine handles the nuances of Arabic phonetics.
3.  **It speaks the language**: The documentation and code use the correct Arabic terminology (Sabab, Watad, Arudh, Dharb) mapped to English, making it a learning resource in itself.

## Installation

```bash
pip install pyarud
```

## Example Analysis

```python
from pyarud.processor import ArudhProcessor

# A verse from Al-Mutanabbi
verse = [("أَلا لا أُري الأحْداثَ حَمْدًا وَلا ذَمّا", "فَما بَطْشُها جَهْلًا وَلا كَفُّها حِلْما")]

processor = ArudhProcessor()
result = processor.process_poem(verse)

print(f"Meter: {result['meter']}") # 'taweel'
print(f"Score: {result['verses'][0]['score']}")
```