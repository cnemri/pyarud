# Quick Start

This guide will get you analyzing Arabic poetry in under 5 minutes.

## 1. Basic Analysis

The primary entry point is the `ArudhProcessor`.

```python
from pyarud.processor import ArudhProcessor

# 1. Initialize
processor = ArudhProcessor()

# 2. Define your verse (Sadr, Ajuz)
verse = ("أَخِي جَاوَزَ الظَّالِمُونَ الْمَدَى", "فَحَقَّ الْجِهَادُ وَحَقَّ الْفِدَا")

# 3. Process
# The input must be a list of tuples
result = processor.process_poem([verse])

# 4. Print Result
print(f"Meter: {result['meter']}")
```

## 2. Interpreting the Result

The `result` is a rich dictionary containing detailed information about every foot in the verse.

```python
{
  "meter": "mutakareb",
  "verses": [
    {
      "verse_index": 0,
      "score": 1.0,
      "sadr_analysis": [
        {
           "foot_index": 0,
           "status": "ok",
           "expected_pattern": "11010",
           "actual_segment": "11010",
           "score": 1.0
        },
        # ... more feet
      ],
      "ajuz_analysis": [...]
    }
  ]
}
```

## 3. Batch Processing

You can analyze an entire poem at once. The processor will determine the global meter based on the majority of verses.

```python
poem = [
    ("أَخِي جَاوَزَ الظَّالِمُونَ الْمَدَى", "فَحَقَّ الْجِهَادُ وَحَقَّ الْفِدَا"),
    ("عَلَامَ التَّعَلُّلُ بِالْآمَالِ", "وَمَا زِلْتُ فِي غَفْلَةٍ رَاقِدَا"),  # Intentionally different/broken for demo
]

result = processor.process_poem(poem)

print(f"Global Meter: {result['meter']}")
for v in result['verses']:
    print(f"Verse {v['verse_index'] + 1} Score: {v['score']}")
```

## 4. Handling Input Text

PyArud works best with **fully diacritized text (Shakl)**.

- **With Diacritics**: `كَتَبَ` -> Detected as `111` (Mutaharrik, Mutaharrik, Mutaharrik).
- **Without Diacritics**: `كتب` -> PyArud has to guess or treat letters as Mutaharrik by default, which may lead to inaccurate results.

**Tip:** If you are building an app, consider using a Tashkeel (diacritization) library like `mishkal` or `tashaphyne` before passing text to PyArud.
