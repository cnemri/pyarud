"""
Deterministic Metric Grammar Engine for Classical Arabic Prosody (العروض الخليلي).

Implements exact formal metric grammars for all 16 Buhur and sub-meters (Tam, Majzoo,
Mashtoor, Manhook, Mukhalla'), with deterministic multi-meter disambiguation,
Zihaf naturalness cost evaluation, and broken verse defect diagnosis.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.constants import METER_PRIORITY
from .bahr import (
    Bahr,
    Baseet,
    BaseetMajzoo,
    BaseetMukhalla,
    Hazaj,
    Kamel,
    KamelMajzoo,
    Khafeef,
    KhafeefMajzoo,
    Madeed,
    Mudhare,
    Mujtath,
    Munsareh,
    MunsarehManhook,
    Muqtadheb,
    Mutadarak,
    MutadarakMajzoo,
    MutadarakMashtoor,
    Mutakareb,
    MutakarebMajzoo,
    Rajaz,
    RajazMajzoo,
    RajazManhook,
    RajazMashtoor,
    Ramal,
    RamalMajzoo,
    Saree,
    SareeMashtoor,
    Taweel,
    Wafer,
    WaferMajzoo,
)
from .tafeela import Tafeela
from .zihaf import (
    BaseEllahZehaf,
    NoZehafNorEllah,
)

# Cost of various Zihaf/'Ilal modifications (0 = Salim/Sound, 1 = Common single, 2 = Rare/Double)
ZIHAF_COST_MAP: dict[str, int] = {
    "NoZehafNorEllah": 0,
    "Khaban": 1,
    "Edmaar": 1,
    "Tay": 1,
    "Qabadh": 1,
    "Asab": 1,
    "Kaff": 2,
    "Aql": 2,
    "Waqs": 2,
    "Khabal": 3,
    "Khazl": 3,
    "Shakal": 3,
    "Hadhf": 1,
    "Qataa": 1,
    "Qasar": 1,
    "Tatheel": 1,
    "Tarfeel": 1,
    "Tasbeegh": 1,
    "Tasheeth": 1,
    "Qataf": 1,
    "Kasf": 1,
    "Waqf": 1,
    "Salam": 1,
    "Batr": 2,
    "Hathath": 2,
    "Thalm": 2,
    "Tharm": 2,
    "HadhfAndKhaban": 2,
    "KhabanAndQataa": 2,
    "QataaAndEdmaar": 2,
    "TarfeelAndEdmaar": 2,
    "TarfeelAndKhaban": 2,
    "TatheelAndEdmaar": 2,
    "TayAndKasf": 2,
    "KhabalAndKasf": 2,
    "WaqfAndTay": 2,
    "HathathAndEdmaar": 2,
    "ThalmAndQasar": 2,
}


@dataclass(slots=True)
class FootVariation:
    """Represents a permissible variation of a metric foot at a specific position."""

    pattern: str
    base_tafeela: str
    actual_tafeela: str
    zihaf_class: type[BaseEllahZehaf]
    zihaf_name_ar: str
    zihaf_name_en: str
    zihaf_cost: int
    is_salim: bool


@dataclass(slots=True)
class ShatrDerivation:
    """Represents a valid decomposition of a hemistich into feet under a specific meter."""

    meter_key: str
    bahr_type: str
    feet: list[FootVariation]
    pattern: str
    total_zihaf_cost: int
    salim_count: int
    arudh_or_dharb_class: type[BaseEllahZehaf]
    is_exact: bool = True


@dataclass(slots=True)
class MeterGrammar:
    """Deterministic formal metric grammar for a specific Bahr or sub-Bahr."""

    bahr_cls: type[Bahr]
    name_ar: str
    name_en: str
    meter_key: str
    bahr_type: str
    only_one_shatr: bool
    sadr_foot_slots: list[list[FootVariation]] = field(default_factory=list)
    ajuz_foot_slots: list[list[FootVariation]] = field(default_factory=list)
    valid_arudh_dharb_pairs: set[tuple[str, str]] = field(default_factory=set)
    valid_arudh_classes: set[type[BaseEllahZehaf]] = field(default_factory=set)
    valid_dharb_classes: set[type[BaseEllahZehaf]] = field(default_factory=set)
    canonical_patterns_sadr: set[str] = field(default_factory=set)
    canonical_patterns_ajuz: set[str] = field(default_factory=set)


def _build_foot_variation(
    base_tafeela_cls: type[Tafeela], form_instance: Tafeela
) -> FootVariation:
    """Constructs a FootVariation descriptor from a Tafeela instance."""
    applied_cls = form_instance.applied_ella_zehaf_class or NoZehafNorEllah
    cls_name = applied_cls.__name__
    cost = ZIHAF_COST_MAP.get(cls_name, 1)
    is_salim = applied_cls is NoZehafNorEllah

    return FootVariation(
        pattern=str(form_instance),
        base_tafeela=base_tafeela_cls().name,
        actual_tafeela=form_instance.name,
        zihaf_class=applied_cls,
        zihaf_name_ar=applied_cls.name_ar if hasattr(applied_cls, "name_ar") else "سالمة",
        zihaf_name_en=applied_cls.name_en if hasattr(applied_cls, "name_en") else "Salim",
        zihaf_cost=cost,
        is_salim=is_salim,
    )


def build_meter_grammar(bahr_cls: type[Bahr]) -> MeterGrammar:
    """Builds the comprehensive deterministic grammar for a Bahr class."""
    grammar = MeterGrammar(
        bahr_cls=bahr_cls,
        name_ar=bahr_cls.name_ar,
        name_en=bahr_cls.name_en,
        meter_key=bahr_cls.key,
        bahr_type=bahr_cls.bahr_type,
        only_one_shatr=bahr_cls.only_one_shatr,
    )

    num_feet = len(bahr_cls.tafeelat)
    if num_feet == 0:
        return grammar

    # Sadr slots
    sadr_slots: list[list[FootVariation]] = []
    # 1. Hashw slots
    for i in range(num_feet - 1):
        slot_variations: list[FootVariation] = []
        base_t_cls = bahr_cls.tafeelat[i]
        all_forms = base_t_cls().all_zehaf_tafeela_forms()

        # Filter disallowed Hashw
        if 0 in bahr_cls.disallowed_zehafs_for_hashw:
            disallowed = bahr_cls.disallowed_zehafs_for_hashw[0]
            if i < len(disallowed):
                disallowed_set = set(disallowed[i])
                all_forms = [f for f in all_forms if f.applied_ella_zehaf_class not in disallowed_set]

        seen_patterns: set[str] = set()
        for f in all_forms:
            fv = _build_foot_variation(base_t_cls, f)
            if fv.pattern not in seen_patterns:
                seen_patterns.add(fv.pattern)
                slot_variations.append(fv)
        sadr_slots.append(slot_variations)

    # 2. Arudh (last foot of Sadr)
    last_t_cls = bahr_cls.tafeelat[-1]
    arudh_variations: list[FootVariation] = []
    seen_arudh: set[str] = set()

    if isinstance(bahr_cls.arod_dharbs_map, dict):
        for arudh_z_cls, dharbs in bahr_cls.arod_dharbs_map.items():
            grammar.valid_arudh_classes.add(arudh_z_cls)
            try:
                mod_t = arudh_z_cls(last_t_cls()).modified_tafeela
                fv = _build_foot_variation(last_t_cls, mod_t)
                if fv.pattern not in seen_arudh:
                    seen_arudh.add(fv.pattern)
                    arudh_variations.append(fv)
                for d_cls in dharbs:
                    grammar.valid_dharb_classes.add(d_cls)
                    grammar.valid_arudh_dharb_pairs.add((arudh_z_cls.__name__, d_cls.__name__))
            except (AssertionError, Exception):
                continue
    elif isinstance(bahr_cls.arod_dharbs_map, set):
        for z_cls in bahr_cls.arod_dharbs_map:
            grammar.valid_arudh_classes.add(z_cls)
            try:
                mod_t = z_cls(last_t_cls()).modified_tafeela
                fv = _build_foot_variation(last_t_cls, mod_t)
                if fv.pattern not in seen_arudh:
                    seen_arudh.add(fv.pattern)
                    arudh_variations.append(fv)
            except (AssertionError, Exception):
                continue
    sadr_slots.append(arudh_variations)
    grammar.sadr_foot_slots = sadr_slots

    # Ajuz slots (if not single shatr)
    if not bahr_cls.only_one_shatr:
        ajuz_slots: list[list[FootVariation]] = []
        # Hashw
        for i in range(num_feet - 1):
            slot_variations = []
            base_t_cls = bahr_cls.tafeelat[i]
            all_forms = base_t_cls().all_zehaf_tafeela_forms()

            if 1 in bahr_cls.disallowed_zehafs_for_hashw:
                disallowed = bahr_cls.disallowed_zehafs_for_hashw[1]
                if i < len(disallowed):
                    disallowed_set = set(disallowed[i])
                    all_forms = [f for f in all_forms if f.applied_ella_zehaf_class not in disallowed_set]

            seen_patterns = set()
            for f in all_forms:
                fv = _build_foot_variation(base_t_cls, f)
                if fv.pattern not in seen_patterns:
                    seen_patterns.add(fv.pattern)
                    slot_variations.append(fv)
            ajuz_slots.append(slot_variations)

        # Dharb
        dharb_variations: list[FootVariation] = []
        seen_dharb: set[str] = set()
        for d_cls in grammar.valid_dharb_classes:
            try:
                mod_t = d_cls(last_t_cls()).modified_tafeela
                fv = _build_foot_variation(last_t_cls, mod_t)
                if fv.pattern not in seen_dharb:
                    seen_dharb.add(fv.pattern)
                    dharb_variations.append(fv)
            except (AssertionError, Exception):
                continue
        ajuz_slots.append(dharb_variations)
        grammar.ajuz_foot_slots = ajuz_slots

    # Compute canonical patterns
    def _gen_patterns(slots: list[list[FootVariation]]) -> set[str]:
        if not slots:
            return set()
        results = {""}
        for slot in slots:
            new_results = set()
            for prefix in results:
                for fv in slot:
                    new_results.add(prefix + fv.pattern)
            results = new_results
        return results

    grammar.canonical_patterns_sadr = _gen_patterns(grammar.sadr_foot_slots)
    if not grammar.only_one_shatr:
        grammar.canonical_patterns_ajuz = _gen_patterns(grammar.ajuz_foot_slots)

    return grammar


# All registered meter and sub-meter grammars
ALL_GRAMMARS: list[MeterGrammar] = [
    # 1. Taweel
    build_meter_grammar(Taweel),
    # 2. Madeed
    build_meter_grammar(Madeed),
    # 3. Baseet (Tam, Majzoo, Mukhalla)
    build_meter_grammar(Baseet),
    build_meter_grammar(BaseetMukhalla),
    build_meter_grammar(BaseetMajzoo),
    # 4. Wafer (Tam, Majzoo)
    build_meter_grammar(Wafer),
    build_meter_grammar(WaferMajzoo),
    # 5. Kamel (Tam, Majzoo)
    build_meter_grammar(Kamel),
    build_meter_grammar(KamelMajzoo),
    # 6. Hazaj
    build_meter_grammar(Hazaj),
    # 7. Rajaz (Tam, Majzoo, Mashtoor, Manhook)
    build_meter_grammar(Rajaz),
    build_meter_grammar(RajazMajzoo),
    build_meter_grammar(RajazMashtoor),
    build_meter_grammar(RajazManhook),
    # 8. Ramal (Tam, Majzoo)
    build_meter_grammar(Ramal),
    build_meter_grammar(RamalMajzoo),
    # 9. Saree (Tam, Mashtoor)
    build_meter_grammar(Saree),
    build_meter_grammar(SareeMashtoor),
    # 10. Munsareh (Tam, Manhook)
    build_meter_grammar(Munsareh),
    build_meter_grammar(MunsarehManhook),
    # 11. Khafeef (Tam, Majzoo)
    build_meter_grammar(Khafeef),
    build_meter_grammar(KhafeefMajzoo),
    # 12. Mudhare
    build_meter_grammar(Mudhare),
    # 13. Muqtadheb
    build_meter_grammar(Muqtadheb),
    # 14. Mujtath
    build_meter_grammar(Mujtath),
    # 15. Mutakareb (Tam, Majzoo)
    build_meter_grammar(Mutakareb),
    build_meter_grammar(MutakarebMajzoo),
    # 16. Mutadarak (Tam, Majzoo, Mashtoor)
    build_meter_grammar(Mutadarak),
    build_meter_grammar(MutadarakMajzoo),
    build_meter_grammar(MutadarakMashtoor),
]


class DeterministicProsodyEngine:
    """
    Deterministic Prosody Parser based on Al-Khalil's formal metric theory.

    Performs exact formal grammar parsing, Zihaf cost optimization,
    disambiguation of ambiguous metric sequences, and diagnostic fault localization.
    """

    def __init__(self) -> None:
        self.grammars = ALL_GRAMMARS

    def parse_shatr_exact(
        self, pattern: str, slots: list[list[FootVariation]], meter_key: str, bahr_type: str
    ) -> list[ShatrDerivation]:
        """
        Deterministically parses a binary pattern against foot slots.
        Returns all exact derivations sorted by lowest Zihaf cost.
        """
        if not pattern or not slots:
            return []

        num_slots = len(slots)
        derivations: list[ShatrDerivation] = []

        def _dfs(slot_idx: int, char_idx: int, current_feet: list[FootVariation]) -> None:
            if slot_idx == num_slots:
                if char_idx == len(pattern):
                    # Found complete exact derivation
                    total_cost = sum(f.zihaf_cost for f in current_feet)
                    salim_count = sum(1 for f in current_feet if f.is_salim)
                    arudh_or_dharb = current_feet[-1].zihaf_class
                    derivations.append(
                        ShatrDerivation(
                            meter_key=meter_key,
                            bahr_type=bahr_type,
                            feet=list(current_feet),
                            pattern=pattern,
                            total_zihaf_cost=total_cost,
                            salim_count=salim_count,
                            arudh_or_dharb_class=arudh_or_dharb,
                            is_exact=True,
                        )
                    )
                return

            remaining_slots = num_slots - slot_idx
            remaining_chars = len(pattern) - char_idx
            # Pruning: minimum foot length is 3, maximum is 8
            if remaining_chars < remaining_slots * 3 or remaining_chars > remaining_slots * 8:
                return

            current_slot = slots[slot_idx]
            for fv in current_slot:
                pat = fv.pattern
                plen = len(pat)
                if char_idx + plen <= len(pattern) and pattern[char_idx : char_idx + plen] == pat:
                    current_feet.append(fv)
                    _dfs(slot_idx + 1, char_idx + plen, current_feet)
                    current_feet.pop()

        _dfs(0, 0, [])
        derivations.sort(key=lambda d: (d.total_zihaf_cost, -d.salim_count))
        return derivations

    def match_verse(
        self,
        sadr_candidates: list[tuple[str, str]],
        ajuz_candidates: list[tuple[str, str]],
        target_meter: str | None = None,
    ) -> list[tuple[MeterGrammar, ShatrDerivation | None, ShatrDerivation | None, float, bool]]:
        """
        Matches candidate patterns against all registered meter grammars.
        Returns list of (grammar, best_sadr_deriv, best_ajuz_deriv, score, valid_pair).
        """
        has_ajuz = any(c[1] for c in ajuz_candidates)
        exact_results: list[
            tuple[MeterGrammar, ShatrDerivation | None, ShatrDerivation | None, float, bool]
        ] = []

        grammars_to_check = self.grammars
        if target_meter:
            grammars_to_check = [g for g in self.grammars if g.meter_key == target_meter]

        for g in grammars_to_check:
            # Sadr matching
            best_sadr_deriv: ShatrDerivation | None = None
            for _cand_text, cand_pat in sadr_candidates:
                derivs = self.parse_shatr_exact(cand_pat, g.sadr_foot_slots, g.meter_key, g.bahr_type)
                if derivs:
                    best_sadr_deriv = derivs[0]
                    break

            if not best_sadr_deriv:
                continue

            # Ajuz matching
            if g.only_one_shatr:
                if has_ajuz:
                    continue  # Single-shatr meters cannot match 2-shatr verses
                arudh_cls = best_sadr_deriv.arudh_or_dharb_class
                is_valid = arudh_cls in g.valid_arudh_classes or not g.valid_arudh_classes
                cost = best_sadr_deriv.total_zihaf_cost
                salim = best_sadr_deriv.salim_count
                score = 1.0 - (cost * 0.001) + (salim * 0.0005)
                exact_results.append((g, best_sadr_deriv, None, score, is_valid))
            elif not has_ajuz:
                # 2-shatr meter analyzed with single shatr input
                arudh_cls = best_sadr_deriv.arudh_or_dharb_class
                is_valid = arudh_cls in g.valid_arudh_classes or not g.valid_arudh_classes
                cost = best_sadr_deriv.total_zihaf_cost
                salim = best_sadr_deriv.salim_count
                score = 1.0 - (cost * 0.001) + (salim * 0.0005)
                exact_results.append((g, best_sadr_deriv, None, score, is_valid))
            else:
                best_ajuz_deriv: ShatrDerivation | None = None
                for _cand_text, cand_pat in ajuz_candidates:
                    derivs = self.parse_shatr_exact(
                        cand_pat, g.ajuz_foot_slots, g.meter_key, g.bahr_type
                    )
                    if derivs:
                        best_ajuz_deriv = derivs[0]
                        break

                if not best_ajuz_deriv:
                    continue

                # Validate Arudh-Dharb pair
                pair_key = (
                    best_sadr_deriv.arudh_or_dharb_class.__name__,
                    best_ajuz_deriv.arudh_or_dharb_class.__name__,
                )
                is_valid_pair = pair_key in g.valid_arudh_dharb_pairs
                if not g.valid_arudh_dharb_pairs:
                    is_valid_pair = True

                total_cost = best_sadr_deriv.total_zihaf_cost + best_ajuz_deriv.total_zihaf_cost
                total_salim = best_sadr_deriv.salim_count + best_ajuz_deriv.salim_count
                score = 1.0 - (total_cost * 0.001) + (total_salim * 0.0005)

                exact_results.append((g, best_sadr_deriv, best_ajuz_deriv, score, is_valid_pair))

        return exact_results

    def disambiguate_exact_matches(
        self,
        candidates: list[
            tuple[MeterGrammar, ShatrDerivation | None, ShatrDerivation | None, float, bool]
        ],
        sadr_pat: str,
        ajuz_pat: str,
    ) -> tuple[MeterGrammar, ShatrDerivation | None, ShatrDerivation | None, float, bool] | None:
        """
        Applies classical Farahidian disambiguation theorems to resolve ambiguities.
        """
        if not candidates:
            return None

        # 1. If single candidate, return it
        if len(candidates) == 1:
            return candidates[0]

        cand_pool = [c for c in candidates if c[4]]
        if not cand_pool:
            cand_pool = candidates

        # 2. Check for signature patterns
        full_pat = sadr_pat + ajuz_pat

        # Single-shatr specific disambiguation
        if not ajuz_pat:
            # Single-shatr verses (Mashtoor / Manhook)
            single_cands = [c for c in cand_pool if c[0].only_one_shatr]
            if single_cands:
                cand_pool = single_cands
                # Mashtoor al-Rajaz preference
                rajaz_mashtoor = [c for c in cand_pool if c[0].meter_key == "rajaz" and c[0].bahr_type == "mashtoor"]
                if rajaz_mashtoor and len(sadr_pat) >= 18:
                    return rajaz_mashtoor[0]
                # Manhook preference for short single lines
                manhook_cands = [c for c in cand_pool if c[0].bahr_type == "manhook"]
                if manhook_cands and len(sadr_pat) <= 15:
                    return max(manhook_cands, key=lambda c: METER_PRIORITY.get(c[0].meter_key, 0))

        # Signature 1: '1110110' (متفاعلن) -> Strictly Kamel
        if "1110110" in full_pat:
            kamel_cands = [c for c in cand_pool if c[0].meter_key == "kamel"]
            if kamel_cands:
                return max(kamel_cands, key=lambda c: (c[3], METER_PRIORITY.get(c[0].meter_key, 0)))

        # Signature 2: '1101110' (مفاعلتن) -> Strictly Wafer
        if "1101110" in full_pat:
            wafer_cands = [c for c in cand_pool if c[0].meter_key == "wafer"]
            if wafer_cands:
                return max(wafer_cands, key=lambda c: (c[3], METER_PRIORITY.get(c[0].meter_key, 0)))

        # Signature 2b: If all '1101010' and NO '1101110', Hazaj strictly wins over Majzoo al-Wafer
        if "1101110" not in full_pat:
            hazaj_cands = [c for c in cand_pool if c[0].meter_key == "hazaj"]
            if hazaj_cands:
                return max(hazaj_cands, key=lambda c: (c[3], METER_PRIORITY.get(c[0].meter_key, 0)))

        # Signature 3: Mukhalla' al-Basit ('10101101011011010') -> Strictly Mukhalla
        mukhalla_cands = [c for c in cand_pool if c[0].bahr_type == "mukhalla"]
        if mukhalla_cands and (
            sadr_pat.endswith("11010") or sadr_pat == "10101101011011010"
        ):
            return mukhalla_cands[0]

        # Signature 4: All '1010110' without any '1110110' -> Rajaz wins over Kamel with Idmar
        rajaz_cands = [c for c in cand_pool if c[0].meter_key == "rajaz"]
        kamel_cands = [c for c in cand_pool if c[0].meter_key == "kamel"]
        if rajaz_cands and kamel_cands and "1110110" not in full_pat:
            # In Rajaz it's 100% Salim, in Kamel it has multiple Idmar
            return max(rajaz_cands, key=lambda c: (c[3], METER_PRIORITY.get(c[0].meter_key, 0)))

        # Signature 5: Saree vs Munsareh vs Baseet
        # Saree ends with '10110' (فاعلن) after two '1010110'
        saree_cands = [c for c in cand_pool if c[0].meter_key == "saree"]
        if saree_cands:
            if sadr_pat.startswith("10101101010110") and sadr_pat.endswith("10110"):
                return saree_cands[0]

        # 3. Disambiguate by score (Zihaf cost + Salim ratio + Meter Priority)
        def _rank_key(
            item: tuple[MeterGrammar, ShatrDerivation | None, ShatrDerivation | None, float, bool]
        ) -> tuple[int, float, int, int]:
            g, _s_deriv, _a_deriv, sc, val_pair = item
            # Tam is prioritized over rare Majzoo/Manhook unless explicit match
            type_bonus = 2 if g.bahr_type == "tam" else (1 if g.bahr_type == "mukhalla" else 0)
            priority = METER_PRIORITY.get(g.meter_key, 0)
            return (1 if val_pair else 0, round(sc, 3), type_bonus, priority)

        cand_pool.sort(key=_rank_key, reverse=True)
        return cand_pool[0]


_GLOBAL_ENGINE: DeterministicProsodyEngine | None = None


def get_deterministic_engine() -> DeterministicProsodyEngine:
    """Singleton getter for the Deterministic Prosody Engine."""
    global _GLOBAL_ENGINE
    if _GLOBAL_ENGINE is None:
        _GLOBAL_ENGINE = DeterministicProsodyEngine()
    return _GLOBAL_ENGINE
