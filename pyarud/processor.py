from collections import Counter
from difflib import SequenceMatcher

from .arudi import ArudiConverter
from .bahr import get_all_meters


class ArudhProcessor:
    """
    The main engine for Arabic prosody analysis.

    This class handles:
    1. Converting Arabic text to Arudi writing (phonetic representation).
    2. Converting Arudi text to binary patterns (1s and 0s).
    3. Detecting the poetic meter (Bahr) from a list of meters.
    4. Performing granular, foot-by-foot analysis to identify defects (Zihaf/Ellah).
    """
    def __init__(self):
        self.converter = ArudiConverter()
        self.meter_classes = get_all_meters()
        self.precomputed_patterns = {}
        self._precompute_patterns()

    def _precompute_patterns(self):
        """
        Generates structured valid patterns for each meter using the detailed_patterns engine.
        """
        for name, bahr_cls in self.meter_classes.items():
            bahr_instance = bahr_cls()
            # detailed_patterns returns {'sadr': [...], 'ajuz': [...], 'pairs': set()}
            self.precomputed_patterns[name] = bahr_instance.detailed_patterns

    def _get_similarity(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def process_poem(self, verses, meter_name=None):
        """
        Analyzes a list of verses to detect the meter and evaluate prosodic correctness.

        Args:
            verses (list[tuple[str, str]]): A list of tuples, where each tuple contains
                the Sadr (first hemistich) and Ajuz (second hemistich) of a verse.
            meter_name (str, optional): The name of a specific meter to force the analysis against.
                If provided, auto-detection is skipped. Defaults to None.

        Returns:
            dict: A dictionary containing:
                - `meter` (str): The name of the detected or forced meter.
                - `verses` (list[dict]): A list of analysis results for each verse, including:
                    - `score` (float): Compatibility score (0.0 - 1.0).
                    - `sadr_analysis` (list[dict]): Detailed foot-by-foot analysis of the Sadr.
                    - `ajuz_analysis` (list[dict]): Detailed foot-by-foot analysis of the Ajuz.
        """
        detected_counts = Counter()
        temp_results = []

        # 1. Detect Meter for each verse (if not forced)
        for i, (sadr, ajuz) in enumerate(verses):
            # Convert text to pattern
            sadr_arudi, sadr_pattern = self.converter.prepare_text(sadr)
            ajuz_arudi, ajuz_pattern = self.converter.prepare_text(ajuz)
            
            # Handle single shatr input if needed (future proofing)
            if not ajuz:
                ajuz_pattern = ""

            match_info = None
            if not meter_name:
                # Auto-detect
                best_match = self._find_best_meter(sadr_pattern, ajuz_pattern)
                if best_match:
                    detected_counts[best_match["meter"]] += 1
                    match_info = best_match
            else:
                # Forced meter - no detection step needed here, 
                # but we might want to store a dummy match object or just skip to analysis
                pass
            
            temp_results.append(
                {
                    "index": i,
                    "sadr": {"text": sadr, "pattern": sadr_pattern, "arudi": sadr_arudi},
                    "ajuz": {"text": ajuz, "pattern": ajuz_pattern, "arudi": ajuz_arudi},
                    "match": match_info,
                }
            )

        if meter_name:
            global_meter = meter_name
        elif detected_counts:
            global_meter = detected_counts.most_common(1)[0][0]
        else:
            return {"error": "Could not detect any valid meter."}

        # 2. Analyze against Global Meter
        final_analysis = []
        for res in temp_results:
            analysis = self._analyze_verse(res, global_meter)
            final_analysis.append(analysis)

        return {"meter": global_meter, "verses": final_analysis}

    def _find_best_meter(self, sadr_pattern, ajuz_pattern):
        METER_PRIORITY = {
            "rajaz": 20,
            "kamel": 10,
            "hazaj": 20,
            "wafer": 10,
            "saree": 20,
            "munsareh": 10,
            "baseet": 10,
            "ramal": 15,
            "mutadarak": 15,
            "mutakareb": 15,
        }

        candidates = []

        for name, patterns in self.precomputed_patterns.items():
            # 1. Score Sadr
            best_sadr = self._find_best_component_match(sadr_pattern, patterns["sadr"])
            
            # 2. Score Ajuz (if exists)
            best_ajuz = None
            if ajuz_pattern:
                best_ajuz = self._find_best_component_match(ajuz_pattern, patterns["ajuz"])
            
            # 3. Calculate Combined Score
            # If single shatr meter, ajuz score is irrelevant (or 0)
            s_score = best_sadr["score"]
            a_score = best_ajuz["score"] if best_ajuz else 0
            
            # Compatibility Check
            is_valid_pair = False
            if best_sadr["ref"] and (not ajuz_pattern or best_ajuz["ref"]):
                s_pat = best_sadr["ref"]["pattern"]
                a_pat = best_ajuz["ref"]["pattern"] if best_ajuz else ""
                if (s_pat, a_pat) in patterns["pairs"]:
                    is_valid_pair = True
            
            # Weighted score? Or Average?
            if ajuz_pattern:
                total_score = (s_score + a_score) / 2
            else:
                total_score = s_score

            candidates.append({
                "meter": name,
                "score": total_score,
                "sadr_match": best_sadr,
                "ajuz_match": best_ajuz,
                "valid_pair": is_valid_pair
            })

        # Sort candidates
        # Priority: Score -> Validity -> Priority Map
        candidates.sort(key=lambda x: (
            round(x["score"], 3),
            x["valid_pair"],
            METER_PRIORITY.get(x["meter"], 0)
        ), reverse=True)

        if not candidates:
            return None
            
        return candidates[0]

    def _find_best_component_match(self, input_pattern, component_patterns):
        best_score = -1
        best_ref = None
        
        for item in component_patterns:
            ref_pat = item["pattern"]
            score = self._get_similarity(ref_pat, input_pattern)
            if score > best_score:
                best_score = score
                best_ref = item
        
        return {"score": best_score, "ref": best_ref}

    def _analyze_verse(self, res, meter_name):
        # Re-run match against specific meter to get details
        patterns = self.precomputed_patterns.get(meter_name)
        if not patterns:
            return {"error": "Meter data not found"}

        sadr_match = self._find_best_component_match(res["sadr"]["pattern"], patterns["sadr"])
        ajuz_match = None
        if res["ajuz"]["pattern"]:
            ajuz_match = self._find_best_component_match(res["ajuz"]["pattern"], patterns["ajuz"])

        # Get allowed feet for this meter for greedy analysis
        bahr_cls = self.meter_classes.get(meter_name)
        allowed_sadr = []
        allowed_ajuz = []
        if bahr_cls:
            inst = bahr_cls()
            allowed_sadr = inst.get_allowed_feet_patterns(0)
            allowed_ajuz = inst.get_allowed_feet_patterns(1)

        # Analyze Sadr Feet
        sadr_analysis = self._analyze_feet(res["sadr"]["pattern"], allowed_sadr, sadr_match["ref"])
        
        ajuz_analysis = None
        if res["ajuz"]["pattern"]:
            ajuz_analysis = self._analyze_feet(res["ajuz"]["pattern"], allowed_ajuz, ajuz_match["ref"])

        return {
            "verse_index": res["index"],
            "sadr_text": res["sadr"]["text"],
            "ajuz_text": res["ajuz"]["text"],
            "input_pattern": res["sadr"]["pattern"] + res["ajuz"]["pattern"],
            "best_ref_pattern": (sadr_match["ref"]["pattern"] if sadr_match["ref"] else "") + 
                                (ajuz_match["ref"]["pattern"] if ajuz_match and ajuz_match["ref"] else ""),
            "score": round(
                (sadr_match["score"] + (ajuz_match["score"] if ajuz_match else 0)) / (2 if ajuz_match else 1), 2
            ),
            "sadr_analysis": sadr_analysis,
            "ajuz_analysis": ajuz_analysis
        }

    def _analyze_feet(self, input_pattern, allowed_feet_list, best_ref):
        """
        Maps input bits to feet using greedy matching against ALLOWED forms.
        This prevents one broken foot from misaligning the rest if they are valid.
        """
        analysis = []
        current_idx = 0
        
        # Fallback to best_ref feet if allowed_feet_list is not provided (should not happen)
        ref_feet_backup = best_ref["feet"] if best_ref else []

        # Determine number of feet to analyze
        num_feet = len(allowed_feet_list) if allowed_feet_list else len(ref_feet_backup)
        
        for i in range(num_feet):
            # 1. Get valid candidates for this foot position
            if allowed_feet_list:
                candidates = allowed_feet_list[i]
            elif i < len(ref_feet_backup):
                candidates = [ref_feet_backup[i]]
            else:
                candidates = []
            
            # Sort candidates by length descending to try longest match first
            candidates = sorted(candidates, key=len, reverse=True)
            
            best_local_match = None
            best_local_score = -1
            
            # Try to find best fit at current_idx
            # We look ahead by len(cand)
            for cand in candidates:
                cand_len = len(cand)
                # Get segment of equal length (or truncated if at end)
                segment = input_pattern[current_idx : current_idx + cand_len]
                
                if not segment:
                    break  # No more input
                
                score = self._get_similarity(cand, segment)
                
                # Boost score if lengths match (to prefer aligning valid feet)
                if len(segment) == cand_len:
                    if score == 1.0:
                        # Found perfect match, take it immediately
                        best_local_match = cand
                        best_local_score = 1.0
                        break
                
                if score > best_local_score:
                    best_local_score = score
                    best_local_match = cand
                    # Consume what we compared against

            # If no candidates (e.g., error in definitions), break
            if not best_local_match and candidates:
                best_local_match = candidates[0] # Default to first/longest
            
            # If we still didn't find anything (e.g. input exhausted), skip
            if not best_local_match:
                analysis.append({
                    "foot_index": i,
                    "expected_pattern": candidates[0] if candidates else "?",
                    "actual_segment": "MISSING",
                    "score": 0.0,
                    "status": "missing"
                })
                continue

            # Extract the segment we decided to consume
            # Logic: If score is low, we should consume the length of the EXPECTED pattern 
            # to keep alignment for next feet? Or length of actual?
            # If we assume the user *tried* to write the pattern, we consume Pattern Length.
            
            consume_len = len(best_local_match)
            # Clamp to input length
            end_idx = min(current_idx + consume_len, len(input_pattern))
            actual_segment = input_pattern[current_idx : end_idx]
            
            # Recalculate score on the final decided segment
            final_score = self._get_similarity(best_local_match, actual_segment)
            
            status = "ok" if final_score == 1.0 else "broken"
            if not actual_segment:
                status = "missing"

            analysis.append({
                "foot_index": i,
                "expected_pattern": best_local_match,
                "actual_segment": actual_segment,
                "score": round(final_score, 2),
                "status": status
            })
            
            current_idx = end_idx
            
        # Check for extra bits
        if current_idx < len(input_pattern):
            extra = input_pattern[current_idx:]
            analysis.append({
                "foot_index": num_feet,
                "expected_pattern": "",
                "actual_segment": extra,
                "score": 0,
                "status": "extra_bits"
            })

        return analysis