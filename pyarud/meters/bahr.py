"""
Classical Arabic Poetic Meters (Buhur / بحور الشعر العربي) for PyArud.

Defines all 16 classical meters established by Al-Khalil ibn Ahmad al-Farahidi
and Al-Akhfash, including their complete sub-bahrs (Tam, Majzoo, Mashtoor,
Manhook, Mukhalla'), permissible Hashw Zihafat, and Arud/Dharb validation matrices.
"""

from __future__ import annotations

import itertools
from typing import Any, ClassVar

from .tafeela import (
    Fae_laton,
    Faelaton,
    Faelon,
    Fawlon,
    Mafaeelon,
    Mafaelaton,
    Mafoolato,
    Mustafe_lon,
    Mustafelon,
    Mutafaelon,
    Tafeela,
)
from .zihaf import (
    Aql,
    Asab,
    BaseEllahZehaf,
    Batr,
    Edmaar,
    Hadhf,
    HadhfAndKhaban,
    Hathath,
    HathathAndEdmaar,
    Kaff,
    Kasf,
    Khabal,
    KhabalAndKasf,
    Khaban,
    KhabanAndQataa,
    NoZehafNorEllah,
    Qabadh,
    Qasar,
    Qataa,
    QataaAndEdmaar,
    Qataf,
    Salam,
    Shakal,
    Tarfeel,
    TarfeelAndEdmaar,
    TarfeelAndKhaban,
    Tasbeegh,
    Tasheeth,
    Tatheel,
    TatheelAndEdmaar,
    Tay,
    TayAndKasf,
    Thalm,
    ThalmAndQasar,
    Tharm,
    Waqf,
    WaqfAndTay,
)


