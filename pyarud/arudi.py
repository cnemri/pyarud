"""
Backwards-compatible Arudi module for PyArud.

Re-exports ArudiConverter and phonetic utilities from pyarud.phonetics.
"""

from .phonetics import ArudiConverter

__all__ = ["ArudiConverter"]
