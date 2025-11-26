# Step-by-Step Analysis Tutorial

In this tutorial, we will manually walk through the process of analyzing a verse, breaking it, and understanding how PyArud "sees" the poem.

## The Verse

We will use a famous line from Al-Mutanabbi (Meter: Basit):

> **أَنَامُ مِلْءَ جُفُونِي عَنْ شَوَارِدِهَا** ... **وَيَسْهَرُ الْخَلْقُ جَرَّاهَا وَيَخْتَصِمُ**

*(I sleep with my eyelids full, ignoring its stray thoughts ... while the people stay awake because of them, arguing)*

## Step 1: The Arudi Conversion

Before looking for patterns, we must convert "Written Arabic" to "Spoken Arabic" (Arudi style).

```python
from pyarud.arudi import ArudiConverter

converter = ArudiConverter()
sadr = "أَنَامُ مِلْءَ جُفُونِي عَنْ شَوَارِدِهَا"

arudi_text, pattern = converter.prepare_text(sadr)

print(f"Arudi Text: {arudi_text}")
print(f"Pattern:    {pattern}")
```

**Output:**
- **Arudi Text**: `أنام ملء جفوني عن شواردها` (Notice: letters pronounced but not written are added, and vice versa. Here, it's mostly straight forward).
- **Pattern**: `11011011101010110110`

## Step 2: Identifying the Meter

The pattern starts with `1101` (`Fa'ilun`) or `1010` (`Mustaf'ilun` via Khaban?).

Let's run it through the processor.

```python
from pyarud.processor import ArudhProcessor

processor = ArudhProcessor()
verse = [
    ("أَنَامُ مِلْءَ جُفُونِي عَنْ شَوَارِدِهَا", "وَيَسْهَرُ الْخَلْقُ جَرَّاهَا وَيَخْتَصِمُ")
]

result = processor.process_poem(verse)
print(result['meter'])
```
**Output**: `baseet`

## Step 3: Introducing a Defect

Let's intentionally break the rhythm to see how PyArud handles it. We will remove the word "ملء" (mil'a) from the first hemistich.

**Broken Sadr**: `أَنَامُ جُفُونِي عَنْ شَوَارِدِهَا`

```python
broken_verse = [
    ("أَنَامُ جُفُونِي عَنْ شَوَارِدِهَا", "وَيَسْهَرُ الْخَلْقُ جَرَّاهَا وَيَخْتَصِمُ")
]

# Force 'baseet' because we know what it SHOULD be
result = processor.process_poem(broken_verse, meter_name="baseet")

# Inspect the Sadr
sadr_feet = result['verses'][0]['sadr_analysis']
for foot in sadr_feet:
    print(f"Expected: {foot['expected_pattern']:<10} | Got: {foot['actual_segment']:<10} | Status: {foot['status']}")
```

**Output Analysis:**
1.  **Foot 1**: `Mustaf'ilun` (1010110). Our text `أَنَامُ جُ` (A-na-mu-ju) -> `11011`. This doesn't match well.
2.  PyArud will try to find the *best* match. It might flag the first foot as broken, or "eat" the wrong characters.

By forcing the meter (`meter_name="baseet"`), you tell PyArud: *"I expect this structure. Tell me where the text deviates."* This is powerful for educational tools or auto-correct features.
