# Cookbook: Common Recipes

This section contains code snippets for common tasks.

## 1. Analyzing a Text File of Poems

If you have a file `poems.txt` where each line is `Sadr | Ajuz`:

```python
from pyarud.processor import ArudhProcessor

processor = ArudhProcessor()
verses = []

with open("poems.txt", "r", encoding="utf-8") as f:
    for line in f:
        if "|" in line:
            parts = line.split("|")
            verses.append((parts[0].strip(), parts[1].strip()))

result = processor.process_poem(verses)
print(f"Detected Meter for file: {result['meter']}")
```

## 2. Filtering by Meter

How to find only lines that match the "Wafir" meter from a list.

```python
all_verses = [...] # Large list of verses
wafir_verses = []

for s, a in all_verses:
    res = processor.process_poem([(s, a)])
    if res['meter'] == 'wafer':
        wafir_verses.append((s, a))
```

## 3. Getting Raw Binary Patterns

Sometimes you just want the `10110` string for your own machine learning model or analysis.

```python
from pyarud.arudi import ArudiConverter

converter = ArudiConverter()
text = "مُسْتَفْعِلُنْ"
_, pattern = converter.prepare_text(text)
print(pattern) # 1010110
```

## 4. Handling Single-Hemistich Lines (Mashtoor)

Some poems or educational texts only have one hemistich.

```python
# Pass an empty string for the Ajuz
result = processor.process_poem([("شَطْرٌ وَاحِدٌ فَقَطْ", "")])

# The result will contain analysis for Sadr, and Ajuz will be None/Empty
print(result['verses'][0]['ajuz_analysis']) # None
```
