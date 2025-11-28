# Arudi Writing (الكتابة العروضية)

Before a poem can be analyzed mathematically, it must be transcribed from standard orthography (Imla\'i) to phonetic orthography (Arudi). This is the "compilation" step of prosody.

## The Golden Rule

> **ما يُنْطَقُ يُكْتَبُ، وَما لا يُنْطَقُ لا يُكْتَبُ**
> **What is pronounced is written, and what is not pronounced is not written.**

Arudh does not care about spelling rules, silent letters, or grammar. It cares only about the sound.

---

## Rules of Addition (ما يُزاد)

Letters that are pronounced but usually hidden in spelling must be made explicit.

### 1. Tanween (Nunation)
The \'n\' sound at the end of indefinite nouns is written as a Nun (`ن`).
-   *Kitabun* (كِتَابٌ) $\rightarrow$ *Kitabun* (كِتَابُنْ).
-   *School* (مَدْرَسَةٍ) $\rightarrow$ *Madrasatin* (مَدْرَسَتِنْ).

### 2. Shadda (Gemination)
A doubled letter is written as two letters: the first Sakin (0), the second Mutaharrik (1).
-   *Madda* (مَدَّ) $\rightarrow$ *Madda* (مَدْدَ).
-   *Shams* (الشَّمْس) $\rightarrow$ *Ash-Shams* (اشْشَمْس).

### 3. Explicit Long Vowels
Some words have a long \'A\' that is pronounced but omitted in standard spelling. PyArud automatically expands these.
-   *Hatha* (هذا) $\rightarrow$ *Haatha* (هَاذَا).
-   *Allah* (الله) $\rightarrow$ *Allaah* (اللَّاه).
-   *Lakin* (لكن) $\rightarrow$ *Laakin* (لَاكِن).
-   *Taha* (طه) $\rightarrow$ *Taaha* (طَاهَا).

### 4. Ashba' (Saturation)
The vowel at the end of a hemistich (especially the *Rawi* or rhyme letter) is often stretched until it becomes a long vowel letter.
-   *Kitabu* (كِتَابُ) at end of line $\rightarrow$ *Kitaboo* (كِتَابُو).
-   *Bihi* (بِهِ) $\rightarrow$ *Bihee* (بِهِي).

---

## Rules of Omission (ما يُحْذَف)

Letters that are written but skipped in pronunciation must be removed.

### 1. Hamzat al-Wasl (Connecting Hamza)
The Alif at the start of words like `al-`, `ibn`, `istama\'a` is dropped when preceded by another word.
-   *Wa-istama\'a* (وَاسْتَمَعَ) $\rightarrow$ *Wastama\'a* (وَسْتَمَعَ).
-   *Fi al-bayt* (فِي الْبَيْت) $\rightarrow$ *Fil-bayt* (فِلْبَيْت).

### 2. Lam Shamsiya (Solar Lam)
The \'L\' of `Al-` is dropped if followed by a solar letter (t, th, d, dh, r, z, s, sh, s, d, t, z, l, n), and the solar letter is doubled.
-   *Ash-Shams* (الشَّمْس) $\rightarrow$ *Ashshams* (اشْشَمْس).
-   *Ar-Rajul* (الرَّجُل) $\rightarrow$ *Arrajul* (ارْرَجُل).

### 3. Iltiqa\' al-Sakinayn (Meeting of Two Stills)
If a long vowel ends a word and the next word starts with a Sakin (usually after a dropped Hamzat Wasl), the long vowel is dropped to prevent two Sakins from meeting.
-   *Fi al-bayt* (فِي الْبَيْت) $\rightarrow$ *Fil-bayt* (فِلْبَيْت) (The Ya is dropped).
-   *Da\'a al-qawm* (دَعَا الْقَوْم) $\rightarrow$ *Da\'al-qawm* (دَعَلْقَوْم) (The Alif is dropped).
-   *Yaghzu al-jaysh* (يَغْزُو الْجَيْش) $\rightarrow$ *Yaghzul-jaysh* (يَغْزُلْجَيْش) (The Waw is dropped).

---

## How PyArud Handles This

The `ArudiConverter` class implements these rules using a pipeline of regex replacements and lookaheads.

1.  **Normalization**: Standardizes text (removes Tatweel).
2.  **Preprocessing**: Applies the `CHANGE_LST` for words like "Hatha". Handles Iltiqa\' al-Sakinayn.
3.  **Tokenization**: Parses the string into letters.
4.  **State Machine**: Iterates through letters to handle:
    -   Shadda expansion.
    -   Tanween conversion.
    -   Solar Lam skipping.
    -   Hamzat Wasl skipping.
5.  **Post-processing**: Handles Ashba\' (saturation) at the end of lines.

You can extend the dictionary of special words using `ArudiConverter.register_custom_spelling()`.
