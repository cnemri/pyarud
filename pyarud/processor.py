"""
Core Prosody Processor and Poetic Meter Detector for PyArud.

Coordinates Arudi conversion, metric pattern alignment, foot-by-foot
Zihaf/'Ilal diagnostics, and rhyme (Qafiyah) analysis.
"""

from __future__ import annotations

import math
from collections import Counter
from difflib import SequenceMatcher
from functools import lru_cache
from typing import Any

from .core.phonetics import ArudiConverter
from .meters.bahr import get_all_meters
from .meters.engine import get_deterministic_engine
from .models.analysis import (
    FootAnalysis,
    MeterMatchCandidate,
    PoemAnalysis,
    QafiyahAnalysis,
    ShatrAnalysis,
    VerseAnalysis,
)
from .qafiyah.analyzer import QafiyahAnalyzer

# Mapping of (expected_pattern, actual_pattern) to Arabic tafeela names and Zihaf diagnostics
TAFEELA_VARIATION_MAP: dict[tuple[str, str], tuple[str, str, str, str]] = {
    # Fawlon (فعولن - 11010)
    ("11010", "11010"): ("فعولن", "فعولن", "سالمة (صحيحة)", "Salim"),
    ("11010", "1101"): ("فعولن", "فعولُ", "مقبوضة (القبض)", "Qabadh"),
    ("11010", "1010"): ("فعولن", "فعلن", "أثلم (الثلم)", "Thalm"),
    ("11010", "101"): ("فعولن", "فعلُ", "أثرم (الثرم)", "Tharm"),
    ("11010", "110"): ("فعولن", "فعو / فل", "محذوفة (الحذف)", "Hadhf"),
    ("11010", "11"): ("فعولن", "فعْ", "أبتر (البتر)", "Batr"),
    ("11010", "10"): ("فعولن", "فعْ", "أبتر (البتر)", "Batr"),
    # Faelon (فاعلن - 10110)
    ("10110", "10110"): ("فاعلن", "فاعلن", "سالمة (صحيحة)", "Salim"),
    ("10110", "1110"): ("فاعلن", "فعلن", "مخبونة (الخبن)", "Khaban"),
    ("10110", "1010"): ("فاعلن", "فالن / فعلن", "مشعثة (التشعيث)", "Tasheeth"),
    ("10110", "101100"): ("فاعلن", "فاعلان", "مذيلة (التذييل)", "Tatheel"),
    ("10110", "11100"): ("فاعلن", "فعلان", "مرفلة مخبونة", "Tarfeel and Khaban"),
    ("10110", "10"): ("فاعلن", "فاعْ / فلن", "أبتر (البتر)", "Batr"),
    # Mafaeelon (مفاعيلن - 1101010)
    ("1101010", "1101010"): ("مفاعيلن", "مفاعيلن", "سالمة (صحيحة)", "Salim"),
    ("1101010", "110110"): ("مفاعيلن", "مفاعلن", "مقبوضة (القبض)", "Qabadh"),
    ("1101010", "110101"): ("مفاعيلن", "مفاعيلُ", "مكفوفة (الكف)", "Kaff"),
    ("1101010", "11010"): ("مفاعيلن", "فعولن", "محذوفة (الحذف)", "Hadhf"),
    # Mustafelon (مستفعلن - 1010110)
    ("1010110", "1010110"): ("مستفعلن", "مستفعلن", "سالمة (صحيحة)", "Salim"),
    ("1010110", "1110110"): ("مستفعلن", "مفاعلن", "مخبونة (الخبن)", "Khaban"),
    ("1010110", "101110"): ("مستفعلن", "مفتعلن", "مطوية (الطي)", "Tay"),
    ("1010110", "111110"): ("مستفعلن", "فعلتن", "مخبولة (الخبل)", "Khabal"),
    ("1010110", "101010"): ("مستفعلن", "مفعولن", "مقطوعة (القطع)", "Qataa"),
    ("1010110", "111010"): ("مستفعلن", "فعولن", "مقطوعة مخبونة", "Khaban and Qataa"),
    ("1010110", "10101100"): ("مستفعلن", "مستفعلان", "مذيلة (التذييل)", "Tatheel"),
    # Mutafaelon (متفاعلن - 1110110)
    ("1110110", "1110110"): ("متفاعلن", "متفاعلن", "سالمة (صحيحة)", "Salim"),
    ("1110110", "1010110"): ("متفاعلن", "مُتْفاعلن", "مضمرة (الإضمار)", "Edmaar"),
    ("1110110", "110110"): ("متفاعلن", "مفاعلن", "موقوصة (الوقص)", "Waqas"),
    ("1110110", "101110"): ("متفاعلن", "مُتَفْعلن", "مخزولة (الخزل)", "Khazal"),
    ("1110110", "111010"): ("متفاعلن", "متفاعلْ", "مقطوعة (القطع)", "Qataa"),
    ("1110110", "101010"): ("متفاعلن", "مُتْفاعلْ", "مقطوعة مضمرة", "Qataa and Edmaar"),
    ("1110110", "1110"): ("متفاعلن", "فعلن", "حذاء (الحذذ)", "Hathath"),
    ("1110110", "1010"): ("متفاعلن", "فعلْ", "حذاء مضمرة", "Hathath and Edmaar"),
    ("1110110", "11101100"): ("متفاعلن", "متفاعلان", "مذيلة (التذييل)", "Tatheel"),
    ("1110110", "10101100"): ("متفاعلن", "مُتْفاعلان", "مذيلة مضمرة", "Tatheel and Edmaar"),
    ("1110110", "111011010"): ("متفاعلن", "متفاعلاتن", "مرفلة (الترفيل)", "Tarfeel"),
    ("1110110", "101011010"): ("متفاعلن", "مُتْفاعلاتن", "مرفلة مضمرة", "Tarfeel and Edmaar"),
    # Mafaelaton (مفاعلتن - 1101110)
    ("1101110", "1101110"): ("مفاعلتن", "مفاعلتن", "سالمة (صحيحة)", "Salim"),
    ("1101110", "1101010"): ("مفاعلتن", "مفاعيلن", "معصوبة (العصب)", "Asab"),
    ("1101110", "110110"): ("مفاعلتن", "مفاعتن", "معقولة (العقل)", "Aql"),
    ("1101110", "110101"): ("مفاعلتن", "مفاعيلُ", "منقوصة (النقص)", "Nakas"),
    ("1101110", "11010"): ("مفاعلتن", "فعولن", "مقطوفة (القطف)", "Qataf"),
    # Mafoolato (مفعولات - 1010101)
    ("1010101", "1010101"): ("مفعولات", "مفعولاتُ", "سالمة", "Salim"),
    ("1010101", "1110101"): ("مفعولات", "مفاعيلُ", "مخبونة (الخبن)", "Khaban"),
    ("1010101", "1011101"): ("مفعولات", "مفتعلاتُ", "مطوية (الطي)", "Tay"),
    ("1010101", "1010110"): ("مفعولات", "مفعولن", "مكسوفة (الكسف)", "Kasf"),
    ("1010101", "10110"): ("مفعولات", "فاعلن", "مطوية مكسوفة", "Tay and Kasf"),
    ("1010101", "11110"): ("مفعولات", "فعلن", "مخبولة مكسوفة", "Khabal and Kasf"),
    ("1010101", "101010"): ("مفعولات", "مفعولاتْ", "موقوفة (الوقف)", "Waqf"),
    ("1010101", "101100"): ("مفعولات", "فاعلان", "موقوفة مطوية", "Waqf and Tay"),
    ("1010101", "1010"): ("مفعولات", "فعلن", "أصلم (الصلم)", "Salam"),
    # Faelaton (فاعلاتن - 1011010)
    ("1011010", "1011010"): ("فاعلاتن", "فاعلاتن", "سالمة (صحيحة)", "Salim"),
    ("1011010", "1111010"): ("فاعلاتن", "فعلاتن", "مخبونة (الخبن)", "Khaban"),
    ("1011010", "101101"): ("فاعلاتن", "فاعلاتُ", "مكفوفة (الكف)", "Kaff"),
    ("1011010", "111101"): ("فاعلاتن", "فعلاتُ", "مشكولة (الشكل)", "Shakal"),
    ("1011010", "10110"): ("فاعلاتن", "فاعلن", "محذوفة (الحذف)", "Hadhf"),
    ("1011010", "11110"): ("فاعلاتن", "فعلن", "محذوفة مخبونة", "Hadhf and Khaban"),
    ("1011010", "101100"): ("فاعلاتن", "فاعلاتان", "مسبغة (التسبيغ)", "Tasbeegh"),
    ("1011010", "1010"): ("فاعلاتن", "فاعْ / فلن", "أبتر (البتر)", "Batr"),
}

