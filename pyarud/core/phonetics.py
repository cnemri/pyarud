"""
Phonetic and Arudi Orthography Converter for PyArud.

Transforms diacritized Arabic poetic text into its phonetic Arudi representation
(الكتابة العروضية) and extracts binary prosodic metric patterns (1s and 0s).
"""

from __future__ import annotations

import re
from typing import Final

from .arabic import (
    normalize_ligatures,
    normalize_orthography,
    strip_tashkeel,
)
from .constants import (
    ALEF,
    ALEF_HAMZA_ABOVE,
    ALEF_MADDA,
    ALEF_MAKSURA,
    DAMMA,
    DAMMATAN,
    FATHA,
    HARAKAT,
    HARAKAT_SET,
    KASRA,
    KASRATAN,
    LETTERS,
    LETTERS_SET,
    LONG_VOWELS,
    NOON,
    SHADDA,
    SUKUN,
    SUN_LETTERS,
    TANWEEN,
    TANWEEN_SET,
    WAW,
    YEH,
)

# Core dictionary of words with non-phonetic or irregular classical spellings
DEFAULT_ARUDI_REPLACEMENTS: Final[dict[str, str]] = {
    "هذا": "هَاذَا",
    "هذه": "هَاذِهِي",
    "هذان": "هَاذَان",
    "هذين": "هَاذَيْن",
    "هؤلاء": "هَاؤُلَاءِ",
    "ذلك": "ذَالِكَ",
    "ذلكما": "ذَالِكُمَا",
    "ذلكم": "ذَالِكُم",
    "ذلكن": "ذَالِكُنَّ",
    "أولئك": "أُلَائِكَ",
    "أولئكم": "أُلَائِكُم",
    "أولو": "أُلُو",
    "أولي": "أُلِي",
    "أولات": "أُلَات",
    "الله": "اللَّاه",
    "اللهم": "اللَّاهُمَّ",
    "إله": "إِلَاه",
    "الإله": "الإِلَاه",
    "إلهي": "إِلَاهِي",
    "إلهنا": "إِلَاهُنَا",
    "إلهكم": "إِلَاهُكُم",
    "إلههم": "إِلَاهُهُم",
    "إلههن": "إِلَاهُهُنَّ",
    "رحمن": "رَحْمَان",
    "الرحمن": "الرَّحْمَان",
    "طاوس": "طَاوُوس",
    "داود": "دَاوُود",
    "ناوس": "نَاوُوس",
    "هارون": "هَارُون",
    "لكن": "لَاكِن",
    "لكنّ": "لَاكِنَّ",
    "لكنه": "لَاكِنَّهُو",
    "لكنها": "لَاكِنَّهَا",
    "طه": "طَاهَا",
    "يس": "يَاسِين",
    "لله": "لِلَّاه",
    "بالله": "بِاللَّاه",
    "والله": "وَاللَّاه",
    "تالله": "تَاللَّاه",
    "آه": "أَاهِ",
    "عمرو": "عَمْر",
    "مائة": "مِئَة",
    "مائتان": "مِئَتَان",
    "مائتين": "مِئَتَيْن",
}

VALID_PREFIXES: Final[tuple[str, ...]] = ("و", "ف", "ك", "ب", "ل", "وب", "فك", "ول", "فل")
PREFIX_HARAKAT: Final[dict[str, str]] = {
    "و": "وَ",
    "ف": "فَ",
    "ك": "كَ",
    "ب": "بِ",
    "ل": "لِ",
}

_RE_LONG_VOWEL_WASL: Final = re.compile(r"([^\s]\S*)([اىيو])\s+ا")
_RE_SPACE_WASL: Final = re.compile(r"\s+ا")
_RE_ALLAH_PREFIX: Final = re.compile(f"([فوبتك])([{FATHA}{DAMMA}{KASRA}]?)ا(لل)")
_RE_DETACH_AL: Final = re.compile(r"(^|\s)([فوبتك])([َُِ])?ال")
_RE_SOLAR_LAM: Final = re.compile(f" ال([{SUN_LETTERS}])")
_RE_MULTI_SPACES: Final = re.compile(r" +")
_RE_DOUBLE_HARAKA: Final = re.compile(f"([{FATHA}{DAMMA}{KASRA}])([{FATHA}{DAMMA}{KASRA}]+)")


