import itertools

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
    Tharm,
    Waqf,
    WaqfAndTay,
)


class Bahr:
    """
    Base class for defining poetic meters (Buhur).

    Subclasses define the standard feet (tafeelat), valid Arudh/Dharb combinations,
    and disallowed variations (Zihaf) for specific positions.
    """
    tafeelat: tuple[type[Tafeela], ...] = ()
    arod_dharbs_map: dict[type[BaseEllahZehaf], tuple[type[BaseEllahZehaf], ...]] | set[type[BaseEllahZehaf]] = {}
    sub_bahrs: tuple[type["Bahr"], ...] = ()
    only_one_shatr = False
    disallowed_zehafs_for_hashw: dict[int, tuple[list[type[BaseEllahZehaf]], ...]] = {}

    @property
    def last_tafeela(self):
        return self.tafeelat[-1]()

    def get_shatr_hashw_combinations(self, shatr_index=0):
        combinations = []
        # Hashw is everything except the last tafeela (Arudh/Dharb)
        for i, tafeela_class in enumerate(self.tafeelat[:-1]):
            tafeela = tafeela_class()
            forms = tafeela.all_zehaf_tafeela_forms()

            # Filter disallowed zehafs
            if shatr_index in self.disallowed_zehafs_for_hashw:
                disallowed = self.disallowed_zehafs_for_hashw[shatr_index]
                if i < len(disallowed):
                    forms = [f for f in forms if f.applied_ella_zehaf_class not in disallowed[i]]

            combinations.append(forms)
        return combinations

    def get_allowed_feet_patterns(self, shatr_index=0):
        """
        Returns a list of lists, where index i contains all valid binary strings for foot i.
        Used for granular analysis to align input to valid feet.
        """
        allowed_per_index = []

        # Hashw feet
        hashw_combs = self.get_shatr_hashw_combinations(shatr_index)
        for _, forms in enumerate(hashw_combs):
            allowed_per_index.append([str(f) for f in forms])

        # Last foot (Arudh/Dharb)
        last_feet = set()
        if self.only_one_shatr:
            # Treat endings as Arudh
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
    def detailed_patterns(self):
        """
        Returns structured patterns for Sadr and Ajuz separately.
        """
        patterns = {
            "sadr": [],
            "ajuz": [],
            "pairs": set() # Set of (sadr_pattern_str, ajuz_pattern_str) for validation
        }

        if self.only_one_shatr:
             # Single shatr meters (Mashtoor/Manhook)
             # We treat them as Sadr only
             hashw = self.get_shatr_hashw_combinations()
             
             # For single shatr, the "Arudh" is the end of the line
             
             # Collect all allowed endings from the map
             # In single shatr, arod_dharbs_map is a set or dict. 
             # If dict, keys are allowed endings? Or values?
             # Looking at subclasses: arod_dharbs_map = {Waqf, Kasf} (Set)
             
             endings = []
             if isinstance(self.arod_dharbs_map, set):
                 for z_cls in self.arod_dharbs_map:
                     try:
                         endings.append(z_cls(self.last_tafeela).modified_tafeela)
                     except AssertionError:
                         continue
             else:
                 # If it's a dict (some Mashtoors might use dict?), iterate keys
                 for z_cls in self.arod_dharbs_map:
                     try:
                         endings.append(z_cls(self.last_tafeela).modified_tafeela)
                     except AssertionError:
                         continue
            
             permutations = list(itertools.product(*hashw, endings))
             for p in permutations:
                 # p is a tuple of Tafeela objects
                 feet_strs = [str(t) for t in p]
                 full_str = "".join(feet_strs)
                 patterns["sadr"].append({
                     "pattern": full_str,
                     "feet": feet_strs,
                     "type": "single_shatr"
                 })
                 # Pairs logic doesn't apply or is trivial
                 patterns["pairs"].add((full_str, ""))

        else:
            # Two shatrs
            sadr_hashw = self.get_shatr_hashw_combinations(0)
            ajuz_hashw = self.get_shatr_hashw_combinations(1)

            for arudh_z_cls, dharb_z_list in self.arod_dharbs_map.items():
                # 1. Generate Arudh (End of Sadr)
                try:
                    arudh_obj = arudh_z_cls(self.last_tafeela).modified_tafeela
                except AssertionError:
                    continue
                
                arudh_str = str(arudh_obj)

                # 2. Generate Sadr variations for this Arudh
                sadr_perms = list(itertools.product(*sadr_hashw, [arudh_obj]))
                
                for sp in sadr_perms:
                    feet_strs = [str(t) for t in sp]
                    full_sadr = "".join(feet_strs)
                    
                    patterns["sadr"].append({
                        "pattern": full_sadr,
                        "feet": feet_strs,
                        "arudh_foot": arudh_str,
                        "arudh_class": arudh_z_cls.__name__
                    })

                    # 3. Generate compatible Dharbs (End of Ajuz)
                    # dharb_z_list is tuple of allowed classes for this Arudh
                    compatible_dharbs = []
                    for d_z in dharb_z_list:
                        try:
                            dharb_obj = d_z(self.last_tafeela).modified_tafeela
                            compatible_dharbs.append(dharb_obj)
                        except AssertionError:
                            continue
                    
                    if not compatible_dharbs:
                        continue

                    # 4. Generate Ajuz variations for these Dharbs
                    ajuz_perms = list(itertools.product(*ajuz_hashw, compatible_dharbs))
                    
                    for ap in ajuz_perms:
                        feet_strs_a = [str(t) for t in ap]
                        full_ajuz = "".join(feet_strs_a)
                        
                        patterns["ajuz"].append({
                            "pattern": full_ajuz,
                            "feet": feet_strs_a,
                            "dharb_foot": feet_strs_a[-1],
                            "allowed_arudhs": [arudh_str] # Valid only if Sadr ended with this
                        })
                        
                        # Register valid pair
                        patterns["pairs"].add((full_sadr, full_ajuz))

        # Deduplicate lists (dicts are not hashable, use careful logic or just return list)
        # Actually, we generated duplicates if multiple Arudh classes result in same pattern?
        # It's fine for now. The Processor will handle matching.
        
        # Add sub-bahrs
        for sub in self.sub_bahrs:
            sub_p = sub().detailed_patterns
            patterns["sadr"].extend(sub_p["sadr"])
            patterns["ajuz"].extend(sub_p["ajuz"])
            patterns["pairs"].update(sub_p["pairs"])
            
        return patterns

    @property
    def bait_combinations(self):
        # Deprecated wrapper for backward compatibility
        # Returns flattened list of full lines
        p = self.detailed_patterns
        if self.only_one_shatr:
            return sorted(list(set(x["pattern"] for x in p["sadr"])), key=len)
        
        # Reconstruct full lines from pairs
        return sorted([s+a for s,a in p["pairs"]], key=len)


