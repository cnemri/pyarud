"""
Performance and Throughput Benchmarks for PyArud.
"""

import time

import pytest

from pyarud import ArudhProcessor


@pytest.fixture
def processor():
    return ArudhProcessor()


def test_converter_throughput(processor):
    text = "إِنَّ البَسِيطَ لَدَيهِ يُبْسَطُ الأَمَلُ"
    n_iterations = 2000

    start = time.perf_counter()
    for _ in range(n_iterations):
        processor.converter.prepare_text(text)
    duration = time.perf_counter() - start

    rate = n_iterations / duration
    print(f"\nPhonetic Conversion Rate: {rate:,.0f} hemistichs/second ({duration * 1000 / n_iterations:.3f} ms/op)")
    assert rate > 2000, f"Expected > 2,000 ops/sec, got {rate:.1f}"


def test_verse_analysis_throughput(processor):
    sadr = "طَوِيلٌ لَهُ دُونَ البُحُورِ فَضَائِلُ"
    ajuz = "فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِلُ"
    n_iterations = 500

    start = time.perf_counter()
    for _ in range(n_iterations):
        processor.analyze_verse(sadr, ajuz)
    duration = time.perf_counter() - start

    rate = n_iterations / duration
    print(f"\nVerse Full Analysis Rate: {rate:,.0f} verses/second ({duration * 1000 / n_iterations:.3f} ms/op)")
    assert rate > 200, f"Expected > 200 verses/sec, got {rate:.1f}"
