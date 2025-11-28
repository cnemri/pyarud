# Modifications: Zihafs and Ellals (الزحافات والعلل)

In Arabic Prosody, the standard feet (Taf'ilas) are ideal templates. Real poetry often modifies these templates for musical variation or necessity. These modifications are strictly categorized into **Zihafs** and **Ellals**.

## 1. Zihaf (الزحاف)

**Definition**: A change that affects the **Sabab** (Cord) letters in the foot.
- **Scope**: Can occur in the *Hashw* (interior feet), *Arudh* (end of 1st hemistich), or *Dharb* (end of 2nd hemistich).
- **Consistency**: Generally **not binding** (*Ghayr Lazim*). If a poet uses a Zihaf in one verse, they are not required to use it in the next (with some exceptions).

### Single Zihafs (الزحاف المفرد)
Changes involving only one letter.

| Name (Arabic) | Name (English) | Definition | Effect | Example |
| :--- | :--- | :--- | :--- | :--- |
| **الإِضْمَار** | **Idmar** | Quieting the 2nd letter. | `11...` $\rightarrow$ `10...` | `Mutafa'ilun` $\rightarrow$ `Mutfa'ilun` |
| **الْخَبْن** | **Khaban** | Deletion of the 2nd letter. | `10...` $\rightarrow$ `1...` | `Mustaf'ilun` $\rightarrow$ `Mutaf'ilun` |
| **الْوَقْص** | **Waqas** | Deletion of the 2nd letter (if moving). | `11...` $\rightarrow$ `1...` | `Mutafa'ilun` $\rightarrow$ `Mufa'ilun` |
| **الطَّي** | **Tay** | Deletion of the 4th letter. | `...10...` $\rightarrow$ `...1...` | `Mustaf'ilun` $\rightarrow$ `Musta'ilun` |
| **الْعَصْب** | **Asab** | Quieting the 5th letter. | `...11...` $\rightarrow$ `...10...` | `Mufa'alatun` $\rightarrow$ `Mufa'altun` |
| **الْقَبْض** | **Qabadh** | Deletion of the 5th letter. | `...10...` $\rightarrow$ `...1...` | `Fa'ulun` $\rightarrow$ `Fa'ulu` |
| **الْعَقْل** | **Akal** | Deletion of the 5th letter (if moving). | `...11...` $\rightarrow$ `...1...` | `Mufa'alatun` $\rightarrow$ `Mufa'atun` |
| **الْكَف** | **Kaff** | Deletion of the 7th letter. | `...10` $\rightarrow$ `...1` | `Fa'ilatun` $\rightarrow$ `Fa'ilatu` |

### Double Zihafs (الزحاف المزدوج)
Changes involving two letters in the same foot.

| Name (Arabic) | Name (English) | Combination | Example |
| :--- | :--- | :--- | :--- |
| **الْخَبْل** | **Khabal** | Khaban + Tay | `Mustaf'ilun` $\rightarrow$ `Mu'ta'ilun` |
| **الْخَزْل** | **Khazal** | Idmar + Tay | `Mutafa'ilun` $\rightarrow$ `Mutfa'il` |
| **الشَّكْل** | **Shakal** | Khaban + Kaff | `Fa'ilatun` $\rightarrow$ `Fa'ilatu` |
| **النَّقْص** | **Nakas** | Asab + Kaff | `Mufa'alatun` $\rightarrow$ `Mufa'altu` |

---

## 2. Ellah (العلة)

**Definition**: A change that affects the **Watad** (Peg) or the ending of the foot.
- **Scope**: Only occurs in the *Arudh* and *Dharb* (the ends of hemistiches).
- **Consistency**: **Binding** (*Lazim*). Once a poet uses an Ellah in the first verse, they must maintain it throughout the entire poem.

### Ellal of Increase (علل الزيادة)
Adding letters to the foot. Occurs mostly in Majzoo meters.

| Name (Arabic) | Name (English) | Definition | Example |
| :--- | :--- | :--- | :--- |
| **التَّرْفِيل** | **Tarfeel** | Adding a Sabab Khafif (`10`) to the end. | `Fa'ilun` $\rightarrow$ `Fa'ilun-tun` (`Fa'ilatun`) |
| **التَّذْيِيل** | **Tatheel** | Adding a Sakin letter to a Watad Majmu'. | `Fa'ilun` $\rightarrow$ `Fa'ilan` |
| **التَّسْبِيغ** | **Tasbeegh** | Adding a Sakin letter to a Sabab Khafif. | `Fa'ilatun` $\rightarrow$ `Fa'ilatan` |

### Ellal of Decrease (علل النقص)
Removing letters from the foot.

| Name (Arabic) | Name (English) | Definition | Example |
| :--- | :--- | :--- | :--- |
| **الْحَذْف** | **Hadhf** | Dropping the final Sabab Khafif. | `Fa'ulun` $\rightarrow$ `Fa'u` |
| **الْقَطْف** | **Qataf** | Dropping Sabab + Asab (Quieting 5th). | `Mufa'alatun` $\rightarrow$ `Fa'ulun` |
| **الْقَطْع** | **Qataa** | Cutting the tail of Watad Majmu' & quieting predecessor. | `Fa'ilun` $\rightarrow$ `Fa'il` |
| **الْبَتْر** | **Batr** | Hadhf + Qataa (Extremity). | `Fa'ulun` $\rightarrow$ `Fa` |
| **الْقَصْر** | **Qasar** | Dropping the Sakin of Sabab Khafif & quieting the mover. | `Fa'ilatun` $\rightarrow$ `Fa'ilat` |
| **الْحَذَذ** | **Hathath** | Dropping a full Watad Majmu'. | `Mutafa'ilun` $\rightarrow$ `Mutfa` |
| **الصَّلْم** | **Salam** | Dropping a full Watad Mafruq. | `Maf'ulatu` $\rightarrow$ `Maf'u` |
| **الْكَشْف** | **Kashf/Kasf** | Dropping the last letter of a Watad Mafruq. | `Maf'ulatu` $\rightarrow$ `Maf'ula` |
| **الْوَقْف** | **Waqf** | Quieting the last letter of a Watad Mafruq. | `Maf'ulatu` $\rightarrow$ `Maf'ulat` |

---

## 3. How PyArud Validates Modifications

PyArud does not just "guess" modifications. Each `Tafeela` class in the code has a list of `allowed_zehafs`.

For example, `Mustafelon` allows `Khaban` and `Tay`.
When analyzing a verse, PyArud generates all mathematically valid permutations of `Mustafelon` (e.g., `1010110`, `110110`, `101010`) and tries to match them against your text.

If a modification is found, the analysis result will explicitly state the `status` and the expected pattern versus the actual segment, allowing you to trace exactly which rule was applied.
