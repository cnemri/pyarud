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
            "طه": "طَاهَ" + FATHA,
            "لله": "لِللَاهِ",
            "آه": "أَاهِ",
            "هو": "هْوَ",
            "هي": "هْيَ",
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

    def _normalize_orthography(self, text):
        # Normalize Dagger Alif (Superscript Alif) to standard Alif
        text = text.replace("\u0670", ALEF)
        
        # Remove Harakat from standard Alif (ALEF cannot carry vowel unless it's Hamza)
        # This fixes cases where text has L+A+Fatha (treated as L+A(mover))
        harakat_pattern = f"[{FATHA}{DAMMA}{KASRA}]"
        text = re.sub(f"{ALEF}{harakat_pattern}", ALEF, text)
        
        # Normalize Alif + Tanween Fath -> Tanween Fath + Alif
        # (Ensures consistent processing order)
        text = re.sub(f"{ALEF}{FATHATAN}", f"{FATHATAN}{ALEF}", text)
        
        return text

    def _normalize_ligatures(self, text):
        # Decompose Lam-Alif ligatures with potential diacritics
        # Matches Ligature + Optional Haraka
        # Replaces with Lam + Optional Haraka + Second Letter
        
        harakat_pattern = f"[{''.join(self.harakat + self.tnween_chars)}]"
        
        def replace_la(match):
            # match.group(0) is the ligature + optional haraka
            # We want L + haraka (if any) + A
            s = match.group(0)
            haraka = s[1:] if len(s) > 1 else ""
            return "ل" + haraka + "ا"

        def replace_la_hamza_above(match):
            s = match.group(0)
            haraka = s[1:] if len(s) > 1 else ""
            return "ل" + haraka + "أ"

        def replace_la_hamza_below(match):
            s = match.group(0)
            haraka = s[1:] if len(s) > 1 else ""
            return "ل" + haraka + "إ"

        def replace_la_madda(match):
            s = match.group(0)
            haraka = s[1:] if len(s) > 1 else ""
            return "ل" + haraka + "آ"

        text = re.sub(f"ﻻ({harakat_pattern})?", replace_la, text)
        text = re.sub(f"ﻷ({harakat_pattern})?", replace_la_hamza_above, text)
        text = re.sub(f"ﻹ({harakat_pattern})?", replace_la_hamza_below, text)
        text = re.sub(f"ﻵ({harakat_pattern})?", replace_la_madda, text)
        
        return text

    def _resolve_wasl(self, text):
        """
        Handles Hamzat al-Wasl (Connecting Alif) and Iltiqa al-Sakinayn.
        1. Drop Long Vowel + Space + Alif Wasl (e.g. "Idhā Ishtadda" -> "Idhshtadda").
        2. Drop Space + Alif Wasl (e.g. "Bika Al-" -> "Bikal-").
        """
        # Pattern: Letter + (Optional Diacritic) + (Long Vowel) + Space + Alif -> Letter + Diacritic
        # The original regex was flawed because it did not capture the diacritic.
        # This version captures the letter and its optional diacritic, preserving it.
        # Using S* to handle multiple diacritics (e.g., shadda + fatha).
        text = re.sub(r"([^\s]\S*)([اىيو])\s+ا", r"\1", text)
        
        # Pattern: Space + Alif (Wasl) -> Drop both
        # Matches any word starting with bare Alif preceded by space.
        text = re.sub(r"\s+ا", "", text)

        # 3. Drop Alif of "Allah" if prefixed by Fa/Wa/Ba/Ta/Kaf
        # Pattern: (Prefix)(Vowel?)Alif(LamLam) -> (Prefix)(Vowel?)LamLam
        prefixes = "\u0641\u0648\u0628\u062a\u0643"
        harakat = "".join(self.harakat)
        text = re.sub(f"([{prefixes}])([{harakat}]?)ا(لل)", r"\1\2\3", text)

        return text

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

        # Detach prefixes to handle Al- logic (WaAl -> Wa Al)
        # Matches: Fa, Waw, Ba, Ta, Kaf followed by Al, at start of word
        bait = re.sub(r"(^|\s)([فوبتك])([َُِ])?ال", r"\1\2\3 ال", bait)

        # Solar Lam Handling: Al + Sun Letter -> A + Sun Letter
        # Drops the Lam which is silent in Solar cases
        sun_letters = "تثدذرزسشصضطظلن"
        bait = re.sub(f" ال([{sun_letters}])", r" ا\1", bait)

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

        # Word replacements from CHANGE_LST
        out = []
        valid_prefixes = ["و", "ف", "ك", "ب", "ل", "وب", "فك", "ول", "فل"]
        
        # Prepare regex for stripping harakat but keeping shadda
        # Exclude SHADDA from removal list
        removable_chars = self.harakat + self.sukun + self.tnween_chars
        strip_harakat_pattern = f"[{''.join(removable_chars)}]"

        for word in bait.split(" "):
            # 1. Try match with Shadda preserved (e.g. for 'لكنّ')
            cleaned_with_shadda = re.sub(strip_harakat_pattern, "", word)
            # 2. Try match with Shadda removed (standard)
            cleaned_plain = strip_tashkeel(word)
            
            found = False
            
            # Check Exact Match (Shadda first, then Plain)
            for candidate in [cleaned_with_shadda, cleaned_plain]:
                if candidate in self.CHANGE_LST:
                    out.append(self.CHANGE_LST[candidate])
                    found = True
                    break
            if found: 
                continue

            # Prefix check
            # We iterate candidates again to check prefixes
            for candidate in [cleaned_with_shadda, cleaned_plain]:
                if found:
                    break
                for key, replacement in self.CHANGE_LST.items():
                    if candidate.endswith(key):
                        prefix = candidate[:-len(key)]
                        if prefix in valid_prefixes:
                            prefix_harakat = {
                                "و": "وَ", "ف": "فَ", "ك": "كَ", "ب": "بِ", "ل": "لِ"
                            }
                            
                            # Construct new word
                            new_prefix = ""
                            for p_char in prefix:
                                new_prefix += prefix_harakat.get(p_char, p_char) 
                                
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

    def _extract_pattern(self, text, saturate=True, muqayyad=False):
        """
        Core logic to extract binary pattern and arudi text.
        Based on Bohour's extract_tf3eelav3.
        """
        text = self._remove_extra_harakat(text)
        chars = list(text.replace(ALEF_MADDA, "ءَا").strip())  # Replace Madda
        chars = [c for c in chars if c in self.prem_chars]
        chars = list(re.sub(" +", " ", "".join(chars).strip()))
        
        # DEBUG
        # print(f"Trace: {chars}")
        
        out_pattern = ""
        plain_chars = ""

        i = 0
        while i < len(chars) - 1:
            char = chars[i]
            next_char = chars[i + 1]
            # print(f"i={i}, char={char}, next={next_char}")

            if char in self.all_chars:
                if char == " ":
                    plain_chars += char
                    i += 1
                    continue

                # Lookahead
                if next_char == " " and i + 2 < len(chars):
                    next_char = chars[i + 2]

                next_next_char = None
                if i < len(chars) - 2:
                    next_next_char = chars[i + 2]

                prev_digit = out_pattern[-1] if len(out_pattern) > 0 else ""

                # Logic
                if next_char in self.harakat:
                    # Check for Muqayyad (Restricted Rhyme) at the very end
                    # If we are at the last character group (char + haraka is end of string)
                    is_last_group = (i + 2 >= len(chars))
                    # Or if followed by space then end? (Arudi usually strips trailing spaces but let's be safe)
                    
                    if muqayyad and is_last_group:
                        # Treat as Sakin (drop vowel)
                        if prev_digit != "0":
                            out_pattern += "0"
                            plain_chars += char
                        else:
                            # If prev was Sakin, we have Iltiqa Sakinayn at end.
                            # In Muqayyad rhyme, this is allowed (e.g. 'Mard').
                            # But typically we avoid 00. 
                            # Standard Arudi: 00 is allowed at end (Waqf).
                            out_pattern += "0"
                            plain_chars += char
                        # Skip the haraka
                    else:
                        out_pattern += "1"
                        plain_chars += char

                elif next_char in self.sukun:
                    if prev_digit != "0":
                        out_pattern += "0"
                        plain_chars += char
                    elif (i + 1) == len(chars) - 1:
                        # End of line sukun handling: Allow consecutive Sukun (00)
                        out_pattern += "0"
                        plain_chars += char
                    else:
                        plain_chars = self._handle_space(plain_chars) + char

                elif next_char in self.tnween_chars:
                    if char != "ا":
                        plain_chars += char
                    plain_chars += "ن"
                    out_pattern += "10"

                    # Skip trailing Alif (Tanween Fath)
                    if i + 2 < len(chars) and chars[i + 2] == "ا":
                        i += 1

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
                            # Check Muqayyad for Shadda+Harakah at end?
                            # Example: "Radd" (R + Shadda).
                            # If "Raddu" -> R(0) R(1).
                            # If Muqayyad "Radd" -> R(0) R(0).
                            is_last_shadda_group = (i + 3 >= len(chars))
                            if muqayyad and is_last_shadda_group:
                                # We already added '01' or '1'. The '1' corresponds to the second letter being Mover.
                                # If Muqayyad, the second letter should be Sakin.
                                # So '01' -> '00'. '1' -> '0'.
                                # We need to fix the last digit added.
                                out_pattern = out_pattern[:-1] + "0"
                                # Skip the harakah
                                i += 1
                            else:
                                i += 1  # Skip harakat processing next loop
                        elif chars[i + 2] in self.tnween_chars:
                            i += 1
                            plain_chars += "ن"
                            out_pattern += "0"

                            # Skip trailing Alif (Shadda + Tanween Fath)
                            if i + 2 < len(chars) and chars[i + 2] == "ا":
                                i += 1

                elif next_char in [ALEF, ALEF_MAKSURA]:
                    out_pattern += "10"
                    plain_chars += char + next_char

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
                        out_pattern += "0"
                    i -= 1  # Backtrack? This logic in Bohour is tricky.
                    # If we assumed it was a letter but it's followed by a letter, we treat current as sakin.
                    # The i -= 1 might be to re-process? No, i += 2 at end.

                # Ha' al-Gha'ib (He) handling
                # Only saturate if previous letter was Mutaharrik (prev_digit != "0")
                # And NOT muqayyad (if muqayyad, we don't saturate)
                if not muqayyad and next_next_char == " " and prev_digit != "0":
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
        # If Muqayyad, we don't saturate.
        # If Not Muqayyad, we saturate.
        
        if not muqayyad and saturate and out_pattern and out_pattern[-1] != "0":
            out_pattern += "0"  # Always end with sukun (Qafiyah)

        # Ashba' (Saturation) of last letter
        # Only if not muqayyad
        if not muqayyad and saturate and chars:
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

    def prepare_text(self, text, saturate=True, muqayyad=False):
        """
        Converts standard Arabic text into Arudi style and extracts the binary pattern.
        """
        text = text.strip()
        if not text:
            return "", ""

        # print(f"Original: {text}")
        text = self._normalize_orthography(text)
        # print(f"Norm Ortho: {text}")
        text = self._normalize_ligatures(text)
        text = self._normalize_shadda(text)
        preprocessed = self._process_specials_before(text)
        # print(f"Specials Before: {preprocessed}")
        preprocessed = self._resolve_wasl(preprocessed)
        # print(f"Resolve Wasl: {preprocessed}")
        arudi_style, pattern = self._extract_pattern(preprocessed, saturate=saturate, muqayyad=muqayyad)
        arudi_style = self._process_specials_after(arudi_style)

        return arudi_style, pattern