class Bahr:
    """
    Base class for defining poetic meters (Buhur).

    Subclasses define standard feet (tafeelat), valid Arudh/Dharb combinations,
    and disallowed variations (Zihaf) for specific positions.
    """

    name_ar: ClassVar[str] = ""
    name_en: ClassVar[str] = ""
    key: ClassVar[str] = ""
    bahr_type: ClassVar[str] = "tam"  # 'tam', 'majzoo', 'mashtoor', 'manhook', 'mukhalla'

    tafeelat: ClassVar[tuple[type[Tafeela], ...]] = ()
    arod_dharbs_map: ClassVar[
        dict[type[BaseEllahZehaf], tuple[type[BaseEllahZehaf], ...]] | set[type[BaseEllahZehaf]]
    ] = {}
    sub_bahrs: ClassVar[tuple[type[Bahr], ...]] = ()
    only_one_shatr: ClassVar[bool] = False
    disallowed_zehafs_for_hashw: ClassVar[dict[int, tuple[list[type[BaseEllahZehaf]], ...]]] = {}

    @property
    def last_tafeela(self) -> Tafeela:
        return self.tafeelat[-1]()

    def get_shatr_hashw_combinations(self, shatr_index: int = 0) -> list[list[Tafeela]]:
        """Generate valid variations for interior feet (Hashw)."""
        combinations: list[list[Tafeela]] = []
        for i, tafeela_class in enumerate(self.tafeelat[:-1]):
            tafeela = tafeela_class()
            forms = tafeela.all_zehaf_tafeela_forms()

            if shatr_index in self.disallowed_zehafs_for_hashw:
                disallowed = self.disallowed_zehafs_for_hashw[shatr_index]
                if i < len(disallowed):
                    forms = [f for f in forms if f.applied_ella_zehaf_class not in disallowed[i]]

            combinations.append(forms)
        return combinations

    def get_allowed_feet_patterns(self, shatr_index: int = 0) -> list[list[str]]:
        """
        Returns a list of lists, where index i contains all valid binary strings for foot i.
        Used for granular foot-by-foot alignment and fault diagnostics.
        """
        allowed_per_index: list[list[str]] = []

        # Hashw feet
        hashw_combs = self.get_shatr_hashw_combinations(shatr_index)
        for forms in hashw_combs:
            allowed_per_index.append([str(f) for f in forms])

        # Last foot (Arudh / Dharb)
        last_feet: set[str] = set()
        if self.only_one_shatr:
            if isinstance(self.arod_dharbs_map, set):
                for z_cls in self.arod_dharbs_map:
                    try:
                        last_feet.add(str(z_cls(self.last_tafeela).modified_tafeela))
                    except AssertionError:
                        continue
            else:
                for z_cls in self.arod_dharbs_map:
                    try:
                        last_feet.add(str(z_cls(self.last_tafeela).modified_tafeela))
                    except AssertionError:
                        continue
        else:
            if isinstance(self.arod_dharbs_map, dict):
                if shatr_index == 0:  # Sadr -> Arudh
                    for z_cls in self.arod_dharbs_map.keys():
                        try:
                            last_feet.add(str(z_cls(self.last_tafeela).modified_tafeela))
                        except AssertionError:
                            continue
                else:  # Ajuz -> Dharb
                    for d_list in self.arod_dharbs_map.values():
                        for z_cls in d_list:
                            try:
                                last_feet.add(str(z_cls(self.last_tafeela).modified_tafeela))
                            except AssertionError:
                                continue

        allowed_per_index.append(list(last_feet))
        return allowed_per_index

    @property
    def detailed_patterns(self) -> dict[str, Any]:
        """
        Returns structured patterns for Sadr and Ajuz separately, along with valid pair constraints.
        """
        patterns: dict[str, Any] = {
            "sadr": [],
            "ajuz": [],
            "pairs": set(),
        }

        if self.only_one_shatr:
            hashw = self.get_shatr_hashw_combinations(0)
            endings: list[Tafeela] = []
            if isinstance(self.arod_dharbs_map, set):
                for z_cls in self.arod_dharbs_map:
                    try:
                        endings.append(z_cls(self.last_tafeela).modified_tafeela)
                    except AssertionError:
                        continue
            elif isinstance(self.arod_dharbs_map, dict):
                for z_cls in self.arod_dharbs_map:
                    try:
                        endings.append(z_cls(self.last_tafeela).modified_tafeela)
                    except AssertionError:
                        continue

            permutations = list(itertools.product(*hashw, endings))
            for p in permutations:
                feet_strs = [str(t) for t in p]
                full_str = "".join(feet_strs)
                patterns["sadr"].append(
                    {
                        "pattern": full_str,
                        "feet": feet_strs,
                        "type": "single_shatr",
                    }
                )
                patterns["pairs"].add((full_str, ""))

        elif isinstance(self.arod_dharbs_map, dict):
            sadr_hashw = self.get_shatr_hashw_combinations(0)
            ajuz_hashw = self.get_shatr_hashw_combinations(1)
            seen_sadr: set[str] = set()
            seen_ajuz: set[str] = set()

            for arudh_z_cls, dharb_z_list in self.arod_dharbs_map.items():
                try:
                    arudh_obj = arudh_z_cls(self.last_tafeela).modified_tafeela
                except AssertionError:
                    continue

                arudh_str = str(arudh_obj)
                sadr_perms = list(itertools.product(*sadr_hashw, [arudh_obj]))
                sadr_pat_list: list[str] = []

                for sp in sadr_perms:
                    feet_strs = [str(t) for t in sp]
                    full_sadr = "".join(feet_strs)
                    sadr_pat_list.append(full_sadr)

                    if full_sadr not in seen_sadr:
                        seen_sadr.add(full_sadr)
                        patterns["sadr"].append(
                            {
                                "pattern": full_sadr,
                                "feet": feet_strs,
                                "arudh_foot": arudh_str,
                                "arudh_class": arudh_z_cls.__name__,
                            }
                        )

                compatible_dharbs: list[Tafeela] = []
                for d_z in dharb_z_list:
                    try:
                        dharb_obj = d_z(self.last_tafeela).modified_tafeela
                        compatible_dharbs.append(dharb_obj)
                    except AssertionError:
                        continue

                if not compatible_dharbs:
                    continue

                ajuz_perms = list(itertools.product(*ajuz_hashw, compatible_dharbs))
                ajuz_pat_list: list[str] = []

                for ap in ajuz_perms:
                    feet_strs_a = [str(t) for t in ap]
                    full_ajuz = "".join(feet_strs_a)
                    ajuz_pat_list.append(full_ajuz)

                    if full_ajuz not in seen_ajuz:
                        seen_ajuz.add(full_ajuz)
                        patterns["ajuz"].append(
                            {
                                "pattern": full_ajuz,
                                "feet": feet_strs_a,
                                "dharb_foot": feet_strs_a[-1],
                                "allowed_arudhs": [arudh_str],
                            }
                        )

                for fs in sadr_pat_list:
                    for fa in ajuz_pat_list:
                        patterns["pairs"].add((fs, fa))

        # Include sub-bahrs
        for sub in self.sub_bahrs:
            sub_p = sub().detailed_patterns
            patterns["sadr"].extend(sub_p["sadr"])
            patterns["ajuz"].extend(sub_p["ajuz"])
            patterns["pairs"].update(sub_p["pairs"])

        return patterns

    @property
    def bait_combinations(self) -> list[str]:
        p = self.detailed_patterns
        if self.only_one_shatr:
            return sorted(list({x["pattern"] for x in p["sadr"]}), key=len)
        return sorted([s + a for s, a in p["pairs"]], key=len)


