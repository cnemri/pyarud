"""
Enumerations for Arabic Prosody and Metric Analysis.
"""

from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """String-compatible Enum for Python 3.10+ support."""

    def __str__(self) -> str:
        return str(self.value)


class MeterKey(StrEnum):
    """Canonical identifier keys for the 16 classical Arabic meters."""

    TAWEEL = "taweel"
    MADEED = "madeed"
    BASEET = "baseet"
    WAFER = "wafer"
    KAMEL = "kamel"
    HAZAJ = "hazaj"
    RAJAZ = "rajaz"
    RAMAL = "ramal"
    SAREE = "saree"
    MUNSAREH = "munsareh"
    KHAFEEF = "khafeef"
    MUDHARE = "mudhare"
    MUQTADHEB = "muqtadheb"
    MUJTATH = "mujtath"
    MUTAKAREB = "mutakareb"
    MUTADARAK = "mutadarak"
    UNKNOWN = "unknown"


class MeterVariation(StrEnum):
    """Sub-meter metric length and structure variations."""

    TAM = "tam"
    MAJZOO = "majzoo"
    MASHTOOR = "mashtoor"
    MANHOOK = "manhook"
    MUKHALLA = "mukhalla"


class FootStatus(StrEnum):
    """Diagnostic scansion status of an individual metric foot (Taf'eela)."""

    OK = "ok"
    BROKEN = "broken"
    MISSING = "missing"
    EXTRA_BITS = "extra_bits"


class RhymeType(StrEnum):
    """Classical Arabic rhyme movement type (حركة القافية)."""

    MUTLAQAH = "mutlaqah"  # المطلقة (Vocalized Rawi)
    MUQAYYADAH = "muqayyadah"  # المقيدة (Sakin Rawi)
