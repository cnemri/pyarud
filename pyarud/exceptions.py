"""
Custom Exception Hierarchy for PyArud.

Defines domain-specific errors for Arabic prosody analysis, metric verification,
and text normalization failures.
"""

from __future__ import annotations


class PyArudError(Exception):
    """Base class for all exceptions raised by the PyArud library."""


class TashkeelError(PyArudError):
    """Raised when Arabic poetic text lacks mandatory diacritics (tashkeel)."""


class InvalidVerseError(PyArudError):
    """Raised when an input verse cannot be parsed or is syntactically malformed."""


class MeterNotFoundError(PyArudError):
    """Raised when a specified or queried meter name is not recognized."""


class ProsodyScansionError(PyArudError):
    """Raised when phonetic or metric scansion encounters an unresolvable error."""
