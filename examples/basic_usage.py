import os
import sys

# Ensure we can import pyarud
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pyarud.processor import ArudhProcessor


def main():
    processor = ArudhProcessor()
    print("Arudh Processor Initialized.")
    print("-" * 60)

    examples = [
        # 1. Mutakarib (Correct)
        {
            "sadr": "أَخِي جَاوَزَ الظَّالِمُونَ الْمَدَى",
            "ajuz": "فَحَقَّ الْجِهَادُ وَحَقَّ الْفِدَا",
            "note": "Mutakarib: Fa'ulun Fa'ulun Fa'ulun Fa'ul",
        },
        # 2. Tawil
        {
            "sadr": "طَوِيلٌ لَهُ دُونَ الْبُحُورِ فَضَائِلُ",
            "ajuz": "فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِلُنْ",
            "note": "Tawil: Fa'ulun Mafa'ilun Fa'ulun Mafa'ilun",
        },
        # 3. Basit
        {
            "sadr": "إِنَّ الْبَسِيطَ لَدَيْهِ يُبْسَطُ الْأَمَلُ",
            "ajuz": "مُسْتَفْعِلُنْ فَاعِلُنْ مُسْتَفْعِلُنْ فَعِلُنْ",
            "note": "Basit: Mustaf'ilun Fa'ilun Mustaf'ilun Fa'ilun",
        },
        # 4. Kamil
        {
            "sadr": "كَمُلَ الْجَمَالُ مِنَ الْبُحُورِ الْكَامِلُ",
            "ajuz": "مُتَفَاعِلُنْ مُتَفَاعِلُنْ مُتَفَاعِلُنْ",
            "note": "Kamil: Muta'fa'ilun Muta'fa'ilun Muta'fa'ilun",
        },
        # 5. Wafir
        {
            "sadr": "بُحُورُ الشِّعْرِ وَافِرُهَا جَمِيلُ",
            "ajuz": "مُفَاعَلَتُنْ مُفَاعَلَتُنْ فَعُولُنْ",
            "note": "Wafir: Mafa'alatun Mafa'alatun Fa'ulun",
        },
        # 6. Rajaz
        {
            "sadr": "فِي أَبْحُرِ الْأَرْجَازِ بَحْرٌ يَسْهُلُ",
            "ajuz": "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ",
            "note": "Rajaz: Mustaf'ilun Mustaf'ilun Mustaf'ilun",
        },
        # 7. Khafif
        {
            "sadr": "يَا خَفِيفاً خَفَّتْ بِهِ الْحَرَكَاتُ",
            "ajuz": "فَاعِلَاتُنْ مُسْتَفْعِ لُنْ فَاعِلَاتُنْ",
            "note": "Khafif: Fa'ilatun Mustaf'i Lun Fa'ilatun",
        },
        # 8. Ramal
        {
            "sadr": "رَمَلُ الْأَبْحُرِ يَرْوِيهِ الثِّقَاتُ",
            "ajuz": "فَاعِلَاتُنْ فَاعِلَاتُنْ فَاعِلَاتُنْ",
            "note": "Ramal: Fa'ilatun Fa'ilatun Fa'ilatun",
        },
        # 9. Mutaqarib (Variation)
        {
            "sadr": "عَنِ الْمَرْءِ لَا تَسْأَلْ وَسَلْ عَنْ قَرِينِهِ",
            "ajuz": "فَكُلُّ قَرِينٍ بِالْمُقَارَنِ يَقْتَدِي",
            "note": "Mutaqarib (Tarafa bin Al-Abd)",
        },
        # 10. Mixed/Broken Example (To test mismatch visualization)
        {
            "sadr": "أَخِي جَاوَزَ الظَّالِمُونَ الْمَدَى",
            "ajuz": "وَهَذَا كَلامٌ ثَقِيلٌ جِدًّا",
            "note": "Broken Mutakarib (Second shatr is heavy/broken)",
        },
    ]

    for i, ex in enumerate(examples, 1):
        print(f"Example {i}: {ex['note']}")
        print(f"Sadr: {ex['sadr']}")
        print(f"Ajuz: {ex['ajuz']}")

        verses = [(ex["sadr"], ex["ajuz"])]
        result = processor.process_poem(verses)

        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Detected Meter: {result['meter']}")
            for verse_analysis in result["verses"]:
                print(f"  Sadr Pattern: {verse_analysis['sadr_text']}")
                print(
                    f"       Arudi: {verse_analysis['input_pattern'][: len(verse_analysis['input_pattern']) // 2]}..."
                )  # Roughly split for display
                print(f"       Match: {verse_analysis['best_ref_pattern']}")
                print(f"       Score: {verse_analysis['score']}")
        print("-" * 60)


if __name__ == "__main__":
    main()
