# PyArud (بيعروض)

**PyArud** is a robust Python library for Arabic prosody (Arud) analysis. It detects poetic meters (Buhur), analyzes verses foot-by-foot, and identifies variations (Zihaf) and defects (Ellah) with granular precision.

[![PyPI](https://img.shields.io/pypi/v/pyarud)](https://pypi.org/project/pyarud/)
[![Documentation](https://img.shields.io/badge/docs-live-blue)](https://cnemri.github.io/pyarud/)
[![License](https://img.shields.io/github/license/cnemri/pyarud)](LICENSE)

## 📚 Documentation

Full documentation is available at **[cnemri.github.io/pyarud](https://cnemri.github.io/pyarud/)**.

## ✨ Features

- **Smart Meter Detection**: Automatically identifies the 16 standard meters.
- **Granular Analysis**: Detailed breakdown of each foot (Tafeela) with status codes (`ok`, `broken`, `missing`, `extra_bits`).
- **Arudi Conversion**: Built-in text processing to handle Arabic diacritics and phonetic writing.
- **Robust**: Handles common poetic variations (Zihaf) and obligatory endings (Ellah).

## 🚀 Installation

Requires Python 3.12+.

```bash
pip install pyarud
```

## ⚡ Quick Start

```python
from pyarud.processor import ArudhProcessor

# Initialize the processor
processor = ArudhProcessor()

# Define a verse (Sadr, Ajuz)
verse = ("أَخِي جَاوَزَ الظَّالِمُونَ الْمَدَى", "فَحَقَّ الْجِهَادُ وَحَقَّ الْفِدَا")

# Process the poem
result = processor.process_poem([verse])

print(f"Detected Meter: {result['meter']}")
# Output: mutakareb
```

## 🛠️ Advanced Usage

For detailed tutorials, debugging guides, and API reference, please visit the [Documentation](https://cnemri.github.io/pyarud/).

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
