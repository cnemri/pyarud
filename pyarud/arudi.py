import re

from pyarabic.araby import (
    ALEF,
    ALEF_MADDA,
    ALEF_MAKSURA,
    DAMMA,
    DAMMATAN,
    FATHA,
    FATHATAN,
    KASRA,
    KASRATAN,
    LETTERS,
    SHADDA,
    SUKUN,
    WAW,
    YEH,
    strip_tashkeel,
)


class ArudiConverter:
    def __init__(self):
        self.harakat = [KASRA, FATHA, DAMMA]  # kasra, fatha, damma
        self.sukun = [SUKUN]  # sukun
        self.mostly_saken = [ALEF, WAW, ALEF_MAKSURA, YEH]  # alef, waw, alef maqsurah, ya'a
        self.tnween_chars = [DAMMATAN, KASRATAN, FATHATAN]  # damm, kasra, fatha tanween
        self.shadda_chars = [SHADDA]
        self.all_chars = list(LETTERS + " ")
        self.prem_chars = (
            self.harakat + self.sukun + self.mostly_saken + self.tnween_chars + self.shadda_chars + self.all_chars
        )

        # Word replacements for Arudi writing
        self.CHANGE_LST = {
            "هذا": "هَاذَا",
            "هذه": "هَاذِه",
            "هذان": "هَاذَان",
            "هذين": "هَاذَين",
            "هؤلاء": "هَاؤُلَاء",
            "ذلك": "ذَالِك",
            "ذلكما": "ذَالِكُمَا",
            "ذلكم": "ذَالِكُم",
            "أولئك": "أُلَائِك",
            "أولئكم": "أُلَائِكُم",
            "الله": "اللَّاه",
            "اللهم": "اللَّاهُمّ",
            "إله": "إِلَاه",
            "الإله": "الإِلَاه",
            "إلهي": "إِلَاهي",
            "إلهنا": "إِلَاهنا",
            "إلهكم": "إِلَاهكم",
            "إلههم": "إِلَاههم",
            "إلههن": "إِلَاههن",
            "رحمن": "رَحمَان",
            "الرحمن": "الرَّحمَان",
            "طاوس": "طَاوُوس",
            "داود": "دَاوُود",
            "لكن": "لَاكِن",
            "لكنّ": "لَاكِنّ",
            "لكنه": "لَاكِنّهُ",
            "طه": "طَاهَا",
            "يس": "يَاسِين",
        }

    def register_custom_spelling(self, word, replacement):
        """
        Register a custom Arudi spelling for a specific word.

        Args:
            word (str): The word (without diacritics) to replace (e.g., 'لكن').
            replacement (str): The phonetic Arudi spelling (e.g., 'لَاكِن').
        """
        self.CHANGE_LST[word] = replacement

    def _normalize_shadda(self, text):
        # Ensure Shadda comes before Harakat/Tanween
        harakat_all = "".join(self.harakat + self.tnween_chars)
        shadda = "".join(self.shadda_chars)
        return re.sub(f"([{harakat_all}])([{shadda}])", r"\2\1", text)

    def _handle_space(self, plain_chars):
        if not plain_chars:
            return plain_chars

        if plain_chars[-1] == " ":
            return plain_chars[:-2]
        else:
            return plain_chars[:-1]

    def _remove_extra_harakat(self, text):
        out = ""
        i = 0
        while i < len(text):
            if i < len(text) - 1:
                if text[i] in self.harakat and text[i + 1] in self.harakat:
                    i += 1
                    continue
            out += text[i]
            i += 1
        return out

    def _process_specials_before(self, bait):
        # Handle specific starting Alif cases
        if bait and bait[0] == "ا":
            # Heuristic: randomly choose or based on context. Bohour used random.
            # We'll default to Fatha for consistency in deterministic output,
            # or Hamza with Fatha.
            bait = "أَ" + bait[1:]

        bait = bait.replace("وا ", "و ")
        if bait.endswith("وا"):
            bait = bait[:-1]

        bait = bait.replace("وْا", "و")
        if bait.endswith("وْا"):
            bait = bait[:-2] + "و"

        # Common substitutions
        bait = bait.replace("الله", "اللاه")
        bait = bait.replace("اللّه", "الله")
        bait = bait.replace("إلَّا", "إِلّا")
        bait = bait.replace("نْ ال", "نَ ال")
        bait = bait.replace("لْ ال", "لِ ال")
        bait = bait.replace("إلَى", "إِلَى")
        bait = bait.replace("إذَا", "إِذَا")
        bait = bait.replace("ك ", "كَ ")
        bait = bait.replace(" ال ", " الْ ")
        bait = bait.replace("ْ ال", "ِ ال")
        bait = bait.replace("عَمْرٍو", "عَمْرٍ")
        bait = bait.replace("عَمْرُو", "عَمْرُ")

        # Shorten long vowels before Al (Hamzat Wasl + Lam Qamariya/Shamsiya)
        # This handles "Iltiqa al-Sakinayn" (meeting of two sakins) by dropping the first long vowel
        # e.g., 'إِلَى الْ' -> 'إِلَ الْ', 'فِي الْ' -> 'فِ الْ', 'ذَا الْ' -> 'ذَ الْ'
        bait = re.sub(r"([^\s])([اىيو])\s+ال", r"\1 ال", bait)

        # Word replacements from CHANGE_LST
        out = []
        valid_prefixes = ["و", "ف", "ك", "ب", "ل", "وب", "فك", "ول", "فل"]
        
        for word in bait.split(" "):
            cleaned_word = strip_tashkeel(word)
            found = False
            
            # 1. Exact match check
            for key, replacement in self.CHANGE_LST.items():
                if cleaned_word == key:
                    out.append(replacement)
                    found = True
                    break
            
            # 2. Prefix check if not found
            if not found:
                for key, replacement in self.CHANGE_LST.items():
                    if cleaned_word.endswith(key):
                        prefix = cleaned_word[:-len(key)]
                        if prefix in valid_prefixes:
                            # We found a prefixed match.
                            # We need to reconstruct the word with the original prefix's diacritics
                            # This is tricky because 'word' has diacritics intermixed.
                            # Simple heuristic: Take the original word string up to the match?
                            # No, diacritics make length differ.
                            # Better: Just prepend the prefix chars? 
                            # "وَهَذَا" -> prefix "وَ" ? 
                            # We know cleaned prefix is "و".
                            # Let's try to find where the key starts in the original word.
                            
                            # Find the index of the key's first char in the original word (last occurrence)
                            # ... This assumes standard orthography.
                            
                            # Simplest robust approach for Arudi:
                            # Just use the cleaned prefix + replacement?
                            # "وهذا" -> "و" + "هَاذَا" -> "وهَاذَا"
                            # But we lose the prefix's original harakat (e.g. "وَ").
                            # Ideally we want "وَ" + "هَاذَا".
                            
                            # Hack: Since prefixes are usually 1-2 chars, we can assume they are at the start.
                            # But we don't know their length in the original string (due to harakat).
                            
                            # Alternative: Use regex to find the suffix in the original word?
                            # Or just use the predefined "cleaned prefix" + standard haraka?
                            # "و" -> "وَ" (Fatha usually). "ب" -> "بِ" (Kasra). "ل" -> "لِ" (Kasra).
                            # "ك" -> "كَ" (Fatha). "ف" -> "فَ" (Fatha).
                            
                            prefix_harakat = {
                                "و": "وَ", "ف": "فَ", "ك": "كَ", "ب": "بِ", "ل": "لِ"
                            }
                            
                            # Construct new word
                            new_prefix = ""
                            for p_char in prefix:
                                new_prefix += prefix_harakat.get(p_char, p_char) # Default to char if no mapping
                                
                            out.append(new_prefix + replacement)
                            found = True
                            break
            
            if not found:
                out.append(word)

        bait = " ".join(out)

        # Ensure second char isn't a bare letter if first is
        if len(bait) > 1 and bait[1] in self.all_chars:
            bait = bait[0] + self.harakat[1] + bait[1:]

        # Filter trailing alif after tanween
        final_chars = []
        i = 0
        while i < len(bait):
            if bait[i] == "ا" and i > 0 and bait[i - 1] in self.tnween_chars:
                i += 1
                # skip following harakat if any
                if i < len(bait) and bait[i] in self.harakat + self.sukun + self.tnween_chars + self.shadda_chars:
                    i += 1
                continue
            final_chars.append(bait[i])
            i += 1

        return "".join(final_chars)

    def _process_specials_after(self, bait):
        bait = bait.replace("ةن", "تن")
        return bait

    def _extract_pattern(self, text):
        """
        Core logic to extract binary pattern and arudi text.
        Based on Bohour's extract_tf3eelav3.
        """
        text = self._remove_extra_harakat(text)
        chars = list(text.replace(ALEF_MADDA, "ءَا").strip())  # Replace Madda
        chars = [c for c in chars if c in self.prem_chars]
        chars = list(re.sub(" +", " ", "".join(chars).strip()))

        out_pattern = ""
        plain_chars = ""

        i = 0
        while i < len(chars) - 1:
            char = chars[i]

            if char in self.all_chars:
                if char == " ":
                    plain_chars += char
                    i += 1
                    continue

                # Lookahead
                next_char = chars[i + 1]
                if next_char == " " and i + 2 < len(chars):
                    next_char = chars[i + 2]

                next_next_char = None
                if i < len(chars) - 2:
                    next_next_char = chars[i + 2]

                prev_digit = out_pattern[-1] if len(out_pattern) > 0 else ""

                # Logic
                if next_char in self.harakat:
                    out_pattern += "1"
                    plain_chars += char

                elif next_char in self.sukun:
                    if prev_digit != "0":
                        out_pattern += "0"
                        plain_chars += char
                    elif (i + 1) == len(chars) - 1:
                        # End of line sukun handling
                        out_pattern = out_pattern[:-1] + "10"
                        plain_chars += char
                    else:
                        plain_chars = self._handle_space(plain_chars) + char

                elif next_char in self.tnween_chars:
                    if char != "ا":
                        plain_chars += char
                    plain_chars += "ن"
                    out_pattern += "10"

                elif next_char in self.shadda_chars:
                    if prev_digit != "0":
                        plain_chars += char + char
                        out_pattern += "01"
                    else:
                        plain_chars = self._handle_space(plain_chars) + char + char
                        out_pattern += "1"

                    # Check what follows Shadda
                    if i + 2 < len(chars):
                        if chars[i + 2] in self.harakat:
                            i += 1  # Skip harakat processing next loop (handled here implicitly?)
                            # Actually Bohour logic just increments i to skip processing the harakah as separate char?
                            # But we added '1' for the second letter of shadda.
                            pass
                        elif chars[i + 2] in self.tnween_chars:
                            i += 1
                            plain_chars += "ن"
                            out_pattern += "0"  # Shadda(1) + Tanween(0) -> 10. Wait. Shadda is 01.
                            # If Shadda + Tanween:
                            # Letter + Shadda + Tanween
                            # 1. Letter Sakin (0)
                            # 2. Letter Mutaharrik (1)
                            # 3. Tanween (0)
                            # Result should be 010.
                            # Above logic adds 01, then adds 0. Correct.

                elif next_char == "ا":
                    out_pattern += "10"
                    plain_chars += char + "ا"

                elif next_char in self.all_chars:
                    # Letter followed by Letter (implies first is Sakin if no haraka in betweeen?)
                    # Or assumes implicit sukun?
                    if prev_digit != "0":
                        out_pattern += "0"
                        plain_chars += char
                    elif prev_digit == "0" and i + 1 < len(chars) and chars[i + 1] == " ":
                        # Special case from Bohour
                        out_pattern += "1"
                        plain_chars += char
                    else:
                        plain_chars = self._handle_space(plain_chars) + char
                    i -= 1  # Backtrack? This logic in Bohour is tricky.
                    # If we assumed it was a letter but it's followed by a letter, we treat current as sakin.
                    # The i -= 1 might be to re-process? No, i += 2 at end.

                # Ha' al-Gha'ib (He) handling
                if next_next_char == " ":
                    if char == "ه":
                        if next_char == self.harakat[0]:  # Kasra
                            plain_chars += "ي"
                            out_pattern += "0"
                        if next_char == self.harakat[2]:  # Damma
                            plain_chars += "و"
                            out_pattern += "0"

                i += 2  # Advance past char and its diacritic/follower
            elif char == "ا":
                # Alef encountered as 'char' (e.g. after a diacritic consumed the previous letter)
                out_pattern += "0"
                plain_chars += char
                i += 1
            else:
                i += 1

        # Finalize
        if out_pattern and out_pattern[-1] != "0":
            out_pattern += "0"  # Always end with sukun (Qafiyah)

        # Ashba' (Saturation) of last letter
        if chars:
            last_char = chars[-1]
            if last_char == self.harakat[0]:  # Kasra
                plain_chars += "ي"
            elif last_char == self.tnween_chars[1]:  # Kasr Tanween
                plain_chars = plain_chars[:-1] + "ي"
            elif last_char == self.harakat[1]:  # Fatha
                plain_chars += "ا"
            elif last_char == self.harakat[2]:  # Damma
                plain_chars += "و"
            elif last_char == self.tnween_chars[0]:  # Damm Tanween
                plain_chars = plain_chars[:-1] + "و"
            elif last_char in self.mostly_saken and len(chars) > 1 and chars[-2] not in self.tnween_chars:
                plain_chars += last_char

        return plain_chars, out_pattern

    def prepare_text(self, text):
        """
        Converts standard Arabic text into Arudi style and extracts the binary pattern.

        Args:
            text (str): The input Arabic text (hemistich or line).

        Returns:
            tuple[str, str]: A tuple containing:
                - `arudi_style` (str): The phonetic Arudi representation (e.g., "مُسْتَفْعِلُنْ").
                - `pattern` (str): The binary pattern string (e.g., "1010110").
        """
        text = text.strip()
        if not text:
            return "", ""

        text = self._normalize_shadda(text)
        preprocessed = self._process_specials_before(text)
        arudi_style, pattern = self._extract_pattern(preprocessed)
        arudi_style = self._process_specials_after(arudi_style)

        return arudi_style, pattern