# --- Sub-Bahrs Definitions ---


class RajazManhook(Bahr):
    tafeelat = (Mustafelon, Mustafelon)
    arod_dharbs_map = {NoZehafNorEllah, Khaban, Tay, Khabal, Qataa, KhabanAndQataa}
    only_one_shatr = True


class RajazMashtoor(Bahr):
    tafeelat = (Mustafelon, Mustafelon, Mustafelon)
    arod_dharbs_map = {NoZehafNorEllah, Khaban, Tay, Khabal, Qataa, KhabanAndQataa}
    only_one_shatr = True


class RajazMajzoo(Bahr):
    tafeelat = (Mustafelon, Mustafelon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Khaban, Tay, Khabal),
        Khaban: (NoZehafNorEllah, Khaban, Tay, Khabal),
        Tay: (NoZehafNorEllah, Khaban, Tay, Khabal),
        Khabal: (NoZehafNorEllah, Khaban, Tay, Khabal),
    }


class RamalMajzoo(Bahr):
    tafeelat = (Faelaton, Faelaton)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Khaban, Tasbeegh, Hadhf, HadhfAndKhaban),
        Khaban: (NoZehafNorEllah, Khaban, Tasbeegh, Hadhf, HadhfAndKhaban),
    }
    disallowed_zehafs_for_hashw = {0: ([Tasheeth],), 1: ([Tasheeth],)}


class SareeMashtoor(Bahr):
    tafeelat = (Mustafelon, Mustafelon, Mafoolato)
    arod_dharbs_map = {Waqf, Kasf}
    only_one_shatr = True


class MunsarehManhook(Bahr):
    tafeelat = (Mustafelon, Mafoolato)
    arod_dharbs_map = {Waqf, Kasf}
    only_one_shatr = True