# ==========================================
# Sub-Bahr Definitions
# ==========================================


class RajazManhook(Bahr):
    name_ar = "منهوك الرجز"
    name_en = "Rajaz Manhook"
    key = "rajaz"
    bahr_type = "manhook"
    tafeelat = (Mustafelon, Mustafelon)
    arod_dharbs_map = {NoZehafNorEllah, Khaban, Tay, Khabal, Qataa, KhabanAndQataa}
    only_one_shatr = True


class RajazMashtoor(Bahr):
    name_ar = "مشطور الرجز"
    name_en = "Rajaz Mashtoor"
    key = "rajaz"
    bahr_type = "mashtoor"
    tafeelat = (Mustafelon, Mustafelon, Mustafelon)
    arod_dharbs_map = {NoZehafNorEllah, Khaban, Tay, Khabal, Qataa, KhabanAndQataa}
    only_one_shatr = True


class RajazMajzoo(Bahr):
    name_ar = "مجزوء الرجز"
    name_en = "Rajaz Majzoo"
    key = "rajaz"
    bahr_type = "majzoo"
    tafeelat = (Mustafelon, Mustafelon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Khaban, Tay, Khabal),
        Khaban: (NoZehafNorEllah, Khaban, Tay, Khabal),
        Tay: (NoZehafNorEllah, Khaban, Tay, Khabal),
        Khabal: (NoZehafNorEllah, Khaban, Tay, Khabal),
    }


class RamalMajzoo(Bahr):
    name_ar = "مجزوء الرمل"
    name_en = "Ramal Majzoo"
    key = "ramal"
    bahr_type = "majzoo"
    tafeelat = (Faelaton, Faelaton)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Khaban, Tasbeegh, Hadhf, HadhfAndKhaban),
        Khaban: (NoZehafNorEllah, Khaban, Tasbeegh, Hadhf, HadhfAndKhaban),
    }
    disallowed_zehafs_for_hashw = {0: ([Tasheeth],), 1: ([Tasheeth],)}


class SareeMashtoor(Bahr):
    name_ar = "مشطور السريع"
    name_en = "Saree Mashtoor"
    key = "saree"
    bahr_type = "mashtoor"
    tafeelat = (Mustafelon, Mustafelon, Mafoolato)
    arod_dharbs_map = {Waqf, Kasf}
    only_one_shatr = True


class MunsarehManhook(Bahr):
    name_ar = "منهوك المنسرح"
    name_en = "Munsareh Manhook"
    key = "munsareh"
    bahr_type = "manhook"
    tafeelat = (Mustafelon, Mafoolato)
    arod_dharbs_map = {Waqf, Kasf}
    only_one_shatr = True


