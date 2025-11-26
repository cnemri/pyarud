from copy import deepcopy


class BaseEllahZehaf:
    """Base class for all Zehaf (changes) and Ellah (causes/defects)."""

    def __init__(self, tafeela):
        self.tafeela = deepcopy(tafeela)

    def modify_tafeela(self):
        """Modify self.tafeela in place. Must be overridden."""
        pass

    @property
    def modified_tafeela(self):
        if hasattr(self, "assertions"):
            assert all(self.assertions), "assertions failed"
        self.modify_tafeela()
        self.tafeela.applied_ella_zehaf_class = self.__class__
        return self.tafeela


class NoZehafNorEllah(BaseEllahZehaf):
    """Represents no change (Salim/Sahih)."""

    @property
    def modified_tafeela(self):
        self.tafeela.applied_ella_zehaf_class = None
        return self.tafeela


class BaseSingleHazfZehaf(BaseEllahZehaf):
    """Removes a character at a specific index."""

    affected_index: int

    def modify_tafeela(self):
        self.tafeela.delete_from_pattern(index=self.affected_index)


class BaseSingleTaskeenZehaf(BaseEllahZehaf):
    """Changes a Mutaharrik (1) to Sakin (0) at a specific index."""

    affected_index: int

    def modify_tafeela(self):
        assert self.tafeela.pattern[self.affected_index] == 1, f"Index {self.affected_index} should be mutaharrik (1)"
        self.tafeela.edit_pattern_at_index(index=self.affected_index, number=0)


# --- Single Zehafs ---
class Khaban(BaseSingleHazfZehaf):
    affected_index = 1


class Tay(BaseSingleHazfZehaf):
    affected_index = 3


class Waqas(BaseSingleHazfZehaf):
    affected_index = 1


class Qabadh(BaseSingleHazfZehaf):
    affected_index = 4


class Kaff(BaseSingleHazfZehaf):
    affected_index = 6


class Akal(BaseSingleHazfZehaf):
    affected_index = 4


class Kasf(BaseSingleHazfZehaf):
    affected_index = 6


class Tasheeth(BaseSingleHazfZehaf):
    affected_index = 2


class Thalm(BaseSingleHazfZehaf):
    affected_index = 0


class Edmaar(BaseSingleTaskeenZehaf):
    affected_index = 1


class Asab(BaseSingleTaskeenZehaf):
    affected_index = 4


# --- Doubled Zehafs ---
class BaseDoubledZehaf(BaseEllahZehaf):
    zehafs: list[type[BaseEllahZehaf]] = []

    def modify_tafeela(self):
        # Apply deletions first (highest index first to avoid shifting issues)
        hazf = [z for z in self.zehafs if issubclass(z, BaseSingleHazfZehaf)]
        taskeen = [z for z in self.zehafs if issubclass(z, BaseSingleTaskeenZehaf)]

        indices = sorted([z.affected_index for z in hazf], reverse=True)
        for idx in indices:
            self.tafeela.delete_from_pattern(index=idx)

        for z_cls in taskeen:
            z = z_cls(self.tafeela)
            self.tafeela = z.modified_tafeela


class Khabal(BaseDoubledZehaf):
    zehafs = [Khaban, Tay]


class Khazal(BaseDoubledZehaf):
    zehafs = [Edmaar, Tay]


class Shakal(BaseDoubledZehaf):
    zehafs = [Khaban, Kaff]


class Nakas(BaseDoubledZehaf):
    zehafs = [Asab, Kaff]


class TayAndKasf(BaseDoubledZehaf):
    zehafs = [Tay, Kasf]


class Tharm(BaseDoubledZehaf):
    zehafs = [Thalm, Qabadh]


# --- Ellal (Causes) ---
class Hadhf(BaseEllahZehaf):
    """Remove the last Sabab Khafif (10)."""

    def modify_tafeela(self):
        assert self.tafeela.pattern[-2:] == [1, 0]
        self.tafeela.delete_from_pattern(len(self.tafeela.pattern) - 1)
        self.tafeela.delete_from_pattern(len(self.tafeela.pattern) - 1)


class HadhfAndKhaban(BaseEllahZehaf):
    def modify_tafeela(self):
        self.tafeela = Hadhf(self.tafeela).modified_tafeela
        self.tafeela = Khaban(self.tafeela).modified_tafeela


class Qataf(BaseEllahZehaf):
    def modify_tafeela(self):
        self.tafeela = Hadhf(self.tafeela).modified_tafeela
        self.tafeela = Asab(self.tafeela).modified_tafeela