class KhafeefMajzoo(Bahr):
    tafeelat = (Faelaton, Mustafe_lon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, KhabanAndQataa),
        Khaban: (Khaban,),
    }
    disallowed_zehafs_for_hashw = {0: ([Kaff, Shakal, Tasheeth],), 1: ([Kaff, Shakal, Tasheeth],)}


class MutakarebMajzoo(Bahr):
    tafeelat = (Fawlon, Fawlon, Fawlon)
    arod_dharbs_map = {Hadhf: (Hadhf, Batr)}
    disallowed_zehafs_for_hashw = {0: ([], [Thalm, Tharm]), 1: ([Thalm, Tharm], [Thalm, Tharm])}


class MutadarakMashtoor(Bahr):
    tafeelat = (Faelon, Faelon, Faelon)
    arod_dharbs_map = {NoZehafNorEllah, Khaban, Tasheeth, Tatheel, TarfeelAndKhaban}
    only_one_shatr = True


class MutadarakMajzoo(Bahr):
    tafeelat = (Faelon, Faelon, Faelon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Khaban, Tasheeth, Tatheel, TarfeelAndKhaban),
        Khaban: (NoZehafNorEllah, Khaban, Tasheeth, Tatheel, TarfeelAndKhaban),
        Tasheeth: (NoZehafNorEllah, Khaban, Tasheeth, Tatheel, TarfeelAndKhaban),
    }


# --- Meters Definition (Mirroring Bohour) ---


class Taweel(Bahr):
    tafeelat = (Fawlon, Mafaeelon, Fawlon, Mafaeelon)
    arod_dharbs_map = {Qabadh: (Qabadh, Hadhf, NoZehafNorEllah)}
    disallowed_zehafs_for_hashw = {
        0: ([], [], [Thalm, Tharm]),
        1: ([Thalm, Tharm], [], [Thalm, Tharm]),
    }


class Madeed(Bahr):
    tafeelat = (Faelaton, Faelon, Faelaton)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah,),
        Hadhf: (Qataa,),
        HadhfAndKhaban: (HadhfAndKhaban,),
    }
    disallowed_zehafs_for_hashw = {
        0: ([Shakal, Tasheeth], [Tasheeth]),
        1: ([Shakal, Tasheeth], [Tasheeth]),
    }


class BaseetMajzoo(Bahr):
    tafeelat = (Mustafelon, Faelon, Mustafelon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Tatheel, Qataa),
        Qataa: (NoZehafNorEllah,),
    }
    disallowed_zehafs_for_hashw = {0: ([], [Tasheeth]), 1: ([], [Tasheeth])}


class BaseetMukhalla(BaseetMajzoo):
    arod_dharbs_map = {KhabanAndQataa: (KhabanAndQataa,)}
    disallowed_zehafs_for_hashw = {0: ([], [Tasheeth]), 1: ([], [Tasheeth])}


class Baseet(Bahr):
    tafeelat = (Mustafelon, Faelon, Mustafelon, Faelon)
    arod_dharbs_map = {Khaban: (Khaban, Qataa)}
    disallowed_zehafs_for_hashw = {0: ([], [Tasheeth], []), 1: ([], [Tasheeth], [])}
    sub_bahrs = (BaseetMajzoo, BaseetMukhalla)


class WaferMajzoo(Bahr):
    tafeelat = (Mafaelaton, Mafaelaton)
    arod_dharbs_map = {NoZehafNorEllah: (NoZehafNorEllah, Asab), Asab: (NoZehafNorEllah, Asab)}


class Wafer(Bahr):
    tafeelat = (Mafaelaton, Mafaelaton, Mafaelaton)
    arod_dharbs_map = {Qataf: (Qataf,)}
    sub_bahrs = (WaferMajzoo,)


class KamelMajzoo(Bahr):
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
        Edmaar: (NoZehafNorEllah, Edmaar, Qataa, QataaAndEdmaar, Tatheel, TatheelAndEdmaar, Tarfeel, TarfeelAndEdmaar),
    }


class Kamel(Bahr):
    tafeelat = (Mutafaelon, Mutafaelon, Mutafaelon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Edmaar, Qataa, QataaAndEdmaar, HathathAndEdmaar),
        Edmaar: (NoZehafNorEllah, Edmaar, Qataa, QataaAndEdmaar, HathathAndEdmaar),
        Hathath: (Hathath, HathathAndEdmaar),
    }
    sub_bahrs = (KamelMajzoo,)