class KhafeefMajzoo(Bahr):
    name_ar = "مجزوء الخفيف"
    name_en = "Khafeef Majzoo"
    key = "khafeef"
    bahr_type = "majzoo"
    tafeelat = (Faelaton, Mustafe_lon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Khaban, KhabanAndQataa),
        Khaban: (NoZehafNorEllah, Khaban, KhabanAndQataa),
    }
    disallowed_zehafs_for_hashw = {0: ([Kaff, Shakal, Tasheeth],), 1: ([Kaff, Shakal, Tasheeth],)}


class MutakarebMajzoo(Bahr):
    name_ar = "مجزوء المتقارب"
    name_en = "Mutakareb Majzoo"
    key = "mutakareb"
    bahr_type = "majzoo"
    tafeelat = (Fawlon, Fawlon, Fawlon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Hadhf, Batr),
        Hadhf: (Hadhf, Batr),
    }
    disallowed_zehafs_for_hashw = {0: ([], [Thalm, Tharm]), 1: ([Thalm, Tharm], [Thalm, Tharm])}


class MutadarakMashtoor(Bahr):
    name_ar = "مشطور المتدارك"
    name_en = "Mutadarak Mashtoor"
    key = "mutadarak"
    bahr_type = "mashtoor"
    tafeelat = (Faelon, Faelon, Faelon)
    arod_dharbs_map = {NoZehafNorEllah, Khaban, Tasheeth, Tatheel, TarfeelAndKhaban}
    only_one_shatr = True


class MutadarakMajzoo(Bahr):
    name_ar = "مجزوء المتدارك"
    name_en = "Mutadarak Majzoo"
    key = "mutadarak"
    bahr_type = "majzoo"
    tafeelat = (Faelon, Faelon, Faelon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Khaban, Tasheeth, Tatheel, TarfeelAndKhaban),
        Khaban: (NoZehafNorEllah, Khaban, Tasheeth, Tatheel, TarfeelAndKhaban),
        Tasheeth: (NoZehafNorEllah, Khaban, Tasheeth, Tatheel, TarfeelAndKhaban),
    }


class BaseetMajzoo(Bahr):
    name_ar = "مجزوء البسيط"
    name_en = "Baseet Majzoo"
    key = "baseet"
    bahr_type = "majzoo"
    tafeelat = (Mustafelon, Faelon, Mustafelon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Tatheel, Qataa),
        Qataa: (NoZehafNorEllah,),
    }
    disallowed_zehafs_for_hashw = {0: ([], [Tasheeth]), 1: ([], [Tasheeth])}


class BaseetMukhalla(BaseetMajzoo):
    name_ar = "مخلع البسيط"
    name_en = "Baseet Mukhalla"
    key = "baseet"
    bahr_type = "mukhalla"
    arod_dharbs_map = {KhabanAndQataa: (KhabanAndQataa,)}
    disallowed_zehafs_for_hashw = {0: ([], [Tasheeth]), 1: ([], [Tasheeth])}


class WaferMajzoo(Bahr):
    name_ar = "مجزوء الوافر"
    name_en = "Wafer Majzoo"
    key = "wafer"
    bahr_type = "majzoo"
    tafeelat = (Mafaelaton, Mafaelaton)
    arod_dharbs_map = {NoZehafNorEllah: (NoZehafNorEllah, Asab), Asab: (NoZehafNorEllah, Asab)}


class KamelMajzoo(Bahr):
    name_ar = "مجزوء الكامل"
    name_en = "Kamel Majzoo"
    key = "kamel"
    bahr_type = "majzoo"
    tafeelat = (Mutafaelon, Mutafaelon)
    arod_dharbs_map = {
        NoZehafNorEllah: (
            NoZehafNorEllah,
            Edmaar,
            Qataa,
            QataaAndEdmaar,
            Tatheel,
            TatheelAndEdmaar,
            Tarfeel,
            TarfeelAndEdmaar,
        ),
        Edmaar: (
            NoZehafNorEllah,
            Edmaar,
            Qataa,
            QataaAndEdmaar,
            Tatheel,
            TatheelAndEdmaar,
            Tarfeel,
            TarfeelAndEdmaar,
        ),
    }