DEFAULT_PATTERN_TAFEELA: dict[str, tuple[str, str, str, str]] = {
    "11010": ("فعولن", "فعولن", "سالمة (صحيحة)", "Salim"),
    "10110": ("فاعلن", "فاعلن", "سالمة (صحيحة)", "Salim"),
    "1101010": ("مفاعيلن", "مفاعيلن", "سالمة (صحيحة)", "Salim"),
    "1010110": ("مستفعلن", "مستفعلن", "سالمة (صحيحة)", "Salim"),
    "1110110": ("متفاعلن", "متفاعلن", "سالمة (صحيحة)", "Salim"),
    "1101110": ("مفاعلتن", "مفاعلتن", "سالمة (صحيحة)", "Salim"),
    "1010101": ("مفعولات", "مفعولاتُ", "سالمة (صحيحة)", "Salim"),
    "1011010": ("فاعلاتن", "فاعلاتن", "سالمة (صحيحة)", "Salim"),
    "1101": ("فعولن", "فعولُ", "مقبوضة (القبض)", "Qabadh"),
    "1110": ("فاعلن", "فعلن", "مخبونة (الخبن)", "Khaban"),
    "110110": ("مفاعيلن", "مفاعلن", "مقبوضة (القبض)", "Qabadh"),
    "101110": ("مستفعلن", "مفتعلن", "مطوية (الطي)", "Tay"),
    "101010": ("مستفعلن", "مفعولن", "مقطوعة (القطع)", "Qataa"),
    "111010": ("متفاعلن", "متفاعلْ", "مقطوعة (القطع)", "Qataa"),
}

