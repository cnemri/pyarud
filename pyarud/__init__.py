"""
PyArud: High-Performance, Zero-Dependency Arabic Prosody and Meter Analysis Engine.

Provides comprehensive tools for:
- Phonetic Arudi transcription (الكتابة العروضية)
- Metric pattern extraction (التقطيع العروضي بالترميز الثنائي)
- Classical Arabic meter identification (16 Buhur with all sub-meters)
- Foot-by-foot defect & variation analysis (الزحافات والعلل)
- Rhyme analysis (علم القافية والروي)
"""

from __future__ import annotations

__version__ = "1.0.0"

from .core.arabic import (
    is_haraka,
    is_moon_letter,
    is_shadda,
    is_sukun,
    is_sun_letter,
    is_tanween,
    normalize_ligatures,
    normalize_orthography,
    strip_punctuation,
    strip_tashkeel,
    strip_tatweel,
)
from .core.phonetics import ArudiConverter
from .exceptions import (
    InvalidVerseError,
    MeterNotFoundError,
    ProsodyScansionError,
    PyArudError,
    TashkeelError,
)
from .formatters.console import format_poem_report, format_verse_report
from .meters.bahr import (
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
    get_all_meters,
)
from .meters.engine import (
    DeterministicProsodyEngine,
    FootVariation,
    MeterGrammar,
    ShatrDerivation,
    get_deterministic_engine,
)
from .meters.tafeela import (
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
from .meters.zihaf import (
    BaseEllahZehaf,
    NoZehafNorEllah,
)
from .models.analysis import (
    FootAnalysis,
    MeterMatchCandidate,
    PoemAnalysis,
    QafiyahAnalysis,
    ShatrAnalysis,
    VerseAnalysis,
)
from .models.enums import (
    FootStatus,
    MeterKey,
    MeterVariation,
    RhymeType,
)
from .processor import ArudhProcessor
from .qafiyah.analyzer import QafiyahAnalyzer

__version__ = "1.0.0"

_DEFAULT_PROCESSOR: ArudhProcessor | None = None


def _get_processor() -> ArudhProcessor:
    global _DEFAULT_PROCESSOR
    if _DEFAULT_PROCESSOR is None:
        _DEFAULT_PROCESSOR = ArudhProcessor()
    return _DEFAULT_PROCESSOR


def analyze_verse(sadr: str, ajuz: str = "", forced_meter: str | None = None) -> VerseAnalysis:
    """Convenience top-level function to analyze a single Arabic verse."""
    return _get_processor().analyze_verse(sadr, ajuz, forced_meter=forced_meter)


def analyze_poem(verses: list[tuple[str, str]] | list[str], forced_meter: str | None = None) -> PoemAnalysis:
    """Convenience top-level function to analyze a full Arabic poem."""
    return _get_processor().analyze_poem(verses, meter_name=forced_meter)


def scan(
    verse_or_poem: str | list[tuple[str, str]] | list[str],
    forced_meter: str | None = None,
) -> VerseAnalysis | PoemAnalysis:
    """
    Ergonomic scansion function accepting either a single verse string (e.g. 'Sadr ... Ajuz' or 'Sadr * Ajuz')
    or a list of verses.
    """
    if isinstance(verse_or_poem, str):
        # Check for common hemistich separators: ' * ', ' ... ', '\t', ' # '
        separators = [" * ", " ... ", "   ", " # ", " - ", "\t"]
        for sep in separators:
            if sep in verse_or_poem:
                parts = verse_or_poem.split(sep, 1)
                return analyze_verse(parts[0].strip(), parts[1].strip(), forced_meter=forced_meter)
        return analyze_verse(verse_or_poem.strip(), "", forced_meter=forced_meter)
    return analyze_poem(verse_or_poem, forced_meter=forced_meter)


def to_arudi(text: str, saturate: bool = True) -> tuple[str, str]:
    """Convert Arabic text to Arudi phonetic text and binary pattern."""
    return _get_processor().converter.prepare_text(text, saturate=saturate)


def get_qafiyah(ajuz_text: str, is_muqayyad: bool = False) -> QafiyahAnalysis:
    """Analyze the rhyme of an Arabic verse ending."""
    return _get_processor().qafiyah_analyzer.analyze(ajuz_text, is_muqayyad=is_muqayyad)


__all__ = [
    # Top-Level Core Classes & Functions
    "ArudhProcessor",
    "ArudiConverter",
    "QafiyahAnalyzer",
    "DeterministicProsodyEngine",
    "analyze_verse",
    "analyze_poem",
    "scan",
    "to_arudi",
    "get_qafiyah",
    "format_verse_report",
    "format_poem_report",
    # Enums & Models
    "MeterKey",
    "MeterVariation",
    "FootStatus",
    "RhymeType",
    "FootAnalysis",
    "ShatrAnalysis",
    "QafiyahAnalysis",
    "VerseAnalysis",
    "PoemAnalysis",
    "MeterMatchCandidate",
    # Exceptions
    "PyArudError",
    "TashkeelError",
    "InvalidVerseError",
    "MeterNotFoundError",
    "ProsodyScansionError",
    # Arabic normalizers & classifiers
    "strip_tashkeel",
    "strip_tatweel",
    "strip_punctuation",
    "normalize_ligatures",
    "normalize_orthography",
    "is_sun_letter",
    "is_moon_letter",
    "is_haraka",
    "is_tanween",
    "is_shadda",
    "is_sukun",
    # Meters & Feet
    "Bahr",
    "get_all_meters",
    "Taweel",
    "Madeed",
    "Baseet",
    "Wafer",
    "Kamel",
    "Hazaj",
    "Rajaz",
    "Ramal",
    "Saree",
    "Munsareh",
    "Khafeef",
    "Mudhare",
    "Muqtadheb",
    "Mujtath",
    "Mutakareb",
    "Mutadarak",
    "BaseetMajzoo",
    "BaseetMukhalla",
    "WaferMajzoo",
    "KamelMajzoo",
    "RajazMajzoo",
    "RajazMashtoor",
    "RajazManhook",
    "RamalMajzoo",
    "SareeMashtoor",
    "MunsarehManhook",
    "KhafeefMajzoo",
    "MutakarebMajzoo",
    "MutadarakMajzoo",
    "MutadarakMashtoor",
    "Tafeela",
    "Fawlon",
    "Faelon",
    "Mafaeelon",
    "Mustafelon",
    "Mutafaelon",
    "Mafaelaton",
    "Mafoolato",
    "Fae_laton",
    "Mustafe_lon",
    "Faelaton",
    "BaseEllahZehaf",
    "NoZehafNorEllah",
    "MeterGrammar",
    "FootVariation",
    "ShatrDerivation",
    "get_deterministic_engine",
    "__version__",
]
