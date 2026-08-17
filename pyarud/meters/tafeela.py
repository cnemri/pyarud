"""
Prosodic Feet (Tafeelat / التفاعيل العروضية) for PyArud.

Defines the fundamental building blocks (feet) of classical Arabic poetry:
- Asbab (الأسباب): Sabab Khafif (10), Sabab Thaqeel (11)
- Awtad (الأوتاد): Watad Majmu' (110), Watad Mafruq (101)
- Fawasil (الفواصل): Fasilah Sughra (1110), Fasilah Kubra (11110)
"""

from __future__ import annotations

from typing import ClassVar

from ..core.constants import SUKUN
from .zihaf import (
    Akal,
    Asab,
    BaseEllahZehaf,
    Edmaar,
    Kaff,
    Kasf,
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

SUKUN_CHAR = SUKUN


class Tafeela:
    """Base class for an Arabic prosodic foot (تفعيلة)."""

    name: ClassVar[str] = ""
    name_en: ClassVar[str] = ""
    allowed_zehafs: ClassVar[list[type[BaseEllahZehaf]]] = []
    pattern_int: int = 0
    applied_ella_zehaf_class: type[BaseEllahZehaf] | None = None

    def __init__(self) -> None:
        self.original_pattern: list[int] = [int(d) for d in str(self.pattern_int)]
        self.pattern: list[int] = list(self.original_pattern)
        self.applied_ella_zehaf_class = None

    def delete_from_pattern(self, index: int) -> None:
        if 0 <= index < len(self.pattern):
            del self.pattern[index]
            self.pattern_int = int("".join(map(str, self.pattern))) if self.pattern else 0

    def add_to_pattern(self, index: int, number: int, char_mask: str = "") -> None:
        self.pattern.insert(index, number)
        self.pattern_int = int("".join(map(str, self.pattern)))

    def edit_pattern_at_index(self, index: int, number: int) -> None:
        if 0 <= index < len(self.pattern):
            self.pattern[index] = number
            self.pattern_int = int("".join(map(str, self.pattern)))

    def all_zehaf_tafeela_forms(self) -> list[Tafeela]:
        """Generate all permissible modified forms of this foot through its allowed Zihafat."""
        forms: list[Tafeela] = [self]
        for zehaf_class in self.allowed_zehafs:
            try:
                zehaf = zehaf_class(self)
                forms.append(zehaf.modified_tafeela)
            except AssertionError:
                continue
        return forms

    @property
    def pattern_str(self) -> str:
        return "".join(map(str, self.pattern))

    def __str__(self) -> str:
        return "".join(map(str, self.pattern))

    def __repr__(self) -> str:
        return f"{self.name}({self.pattern_str})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Tafeela):
            return self.pattern == other.pattern and self.name == other.name
        return False

    def __hash__(self) -> int:
        return hash((self.name, self.pattern_str))


class Fawlon(Tafeela):
    """فعولن (11010): Watad Majmu' (110) + Sabab Khafif (10)."""

    name = "فعولن"
    name_en = "Fawlon"
    allowed_zehafs = [Qabadh, Thalm, Tharm]
    pattern_int = 11010


class Faelon(Tafeela):
    """فاعلن (10110): Sabab Khafif (10) + Watad Majmu' (110)."""

    name = "فاعلن"
    name_en = "Faelon"
    allowed_zehafs = [Khaban, Tasheeth]
    pattern_int = 10110


class Mafaeelon(Tafeela):
    """مفاعيلن (1101010): Watad Majmu' (110) + 2 Sabab Khafif (10 10)."""

    name = "مفاعيلن"
    name_en = "Mafaeelon"
    allowed_zehafs = [Qabadh, Kaff]
    pattern_int = 1101010


class Mustafelon(Tafeela):
    """مستفعلن (1010110): 2 Sabab Khafif (10 10) + Watad Majmu' (110)."""

    name = "مستفعلن"
    name_en = "Mustafelon"
    allowed_zehafs = [Khaban, Tay, Khabal]
    pattern_int = 1010110


class Mutafaelon(Tafeela):
    """متفاعلن (1110110): Fasilah Sughra (1110) + Watad Majmu' (110)."""

    name = "متفاعلن"
    name_en = "Mutafaelon"
    allowed_zehafs = [Edmaar, Waqas, Khazal]
    pattern_int = 1110110


class Mafaelaton(Tafeela):
    """مفاعلتن (1101110): Watad Majmu' (110) + Fasilah Sughra (1110)."""

    name = "مفاعلتن"
    name_en = "Mafaelaton"
    allowed_zehafs = [Asab, Akal, Nakas]
    pattern_int = 1101110


class Mafoolato(Tafeela):
    """مفعولات (1010101): 2 Sabab Khafif (10 10) + Watad Mafruq (101)."""

    name = "مفعولات"
    name_en = "Mafoolato"
    allowed_zehafs = [Khaban, Tay, Khabal, Kasf]
    pattern_int = 1010101


class Fae_laton(Tafeela):
    """فاع لاتن (1011010): Watad Mafruq (101) + 2 Sabab Khafif (10 10)."""

    name = "فاع لاتن"
    name_en = "Fae_laton"
    allowed_zehafs = [Kaff]
    pattern_int = 1011010


class Mustafe_lon(Tafeela):
    """مستفع لن (1010110): Sabab Khafif (10) + Watad Mafruq (101) + Sabab Khafif (10)."""

    name = "مستفع لن"
    name_en = "Mustafe_lon"
    allowed_zehafs = [Khaban, Kaff, Tay, Shakal]
    pattern_int = 1010110


class Faelaton(Tafeela):
    """فاعلاتن (1011010): Sabab Khafif (10) + Watad Majmu' (110) + Sabab Khafif (10)."""

    name = "فاعلاتن"
    name_en = "Faelaton"
    allowed_zehafs = [Khaban, Kaff, Shakal]
    pattern_int = 1011010
