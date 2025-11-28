# Technical Architecture

PyArud is designed as a modular pipeline. It separates the linguistic processing (normalization, phonetics) from the mathematical analysis (pattern matching).

## 1. The Pipeline

Data flows through the system in three stages:

1.  **Input**: Raw Arabic text (Unicode strings).
2.  **Conversion (`ArudiConverter`)**: Transforms text into Arudi Phonetic representation and then into a binary string.
3.  **Analysis (`ArudhProcessor`)**: Matches binary strings against precomputed meter patterns and performs detailed foot-by-foot analysis.

---

## 2. Arudi Conversion (`arudi.py`)

The `ArudiConverter` class is the linguistic engine. It does not know about meters; it only knows about phonetics.

### Key Components
-   **Constants**: Uses `pyarabic.araby` constants (`FATHA`, `SUKUN`, etc.) for robustness.
-   **`CHANGE_LST`**: A dictionary of words with implicit letters (e.g., `هذا` $\rightarrow$ `هاذا`).
    -   *Extensibility:* Users can add to this via `register_custom_spelling()`.
-   **Regex Engine**: Uses regular expressions to handle context-dependent rules:
    -   **Iltiqa Sakinayn**: Dropping vowels before `Al-`.
    -   **Solar Lam**: Assimilating `Al-` into solar letters.
-   **Tokenization**: The text is processed letter-by-letter (or token-by-token) to generate the binary string (`1` for Mutaharrik, `0` for Sakin).

---

## 3. The Meter System (`bahr.py` & `tafeela.py`)

PyArud uses a strict Object-Oriented model to define meters.

### `Tafeela` Class
Represents a single foot (e.g., `Mustafelon`).
-   Stores the standard binary pattern (`1010110`).
-   Defines `allowed_zehafs`: A list of Modification classes (e.g., `Khaban`) that can modify this specific foot.
-   **Generative**: The `all_zehaf_tafeela_forms()` method dynamically generates all valid permutations of the foot based on its allowed modifications.

### `Bahr` Class
Represents a poetic meter (e.g., `Kamel`).
-   **Composition**: Defined as a tuple of `Tafeela` classes (e.g., `(Mutafaelon, Mutafaelon, Mutafaelon)`).
-   **Arudh/Dharb Map**: A dictionary defining valid endings.
    -   Example: `{NoZehafNorEllah: (NoZehafNorEllah, Hadhf)}`. This means "If the Arudh is healthy, the Dharb can be healthy or deleted."
-   **Pattern Generation**: The `detailed_patterns` property permutes all valid `Hashw` (interior) feet with all valid `Arudh/Dharb` endings to create a comprehensive set of valid line patterns.

---

## 4. The Processing Engine (`processor.py`)

The `ArudhProcessor` binds everything together.

### Algorithm: Cubic Similarity Scoring
To distinguish between meters with similar patterns (e.g., a `Rajaz` line that looks like `Kamel` due to Zihaf), the processor uses a cubic scoring function:
$$ Score = (RawRatio)^6 $$
This penalizes small mismatches heavily, ensuring that only structurally sound matches rise to the top.

### Algorithm: Greedy Foot Analysis
Once a meter is detected, the processor performs a "Greedy Match" to segment the verse.
1.  It looks at the binary stream.
2.  It compares the beginning of the stream against all valid forms of the first foot.
3.  It selects the longest valid match (to prefer `Mustaf'ilun` over `Mutaf'ilun` if both fit, though context matters).
4.  It consumes that segment and moves to the next foot.

This approach allows PyArud to pinpoint exactly where a verse breaks, rather than just failing the whole line.