# ==========================================
# 16 Primary Classical Meters (Tam)
# ==========================================


class Taweel(Bahr):
    """بحر الطويل: فعولن مفاعيلن فعولن مفاعيلن (مرتان)."""

    name_ar = "بحر الطويل"
    name_en = "Al-Taweel"
    key = "taweel"
    bahr_type = "tam"
    tafeelat = (Fawlon, Mafaeelon, Fawlon, Mafaeelon)
    arod_dharbs_map = {Qabadh: (Qabadh, Hadhf, NoZehafNorEllah)}
    disallowed_zehafs_for_hashw = {
        0: ([], [], [Thalm, Tharm]),
        1: ([Thalm, Tharm], [], [Thalm, Tharm]),
    }


class Madeed(Bahr):
    """بحر المديد: فاعلاتن فاعلن فاعلاتن (مرتان)."""

    name_ar = "بحر المديد"
    name_en = "Al-Madeed"
    key = "madeed"
    bahr_type = "tam"
    tafeelat = (Faelaton, Faelon, Faelaton)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah,),
        Hadhf: (Hadhf, Batr),
        HadhfAndKhaban: (HadhfAndKhaban,),
        Batr: (Batr,),
    }
    disallowed_zehafs_for_hashw = {
        0: ([Shakal, Tasheeth], [Tasheeth]),
        1: ([Shakal, Tasheeth], [Tasheeth]),
    }


class Baseet(Bahr):
    """بحر البسيط: مستفعلن فاعلن مستفعلن فاعلن (مرتان)."""

    name_ar = "بحر البسيط"
    name_en = "Al-Baseet"
    key = "baseet"
    bahr_type = "tam"
    tafeelat = (Mustafelon, Faelon, Mustafelon, Faelon)
    arod_dharbs_map = {Khaban: (Khaban, Qataa)}
    disallowed_zehafs_for_hashw = {0: ([], [Tasheeth], []), 1: ([], [Tasheeth], [])}
    sub_bahrs = (BaseetMajzoo, BaseetMukhalla)


class Wafer(Bahr):
    """بحر الوافر: مفاعلتن مفاعلتن فعولن (مرتان)."""

    name_ar = "بحر الوافر"
    name_en = "Al-Wafer"
    key = "wafer"
    bahr_type = "tam"
    tafeelat = (Mafaelaton, Mafaelaton, Mafaelaton)
    arod_dharbs_map = {Qataf: (Qataf, Aql)}
    sub_bahrs = (WaferMajzoo,)


class Kamel(Bahr):
    """بحر الكامل: متفاعلن متفاعلن متفاعلن (مرتان)."""

    name_ar = "بحر الكامل"
    name_en = "Al-Kamel"
    key = "kamel"
    bahr_type = "tam"
    tafeelat = (Mutafaelon, Mutafaelon, Mutafaelon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Edmaar, Qataa, QataaAndEdmaar, HathathAndEdmaar),
        Edmaar: (NoZehafNorEllah, Edmaar, Qataa, QataaAndEdmaar, HathathAndEdmaar),
        Hathath: (Hathath, HathathAndEdmaar),
    }
    sub_bahrs = (KamelMajzoo,)


class Hazaj(Bahr):
    """بحر الهزج: مفاعيلن مفاعيلن (مرتان)."""

    name_ar = "بحر الهزج"
    name_en = "Al-Hazaj"
    key = "hazaj"
    bahr_type = "tam"
    tafeelat = (Mafaeelon, Mafaeelon)
    arod_dharbs_map = {NoZehafNorEllah: (NoZehafNorEllah, Hadhf), Kaff: (NoZehafNorEllah, Hadhf)}
    disallowed_zehafs_for_hashw = {0: ([Qabadh],), 1: ([Qabadh],)}


