"""
Domain Models and Strongly Typed Dataclasses for Arabic Prosody Scansion.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterator


@dataclass(slots=True)
class FootAnalysis:
    """Detailed metric analysis of a single poetic foot (Taf'eela)."""

    foot_index: int
    expected_pattern: str
    actual_segment: str
    base_tafeela: str = ""
    actual_tafeela: str = ""
    zihaf_name_ar: str = "سالمة"
    zihaf_name_en: str = "Salim"
    score: float = 1.0
    status: str = "ok"  # 'ok', 'broken', 'missing', 'extra_bits'

    @property
    def is_valid(self) -> bool:
        """True if the foot matched standard or permitted Zihaf variations."""
        return self.status == "ok"

    def to_dict(self) -> dict[str, Any]:
        """Convert foot analysis to a JSON-serializable dictionary."""
        return asdict(self)

    def __bool__(self) -> bool:
        return bool(self.actual_segment)

    def __str__(self) -> str:
        name = self.actual_tafeela or self.base_tafeela or "تفعيلة"
        return f"{name} ({self.actual_segment}) - {self.zihaf_name_ar}"


@dataclass(slots=True)
class ShatrAnalysis:
    """Prosodic analysis of a single hemistich (Sadr or Ajuz)."""

    text: str
    arudi_text: str
    pattern: str
    feet: list[FootAnalysis] = field(default_factory=list)
    score: float = 1.0
    is_valid: bool = True

    def __iter__(self) -> Iterator[FootAnalysis]:
        """Iterate over individual feet within this hemistich."""
        return iter(self.feet)

    def __len__(self) -> int:
        """Number of feet in this hemistich."""
        return len(self.feet)

    def __getitem__(self, index: int) -> FootAnalysis:
        """Access foot analysis by index."""
        return self.feet[index]

    def __bool__(self) -> bool:
        return bool(self.text)

    def to_dict(self) -> dict[str, Any]:
        """Convert shatr analysis to a dictionary."""
        return {
            "text": self.text,
            "arudi_text": self.arudi_text,
            "pattern": self.pattern,
            "score": self.score,
            "is_valid": self.is_valid,
            "feet": [f.to_dict() for f in self.feet],
        }


@dataclass(slots=True)
class QafiyahAnalysis:
    """Comprehensive Rhyme (علم القافية) extraction and classification."""

    rawi: str = ""
    rawi_haraka: str = ""
    wasl: str | None = None
    khuruj: str | None = None
    ridf: str | None = None
    tasees: str | None = None
    dakhil: str | None = None
    qafiyah_text: str = ""
    qafiyah_pattern: str = ""
    qafiyah_type_ar: str = "المتواتر"
    qafiyah_type_en: str = "Al-Mutawatir"
    rhyme_classification: str = "mutlaqah"  # 'mutlaqah' or 'muqayyadah'

    def to_dict(self) -> dict[str, Any]:
        """Convert rhyme analysis to a dictionary."""
        return asdict(self)

    def __bool__(self) -> bool:
        return bool(self.rawi)

    def __str__(self) -> str:
        return f"الروي: {self.rawi} ({self.rawi_haraka}) | القافية: {self.qafiyah_type_ar}"


@dataclass(slots=True)
class VerseAnalysis:
    """Full prosodic analysis of an entire poetic verse (Bait)."""

    verse_index: int = 0
    sadr_text: str = ""
    ajuz_text: str = ""
    meter_key: str = "unknown"
    meter_name_ar: str = "غير معروف"
    meter_name_en: str = "Unknown"
    bahr_type: str = "tam"
    standard_pattern: str = ""
    score: float = 0.0
    sadr: ShatrAnalysis | None = None
    ajuz: ShatrAnalysis | None = None
    qafiyah: QafiyahAnalysis | None = None
    is_valid: bool = True
    errors: list[str] = field(default_factory=list)

    @property
    def meter(self) -> str:
        """Alias for meter_key for ergonomic access."""
        return self.meter_key

    @property
    def is_sound(self) -> bool:
        """Alias for is_valid."""
        return self.is_valid

    def __bool__(self) -> bool:
        """Truthiness of the verse evaluation: True if verse has text."""
        return bool(self.sadr_text or self.ajuz_text)

    def __str__(self) -> str:
        status = "صحيح" if self.is_valid else "مكسور"
        return f"[{self.meter_name_ar} ({self.bahr_type})] {self.sadr_text} ... {self.ajuz_text} ({status})"

    def to_dict(self) -> dict[str, Any]:
        """Convert entire verse analysis to a deeply nested JSON-serializable dictionary."""
        return {
            "verse_index": self.verse_index,
            "sadr_text": self.sadr_text,
            "ajuz_text": self.ajuz_text,
            "meter_key": self.meter_key,
            "meter_name_ar": self.meter_name_ar,
            "meter_name_en": self.meter_name_en,
            "bahr_type": self.bahr_type,
            "standard_pattern": self.standard_pattern,
            "score": self.score,
            "is_valid": self.is_valid,
            "errors": list(self.errors),
            "sadr": self.sadr.to_dict() if self.sadr is not None else None,
            "ajuz": self.ajuz.to_dict() if self.ajuz is not None else None,
            "qafiyah": self.qafiyah.to_dict() if self.qafiyah is not None else None,
        }


@dataclass(slots=True)
class PoemAnalysis:
    """Comprehensive prosodic and metric analysis of an entire multi-verse poem."""

    meter_key: str = "unknown"
    meter_name_ar: str = "غير محدد"
    meter_name_en: str = "Unknown"
    bahr_type: str = "unknown"
    verses: list[VerseAnalysis] = field(default_factory=list)
    average_score: float = 0.0
    is_homogeneous: bool = True
    dominant_rawi: str | None = None
    total_verses: int = 0
    valid_verses_count: int = 0

    def __iter__(self) -> Iterator[VerseAnalysis]:
        """Iterate over the verses in the poem."""
        return iter(self.verses)

    def __len__(self) -> int:
        """Total number of verses in the poem."""
        return len(self.verses)

    def __getitem__(self, index: int) -> VerseAnalysis:
        """Access a verse analysis by index."""
        return self.verses[index]

    def __bool__(self) -> bool:
        """True if the poem has analyzed verses and a recognized meter."""
        return bool(self.verses) and self.meter_key != "unknown"

    def __str__(self) -> str:
        return (
            f"Poem({self.meter_name_ar}, {self.total_verses} verses, "
            f"{self.valid_verses_count} valid, avg_score={self.average_score:.2f})"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert entire poem analysis to dictionary."""
        return {
            "meter_key": self.meter_key,
            "meter_name_ar": self.meter_name_ar,
            "meter_name_en": self.meter_name_en,
            "bahr_type": self.bahr_type,
            "average_score": self.average_score,
            "is_homogeneous": self.is_homogeneous,
            "dominant_rawi": self.dominant_rawi,
            "total_verses": self.total_verses,
            "valid_verses_count": self.valid_verses_count,
            "verses": [v.to_dict() for v in self.verses],
        }


@dataclass(slots=True)
class MeterMatchCandidate:
    """Internal candidate score for diagnostic alignment."""

    meter_key: str
    meter_name_ar: str
    meter_name_en: str
    bahr_type: str
    score: float
    valid_pair: bool
    sadr_match: dict[str, Any] | None = None
    ajuz_match: dict[str, Any] | None = None
    sadr_input_pattern: str = ""
    ajuz_input_pattern: str = ""
