"""
Backward-compatibility shim for pyarud.models -> pyarud.models.analysis & enums.
"""

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

__all__ = [
    "FootAnalysis",
    "MeterMatchCandidate",
    "PoemAnalysis",
    "QafiyahAnalysis",
    "ShatrAnalysis",
    "VerseAnalysis",
    "MeterKey",
    "MeterVariation",
    "FootStatus",
    "RhymeType",
]
