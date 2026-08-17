"""
Backward-compatibility shim for pyarud.phonetics -> pyarud.core.phonetics.
"""

from .core.phonetics import ArudiConverter

__all__ = ["ArudiConverter"]