class Hazaj(Bahr):
    tafeelat = (Mafaeelon, Mafaeelon)
    arod_dharbs_map = {NoZehafNorEllah: (NoZehafNorEllah, Hadhf), Kaff: (NoZehafNorEllah, Hadhf)}
    disallowed_zehafs_for_hashw = {0: ([Qabadh],), 1: ([Qabadh],)}


class Rajaz(Bahr):
    tafeelat = (Mustafelon, Mustafelon, Mustafelon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Khaban, Tay, Khabal, Qataa, KhabanAndQataa),
        Khaban: (NoZehafNorEllah, Khaban, Tay, Khabal, Qataa, KhabanAndQataa),
        Tay: (NoZehafNorEllah, Khaban, Tay, Khabal, Qataa, KhabanAndQataa),
        Khabal: (NoZehafNorEllah, Khaban, Tay, Khabal, Qataa, KhabanAndQataa),
    }
    sub_bahrs = (RajazMajzoo, RajazMashtoor, RajazManhook)


class Ramal(Bahr):
    tafeelat = (Faelaton, Faelaton, Faelaton)
    arod_dharbs_map = {
        # Added NoZehafNorEllah (Sahih) to allowed Arudhs
        NoZehafNorEllah: (
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
            Qataa,  # originally Qasar
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
    tafeelat = (Mustafelon, Mustafelon, Mafoolato)
    arod_dharbs_map = {TayAndKasf: (TayAndKasf, Salam, WaqfAndTay), KhabalAndKasf: (KhabalAndKasf, Salam)}
    sub_bahrs = (SareeMashtoor,)


class Munsareh(Bahr):
    tafeelat = (Mustafelon, Mafoolato, Mustafelon)
    arod_dharbs_map = {Tay: (Tay, Qataa)}
    sub_bahrs = (MunsarehManhook,)


class Khafeef(Bahr):
    tafeelat = (Faelaton, Mustafe_lon, Faelaton)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Tasheeth, Hadhf, HadhfAndKhaban),
        Khaban: (NoZehafNorEllah, Tasheeth, Hadhf, HadhfAndKhaban),
    }
    sub_bahrs = (KhafeefMajzoo,)
    disallowed_zehafs_for_hashw = {0: ([Kaff, Shakal], []), 1: ([Kaff, Shakal], [])}


class Mudhare(Bahr):
    tafeelat = (Mafaeelon, Fae_laton)
    arod_dharbs_map = {NoZehafNorEllah: (NoZehafNorEllah,)}


class Muqtadheb(Bahr):
    tafeelat = (Mafoolato, Mustafelon)
    arod_dharbs_map = {Tay: (Tay,)}
    disallowed_zehafs_for_hashw = {0: ([Khabal],), 1: ([Khabal],)}


class Mujtath(Bahr):
    tafeelat = (Mustafe_lon, Faelaton)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Khaban, Tasheeth),
        Khaban: (NoZehafNorEllah, Khaban, Tasheeth),
    }
    disallowed_zehafs_for_hashw = {0: ([Kaff],), 1: ([Kaff],)}


class Mutakareb(Bahr):
    tafeelat = (Fawlon, Fawlon, Fawlon, Fawlon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Hadhf, Qataa, Batr),
        Qabadh: (NoZehafNorEllah, Hadhf, Qataa, Batr),
        Hadhf: (NoZehafNorEllah, Hadhf, Qataa, Batr),
    }
    disallowed_zehafs_for_hashw = {
        0: ([], [Thalm, Tharm], [Thalm, Tharm]),
        1: ([Thalm, Tharm], [Thalm, Tharm], [Thalm, Tharm]),
    }
    sub_bahrs = (MutakarebMajzoo,)


class Mutadarak(Bahr):
    tafeelat = (Faelon, Faelon, Faelon, Faelon)
    arod_dharbs_map = {
        NoZehafNorEllah: (NoZehafNorEllah, Khaban, Tasheeth),
        Khaban: (NoZehafNorEllah, Khaban, Tasheeth),
        Tasheeth: (NoZehafNorEllah, Khaban, Tasheeth),
    }
    sub_bahrs = (MutadarakMajzoo, MutadarakMashtoor)


def get_all_meters():
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
