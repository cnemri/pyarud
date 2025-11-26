# Core Concepts

Understanding how PyArud (بيعروض) analyzes poetry requires familiarity with a few key concepts from Arabic prosody (Arud).

## 1. The Arudi Pattern

At its core, Arud is binary. Every letter in a spoken poem is either:
- **Mutaharrik (Moved)**: Has a vowel (Fatha, Damma, Kasra). Represented as `1`.
- **Sakin (Still)**: Has a Sukun or is a long vowel (Alif, Waw, Ya). Represented as `0`.

PyArud converts your text into this binary string.
**Example:**
`فَعُولُنْ` (Fa-u-lun) -> `11010`

---

## 2. Meters (Buhur)

Arabic poetry is classified into 16 standard meters (Buhur), each defined by a specific rhythm of feet (Tafila).

Below is the list of meters supported by PyArud, along with their standard mnemonic (Meftah) and feet.

| Meter (Bahr) | Mnemonic (Meftah) | Standard Feet |
| :--- | :--- | :--- |
| **Tawil** | طَوِيلٌ لَهُ دُونَ الْبُحُورِ فَضَائِلُ | `Fa'ulun Mafa'ilun Fa'ulun Mafa'ilun` |
| **Madid** | لِمَدِيدِ الشِّعْرِ عِنْدِي صِفَاتُ | `Fa'ilatun Fa'ilun Fa'ilatun` |
| **Basit** | إِنَّ الْبَسِيطَ لَدَيْهِ يُبْسَطُ الْأَمَلُ | `Mustaf'ilun Fa'ilun Mustaf'ilun Fa'ilun` |
| **Wafir** | بُحُورُ الشِّعْرِ وَافِرُهَا جَمِيلُ | `Mufa'alatun Mufa'alatun Fa'ulun` |
| **Kamil** | كَمُلَ الْجَمَالُ مِنَ الْبُحُورِ الْكَامِلُ | `Mutafa'ilun Mutafa'ilun Mutafa'ilun` |
| **Hazaj** | عَلَى الْأَهْزَاجِ تَسْهِيلُ | `Mafa'ilun Mafa'ilun` |
| **Rajaz** | فِي أَبْحُرِ الْأَرْجَازِ بَحْرٌ يَسْهُلُ | `Mustaf'ilun Mustaf'ilun Mustaf'ilun` |
| **Ramal** | رَمَلُ الْأَبْحُرِ يَرْوِيهِ الثِّقَاتُ | `Fa'ilatun Fa'ilatun Fa'ilatun` |
| **Saree** | بَحْرٌ سَرِيعٌ مَا لَهُ سَاحِلُ | `Mustaf'ilun Mustaf'ilun Fa'ilun` |
| **Munsarih** | مُنْسَرِحٌ فِيهِ يُضْرَبُ الْمَثَلُ | `Mustaf'ilun Maf'ulatu Mufta'ilun` |
| **Khafif** | يَا خَفِيفاً خَفَّتْ بِهِ الْحَرَكَاتُ | `Fa'ilatun Mustaf'ilun Fa'ilatun` |
| **Mudhari** | تَعَدَّ مَعَ الْعَوَاقِلْ | `Mafa'ilun Fa'ilatun` |
| **Muqtadhib** | اقْتَضِبْ كَمَا سَأَلُوا | `Maf'ulatu Mufta'ilun` |
| **Mujtath** | إِنْ جُثَّتِ الْحَرَكَاتُ | `Mustaf'ilun Fa'ilatun` |
| **Mutakarib** | عَنِ الْمُتَقَارِبِ قَالَ الْخَلِيلُ | `Fa'ulun Fa'ulun Fa'ulun Fa'ulun` |
| **Mutadarak** | حَرَكَاتُ الْمُحْدَثِ تَنْتَقِلُ | `Fa'ilun Fa'ilun Fa'ilun Fa'ilun` |

---

## 3. Variations (Zihaf & Ellah)

Poets often deviate from the standard pattern. These deviations are strictly categorized.

### Zihaf (Relaxation)
Changes that occur in the "Hashw" (internal feet) of the verse. They are usually optional and do not have to be consistent throughout the poem.

| Name | Description | Example |
| :--- | :--- | :--- |
| **Khaban** | Deletion of the 2nd letter. | `Mustaf'ilun` -> `Mutaf'ilun` |
| **Tay** | Deletion of the 4th letter. | `Mustaf'ilun` -> `Musta'ilun` |
| **Qabadh** | Deletion of the 5th letter. | `Fa'ulun` -> `Fa'ulu` |
| **Kaff** | Deletion of the 7th letter. | `Fa'ilatun` -> `Fa'ilatu` |
| **Idmar** | Quieting the 2nd moved letter. | `Mutafa'ilun` -> `Mutfa'ilun` (becomes `Mustaf'ilun`) |
| **Asab** | Quieting the 5th moved letter. | `Mufa'alatun` -> `Mufa'altun` |

### Ellah (Defect/Cause)
Changes that usually occur in the "Arudh" (end of first hemistich) or "Dharb" (end of second hemistich). Once applied, they often must be consistent throughout the poem.

| Name | Description |
| :--- | :--- |
| **Hadhf** | Removal of the last light syllable (Sabab Khafif). |
| **Qataa** | Cutting the end of a Watad Majmu' and quieting the previous letter. |
| **Batr** | A combination of Hadhf and Qataa (severe reduction). |
| **Tatheel** | Adding a letter to the end (increasing length). |
| **Tarfeel** | Adding a syllable to the end. |

---

## 4. Pattern Matching Strategy

PyArud uses a **Greedy Matching** strategy to analyze verses.

1.  **Identification**: It first detects the meter that best fits the overall line.
2.  **Segmentation**: It tries to map the binary string of your verse to the valid feet of that meter.
3.  **Optimization**: If a perfect match isn't found, it looks for the longest valid foot (standard or modified by Zihaf) that matches the current position.
4.  **Error Reporting**:
    *   If it finds text that matches a foot, it marks it `ok`.
    *   If it finds text but it doesn't match any valid variation, it marks it `broken`.
    *   If the verse ends prematurely, it marks the remaining feet as `missing`.
    *   If there are leftover syllables after the verse is complete, it marks them as `extra_bits`.
