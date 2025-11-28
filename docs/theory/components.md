# The Foundation: Components (الأركان والتفاعيل)

Arabic prosody is built on a binary system. Every sound is either moving or still. These atoms combine to form molecules (Sabab, Watad), which combine to form the DNA of the verse (Taf'ila).

## 1. The Atoms: Haraka and Sukun

-   **Haraka (Movement - / or 1)**: A letter with a vowel (Fatha, Damma, Kasra).
    -   Example: The 'K' in *Ka-taba* (كَ).
-   **Sukun (Stillness - o or 0)**: A letter with no vowel, or a long vowel (Alif, Waw, Ya).
    -   Example: The 'L' in *Qul* (قُلْ), or the 'A' in *Qaala* (قَالَ).

In PyArud, we represent these digitally as `1` (Haraka) and `0` (Sukun).

---

## 2. The Molecules: Roots (الأصول)

These atoms combine to form linguistic units used to build feet. Al-Khalil identified six types:

### A. Asbab (Cords) - الأسباب
Named after the rope of a tent.
1.  **Sabab Khafif (Light Cord)**: A moving letter followed by a still one (`/o` or `10`).
    -   Example: *Laml* (لَمْ), *Man* (مَنْ).
2.  **Sabab Thaqil (Heavy Cord)**: Two moving letters (`//` or `11`).
    -   Example: *Laka* (لَكَ), *Bika* (بِكَ).

### B. Awtad (Pegs) - الأوتاد
Named after the peg used to secure the tent. Pegs are stronger than Cords and rarely suffer from deletion (Zihaf).
3.  **Watad Majmu' (Joined Peg)**: Two moving letters followed by a still one (`//o` or `110`).
    -   Example: *Laqad* (لَقَدْ), *Na'am* (نَعَمْ).
    -   *Note:* This is the most stable unit in Arabic prosody.
4.  **Watad Mafruq (Separated Peg)**: A moving letter, a still one, then a moving one (`/o/` or `101`).
    -   Example: *Qama* (قَامَ) in *Qama Zaid* (where Z is next). Or *Lay-ta* (لَيْتَ).

### C. Fawasil (Separators) - الفواصل
5.  **Fasila Sughra (Small Separator)**: Three moving letters followed by a still one (`///o` or `1110`).
    -   Example: *Jabalun* (جَبَلٌ).
    -   *Analysis:* Effectively a Sabab Thaqil + Sabab Khafif (`//` + `/o`).
6.  **Fasila Kubra (Large Separator)**: Four moving letters followed by a still one (`////o` or `11110`).
    -   Example: *Samakatun* (سَمَكَةٌ).
    -   *Analysis:* Effectively a Sabab Thaqil + Watad Majmu' (`//` + `//o`).

### Mnemonic
Generations of students have memorized these units with the phrase:
> **لَمْ أَرَ عَلَى ظَهْرِ جَبَلٍ سَمَكَةً**
> *(Lam Ara 'Ala Zahri Jabalin Samakatan)*
> I have not seen a fish on the back of a mountain.

- **Lam** (`/o`): Sabab Khafif.
- **Ara** (`//`): Sabab Thaqil.
- **'Ala** (`//o`): Watad Majmu'.
- **Zahri** (`/o/`): Watad Mafruq (ignoring the final Kasra logic for isolation).
- **Jabalin** (`///o`): Fasila Sughra.
- **Samakatan** (`////o`): Fasila Kubra.

---

## 3. The DNA: Feet (التفاعيل)

Al-Khalil combined these molecules into 10 standard "Feet" (Taf'ila). These are the templates used to measure verses. They are built from the root word **F-'-L** (فعل).

| Taf'ila (Arabic) | Taf'ila (English) | Pattern | Structure | Used in Meters |
| :--- | :--- | :--- | :--- | :--- |
| **فَعُولُنْ** | Fa'ulun | `11010` | Watad Majmu' + Sabab Khafif | Tawil, Mutaqarib, Hazaj |
| **مَفَاعِيلُنْ** | Mafa'ilun | `1101010` | Watad Majmu' + 2 Sabab Khafif | Hazaj, Tawil, Mudhari |
| **مُفَاعَلَتُنْ** | Mufa'alatun | `1101110` | Watad Majmu' + Fasila Sughra | Wafir |
| **مُتَفَاعِلُنْ** | Mutafa'ilun | `1110110` | Fasila Sughra + Watad Majmu' | Kamil |
| **فَاعِلُنْ** | Fa'ilun | `10110` | Sabab Khafif + Watad Majmu' | Madid, Basit, Mutadarak |
| **فَاعِلاتُنْ** | Fa'ilatun | `1011010` | Watad Mafruq + 2 Sabab Khafif | Ramal, Madid, Khafif |
| **مُسْتَفْعِلُنْ** | Mustaf'ilun | `1010110` | 2 Sabab Khafif + Watad Majmu' | Rajaz, Basit, Saree |
| **مَفْعُولاتُ** | Maf'ulatu | `1010101` | 2 Sabab Khafif + Watad Mafruq | Munsarih, Muqtadhib |
| **فَاعِ لاتُنْ** | Fa'i Latun | `101 1010` | Watad Mafruq + 2 Sabab Khafif | Mudhari (Split version) |
| **مُسْتَفْعِ لُنْ** | Mustaf'i Lun | `1010 110` | 2 Sabab Khafif + Watad Majmu' | Khafif, Mujtath (Split version) |

*Note on Split Feet:*
Some feet like `Mustaf'ilun` can be effectively the same pattern (`1010110`), but their internal structure differs depending on the meter.
- In **Rajaz**, it is `Sabab, Sabab, Watad` (`10, 10, 110`).
- In **Khafif**, it is `Sabab, Watad, Sabab` (`10, 110, 10`), written as `Mustaf'i Lun`.
This distinction is crucial because **Zihaf (Deletion) usually only affects Sababs, not Watads.** A letter that is the 7th in one version might be part of a protected Watad in another.