class Rajaz(Bahr):
    """بحر الرجز: مستفعلن مستفعلن مستفعلن (مرتان)."""

    name_ar = "بحر الرجز"
    name_en = "Al-Rajaz"
    key = "rajaz"
    bahr_type = "tam"
    tafeelat = (Mustafelon, Mustafelon, Mustafelon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Khaban, Tay, Khabal, Qataa, KhabanAndQataa),
        Khaban: (NoZehafNorEllah, Khaban, Tay, Khabal, Qataa, KhabanAndQataa),
        Tay: (NoZehafNorEllah, Khaban, Tay, Khabal, Qataa, KhabanAndQataa),
        Khabal: (NoZehafNorEllah, Khaban, Tay, Khabal, Qataa, KhabanAndQataa),
    }
    sub_bahrs = (RajazMajzoo, RajazMashtoor, RajazManhook)


class Ramal(Bahr):
    """بحر الرمل: فاعلاتن فاعلاتن فاعلاتن (مرتان)."""

    name_ar = "بحر الرمل"
    name_en = "Al-Ramal"
    key = "ramal"
    bahr_type = "tam"
    tafeelat = (Faelaton, Faelaton, Faelaton)
    arod_dharbs_map = {
        NoZehafNorEllah: (
            NoZehafNorEllah,
            Khaban,
            Hadhf,
            HadhfAndKhaban,
            Qataa,
            KhabanAndQataa,
        ),
        Khaban: (
            NoZehafNorEllah,
            Khaban,
            Hadhf,
            HadhfAndKhaban,
            Qataa,
            KhabanAndQataa,
        ),
        Hadhf: (
            NoZehafNorEllah,
            Khaban,
            Hadhf,
            HadhfAndKhaban,
            Qasar,
            KhabanAndQataa,
        ),
        HadhfAndKhaban: (
            NoZehafNorEllah,
            Khaban,
            Hadhf,
            HadhfAndKhaban,
            Qataa,
            KhabanAndQataa,
        ),
    }
    sub_bahrs = (RamalMajzoo,)
    disallowed_zehafs_for_hashw = {0: ([Tasheeth], [Tasheeth]), 1: ([Tasheeth], [Tasheeth])}


class Saree(Bahr):
    """بحر السريع: مستفعلن مستفعلن مفعولات (مرتان)."""

    name_ar = "بحر السريع"
    name_en = "Al-Saree"
    key = "saree"
    bahr_type = "tam"
    tafeelat = (Mustafelon, Mustafelon, Mafoolato)
    arod_dharbs_map = {
        TayAndKasf: (TayAndKasf, Salam, WaqfAndTay),
        KhabalAndKasf: (KhabalAndKasf, Salam),
    }
    sub_bahrs = (SareeMashtoor,)


class Munsareh(Bahr):
    """بحر المنسرح: مستفعلن مفعولات مستفعلن (مرتان)."""

    name_ar = "بحر المنسرح"
    name_en = "Al-Munsareh"
    key = "munsareh"
    bahr_type = "tam"
    tafeelat = (Mustafelon, Mafoolato, Mustafelon)
    arod_dharbs_map = {Tay: (Tay, Qataa)}
    sub_bahrs = (MunsarehManhook,)


class Khafeef(Bahr):
    """بحر الخفيف: فاعلاتن مستفع لن فاعلاتن (مرتان)."""

    name_ar = "بحر الخفيف"
    name_en = "Al-Khafeef"
    key = "khafeef"
    bahr_type = "tam"
    tafeelat = (Faelaton, Mustafe_lon, Faelaton)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Khaban, Tasheeth, Hadhf, HadhfAndKhaban),
        Khaban: (NoZehafNorEllah, Khaban, Tasheeth, Hadhf, HadhfAndKhaban),
        Hadhf: (NoZehafNorEllah, Khaban, Tasheeth, Hadhf, HadhfAndKhaban),
    }
    sub_bahrs = (KhafeefMajzoo,)
    disallowed_zehafs_for_hashw = {0: ([Kaff, Shakal], []), 1: ([Kaff, Shakal], [])}