class ArudiConverter:
    """
    Phonetic Converter for Arabic Prosody (*Ilm al-Arud*).

    Converts standard diacritized Arabic poetry into phonetic Arudi writing
    and extracts binary patterns (1 = Mutaharrik, 0 = Sakin).
    """

    def __init__(self, custom_replacements: dict[str, str] | None = None) -> None:
        self.replacements = dict(DEFAULT_ARUDI_REPLACEMENTS)
        if custom_replacements:
            self.replacements.update(custom_replacements)

        self.harakat = HARAKAT
        self.sukun = (SUKUN,)
        self.mostly_saken = LONG_VOWELS
        self.tnween_chars = TANWEEN
        self.shadda_chars = (SHADDA,)
        self.all_chars = list(LETTERS + " ")
        self.prem_chars = set(
            self.harakat
            + self.sukun
            + self.mostly_saken
            + self.tnween_chars
            + self.shadda_chars
            + tuple(self.all_chars)
        )

    def register_custom_spelling(self, word: str, replacement: str) -> None:
        """Register a custom phonetic spelling for a specific unvocalized word."""
        self.replacements[word] = replacement

    def _normalize_shadda(self, text: str) -> str:
        """Ensure Shadda precedes short vowels or tanween."""
        harakat_all = "".join(HARAKAT + TANWEEN)
        return re.sub(f"([{harakat_all}])([{SHADDA}])", r"\2\1", text)

    def _clean_extra_harakat(self, text: str) -> str:
        """Collapse consecutive vowel marks to a single mark."""
        return _RE_DOUBLE_HARAKA.sub(r"\1", text)

    def _resolve_wasl(self, text: str) -> str:
        """
        Handles Hamzat al-Wasl (همزة الوصل) and Iltiqa al-Sakinayn (التقاء الساكنين).
        1. Drop preceding long vowel + space + Wasl Alif (e.g. 'في البيت' -> 'فِلْبَيْتِ').
        2. Drop space + Wasl Alif in connected speech.
        3. Drop Alif in 'Allah' when prefixed by prepositions/particles.
        """
        # Long vowel before Wasl: 'فِي البَيْتِ' -> 'فِالبَيْتِ' -> 'فِلْبَيْتِ'
        text = _RE_LONG_VOWEL_WASL.sub(r"\1", text)

        # Space + Wasl: drop both
        text = _RE_SPACE_WASL.sub("", text)

        # Prefix + Allah: 'فَالله' -> 'فَلله'
        text = _RE_ALLAH_PREFIX.sub(r"\1\2\3", text)

        return text

    def _process_specials_before(self, bait: str) -> str:
        """Handle pre-phonetic orthographic and grammatical replacements."""
        # Initial bare Alif -> hamza with fatha for prosody
        if bait and bait[0] == ALEF:
            bait = ALEF_HAMZA_ABOVE + FATHA + bait[1:]

        # Detach prefixes before 'Al-' (e.g., 'والبيت' -> 'وَ ال بيت')
        bait = _RE_DETACH_AL.sub(r"\1\2\3 ال", bait)

        # Solar Lam Handling: ' ال شمس' -> ' ا شمس' (Lam is assimilated)
        bait = _RE_SOLAR_LAM.sub(r" ا\1", bait)

        # Waw of plural: 'قالوا ' -> 'قالو '
        bait = bait.replace("وا ", "و ")
        if bait.endswith("وا"):
            bait = bait[:-1]
        bait = bait.replace("وْا", "و")
        if bait.endswith("وْا"):
            bait = bait[:-2] + "و"

        # Common phrases & contractions
        bait = bait.replace("الله", "اللاه")
        bait = bait.replace("اللّه", "اللاه")
        bait = bait.replace("إلَّا", "إِلَّا")
        bait = bait.replace("نْ ال", "نَ ال")
        bait = bait.replace("لْ ال", "لِ ال")
        bait = bait.replace("ْ ال", "ِ ال")
        bait = bait.replace("عَمْرٍو", "عَمْرٍ")
        bait = bait.replace("عَمْرُو", "عَمْرُ")
        bait = bait.replace("عَمْرٌو", "عَمْرٌ")

        # Replace irregular words using dictionary
        words = bait.split(" ")
        out: list[str] = []

        removable_chars = "".join(HARAKAT + TANWEEN + (SUKUN,))
        strip_harakat_pattern = f"[{removable_chars}]"

        for word in words:
            if not word:
                continue

            cleaned_with_shadda = re.sub(strip_harakat_pattern, "", word)
            cleaned_plain = strip_tashkeel(word)

            found = False
            for candidate in (cleaned_with_shadda, cleaned_plain):
                if candidate in self.replacements:
                    out.append(self.replacements[candidate])
                    found = True
                    break

            if found:
                continue

            # Check prefixes
            for candidate in (cleaned_with_shadda, cleaned_plain):
                if found:
                    break
                for key, replacement in self.replacements.items():
                    if candidate.endswith(key) and len(candidate) > len(key):
                        prefix = candidate[: -len(key)]
                        if prefix in VALID_PREFIXES:
                            new_prefix = "".join(PREFIX_HARAKAT.get(p, p) for p in prefix)
                            out.append(new_prefix + replacement)
                            found = True
                            break

            if not found:
                out.append(word)

        bait = " ".join(out)

        # If second char is bare consonant when first is consonant, assume default vowel
        if (
            len(bait) > 1
            and bait[0] in LETTERS_SET
            and bait[1] in LETTERS_SET
            and bait[1] != " "
            and bait[1] not in (ALEF, WAW, YEH, ALEF_MAKSURA)
        ):
            bait = bait[0] + FATHA + bait[1:]

        # Filter trailing Alif of Tanween Fath (e.g. 'كِتَاباً' -> 'كِتَابَنْ')
        final_chars: list[str] = []
        i = 0
        while i < len(bait):
            if bait[i] == ALEF and i > 0 and bait[i - 1] in TANWEEN_SET:
                i += 1
                while i < len(bait) and bait[i] in self.prem_chars and bait[i] not in LETTERS_SET:
                    i += 1
                continue
            final_chars.append(bait[i])
            i += 1

        return "".join(final_chars)

    def _extract_pattern(self, text: str, saturate: bool = True, muqayyad: bool = False) -> tuple[str, str]:
        """
        Extract the Arudi phonetic text and binary prosodic pattern (1s and 0s).
        """
        text = self._clean_extra_harakat(text)
        # Expand Madda (آ -> ءَا)
        text = text.replace(ALEF_MADDA, "ءَ" + ALEF)
        chars = [c for c in text if c in self.prem_chars]
        chars = list(_RE_MULTI_SPACES.sub(" ", "".join(chars)).strip())

        out_pattern: list[str] = []
        plain_chars: list[str] = []

        i = 0
        n = len(chars)

        while i < n:
            char = chars[i]
            next_char = chars[i + 1] if i + 1 < n else ""
            next_next_char = chars[i + 2] if i + 2 < n else ""
            prev_digit = out_pattern[-1] if out_pattern else ""

            if char == " ":
                plain_chars.append(" ")
                i += 1
                continue

            if char in (ALEF, ALEF_MAKSURA):
                if prev_digit != "0":
                    out_pattern.append("0")
                plain_chars.append(char)
                i += 1
                continue

            if char in LETTERS_SET:
                # Look ahead past spaces
                if next_char == " " and next_next_char:
                    next_char = next_next_char

                if next_char in HARAKAT_SET:
                    is_last_group = i + 2 >= n
                    if muqayyad and is_last_group:
                        out_pattern.append("0")
                        plain_chars.append(char)
                    else:
                        out_pattern.append("1")
                        plain_chars.append(char)

                elif next_char in self.sukun:
                    if prev_digit != "0" or (i + 1) == n - 1:
                        out_pattern.append("0")
                        plain_chars.append(char)
                    else:
                        if plain_chars and plain_chars[-1] == " ":
                            plain_chars.pop()
                        plain_chars.append(char)

                elif next_char in TANWEEN_SET:
                    if char != ALEF:
                        plain_chars.append(char)
                    plain_chars.append(NOON)
                    out_pattern.extend(["1", "0"])

                    # Skip trailing alif after tanween fath
                    if i + 2 < n and chars[i + 2] == ALEF:
                        i += 1

                elif next_char in self.shadda_chars:
                    if prev_digit != "0":
                        plain_chars.extend([char, char])
                        out_pattern.extend(["0", "1"])
                    else:
                        if plain_chars and plain_chars[-1] == " ":
                            plain_chars.pop()
                        plain_chars.extend([char, char])
                        out_pattern.append("1")

                    # Check what follows Shadda
                    if i + 2 < n:
                        if chars[i + 2] in HARAKAT_SET:
                            is_last_shadda = i + 3 >= n
                            if muqayyad and is_last_shadda:
                                out_pattern[-1] = "0"
                            i += 1  # consume haraka
                        elif chars[i + 2] in TANWEEN_SET:
                            i += 1
                            plain_chars.append(NOON)
                            out_pattern.append("0")
                            if i + 2 < n and chars[i + 2] == ALEF:
                                i += 1

                elif next_char in (ALEF, ALEF_MAKSURA):
                    out_pattern.extend(["1", "0"])
                    plain_chars.extend([char, next_char])

                elif next_char in LETTERS_SET:
                    if prev_digit != "0":
                        out_pattern.append("0")
                        plain_chars.append(char)
                    elif prev_digit == "0" and i + 1 < n and chars[i + 1] == " ":
                        out_pattern.append("1")
                        plain_chars.append(char)
                    else:
                        if plain_chars and plain_chars[-1] == " ":
                            plain_chars.pop()
                        plain_chars.append(char)
                        out_pattern.append("0")
                    i -= 1
                else:
                    # End of text without explicit haraka/sukun
                    if prev_digit != "0":
                        out_pattern.append("0")
                    else:
                        out_pattern.append("1")
                    plain_chars.append(char)
                    i += 1
                    continue

                # Pronoun Ha saturation (هاء الضمير / هاء الغائب):
                # In Arabic prosody, Haa al-Dhamir saturates only when preceded by a mutaharrik (vocalized) consonant
                if not muqayyad and next_next_char == " " and len(out_pattern) >= 2 and out_pattern[-2] == "1":
                    if char == "ه":
                        if next_char == KASRA:
                            plain_chars.append(YEH)
                            out_pattern.append("0")
                        elif next_char == DAMMA:
                            plain_chars.append(WAW)
                            out_pattern.append("0")

                i += 2
            else:
                i += 1

        pattern_str = "".join(out_pattern)
        arudi_str = "".join(plain_chars)

        # Final saturation of Mutlaq rhyme
        if not muqayyad and saturate and pattern_str and pattern_str[-1] != "0":
            pattern_str += "0"

        if not muqayyad and saturate and chars:
            last_char = chars[-1]
            if last_char == KASRA:
                arudi_str += YEH
            elif last_char == KASRATAN:
                arudi_str = arudi_str[:-1] + YEH if arudi_str.endswith(NOON) else arudi_str + YEH
            elif last_char == FATHA:
                arudi_str += ALEF
            elif last_char == DAMMA:
                arudi_str += WAW
            elif last_char == DAMMATAN:
                arudi_str = arudi_str[:-1] + WAW if arudi_str.endswith(NOON) else arudi_str + WAW
            elif last_char in LONG_VOWELS and len(chars) > 1 and chars[-2] not in TANWEEN_SET:
                arudi_str += last_char

        return arudi_str, pattern_str

    def prepare_text(self, text: str, saturate: bool = True, muqayyad: bool = False) -> tuple[str, str]:
        """
        Converts standard Arabic text into phonetic Arudi writing and extracts its binary pattern.

        Args:
            text (str): Input Arabic verse or hemistich.
            saturate (bool): Whether to apply end-of-shatr saturation (Ishba'). Defaults to True.
            muqayyad (bool): Whether the verse has a restricted/quiescent rhyme (Muqayyad).

        Returns:
            tuple[str, str]: (arudi_phonetic_text, binary_pattern)
        """
        text = text.strip()
        if not text:
            return "", ""

        text = text.replace(ALEF_MADDA, "ءَ" + ALEF)
        text = normalize_orthography(text)
        text = normalize_ligatures(text)
        text = self._normalize_shadda(text)
        preprocessed = self._process_specials_before(text)
        preprocessed = self._resolve_wasl(preprocessed)
        arudi_style, pattern = self._extract_pattern(preprocessed, saturate=saturate, muqayyad=muqayyad)

        # Post-processing special orthography
        arudi_style = arudi_style.replace("ةن", "تن")

        return arudi_style, pattern
