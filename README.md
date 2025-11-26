# Pyarud: Arabic Prosody Analysis Library

**Pyarud** is a Python library for analyzing Arabic poetry, specifically focused on **Arud** (prosody). It helps identify the meter (Bahr) of Arabic verses, detect poetic feet (Taf'ila), and analyze changes (Zihaf/Illah).

## Features

- **Meter Detection**: Identifies standard Arabic poetic meters (e.g., Tawil, Basit, Kamil).
- **Verse Analysis**: Breaks down verses into their prosodic components.
- **Scoring System**: Provides a match score to indicate confidence in the detected meter.

## Installation

You can install `pyarud` via pip (once published) or directly from the source.

```bash
pip install pyarud
```

## Quick Start

Here is a simple example of how to use `pyarud` to analyze a verse:

```python
from pyarud.processor import ArudhProcessor

# Initialize the processor
processor = ArudhProcessor()

# Define a verse (Sadr and Ajuz)
verse = ("أَخِي جَاوَزَ الظَّالِمُونَ الْمَدَى", "فَحَقَّ الْجِهَادُ وَحَقَّ الْفِدَا")

# Process the poem (list of verses)
result = processor.process_poem([verse])

# Print the results
if "error" in result:
    print(f"Error: {result['error']}")
else:
    print(f"Detected Meter: {result['meter']}")
    for v in result['verses']:
        print(f"Sadr Pattern: {v['sadr_text']}")
        print(f"Match: {v['best_ref_pattern']}")
```

## Development

To set up the development environment:

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -e .[dev]
    ```
3.  Run tests:
    ```bash
    pytest
    ```

## Credits & Acknowledgements

This project is a restructured and improved version of **Bohour** by Maged Saeed. We gratefully acknowledge the original work which served as the foundation for this library.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.