class Mudhare(Bahr):
    """بحر المضارع: مفاعيلن فاع لاتن (مرتان)."""

    name_ar = "بحر المضارع"
    name_en = "Al-Mudhare"
    key = "mudhare"
    bahr_type = "majzoo"
    tafeelat = (Mafaeelon, Fae_laton)
    arod_dharbs_map = {NoZehafNorEllah: (NoZehafNorEllah,)}


class Muqtadheb(Bahr):
    """بحر المقتضب: مفعولات مستفعلن (مرتان)."""

    name_ar = "بحر المقتضب"
    name_en = "Al-Muqtadheb"
    key = "muqtadheb"
    bahr_type = "majzoo"
    tafeelat = (Mafoolato, Mustafelon)
    arod_dharbs_map = {Tay: (Tay,), Khabal: (Tay,)}
    disallowed_zehafs_for_hashw = {0: ([],), 1: ([],)}


class Mujtath(Bahr):
    """بحر المجتث: مستفع لن فاعلاتن (مرتان)."""

    name_ar = "بحر المجتث"
    name_en = "Al-Mujtath"
    key = "mujtath"
    bahr_type = "majzoo"
    tafeelat = (Mustafe_lon, Faelaton)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Khaban, Tasheeth),
        Khaban: (NoZehafNorEllah, Khaban, Tasheeth),
    }
    disallowed_zehafs_for_hashw = {0: ([Kaff],), 1: ([Kaff],)}


class Mutakareb(Bahr):
    """بحر المتقارب: فعولن فعولن فعولن فعولن (مرتان)."""

    name_ar = "بحر المتقارب"
    name_en = "Al-Mutakareb"
    key = "mutakareb"
    bahr_type = "tam"
    tafeelat = (Fawlon, Fawlon, Fawlon, Fawlon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Hadhf, Qataa, Batr, Qasar, ThalmAndQasar),
        Qabadh: (NoZehafNorEllah, Hadhf, Qataa, Batr, Qasar, ThalmAndQasar),
        Hadhf: (NoZehafNorEllah, Hadhf, Qataa, Batr, Qasar, ThalmAndQasar),
    }
    disallowed_zehafs_for_hashw = {
        0: ([], [Thalm, Tharm], [Thalm, Tharm]),
        1: ([Thalm, Tharm], [Thalm, Tharm], [Thalm, Tharm]),
    }
    sub_bahrs = (MutakarebMajzoo,)


class Mutadarak(Bahr):
    """بحر المتدارك (الخبب / المحدث): فاعلن فاعلن فاعلن فاعلن (مرتان)."""

    name_ar = "بحر المتدارك"
    name_en = "Al-Mutadarak"
    key = "mutadarak"
    bahr_type = "tam"
    tafeelat = (Faelon, Faelon, Faelon, Faelon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Khaban, Tasheeth),
        Khaban: (NoZehafNorEllah, Khaban, Tasheeth),
        Tasheeth: (NoZehafNorEllah, Khaban, Tasheeth),
    }
    sub_bahrs = (MutadarakMajzoo, MutadarakMashtoor)


def get_all_meters() -> dict[str, type[Bahr]]:
    """Returns a dictionary mapping meter key names to their Bahr classes."""
    return {
        "taweel": Taweel,
        "madeed": Madeed,
        "baseet": Baseet,
        "wafer": Wafer,
        "kamel": Kamel,
        "hazaj": Hazaj,
        "rajaz": Rajaz,
        "ramal": Ramal,
        "saree": Saree,
        "munsareh": Munsareh,
        "khafeef": Khafeef,
        "mudhare": Mudhare,
        "muqtadheb": Muqtadheb,
        "mujtath": Mujtath,
        "mutakareb": Mutakareb,
        "mutadarak": Mutadarak,
    }
