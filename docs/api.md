# API Reference

This reference documents the public API of **PyArud v1.0.0**.

## Arudh Processor

::: pyarud.processor.ArudhProcessor
    options:
      members:
        - analyze_verse
        - analyze_poem
        - process_poem
        - validate_tashkeel

## Formatter Utilities

::: pyarud.formatters.console
    options:
      members:
        - format_verse_report
        - format_poem_report

## Arudi Converter (Phonetics Engine)

::: pyarud.core.phonetics.ArudiConverter
    options:
      members:
        - prepare_text
        - register_custom_spelling

## Qafiyah Analyzer (Rhyme Engine)

::: pyarud.qafiyah.analyzer.QafiyahAnalyzer
    options:
      members:
        - analyze

## Models & Data Classes

::: pyarud.models.analysis.VerseAnalysis
::: pyarud.models.analysis.PoemAnalysis
::: pyarud.models.analysis.ShatrAnalysis
::: pyarud.models.analysis.FootAnalysis
::: pyarud.models.analysis.QafiyahAnalysis