METER_PRIORITY: dict[str, int] = {
    "taweel": 30,
    "hazaj": 25,
    "rajaz": 25,
    "saree": 25,
    "kamel": 20,
    "baseet": 20,
    "ramal": 20,
    "khafeef": 20,
    "mutakareb": 20,
    "mutadarak": 20,
    "wafer": 10,
    "munsareh": 15,
    "madeed": 15,
    "mujtath": 10,
    "mudhare": 10,
    "muqtadheb": 10,
}


_GLOBAL_PRECOMPUTED_PATTERNS: dict[str, dict[str, Any]] | None = None
_GLOBAL_SADR_EXACT_MAPS: dict[str, dict[str, dict[str, Any]]] | None = None
_GLOBAL_AJUZ_EXACT_MAPS: dict[str, dict[str, dict[str, Any]]] | None = None


def _init_global_patterns() -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, dict[str, Any]]],
    dict[str, dict[str, dict[str, Any]]],
]:
    global _GLOBAL_PRECOMPUTED_PATTERNS, _GLOBAL_SADR_EXACT_MAPS, _GLOBAL_AJUZ_EXACT_MAPS
    if _GLOBAL_PRECOMPUTED_PATTERNS is not None:
        assert _GLOBAL_SADR_EXACT_MAPS is not None and _GLOBAL_AJUZ_EXACT_MAPS is not None
        return _GLOBAL_PRECOMPUTED_PATTERNS, _GLOBAL_SADR_EXACT_MAPS, _GLOBAL_AJUZ_EXACT_MAPS

    precomputed: dict[str, dict[str, Any]] = {}
    sadr_exact_maps: dict[str, dict[str, dict[str, Any]]] = {}
    ajuz_exact_maps: dict[str, dict[str, dict[str, Any]]] = {}

    meter_classes = get_all_meters()
    for name, bahr_cls in meter_classes.items():
        bahr_instance = bahr_cls()
        detailed = bahr_instance.detailed_patterns
        precomputed[name] = detailed

        s_map: dict[str, dict[str, Any]] = {}
        for s in detailed["sadr"]:
            s_map.setdefault(s["pattern"], s)
        sadr_exact_maps[name] = s_map

        a_map: dict[str, dict[str, Any]] = {}
        for a in detailed["ajuz"]:
            a_map.setdefault(a["pattern"], a)
        ajuz_exact_maps[name] = a_map

    _GLOBAL_PRECOMPUTED_PATTERNS = precomputed
    _GLOBAL_SADR_EXACT_MAPS = sadr_exact_maps
    _GLOBAL_AJUZ_EXACT_MAPS = ajuz_exact_maps
    return precomputed, sadr_exact_maps, ajuz_exact_maps


