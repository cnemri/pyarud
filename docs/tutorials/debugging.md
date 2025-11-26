# Debugging Poetry with PyArud

One of PyArud's strongest features is its granular error reporting. This guide explains how to interpret different error statuses.

## The 4 Status Codes

Every foot analyzed by PyArud has a `status` field.

| Status | Icon | Meaning | Action Required |
| :--- | :--- | :--- | :--- |
| `ok` | ✅ | The text perfectly matches the foot pattern (or a valid variation). | None. |
| `broken` | ❌ | Text exists at this position, but it doesn't match any allowed variation for this meter. | Check for typos, missing vowels (Harakat), or incorrect word choice. |
| `missing` | ❓ | The line ended before this foot could be formed. | The verse is too short (Majzoo/Mashtoor?) or words are missing. |
| `extra_bits` | ⚠️ | The line has valid feet, but there are leftover syllables at the end. | The verse is too long. Remove extra words. |

## Case Study: The Extra Word

Imagine a student writes a Mutakarib line but adds an extra adjective at the end.

> **Correct**: `فَعُولُنْ فَعُولُنْ فَعُولُنْ فَعُولُنْ`
> **Student**: `فَعُولُنْ فَعُولُنْ فَعُولُنْ فَعُولُنْ كَبِيرْ` (Added 'Kabir')

```python
result = processor.process_poem([(..., ...)], meter_name="mutakareb")
last_foot = result['verses'][0]['sadr_analysis'][-1]

if last_foot['status'] == 'extra_bits':
    print(f"Warning: You have extra text: {last_foot['actual_segment']}")
```

## Case Study: The Missing Foot

If a line is significantly shorter than expected for the meter (e.g., a *Tam* (full) meter used as *Majzoo* (shortened)), PyArud will report `missing` feet.

```python
# Using a Majzoo line but checking against full Kamil
result = processor.process_poem([(majzoo_line, ...)], meter_name="kamel")
```

The last one or two feet will show as `status: "missing"`. This is often a hint that the poem might actually be *Kamel Majzoo* instead of *Kamel Tam*.

## Visualizing Errors

When building a UI for PyArud, you can use these statuses to color-code the text:
- Green highlight for `ok`.
- Red underline for `broken`.
- Grey ghost text for `missing`.
- Yellow highlight for `extra_bits`.
