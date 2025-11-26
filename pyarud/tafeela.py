from .zihaf import (
    Akal,
    Asab,
    Edmaar,
    Kaff,
    Khabal,
    Khaban,
    Khazal,
    Nakas,
    Qabadh,
    Shakal,
    Tasheeth,
    Tay,
    Thalm,
    Tharm,
    Waqas,
)

SUKUN_CHAR = "ْ"


class Tafeela:
    name = ""
    allowed_zehafs: list[type] = []
    pattern_int = 0
    applied_ella_zehaf_class = None

    def __init__(self):
        self.original_pattern = [int(d) for d in str(self.pattern_int)]
        self.pattern = self.original_pattern[:]
        self._manage_sukun_char()

    def _manage_sukun_char(self):
        pass

    def delete_from_pattern(self, index):
        if 0 <= index < len(self.pattern):
            del self.pattern[index]
            self.pattern_int = int("".join(map(str, self.pattern)))

    def add_to_pattern(self, index, number, char_mask):
        self.pattern.insert(index, number)
        self.pattern_int = int("".join(map(str, self.pattern)))

    def edit_pattern_at_index(self, index, number):
        if 0 <= index < len(self.pattern):
            self.pattern[index] = number
            self.pattern_int = int("".join(map(str, self.pattern)))

    def all_zehaf_tafeela_forms(self):
        forms = [self]
        for zehaf_class in self.allowed_zehafs:
            try:
                zehaf = zehaf_class(self)
                # Create a deep copy or new instance for the transformation
                # The Zehaf class takes a tafeela in constructor and modifies it in place
                # But wait, Zehaf logic: self.tafeela = deepcopy(tafeela)
                # So we get a new modified instance.
                forms.append(zehaf.modified_tafeela)
            except AssertionError:
                continue
        return forms

    def __str__(self):
        return "".join(map(str, self.pattern))

    def __repr__(self):
        return f"{self.name}({self.pattern_int})"

    def __eq__(self, other):
        if isinstance(other, Tafeela):
            return self.pattern_int == other.pattern_int
        return False

    def __hash__(self):
        return hash((self.name, self.pattern_int))


class Fawlon(Tafeela):
    name = "فعولن"
    allowed_zehafs = [Qabadh, Thalm, Tharm]
    pattern_int = 11010


class Faelon(Tafeela):
    name = "فاعلن"
    allowed_zehafs = [Khaban, Tasheeth]
    pattern_int = 10110


class Mafaeelon(Tafeela):
    name = "مفاعيلن"
    allowed_zehafs = [Qabadh, Kaff]
    pattern_int = 1101010


class Mustafelon(Tafeela):
    name = "مستفعلن"
    allowed_zehafs = [Khaban, Tay, Khabal]
    pattern_int = 1010110


class Mutafaelon(Tafeela):
    name = "متفاعلن"
    allowed_zehafs = [Edmaar, Waqas, Khazal]
    pattern_int = 1110110


class Mafaelaton(Tafeela):
    name = "مفاعلتن"
    allowed_zehafs = [Asab, Akal, Nakas]
    pattern_int = 1101110


class Mafoolato(Tafeela):
    name = "مفعولات"
    allowed_zehafs = [Khaban, Tay, Khabal]
    pattern_int = 1010101


class Fae_laton(Tafeela):
    name = "فاع لاتن"
    allowed_zehafs = [Kaff]
    pattern_int = 1011010


class Mustafe_lon(Tafeela):
    name = "مستفع لن"
    allowed_zehafs = [Khaban, Kaff]
    pattern_int = 1010110


class Faelaton(Tafeela):
    name = "فاعلاتن"
    allowed_zehafs = [Khaban, Kaff, Shakal, Tasheeth]
    pattern_int = 1011010
