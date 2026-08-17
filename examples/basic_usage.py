import os
import sys

# Ensure we can import pyarud
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from pyarud.processor import ArudhProcessor


def main():
    processor = ArudhProcessor()
    print("Arudh Processor Initialized.")
    print("-" * 60)

    examples = [
        # --- Standard Correct Examples ---
        {
            "sadr": "أَخِي جَاوَزَ الظَّالِمُونَ الْمَدَى",
            "ajuz": "فَحَقَّ الْجِهَادُ وَحَقَّ الْفِدَا",
            "note": "1. Mutakarib (Correct)",
        },
        {
            "sadr": "طَوِيلٌ لَهُ دُونَ الْبُحُورِ فَضَائِلُ",
            "ajuz": "فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِلُنْ",
            "note": "2. Tawil (Correct)",
        },
        {
            "sadr": "بَحْرٌ سَرِيعٌ مَا لَهُ سَاحِلُ",
            "ajuz": "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ فَاعِلُنْ",
            "note": "3. Saree (Correct)",
        },
        # --- Broken Examples (Forced Meter) ---
        # Example 1: Broken Mutakarib (The original broken case)
        # Broken Ajuz: "Wa hadha kalamun thaqilun jidda"
        # Analysis: "Jidda" breaks the flow or has extra bits.
        {
            "sadr": "أَخِي جَاوَزَ الظَّالِمُونَ الْمَدَى",
            "ajuz": "وَهَذَا كَلامٌ ثَقِيلٌ جِدًّا",
            "note": "4. Broken Mutakarib (Extra bits at end)",
            "force_meter": "mutakareb",
        },
        # Example 2: Broken Kamil
        # Sadr is correct Kamil.
        # Ajuz: "Wa la-kin-na fi-hi kash-run ka-beer" (Intentionally messed up scanning)
        # "Mustafa'ilun" pattern broken in middle.
        {
            "sadr": "كَمُلَ الْجَمَالُ مِنَ الْبُحُورِ الْكَامِلُ",
            "ajuz": "وَلَكِنَّ فِيهِ كَسْرٌ كَبِيرٌ جِدًّا",
            "note": "5. Broken Kamil (Rhythm break in Ajuz)",
            "force_meter": "kamel",
        },
        # Example 3: Broken Wafir
        # Sadr: Correct Wafir.
        # Ajuz: "Mufa'alatun Mufa'alatun" but missing last foot.
        {
            "sadr": "بُحُورُ الشِّعْرِ وَافِرُهَا جَمِيلُ",
            "ajuz": "مُفَاعَلَتُنْ مُفَاعَلَتُنْ",
            "note": "6. Broken Wafir (Missing last foot in Ajuz)",
            "force_meter": "wafer",
        },
        # Example 4: Broken Rajaz
        # "Fi abhuril arjazi bahrun yashulu"
        # Let's add a word that breaks the "Mustaf'ilun" flow.
        {
            "sadr": "فِي أَبْحُرِ الْأَرْجَازِ بَحْرٌ لَيْسَ يَسْهُلُ",
            "ajuz": "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ",
            "note": "7. Broken Rajaz (Added 'laysa' in Sadr breaking flow)",
            "force_meter": "rajaz",
        },
        # Example 5: Broken Basit
        # "Inna al-basita ladayhi yubsatu al-amalu"
        # Let's truncate the Sadr significantly.
        {
            "sadr": "إِنَّ الْبَسِيطَ لَدَيْهِ",
            "ajuz": "مُسْتَفْعِلُنْ فَاعِلُنْ مُسْتَفْعِلُنْ فَعِلُنْ",
            "note": "8. Broken Basit (Significantly truncated Sadr)",
            "force_meter": "baseet",
        },
    ]

    for ex in examples:
        print(f"Example: {ex['note']}")
        print(f"Sadr: {ex['sadr']}")
        print(f"Ajuz: {ex['ajuz']}")

        verses = [(ex["sadr"], ex["ajuz"])]
        force_meter = ex.get("force_meter")

        if force_meter:
            print(f"ℹ️  Forcing Meter: {force_meter}")
        else:
            print("ℹ️  Auto-detecting Meter...")

        result = processor.process_poem(verses, meter_name=force_meter)

        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            detected = result["meter"]
            print(f"📊 Meter: {detected}")

            for v in result["verses"]:
                print(f"  Overall Score: {v['score']}")

                # Function to print analysis nicely
                def print_shatr(shatr_name, analysis):
                    print(f"  {shatr_name} Analysis:")
                    if not analysis:
                        print("    (None)")
                        return
                    for foot in analysis:
                        status = foot["status"]
                        if status == "ok":
                            icon = "✅"
                        elif status == "missing":
                            icon = "❓"
                        elif status == "extra_bits":
                            icon = "⚠️ "
                        else:
                            icon = "❌"

                        # Formatting pattern display
                        exp = foot["expected_pattern"] if foot["expected_pattern"] else "None"
                        act = foot["actual_segment"]

                        print(f"    {icon} Foot {foot['foot_index']}: Expected {exp:<8} | Got {act:<8} ({status})")

                print_shatr("Sadr", v["sadr_analysis"])
                if v["ajuz_analysis"]:
                    print_shatr("Ajuz", v["ajuz_analysis"])

        print("-" * 60)


if __name__ == "__main__":
    main()