class Qataa(BaseEllahZehaf):
    """Remove last letter of Watad Majmu' and make previous letter Sakin."""

    def modify_tafeela(self):
        assert self.tafeela.pattern[-2:] == [1, 0]  # Ends in Watad Majmu (110 -> 10 after drop?)
        # Actually Watad Majmu is 110.
        # This asserts 1,0 at end.
        # Logic from source: delete last, make new last 0.
        self.tafeela.delete_from_pattern(len(self.tafeela.pattern) - 1)
        self.tafeela.edit_pattern_at_index(len(self.tafeela.pattern) - 1, 0)


class Tatheel(BaseEllahZehaf):
    """Add Sakin letter to Watad Majmu'."""

    def modify_tafeela(self):
        assert self.tafeela.pattern[-3:] == [1, 1, 0]
        self.tafeela.add_to_pattern(len(self.tafeela.pattern) - 1, 0, "ا")


class Tasbeegh(BaseEllahZehaf):
    """Add Sakin letter to Sabab Khafif."""

    def modify_tafeela(self):
        assert self.tafeela.pattern[-2:] == [1, 0]
        self.tafeela.add_to_pattern(len(self.tafeela.pattern) - 1, 0, "ا")


class TatheelAndEdmaar(BaseEllahZehaf):
    def modify_tafeela(self):
        self.tafeela = Tatheel(self.tafeela).modified_tafeela
        self.tafeela = Edmaar(self.tafeela).modified_tafeela


class Tarfeel(BaseEllahZehaf):
    """Add Sabab Khafif (10) to the end."""

    def modify_tafeela(self):
        # Add 'tun' (10)
        self.tafeela.add_to_pattern(len(self.tafeela.pattern), 1, "ت")
        self.tafeela.add_to_pattern(len(self.tafeela.pattern), 0, "ن")


class TarfeelAndEdmaar(BaseEllahZehaf):
    def modify_tafeela(self):
        self.tafeela = Tarfeel(self.tafeela).modified_tafeela
        self.tafeela = Edmaar(self.tafeela).modified_tafeela


class TarfeelAndKhaban(BaseEllahZehaf):
    def modify_tafeela(self):
        self.tafeela = Khaban(self.tafeela).modified_tafeela
        self.tafeela = Tarfeel(self.tafeela).modified_tafeela


class KhabanAndQataa(BaseEllahZehaf):
    def modify_tafeela(self):
        self.tafeela = Qataa(self.tafeela).modified_tafeela
        self.tafeela = Khaban(self.tafeela).modified_tafeela


class QataaAndEdmaar(BaseEllahZehaf):
    def modify_tafeela(self):
        self.tafeela = Qataa(self.tafeela).modified_tafeela
        self.tafeela = Edmaar(self.tafeela).modified_tafeela


class Hathath(BaseEllahZehaf):
    """Remove a full Watad Majmu' (110) from end."""

    def modify_tafeela(self):
        assert self.tafeela.pattern[-3:] == [1, 1, 0]
        for _ in range(3):
            self.tafeela.delete_from_pattern(len(self.tafeela.pattern) - 1)


class HathathAndEdmaar(BaseEllahZehaf):
    def modify_tafeela(self):
        self.tafeela = Hathath(self.tafeela).modified_tafeela
        self.tafeela = Edmaar(self.tafeela).modified_tafeela


class Salam(BaseEllahZehaf):
    """Remove Watad Mafruq (101) from end."""

    def modify_tafeela(self):
        assert self.tafeela.pattern[-3:] == [1, 0, 1]
        for _ in range(3):
            self.tafeela.delete_from_pattern(len(self.tafeela.pattern) - 1)


class Waqf(BaseEllahZehaf):
    """Sakin last letter of Watad Mafruq."""

    def modify_tafeela(self):
        assert self.tafeela.pattern[-3:] == [1, 0, 1]
        self.tafeela.edit_pattern_at_index(len(self.tafeela.pattern) - 1, 0)


class WaqfAndTay(BaseEllahZehaf):
    def modify_tafeela(self):
        self.tafeela = Tay(self.tafeela).modified_tafeela
        self.tafeela = Waqf(self.tafeela).modified_tafeela


class KhabalAndKasf(BaseEllahZehaf):
    def modify_tafeela(self):
        self.tafeela = Khabal(self.tafeela).modified_tafeela
        # Kasf is normally index 6, but after Khabal deletions?
        # Original logic: Kasf.affected_index -= 2
        k = Kasf(self.tafeela)
        k.affected_index -= 2
        self.tafeela = k.modified_tafeela


class Batr(BaseEllahZehaf):
    """Hadhf + Qataa (Cut tail, then cut new tail)."""

    def modify_tafeela(self):
        self.tafeela = Hadhf(self.tafeela).modified_tafeela
        self.tafeela = Qataa(self.tafeela).modified_tafeela
