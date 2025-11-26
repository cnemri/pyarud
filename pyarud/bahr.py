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

    @property
    def bait_combinations(self):
        all_combs = []

        if self.only_one_shatr:
            # Just generate one shatr permutations
            hashw = self.get_shatr_hashw_combinations()
            arudh_dharbs = []
            for z_cls in self.arod_dharbs_map:
                try:
                    arudh_dharbs.append(z_cls(self.last_tafeela).modified_tafeela)
                except AssertionError:
                    continue

            permutations = list(itertools.product(*hashw, arudh_dharbs))
            # Convert tuples to pattern strings
            for p in permutations:
                all_combs.append("".join(str(t) for t in p))
        else:
            # Two shatrs
            for arudh_z_cls, dharb_z_list in self.arod_dharbs_map.items():
                try:
                    arudh = arudh_z_cls(self.last_tafeela).modified_tafeela
                except AssertionError:
                    continue

                dharbs = []
                for d_z in dharb_z_list:
                    try:
                        dharbs.append(d_z(self.last_tafeela).modified_tafeela)
                    except AssertionError:
                        continue

                # Generate Sadr
                sadr_hashw = self.get_shatr_hashw_combinations(0)
                sadr_perms = list(itertools.product(*sadr_hashw, [arudh]))

                # Generate Ajuz
                ajuz_hashw = self.get_shatr_hashw_combinations(1)
                ajuz_perms = list(itertools.product(*ajuz_hashw, dharbs))

                # Combine
                for s in sadr_perms:
                    s_str = "".join(str(t) for t in s)
                    for a in ajuz_perms:
                        a_str = "".join(str(t) for t in a)
                        all_combs.append(s_str + a_str)

        # Add sub-bahrs
        for sub in self.sub_bahrs:
            all_combs.extend(sub().bait_combinations)

        return sorted(list(set(all_combs)), key=len)


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
