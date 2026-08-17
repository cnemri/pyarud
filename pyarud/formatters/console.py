"""
Console and ASCII formatting utilities for prosodic analysis.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.analysis import PoemAnalysis, VerseAnalysis


def format_verse_report(verse: VerseAnalysis) -> str:
    """Formats a single verse analysis into a structured summary report."""
    lines: list[str] = []
    lines.append(f"═══ [البيت {verse.verse_index + 1}] {verse.meter_name_ar} ({verse.meter_name_en}) ═══")
    lines.append(f"• الصدر: {verse.sadr_text}")
    if verse.ajuz_text:
        lines.append(f"• العجز: {verse.ajuz_text}")
    lines.append(f"• النمط العروضي: {verse.standard_pattern}")
    status_str = "صحيح موزون" if verse.is_valid else "مكسور أو به خلل"
    lines.append(f"• درجة التوافق: {verse.score * 100:.1f}% | الحالة: {status_str}")

    # Sadr breakdown
    if verse.sadr:
        lines.append("\n  [تقطيع الصدر]")
        for foot in verse.sadr.feet:
            status_sym = "✓" if foot.status == "ok" else "✗"
            lines.append(
                f"    {status_sym} التفعيلة {foot.foot_index + 1}: {foot.actual_tafeela or foot.base_tafeela} "
                f"({foot.actual_segment}) - {foot.zihaf_name_ar}"
            )

    # Ajuz breakdown
    if verse.ajuz:
        lines.append("\n  [تقطيع العجز]")
        for foot in verse.ajuz.feet:
            status_sym = "✓" if foot.status == "ok" else "✗"
            lines.append(
                f"    {status_sym} التفعيلة {foot.foot_index + 1}: {foot.actual_tafeela or foot.base_tafeela} "
                f"({foot.actual_segment}) - {foot.zihaf_name_ar}"
            )

    # Qafiyah
    if verse.qafiyah and verse.qafiyah.rawi:
        lines.append("\n  [علم القافية]")
        lines.append(f"    • الروي: {verse.qafiyah.rawi} ({verse.qafiyah.rawi_haraka or 'ساكن'})")
        if verse.qafiyah.wasl:
            lines.append(f"    • الوصل: {verse.qafiyah.wasl}")
        if verse.qafiyah.ridf:
            lines.append(f"    • الردف: {verse.qafiyah.ridf}")
        if verse.qafiyah.tasees:
            lines.append(f"    • التأسيس: {verse.qafiyah.tasees} (الدخيل: {verse.qafiyah.dakhil})")
        lines.append(f"    • نوع القافية: {verse.qafiyah.qafiyah_type_ar} ({verse.qafiyah.rhyme_classification})")
        lines.append(f"    • مقطع القافية: {verse.qafiyah.qafiyah_text} [{verse.qafiyah.qafiyah_pattern}]")

    return "\n".join(lines)


def format_poem_report(poem: PoemAnalysis) -> str:
    """Formats an entire poem analysis into an executive prosodic report."""
    lines: list[str] = [
        "╔══════════════════════════════════════════════════════════════╗",
        f"║  تقرير التحليل العروضي الشامل: {poem.meter_name_ar:<28} ║",
        "╚══════════════════════════════════════════════════════════════╝",
        f"• البحر المكتشف: {poem.meter_name_ar} ({poem.meter_name_en}) - نوع البحر: {poem.bahr_type}",
        f"• عدد الأبيات: {poem.total_verses} | الأبيات السليمة: {poem.valid_verses_count}",
        f"• متوسط التوافق العروضي: {poem.average_score * 100:.1f}%",
        f"• وحدة البحر: {'تام ومتجانس' if poem.is_homogeneous else 'متفاوت / متعدد البحور'}",
    ]

    if poem.dominant_rawi:
        lines.append(f"• حرف الروي السائد: {poem.dominant_rawi}")

    lines.append("\n" + "─" * 64 + "\n")

    for v in poem.verses:
        lines.append(format_verse_report(v))
        lines.append("")

    return "\n".join(lines)
