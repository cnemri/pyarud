"""
Arabic Poetic Rhyme Analyzer (Ilm al-Qafiyah / علم القافية) for PyArud.

Extracts the rhyme span, Rawi, Wasl, Khuruj, Ridf, Ta'sis, Dakhil,
rhyme vowels (Majra, Rass, etc.), and rhythmic classifications (Mutawatir, Mutadarak, etc.).
"""

from __future__ import annotations

from ..core.constants import (
    ALEF,
    ALEF_MAKSURA,
    DAMMA,
    DAMMATAN,
    FATHA,
    FATHATAN,
    HAA,
    HARAKAT_SET,
    KASRA,
    KASRATAN,
    LETTERS_SET,
    NOON,
    SUKUN,
    TANWEEN_SET,
    WAW,
    YEH,
)
from ..core.phonetics import ArudiConverter
from ..models.analysis import QafiyahAnalysis


class QafiyahAnalyzer:
    """
    Analyzes Arabic poetic rhyme (Qafiyah) according to classical prosody.
    """

    def __init__(self) -> None:
        self.converter = ArudiConverter()

    def analyze(self, ajuz_text: str, is_muqayyad: bool = False) -> QafiyahAnalysis:
        """
        Extracts the full Qafiyah breakdown for the concluding hemistich (Ajuz).

        Args:
            ajuz_text (str): The second hemistich of the verse.
            is_muqayyad (bool): True if the poem uses a quiescent/restricted Rawi.

        Returns:
            QafiyahAnalysis: Detailed dataclass with Rawi, Wasl, Ridf, Qafiyah span, etc.
        """
        if not ajuz_text.strip():
            return QafiyahAnalysis(rawi="")

        # Get arudi phonetic text and pattern
        arudi_text, pattern = self.converter.prepare_text(ajuz_text, saturate=not is_muqayyad, muqayyad=is_muqayyad)

        # 1. Determine Qafiyah boundaries:
        # From the last Sakin ('0') back to the preceding Sakin ('0'), plus the preceding Mutaharrik ('1').
        qafiyah_pattern = ""
        qafiyah_type_ar = "المتواتر"
        qafiyah_type_en = "Al-Mutawatir"

        # Find indices of Sakins in pattern
        sakin_indices = [i for i, c in enumerate(pattern) if c == "0"]

        if len(sakin_indices) >= 2:
            last_sakin_idx = sakin_indices[-1]
            prev_sakin_idx = sakin_indices[-2]
            start_idx = max(0, prev_sakin_idx - 1)  # include mutaharrik before previous sakin
            qafiyah_pattern = pattern[start_idx : last_sakin_idx + 1]

            # Count mutaharriks between the two sakins
            num_mutaharriks = max(0, last_sakin_idx - prev_sakin_idx - 1)
            if num_mutaharriks == 0:
                qafiyah_type_ar = "المترادف"
                qafiyah_type_en = "Al-Mutaradif"
            elif num_mutaharriks == 1:
                qafiyah_type_ar = "المتواتر"
                qafiyah_type_en = "Al-Mutawatir"
            elif num_mutaharriks == 2:
                qafiyah_type_ar = "المتدارك"
                qafiyah_type_en = "Al-Mutadarak"
            elif num_mutaharriks == 3:
                qafiyah_type_ar = "المتراكب"
                qafiyah_type_en = "Al-Mutarakib"
            else:
                qafiyah_type_ar = "المتكاوس"
                qafiyah_type_en = "Al-Mutakawis"
        elif len(sakin_indices) == 1:
            qafiyah_pattern = pattern[max(0, sakin_indices[0] - 1) :]
            qafiyah_type_ar = "المتواتر"
            qafiyah_type_en = "Al-Mutawatir"

        # 2. Extract Rawi and ancillary rhyme letters
        rawi, rawi_haraka, wasl, khuruj, ridf, tasees, dakhil = self._extract_rhyme_letters(
            ajuz_text, arudi_text, is_muqayyad
        )

        # 3. Extract Qafiyah Text Span
        words = ajuz_text.strip().split()
        qafiyah_text = words[-1] if words else ""
        if len(words) > 1 and len(qafiyah_pattern) > 5:
            qafiyah_text = f"{words[-2]} {words[-1]}"

        classification = "muqayyadah" if is_muqayyad or not wasl else "mutlaqah"

        return QafiyahAnalysis(
            rawi=rawi,
            rawi_haraka=rawi_haraka,
            wasl=wasl,
            khuruj=khuruj,
            ridf=ridf,
            tasees=tasees,
            dakhil=dakhil,
            qafiyah_text=qafiyah_text,
            qafiyah_pattern=qafiyah_pattern,
            qafiyah_type_ar=qafiyah_type_ar,
            qafiyah_type_en=qafiyah_type_en,
            rhyme_classification=classification,
        )

    def _extract_rhyme_letters(
        self, original_text: str, arudi_text: str, is_muqayyad: bool
    ) -> tuple[str, str, str | None, str | None, str | None, str | None, str | None]:
        """
        Identifies the Rawi and accompanying letters: Wasl, Khuruj, Ridf, Ta'sis, Dakhil.
        """
        clean_text = original_text.strip()
        if not clean_text:
            return "", "", None, None, None, None, None

        # Filter out punctuation
        clean_text = "".join(
            c for c in clean_text if c in LETTERS_SET or c in HARAKAT_SET or c in TANWEEN_SET or c == SUKUN or c == " "
        )

        tokens = [c for c in clean_text if c != " "]
        if not tokens:
            return "", "", None, None, None, None, None

        # Analyze from tail to head
        # Find the last base Arabic consonant
        letters_only = [c for c in clean_text if c in LETTERS_SET]
        if not letters_only:
            return "", "", None, None, None, None, None

        rawi = ""
        rawi_haraka = ""
        wasl: str | None = None
        khuruj: str | None = None
        ridf: str | None = None
        tasees: str | None = None
        dakhil: str | None = None

        last_letter = letters_only[-1]
        second_last_letter = letters_only[-2] if len(letters_only) >= 2 else ""
        third_last_letter = letters_only[-3] if len(letters_only) >= 3 else ""

        # Check if last letter is an elongation letter (Alif, Waw, Yeh) or Haa of Wasl
        if last_letter in (ALEF, ALEF_MAKSURA, WAW, YEH):
            wasl = last_letter
            rawi = second_last_letter
            # Check for Ridf before Rawi
            if third_last_letter in (ALEF, ALEF_MAKSURA, WAW, YEH):
                ridf = third_last_letter
            elif len(letters_only) >= 4 and letters_only[-4] == ALEF:
                tasees = ALEF
                dakhil = third_last_letter

        elif last_letter == HAA and len(letters_only) >= 2:
            # Haa can be Rawi (if root letter like وجه) or Wasl (if pronoun like كتابه)
            wasl = HAA
            rawi = second_last_letter
            if third_last_letter in (ALEF, WAW, YEH):
                ridf = third_last_letter
            elif len(letters_only) >= 4 and letters_only[-4] == ALEF:
                tasees = ALEF
                dakhil = third_last_letter

        elif last_letter == NOON and any(c in TANWEEN_SET for c in original_text[-4:]):
            # Trailing Noon from Tanween
            rawi = second_last_letter
        else:
            rawi = last_letter
            if second_last_letter in (ALEF, WAW, YEH):
                ridf = second_last_letter
            elif len(letters_only) >= 3 and letters_only[-3] == ALEF:
                tasees = ALEF
                dakhil = second_last_letter

        # Determine Rawi Haraka
        if rawi:
            idx = clean_text.rfind(rawi)
            if idx != -1 and idx + 1 < len(clean_text):
                next_c = clean_text[idx + 1]
                if next_c in HARAKAT_SET or next_c in TANWEEN_SET:
                    if next_c in (FATHA, FATHATAN):
                        rawi_haraka = "fatha"
                    elif next_c in (DAMMA, DAMMATAN):
                        rawi_haraka = "damma"
                    elif next_c in (KASRA, KASRATAN):
                        rawi_haraka = "kasra"
                elif next_c == SUKUN:
                    rawi_haraka = "sukun"

        return rawi, rawi_haraka, wasl, khuruj, ridf, tasees, dakhil