@lru_cache(maxsize=65536)
def _fast_similarity(a: str, b: str) -> float:
    """Calculates non-linear metric pattern similarity with LRU caching."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0

    ratio = SequenceMatcher(None, a, b).ratio()
    return math.pow(ratio, 6)


class ArudhProcessor:
    """
    Prosodic Engine for Arabic Poetry.

    Performs phonetic Arudi transcription, metric pattern extraction,
    Bahr identification, foot-by-foot Zihaf diagnostic decomposition, and rhyme analysis.
    """

    def __init__(self, custom_replacements: dict[str, str] | None = None) -> None:
        self.converter = ArudiConverter(custom_replacements=custom_replacements)
        self.qafiyah_analyzer = QafiyahAnalyzer()
        self.engine = get_deterministic_engine()
        self.meter_classes = get_all_meters()
        (
            self.precomputed_patterns,
            self._sadr_exact_maps,
            self._ajuz_exact_maps,
        ) = _init_global_patterns()

    @staticmethod
    def _get_similarity(a: str, b: str) -> float:
        return _fast_similarity(a, b)

    def analyze_verse(
        self,
        sadr_text: str,
        ajuz_text: str | None = None,
        forced_meter: str | None = None,
        verse_index: int = 0,
    ) -> VerseAnalysis:
        """
        Analyzes a single poetic verse (Sadr and optional Ajuz).

        Args:
            sadr_text (str): First hemistich (الصدر).
            ajuz_text (str): Second hemistich (العجز).
            forced_meter (str, optional): Target meter key to force analysis against.
            verse_index (int): Index of the verse in the poem.

        Returns:
            VerseAnalysis: Strongly typed dataclass containing the complete prosodic breakdown.
        """
        ajuz_text = ajuz_text or ""
        # Generate candidates for Sadr (saturated and unsaturated)
        sadr_res_sat = self.converter.prepare_text(sadr_text, saturate=True)
        sadr_res_unsat = self.converter.prepare_text(sadr_text, saturate=False)

        # Generate candidates for Ajuz (saturated/Mutlaq and unsaturated/Muqayyad)
        ajuz_res_sat = self.converter.prepare_text(ajuz_text, saturate=True) if ajuz_text else ("", "")
        ajuz_res_unsat = (
            self.converter.prepare_text(ajuz_text, saturate=False, muqayyad=True) if ajuz_text else ("", "")
        )

        sadr_candidates = [sadr_res_sat]
        if sadr_res_unsat[1] != sadr_res_sat[1]:
            sadr_candidates.append(sadr_res_unsat)

        ajuz_candidates = [ajuz_res_sat]
        if ajuz_text and ajuz_res_unsat[1] != ajuz_res_sat[1]:
            ajuz_candidates.append(ajuz_res_unsat)

        # 1. Deterministic Formal Metric Grammar Matching
        det_matches = self.engine.match_verse(
            sadr_candidates, ajuz_candidates, target_meter=forced_meter
        )
        best_det = self.engine.disambiguate_exact_matches(
            det_matches,
            sadr_candidates[0][1],
            ajuz_candidates[0][1] if ajuz_candidates else "",
        )

        if best_det is not None:
            grammar, s_deriv, a_deriv, det_score, _is_valid_pair = best_det
            meter_key = grammar.meter_key
            meter_name_ar = grammar.name_ar
            meter_name_en = grammar.name_en
            bahr_type = grammar.bahr_type

            # Find matching candidate text/pattern
            chosen_sadr = sadr_candidates[0]
            if s_deriv:
                for cand in sadr_candidates:
                    if cand[1] == s_deriv.pattern:
                        chosen_sadr = cand
                        break

            chosen_ajuz = ajuz_candidates[0] if ajuz_candidates else ("", "")
            if a_deriv and ajuz_text:
                for cand in ajuz_candidates:
                    if cand[1] == a_deriv.pattern:
                        chosen_ajuz = cand
                        break

            sadr_feet = [
                FootAnalysis(
                    foot_index=i,
                    expected_pattern=fv.pattern,
                    actual_segment=fv.pattern,
                    base_tafeela=fv.base_tafeela,
                    actual_tafeela=fv.actual_tafeela,
                    zihaf_name_ar=fv.zihaf_name_ar,
                    zihaf_name_en=fv.zihaf_name_en,
                    score=1.0,
                    status="ok",
                )
                for i, fv in enumerate(s_deriv.feet)
            ] if s_deriv else []

            ajuz_feet = [
                FootAnalysis(
                    foot_index=i,
                    expected_pattern=fv.pattern,
                    actual_segment=fv.pattern,
                    base_tafeela=fv.base_tafeela,
                    actual_tafeela=fv.actual_tafeela,
                    zihaf_name_ar=fv.zihaf_name_ar,
                    zihaf_name_en=fv.zihaf_name_en,
                    score=1.0,
                    status="ok",
                )
                for i, fv in enumerate(a_deriv.feet)
            ] if (a_deriv and ajuz_text) else None

            sadr_analysis_obj = ShatrAnalysis(
                text=sadr_text,
                arudi_text=chosen_sadr[0],
                pattern=chosen_sadr[1],
                feet=sadr_feet,
                score=1.0,
                is_valid=True,
            )

            ajuz_analysis_obj = (
                ShatrAnalysis(
                    text=ajuz_text,
                    arudi_text=chosen_ajuz[0],
                    pattern=chosen_ajuz[1],
                    feet=ajuz_feet or [],
                    score=1.0,
                    is_valid=True,
                )
                if ajuz_text
                else None
            )

            # Rhyme (Qafiyah) analysis
            qafiyah_obj: QafiyahAnalysis | None = None
            if ajuz_text:
                qafiyah_obj = self.qafiyah_analyzer.analyze(
                    ajuz_text,
                    is_muqayyad=(chosen_ajuz[1].endswith("0") and chosen_ajuz == ajuz_res_unsat),
                )

            sadr_std = " ".join(f.pattern for f in s_deriv.feet) if s_deriv else ""
            ajuz_std = (" " + " ".join(f.pattern for f in a_deriv.feet)) if a_deriv else ""
            standard_pattern = (sadr_std + ajuz_std).strip()

            return VerseAnalysis(
                verse_index=verse_index,
                sadr_text=sadr_text,
                ajuz_text=ajuz_text,
                meter_key=meter_key,
                meter_name_ar=meter_name_ar,
                meter_name_en=meter_name_en,
                bahr_type=bahr_type,
                standard_pattern=standard_pattern,
                score=round(det_score, 3),
                sadr=sadr_analysis_obj,
                ajuz=ajuz_analysis_obj,
                qafiyah=qafiyah_obj,
                is_valid=True,
                errors=[],
            )

        # 2. Diagnostic Fallback when verse is broken or irregular
        candidates = self._find_best_meter(sadr_candidates, ajuz_candidates, target_meter=forced_meter)

        if not candidates:
            # Fallback when no meter could be detected
            s_shatr = ShatrAnalysis(
                text=sadr_text,
                arudi_text=sadr_res_sat[0],
                pattern=sadr_res_sat[1],
                score=0.0,
                is_valid=False,
            )
            a_shatr = (
                ShatrAnalysis(
                    text=ajuz_text,
                    arudi_text=ajuz_res_sat[0],
                    pattern=ajuz_res_sat[1],
                    score=0.0,
                    is_valid=False,
                )
                if ajuz_text
                else None
            )
            return VerseAnalysis(
                verse_index=verse_index,
                sadr_text=sadr_text,
                ajuz_text=ajuz_text,
                meter_key="unknown",
                meter_name_ar="بحر غير محدد",
                meter_name_en="Unknown Meter",
                bahr_type="unknown",
                standard_pattern="",
                score=0.0,
                sadr=s_shatr,
                ajuz=a_shatr,
                is_valid=False,
                errors=["Could not determine poetic meter."],
            )

        best_match = candidates[0]
        meter_key = best_match.meter_key
        meter_cls = self.meter_classes.get(meter_key)

        meter_name_ar = meter_cls.name_ar if meter_cls else meter_key
        meter_name_en = meter_cls.name_en if meter_cls else meter_key
        bahr_type = meter_cls.bahr_type if meter_cls else "tam"

        # Determine winning phonetic variations
        chosen_sadr = sadr_candidates[0]
        for cand in sadr_candidates:
            if cand[1] == best_match.sadr_input_pattern:
                chosen_sadr = cand
                break

        chosen_ajuz = ajuz_candidates[0]
        if ajuz_text:
            for cand in ajuz_candidates:
                if cand[1] == best_match.ajuz_input_pattern:
                    chosen_ajuz = cand
                    break

        patterns = self.precomputed_patterns.get(meter_key, {})
        sadr_comp = self._find_best_component_match(chosen_sadr[1], patterns.get("sadr", []))
        ajuz_comp = self._find_best_component_match(chosen_ajuz[1], patterns.get("ajuz", [])) if ajuz_text else None

        sadr_ref_feet = sadr_comp["ref"]["feet"] if sadr_comp.get("ref") else []
        ajuz_ref_feet = ajuz_comp["ref"]["feet"] if ajuz_comp and ajuz_comp.get("ref") else []

        sadr_feet = self._analyze_feet(chosen_sadr[1], sadr_ref_feet, sadr_comp.get("ref"))
        ajuz_feet = (
            self._analyze_feet(chosen_ajuz[1], ajuz_ref_feet, ajuz_comp.get("ref") if ajuz_comp else None)
            if ajuz_text
            else None
        )

        sadr_score = float(sadr_comp.get("score", 0.0))
        ajuz_score = float(ajuz_comp.get("score", 0.0)) if ajuz_comp else 1.0
        combined_score = (sadr_score + ajuz_score) / (2 if ajuz_text else 1)

        sadr_analysis_obj = ShatrAnalysis(
            text=sadr_text,
            arudi_text=chosen_sadr[0],
            pattern=chosen_sadr[1],
            feet=sadr_feet,
            score=sadr_score,
            is_valid=all(f.status == "ok" for f in sadr_feet),
        )

        ajuz_analysis_obj = (
            ShatrAnalysis(
                text=ajuz_text,
                arudi_text=chosen_ajuz[0],
                pattern=chosen_ajuz[1],
                feet=ajuz_feet or [],
                score=ajuz_score,
                is_valid=all(f.status == "ok" for f in (ajuz_feet or [])),
            )
            if ajuz_text
            else None
        )

        # Rhyme (Qafiyah) analysis
        qafiyah_obj = None
        if ajuz_text:
            qafiyah_obj = self.qafiyah_analyzer.analyze(
                ajuz_text, is_muqayyad=(chosen_ajuz[1].endswith("0") and chosen_ajuz == ajuz_res_unsat)
            )

        ref_sadr_pat = sadr_comp["ref"]["pattern"] if sadr_comp.get("ref") else ""
        ref_ajuz_pat = ajuz_comp["ref"]["pattern"] if ajuz_comp and ajuz_comp.get("ref") else ""
        standard_pattern = ref_sadr_pat + (" " + ref_ajuz_pat if ref_ajuz_pat else "")

        is_valid = (
            combined_score >= 0.85
            and sadr_analysis_obj.is_valid
            and (ajuz_analysis_obj is None or ajuz_analysis_obj.is_valid)
        )

        errors: list[str] = []
        if combined_score < 0.85:
            errors.append(f"Low metric similarity score: {combined_score:.2f}")
        for foot in sadr_feet:
            if foot.status != "ok":
                errors.append(
                    f"Sadr Foot {foot.foot_index + 1} is {foot.status}: "
                    f"expected {foot.expected_pattern}, got {foot.actual_segment}"
                )
        if ajuz_feet:
            for foot in ajuz_feet:
                if foot.status != "ok":
                    errors.append(
                        f"Ajuz Foot {foot.foot_index + 1} is {foot.status}: "
                        f"expected {foot.expected_pattern}, got {foot.actual_segment}"
                    )

        return VerseAnalysis(
            verse_index=verse_index,
            sadr_text=sadr_text,
            ajuz_text=ajuz_text,
            meter_key=meter_key,
            meter_name_ar=meter_name_ar,
            meter_name_en=meter_name_en,
            bahr_type=bahr_type,
            standard_pattern=standard_pattern,
            score=combined_score,
            sadr=sadr_analysis_obj,
            ajuz=ajuz_analysis_obj,
            qafiyah=qafiyah_obj,
            is_valid=is_valid,
            errors=errors,
        )

    def analyze_poem(
        self,
        verses: list[tuple[str, str]] | list[str],
        meter_name: str | None = None,
    ) -> PoemAnalysis:
        """
        Analyzes a collection of verses composing a complete poem.
        """
        normalized_verses: list[tuple[str, str]] = []
        for v in verses:
            if isinstance(v, tuple):
                normalized_verses.append(v)
            elif isinstance(v, list) and len(v) >= 2:
                normalized_verses.append((v[0], v[1]))
            elif isinstance(v, str):
                parts = v.split("...", 1) if "..." in v else v.split(" - ", 1)
                if len(parts) == 2:
                    normalized_verses.append((parts[0].strip(), parts[1].strip()))
                else:
                    normalized_verses.append((v.strip(), ""))

        detected_counts: Counter[str] = Counter()
        first_pass_analyses: list[VerseAnalysis] = []

        for i, (sadr, ajuz) in enumerate(normalized_verses):
            v_analysis = self.analyze_verse(sadr, ajuz, forced_meter=meter_name, verse_index=i)
            first_pass_analyses.append(v_analysis)
            if v_analysis.meter_key != "unknown":
                detected_counts[v_analysis.meter_key] += 1

        if meter_name:
            global_meter = meter_name
        elif detected_counts:
            global_meter = detected_counts.most_common(1)[0][0]
        else:
            global_meter = "unknown"

        # If global meter was determined by consensus and some verses differed, re-evaluate against global meter
        final_verses: list[VerseAnalysis] = []
        rawi_counter: Counter[str] = Counter()

        for i, (sadr, ajuz) in enumerate(normalized_verses):
            if meter_name or global_meter == "unknown" or first_pass_analyses[i].meter_key == global_meter:
                v_res = first_pass_analyses[i]
            else:
                v_res = self.analyze_verse(sadr, ajuz, forced_meter=global_meter, verse_index=i)

            final_verses.append(v_res)
            if v_res.qafiyah and v_res.qafiyah.rawi:
                rawi_counter[v_res.qafiyah.rawi] += 1

        meter_cls = self.meter_classes.get(global_meter)
        meter_name_ar = meter_cls.name_ar if meter_cls else "غير محدد"
        meter_name_en = meter_cls.name_en if meter_cls else "Unknown"
        bahr_type = meter_cls.bahr_type if meter_cls else "unknown"

        scores = [v.score for v in final_verses]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        valid_count = sum(1 for v in final_verses if v.is_valid)
        is_homogeneous = len({v.meter_key for v in final_verses if v.meter_key != "unknown"}) <= 1
        dominant_rawi = rawi_counter.most_common(1)[0][0] if rawi_counter else None

        return PoemAnalysis(
            meter_key=global_meter,
            meter_name_ar=meter_name_ar,
            meter_name_en=meter_name_en,
            bahr_type=bahr_type,
            verses=final_verses,
            average_score=avg_score,
            is_homogeneous=is_homogeneous,
            dominant_rawi=dominant_rawi,
            total_verses=len(final_verses),
            valid_verses_count=valid_count,
        )

    def process_poem(
        self,
        verses: list[tuple[str, str]],
        meter_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Backwards-compatible wrapper matching the legacy PyArud interface.
        """
        poem_analysis = self.analyze_poem(verses, meter_name=meter_name)
        if poem_analysis.meter_key == "unknown":
            return {"error": "Could not detect any valid meter."}

        # Format legacy dict
        legacy_verses: list[dict[str, Any]] = []
        for v in poem_analysis.verses:
            v_dict = v.to_dict()
            v_dict["sadr_analysis"] = [f.to_dict() for f in v.sadr.feet] if v.sadr is not None else None
            v_dict["ajuz_analysis"] = [f.to_dict() for f in v.ajuz.feet] if v.ajuz is not None else None
            legacy_verses.append(v_dict)

        return {
            "meter": poem_analysis.meter_key,
            "meter_name_ar": poem_analysis.meter_name_ar,
            "meter_name_en": poem_analysis.meter_name_en,
            "verses": legacy_verses,
        }

    def _find_best_meter(
        self,
        sadr_candidates: list[tuple[str, str]],
        ajuz_candidates: list[tuple[str, str]],
        target_meter: str | None = None,
    ) -> list[MeterMatchCandidate]:
        """Matches candidate patterns against all registered meters and scores them."""
        candidates: list[MeterMatchCandidate] = []

        meters_to_check: list[tuple[str, dict[str, Any]]] = list(self.precomputed_patterns.items())
        if target_meter:
            if target_meter in self.precomputed_patterns:
                meters_to_check = [(target_meter, self.precomputed_patterns[target_meter])]
            else:
                return []

        has_ajuz = any(c[1] for c in ajuz_candidates)

        for name, patterns in meters_to_check:
            s_exact = self._sadr_exact_maps.get(name, {})
            a_exact = self._ajuz_exact_maps.get(name, {})

            # 1. Score Sadr candidates
            best_sadr: dict[str, Any] | None = None
            best_sadr_score = -1.0
            best_sadr_input = ""

            for cand in sadr_candidates:
                cand_pat = cand[1]
                if cand_pat in s_exact:
                    match: dict[str, Any] = {"score": 1.0, "ref": s_exact[cand_pat]}
                else:
                    match = self._find_best_component_match(cand_pat, patterns["sadr"])

                score_val: float = float(match["score"])
                if score_val > best_sadr_score:
                    best_sadr_score = score_val
                    best_sadr = match
                    best_sadr_input = cand_pat
                    if best_sadr_score == 1.0:
                        break

            # 2. Score Ajuz candidates
            best_ajuz: dict[str, Any] | None = None
            best_ajuz_score = -1.0
            best_ajuz_input = ""

            if has_ajuz:
                for cand in ajuz_candidates:
                    cand_pat = cand[1]
                    if not cand_pat:
                        continue
                    if cand_pat in a_exact:
                        match = {"score": 1.0, "ref": a_exact[cand_pat]}
                    else:
                        match = self._find_best_component_match(cand_pat, patterns["ajuz"])

                    score_val = float(match["score"])
                    if score_val > best_ajuz_score:
                        best_ajuz_score = score_val
                        best_ajuz = match
                        best_ajuz_input = cand_pat
                        if best_ajuz_score == 1.0:
                            break

            s_score = best_sadr_score
            a_score = best_ajuz_score if best_ajuz else 0.0

            # Compatibility check for valid pair
            is_valid_pair = False
            if best_sadr and best_sadr["ref"] and (not has_ajuz or (best_ajuz and best_ajuz["ref"])):
                s_pat = best_sadr["ref"]["pattern"]
                a_pat = best_ajuz["ref"]["pattern"] if best_ajuz else ""
                if (s_pat, a_pat) in patterns["pairs"]:
                    is_valid_pair = True

            total_score = (s_score + a_score) / 2 if has_ajuz else s_score

            meter_cls = self.meter_classes.get(name)
            candidates.append(
                MeterMatchCandidate(
                    meter_key=name,
                    meter_name_ar=meter_cls.name_ar if meter_cls else name,
                    meter_name_en=meter_cls.name_en if meter_cls else name,
                    bahr_type=meter_cls.bahr_type if meter_cls else "tam",
                    score=total_score,
                    valid_pair=is_valid_pair,
                    sadr_match=best_sadr,
                    ajuz_match=best_ajuz,
                    sadr_input_pattern=best_sadr_input,
                    ajuz_input_pattern=best_ajuz_input,
                )
            )

        # Sort candidates: exact score first, then valid pair, then standard meter priority
        candidates.sort(
            key=lambda x: (
                round(x.score, 3),
                x.valid_pair,
                METER_PRIORITY.get(x.meter_key, 0),
            ),
            reverse=True,
        )

        return candidates

    def _find_best_component_match(
        self, input_pattern: str, component_patterns: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Finds closest matching reference pattern in a component list with length pruning."""
        if not input_pattern:
            return {"score": 0.0, "ref": None}

        # Fast exact check
        for item in component_patterns:
            if item["pattern"] == input_pattern:
                return {"score": 1.0, "ref": item}

        best_score = -1.0
        best_ref: dict[str, Any] | None = None
        input_len = len(input_pattern)

        for item in component_patterns:
            ref_pat = item["pattern"]
            # Prune candidates with incompatible length
            if abs(len(ref_pat) - input_len) > 4:
                continue
            score = self._get_similarity(ref_pat, input_pattern)
            if score > best_score:
                best_score = score
                best_ref = item
                if score == 1.0:
                    break

        if best_ref is None and component_patterns:
            best_ref = component_patterns[0]
            best_score = self._get_similarity(best_ref["pattern"], input_pattern)

        return {"score": best_score, "ref": best_ref}

    def _analyze_feet(
        self,
        input_pattern: str,
        ref_feet: list[str],
        best_ref: dict[str, Any] | None,
    ) -> list[FootAnalysis]:
        """
        Decomposes the binary metric pattern into feet using reference foot sequence,
        mapping each segment to its specific Zihaf/'Ilal variation and Arabic names.
        """
        analysis: list[FootAnalysis] = []
        current_idx = 0
        num_feet = len(ref_feet)

        for i in range(num_feet):
            expected_pat = ref_feet[i]
            cand_len = len(expected_pat)
            end_idx = min(current_idx + cand_len, len(input_pattern))
            actual_segment = input_pattern[current_idx:end_idx]

            if not actual_segment:
                analysis.append(
                    FootAnalysis(
                        foot_index=i,
                        expected_pattern=expected_pat,
                        actual_segment="MISSING",
                        base_tafeela="",
                        actual_tafeela="",
                        zihaf_name_ar="مفقودة",
                        zihaf_name_en="Missing",
                        score=0.0,
                        status="missing",
                    )
                )
                continue

            final_score = self._get_similarity(expected_pat, actual_segment)
            status = "ok" if final_score == 1.0 else "broken"

            # Look up Tafeela and Zihaf information
            tafeela_info = TAFEELA_VARIATION_MAP.get((expected_pat, actual_segment)) or DEFAULT_PATTERN_TAFEELA.get(
                expected_pat
            )

            if tafeela_info:
                base_t, act_t, z_ar, z_en = tafeela_info
            else:
                base_t, act_t, z_ar, z_en = "", "", "سالمة", "Salim"

            analysis.append(
                FootAnalysis(
                    foot_index=i,
                    expected_pattern=expected_pat,
                    actual_segment=actual_segment,
                    base_tafeela=base_t,
                    actual_tafeela=act_t,
                    zihaf_name_ar=z_ar,
                    zihaf_name_en=z_en,
                    score=final_score,
                    status=status,
                )
            )

            current_idx = end_idx

        # Extra bits at end of hemistich
        if current_idx < len(input_pattern):
            extra = input_pattern[current_idx:]
            analysis.append(
                FootAnalysis(
                    foot_index=num_feet,
                    expected_pattern="",
                    actual_segment=extra,
                    base_tafeela="",
                    actual_tafeela="",
                    zihaf_name_ar="زيادة غير مطابقة",
                    zihaf_name_en="Extra Bits",
                    score=0.0,
                    status="extra_bits",
                )
            )

        return analysis
