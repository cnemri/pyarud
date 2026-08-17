"""
Backward-compatibility shim for pyarud.qafiyah -> pyarud.qafiyah.analyzer.
"""

from .qafiyah.analyzer import QafiyahAnalyzer

__all__ = ["QafiyahAnalyzer"]
