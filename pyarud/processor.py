from collections import Counter
from difflib import SequenceMatcher

from .arudi import ArudiConverter
from .bahr import get_all_meters


class ArudhProcessor:
    def __init__(self):
        self.converter = ArudiConverter()
        self.meter_classes = get_all_meters()
        self.precomputed_patterns = {}
        self._precompute_patterns()

    def _precompute_patterns(self):
        """
        Generates all valid binary patterns for each meter using the new object-oriented engine.
        """
        for name, bahr_cls in self.meter_classes.items():
            bahr_instance = bahr_cls()
            # bait_combinations returns full binary strings of valid forms
            self.precomputed_patterns[name] = bahr_instance.bait_combinations

    def _get_similarity(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def process_poem(self, verses):
        detected_counts = Counter()
        temp_results = []

        # 1. Detect Meter
        for i, (sadr, ajuz) in enumerate(verses):
            # Convert text to pattern
            sadr_arudi, sadr_pattern = self.converter.prepare_text(sadr)
            ajuz_arudi, ajuz_pattern = self.converter.prepare_text(ajuz)
            full_pattern = sadr_pattern + ajuz_pattern

            best_match = self._find_best_match(full_pattern)
            if best_match:
                detected_counts[best_match["meter"]] += 1

            temp_results.append(
                {
                    "index": i,
                    "text_pattern": full_pattern,
                    "sadr": {"text": sadr, "pattern": sadr_pattern, "arudi": sadr_arudi},
                    "ajuz": {"text": ajuz, "pattern": ajuz_pattern, "arudi": ajuz_arudi},
                    "match": best_match,
                }
            )

        if not detected_counts:
            return {"error": "Could not detect any valid meter."}

        global_meter = detected_counts.most_common(1)[0][0]

        # 2. Analyze
        final_analysis = []
        for res in temp_results:
            # Analyze against global meter
            analysis = self._analyze_against_meter(res, global_meter)
            final_analysis.append(analysis)

        return {"meter": global_meter, "verses": final_analysis}

    def _find_best_match(self, input_pattern):
        # Priority map to resolve ambiguities (Higher is better)
        # e.g., Rajaz (Mustaf'ilun) is preferred over Kamil (Mutaf'ilun + Idmar)
        METER_PRIORITY = {
            "rajaz": 20,
            "kamel": 10,
            "hazaj": 20,
            "wafer": 10,
            "saree": 20,
            "baseet": 10,
            "ramal": 15,
            "mutadarak": 15,
            "mutakareb": 15,
        }

        best_score = -1
        candidates = []

        for name, patterns in self.precomputed_patterns.items():
            # Check against all valid variations for this meter
            for ref_pattern in patterns:
                score = self._get_similarity(ref_pattern, input_pattern)

                if score > best_score:
                    best_score = score
                    candidates = [{"meter": name, "score": score, "ref_pattern": ref_pattern}]
                elif score == best_score and score > 0:
                    candidates.append({"meter": name, "score": score, "ref_pattern": ref_pattern})

        if not candidates:
            return None

        # Sort candidates:
        # 1. By Score (Descending) - already handled by logic above essentially, but good for safety
        # 2. By Priority (Descending)
        # 3. By Meter Name (Alphabetical) - for deterministic results on total ties

        candidates.sort(key=lambda x: (x["score"], METER_PRIORITY.get(x["meter"], 0), x["meter"]), reverse=True)

        return candidates[0]

    def _analyze_against_meter(self, res, meter_name):
        patterns = self.precomputed_patterns.get(meter_name, [])
        input_pattern = res["text_pattern"]

        best_ref = None
        best_score = -1

        for p in patterns:
            score = self._get_similarity(p, input_pattern)
            if score > best_score:
                best_score = score
                best_ref = p

        # Split best_ref back into Sadr/Ajuz for display if possible
        # This is tricky without knowing the exact cut.
        # Assumption: best_ref length proportional to input split?
        # Simple approach: just show mismatch on full line

        return {
            "verse_index": res["index"],
            "sadr_text": res["sadr"]["text"],
            "ajuz_text": res["ajuz"]["text"],
            "input_pattern": input_pattern,
            "best_ref_pattern": best_ref,
            "score": round(best_score, 2),
            # Detailed tafeela breakdown would require mapping back the pattern to the Tafeela objects
        }
