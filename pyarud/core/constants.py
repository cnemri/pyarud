"""
Arabic Unicode Constants for PyArud.

Zero-dependency definitions for all Arabic letters, diacritics, Hamza variants,
and phonetic classification categories.
"""

# Base Letters
HAMZA = "\u0621"  # ء
ALEF_MADDA = "\u0622"  # آ
ALEF_HAMZA_ABOVE = "\u0623"  # أ
WAW_HAMZA = "\u0624"  # ؤ
ALEF_HAMZA_BELOW = "\u0625"  # إ
YEH_HAMZA = "\u0626"  # ئ
ALEF = "\u0627"  # ا
BEH = "\u0628"  # ب
TEH_MARBUTA = "\u0629"  # ة
TEH = "\u062a"  # ت
THEH = "\u062b"  # ث
JEEM = "\u062c"  # ج
HAH = "\u062d"  # ح
KHAH = "\u062e"  # خ
DAL = "\u062f"  # د
THAL = "\u0630"  # ذ
REH = "\u0631"  # ر
ZAIN = "\u0632"  # ز
SEEN = "\u0633"  # س
SHEEN = "\u0634"  # ش
SAD = "\u0635"  # ص
DAD = "\u0636"  # ض
TAH = "\u0637"  # ط
ZAH = "\u0638"  # ظ
AIN = "\u0639"  # ع
GHAIN = "\u063a"  # غ
TATWEEL = "\u0640"  # ـ
FEH = "\u0641"  # ف
QAF = "\u0642"  # ق
KAF = "\u0643"  # ك
LAM = "\u0644"  # ل
MEEM = "\u0645"  # م
NOON = "\u0646"  # ن
HEH = "\u0647"  # ه
HAA = HEH  # ه
HA = HEH  # ه
WAW = "\u0648"  # و
ALEF_MAKSURA = "\u0649"  # ى
YEH = "\u064a"  # ي
WASLA = "\u0671"  # ٱ
DAGGER_ALEF = "\u0670"  # ٰ (superscript / dagger alif)

# Diacritics (Harakat & Tanween)
FATHATAN = "\u064b"  # ً
DAMMATAN = "\u064c"  # ٌ
KASRATAN = "\u064d"  # ٍ
FATHA = "\u064e"  # َ
DAMMA = "\u064f"  # ُ
KASRA = "\u0650"  # ِ
SHADDA = "\u0651"  # ّ
SUKUN = "\u0652"  # ْ
MADDA_ABOVE = "\u0653"  # ٓ
HAMZA_ABOVE = "\u0654"  # ٔ
HAMZA_BELOW = "\u0655"  # ٕ

# Character Groupings
HARAKAT = (FATHA, DAMMA, KASRA)
TANWEEN = (FATHATAN, DAMMATAN, KASRATAN)
SHORT_VOWELS = HARAKAT
LONG_VOWELS = (ALEF, WAW, YEH, ALEF_MAKSURA, DAGGER_ALEF)
TASHKEEL = (
    FATHATAN,
    DAMMATAN,
    KASRATAN,
    FATHA,
    DAMMA,
    KASRA,
    SHADDA,
    SUKUN,
    MADDA_ABOVE,
    HAMZA_ABOVE,
    HAMZA_BELOW,
    DAGGER_ALEF,
)

ALPHABETIC_LETTERS = (
    ALEF,
    BEH,
    TEH,
    THEH,
    JEEM,
    HAH,
    KHAH,
    DAL,
    THAL,
    REH,
    ZAIN,
    SEEN,
    SHEEN,
    SAD,
    DAD,
    TAH,
    ZAH,
    AIN,
    GHAIN,
    FEH,
    QAF,
    KAF,
    LAM,
    MEEM,
    NOON,
    HEH,
    WAW,
    YEH,
)

HAMZAT = (
    HAMZA,
    ALEF_MADDA,
    ALEF_HAMZA_ABOVE,
    ALEF_HAMZA_BELOW,
    WAW_HAMZA,
    YEH_HAMZA,
    WASLA,
)

LETTERS = "".join(ALPHABETIC_LETTERS + HAMZAT + (ALEF_MAKSURA, TEH_MARBUTA))

SUN_LETTERS = "تثدذرزسشصضطظلن"
MOON_LETTERS = "ءأإآؤئابةحخعغفقكمهوياى"

ARABIC_PUNCTUATION = "،؛؟«»ـ"
ALL_PUNCTUATION = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~،؛؟«»"

# Fast lookup sets for O(1) membership testing
HARAKAT_SET = frozenset(HARAKAT)
TANWEEN_SET = frozenset(TANWEEN)
TASHKEEL_SET = frozenset(TASHKEEL)
SUN_LETTERS_SET = frozenset(SUN_LETTERS)
MOON_LETTERS_SET = frozenset(MOON_LETTERS)
LONG_VOWELS_SET = frozenset(LONG_VOWELS)
LETTERS_SET = frozenset(LETTERS)

# Deterministic meter priority weights for classical Farahidian ranking
METER_PRIORITY: dict[str, int] = {
    "taweel": 30,
    "hazaj": 25,
    "rajaz": 25,
    "saree": 25,
    "kamel": 20,
    "baseet": 20,
    "ramal": 20,
    "khafeef": 20,
    "mutakareb": 20,
    "mutadarak": 20,
    "wafer": 10,
    "munsareh": 15,
    "madeed": 15,
    "mujtath": 10,
    "mudhare": 10,
    "muqtadheb": 10,
}
