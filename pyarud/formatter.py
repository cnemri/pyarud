"""
Backward-compatibility shim for pyarud.formatter -> pyarud.formatters.console.
"""

from .formatters.console import format_poem_report, format_verse_report

__all__ = [
    "format_verse_report",
    "format_poem_report",
]
