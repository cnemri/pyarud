"""
Classical Zihafat (Poetic Variations) and 'Ilal (Defects/Modifications) for PyArud.

In Arabic prosody:
- Zihaf (زحاف): A non-binding modification occurring mostly in the Hashw (interior feet)
  by dropping a Sakin or muting a Mutaharrik in a Sabab.
- 'Ilah (علة): A binding modification occurring in the Arudh (hemistich end) or Dharb (verse end),
  which may involve addition (زيادة) or deletion (نقص).
"""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from .tafeela import Tafeela


class BaseEllahZehaf:
    """Base class for all Zihaf (prosodic modifications) and 'Ilal (cadence defects)."""

    name_ar: ClassVar[str] = "سالمة"
    name_en: ClassVar[str] = "Salim"
    description_ar: ClassVar[str] = "خالية من التغيير"

    def __init__(self, tafeela: Tafeela) -> None:
        self.tafeela = deepcopy(tafeela)
        self._modified = False

    def modify_tafeela(self) -> None:
        """Modify self.tafeela pattern in place."""
        pass

    @property
    def modified_tafeela(self) -> Tafeela:
        if self._modified:
            return self.tafeela

        self.modify_tafeela()
        self.tafeela.applied_ella_zehaf_class = self.__class__
        self._modified = True
        return self.tafeela


class NoZehafNorEllah(BaseEllahZehaf):
    """Represents a sound, unmodified foot (سالم / صحيح)."""

    name_ar = "سالمة (صحيحة)"
    name_en = "Salim / Sahih"
    description_ar = "تفعيلة سالمة من الزحاف والعلة"

    @property
    def modified_tafeela(self) -> Tafeela:
        self.tafeela.applied_ella_zehaf_class = None
        return self.tafeela


class BaseSingleHazfZehaf(BaseEllahZehaf):
    """Removes a character (Sakin or Mutaharrik) at a specific index."""

    affected_index: int = 0

    def modify_tafeela(self) -> None:
        self.tafeela.delete_from_pattern(index=self.affected_index)


class BaseSingleTaskeenZehaf(BaseEllahZehaf):
    """Changes a Mutaharrik (1) to Sakin (0) at a specific index."""

    affected_index: int = 0

    def modify_tafeela(self) -> None:
        if self.tafeela.pattern[self.affected_index] == 1:
            self.tafeela.edit_pattern_at_index(index=self.affected_index, number=0)


# ==========================================
# 1. Single Zihafat (الزحاف المفرد)
# ==========================================


class Khaban(BaseSingleHazfZehaf):
    """Khabn (الخبن): Deletion of the 2nd Sakin letter (e.g. فاعلن -> فعلن, مستفعلن -> مفاعلن)."""

    name_ar = "مخبونة (الخبن)"
    name_en = "Khaban"
    description_ar = "حذف الثاني الساكن"
    affected_index = 1


class Tay(BaseSingleHazfZehaf):
    """Tayy (الطي): Deletion of the 4th Sakin letter (e.g. مستفعلن -> مفتعلن)."""

    name_ar = "مطوية (الطي)"
    name_en = "Tay"
    description_ar = "حذف الرابع الساكن"
    affected_index = 3


class Waqas(BaseSingleHazfZehaf):
    """Waqas (الوقص): Deletion of the 2nd Mutaharrik letter (e.g. متفاعلن -> مفاعلن)."""

    name_ar = "موقوصة (الوقص)"
    name_en = "Waqas"
    description_ar = "حذف الثاني المتحرك"
    affected_index = 1


class Qabadh(BaseSingleHazfZehaf):
    """Qabdh (القبض): Deletion of the 5th Sakin letter (e.g. فعولن -> فعولُ, مفاعيلن -> مفاعلن)."""

    name_ar = "مقبوضة (القبض)"
    name_en = "Qabadh"
    description_ar = "حذف الخامس الساكن"
    affected_index = 4


class Kaff(BaseSingleHazfZehaf):
    """Kaff (الكف): Deletion of the 7th Sakin letter (e.g. مفاعيلن -> مفاعيلُ, فاعلاتن -> فاعلاتُ)."""

    name_ar = "مكفوفة (الكف)"
    name_en = "Kaff"
    description_ar = "حذف السابع الساكن"
    affected_index = 6


class Akal(BaseSingleHazfZehaf):
    """'Aql (العقل): Deletion of the 5th Mutaharrik letter (e.g. مفاعلتن -> مفاعتن)."""

    name_ar = "معقولة (العقل)"
    name_en = "Aql"
    description_ar = "حذف الخامس المتحرك"
    affected_index = 4


class Kasf(BaseSingleHazfZehaf):
    """Kasf (الكسف): Deletion of the 7th Mutaharrik letter (e.g. مفعولاتُ -> مفعولا / مفعولن)."""

    name_ar = "مكسوفة (الكسف)"
    name_en = "Kasf"
    description_ar = "حذف السابع المتحرك"
    affected_index = 6


class Tasheeth(BaseSingleHazfZehaf):
    """Tasheeth (التشعيث): Deletion of the 1st letter of Watad Majmu' (e.g. فاعلاتن -> فالاتن / مفعولن)."""

    name_ar = "مشعثة (التشعيث)"
    name_en = "Tasheeth"
    description_ar = "حذف أول الوتد المجموع"
    affected_index = 2


class Thalm(BaseSingleHazfZehaf):
    """Thalm (الثلم): Deletion of the 1st Mutaharrik letter of Watad Majmu' in Fawlon (فعولن -> عولن / فعلن)."""

    name_ar = "أثلم (الثلم)"
    name_en = "Thalm"
    description_ar = "حذف أول الوتد المجموع في أول البيت"
    affected_index = 0


class Edmaar(BaseSingleTaskeenZehaf):
    """Idmar (الإضمار): Quiescence (Taskeen) of the 2nd Mutaharrik (e.g. متفاعلن -> مُتْفاعلن / مستفعلن)."""

    name_ar = "مضمرة (الإضمار)"
    name_en = "Edmaar"
    description_ar = "تسكين الثاني المتحرك"
    affected_index = 1


class Asab(BaseSingleTaskeenZehaf):
    """'Asb (العصب): Quiescence of the 5th Mutaharrik (e.g. مفاعلتن -> مفاعَلْتُنْ / مفاعيلن)."""

    name_ar = "معصوبة (العصب)"
    name_en = "Asab"
    description_ar = "تسكين الخامس المتحرك"
    affected_index = 4


class Ziyada(BaseEllahZehaf):
    """Ziyada (الزيادة): Adds a Mutaharrik at index 3."""

    name_ar = "مزيد (الزيادة)"
    name_en = "Ziyada"
    description_ar = "زيادة حرف متحرك"

    def modify_tafeela(self) -> None:
        self.tafeela.add_to_pattern(3, 1, "1")


# ==========================================
# 2. Compound/Doubled Zihafat (الزحاف المزدوج / المركب)
# ==========================================


class BaseDoubledZehaf(BaseEllahZehaf):
    """Base class for compound Zihafat consisting of multiple single modifications."""

    zehafs: ClassVar[list[type[BaseEllahZehaf]]] = []

    def modify_tafeela(self) -> None:
        hazf = [z for z in self.zehafs if issubclass(z, BaseSingleHazfZehaf)]
        taskeen = [z for z in self.zehafs if issubclass(z, BaseSingleTaskeenZehaf)]

        # Delete highest index first to keep earlier indices stable
        indices = sorted([z.affected_index for z in hazf], reverse=True)
        for idx in indices:
            self.tafeela.delete_from_pattern(index=idx)

        for z_cls in taskeen:
            z = z_cls(self.tafeela)
            self.tafeela = z.modified_tafeela


class Khabal(BaseDoubledZehaf):
    """Khabal (الخبل): Combination of Khabn + Tayy (حذف الثاني والرابع الساكنين)."""

    name_ar = "مخبولة (الخبل)"
    name_en = "Khabal"
    description_ar = "اجتماع الخبن والطي (حذف الثاني والرابع الساكنين)"
    zehafs = [Khaban, Tay]


class Khazal(BaseDoubledZehaf):
    """Khazal (الخزل): Combination of Idmar + Tayy (تسكين الثاني وحذف الرابع الساكن)."""

    name_ar = "مخزولة (الخزل)"
    name_en = "Khazal"
    description_ar = "اجتماع الإضمار والطي (تسكين الثاني وحذف الرابع)"
    zehafs = [Edmaar, Tay]


class Shakal(BaseDoubledZehaf):
    """Shakal (الشكل): Combination of Khabn + Kaff (حذف الثاني والسابع الساكنين)."""

    name_ar = "مشكولة (الشكل)"
    name_en = "Shakal"
    description_ar = "اجتماع الخبن والكف (حذف الثاني والسابع الساكنين)"
    zehafs = [Khaban, Kaff]


class Nakas(BaseDoubledZehaf):
    """Naqs (النقص): Combination of 'Asb + Kaff (تسكين الخامس وحذف السابع الساكن)."""

    name_ar = "منقوصة (النقص)"
    name_en = "Nakas"
    description_ar = "اجتماع العصب والكف (تسكين الخامس وحذف السابع)"
    zehafs = [Asab, Kaff]


class TayAndKasf(BaseDoubledZehaf):
    """Tayy and Kasf (الطي والكسف): In Saree (مفعولات -> فاعلن / 10110)."""

    name_ar = "مطوية مكسوفة"
    name_en = "Tay and Kasf"
    description_ar = "اجتماع الطي والكسف في مفعولات"
    zehafs = [Tay, Kasf]


class Tharm(BaseDoubledZehaf):
    """Tharm (الثرم): Combination of Thalm + Qabdh (حذف أول الوتد وحذف الخامس)."""

    name_ar = "أثرم (الثرم)"
    name_en = "Tharm"
    description_ar = "اجتماع الثلم والقبض"
    zehafs = [Thalm, Qabadh]


# ==========================================
# 3. 'Ilal by Addition (علل الزيادة)
# ==========================================


class Tarfeel(BaseEllahZehaf):
    """Tarfeel (الترفيل): Addition of a Sabab Khafif (10) to the end of a Watad Majmu'."""

    name_ar = "مرفلة (الترفيل)"
    name_en = "Tarfeel"
    description_ar = "زيادة سبب خفيف على ما آخره وتد مجموع"

    def modify_tafeela(self) -> None:
        self.tafeela.add_to_pattern(len(self.tafeela.pattern), 1, "ت")
        self.tafeela.add_to_pattern(len(self.tafeela.pattern), 0, "ن")


class Tatheel(BaseEllahZehaf):
    """Tatheel (التذييل): Addition of a Sakin letter (0) to the end of a Watad Majmu'."""

    name_ar = "مذيلة (التذييل)"
    name_en = "Tatheel"
    description_ar = "زيادة حرف ساكن على ما آخره وتد مجموع"

    def modify_tafeela(self) -> None:
        if self.tafeela.pattern[-2:] == [1, 0]:
            self.tafeela.add_to_pattern(len(self.tafeela.pattern), 0, "ا")


class Tasbeegh(BaseEllahZehaf):
    """Tasbeegh (التسبيغ): Addition of a Sakin letter (0) to the end of a Sabab Khafif."""

    name_ar = "مسبغة (التسبيغ)"
    name_en = "Tasbeegh"
    description_ar = "زيادة حرف ساكن على ما آخره سبب خفيف"

    def modify_tafeela(self) -> None:
        if self.tafeela.pattern[-2:] == [1, 0]:
            self.tafeela.add_to_pattern(len(self.tafeela.pattern), 0, "ا")


class TatheelAndEdmaar(BaseEllahZehaf):
    """Tatheel + Idmar (التذييل والإضمار)."""

    name_ar = "مذيلة مضمرة"
    name_en = "Tatheel and Edmaar"
    description_ar = "اجتماع التذييل والإضمار"

    def modify_tafeela(self) -> None:
        self.tafeela = Tatheel(self.tafeela).modified_tafeela
        self.tafeela = Edmaar(self.tafeela).modified_tafeela


class TarfeelAndEdmaar(BaseEllahZehaf):
    """Tarfeel + Idmar (الترفيل والإضمار)."""

    name_ar = "مرفلة مضمرة"
    name_en = "Tarfeel and Edmaar"
    description_ar = "اجتماع الترفيل والإضمار"

    def modify_tafeela(self) -> None:
        self.tafeela = Tarfeel(self.tafeela).modified_tafeela
        self.tafeela = Edmaar(self.tafeela).modified_tafeela


class TarfeelAndKhaban(BaseEllahZehaf):
    """Tarfeel + Khabn (الترفيل والخبن)."""

    name_ar = "مرفلة مخبونة"
    name_en = "Tarfeel and Khaban"
    description_ar = "اجتماع الترفيل والخبن"

    def modify_tafeela(self) -> None:
        self.tafeela = Khaban(self.tafeela).modified_tafeela
        self.tafeela = Tarfeel(self.tafeela).modified_tafeela


# ==========================================
# 4. 'Ilal by Deletion (علل النقص)
# ==========================================


class Hadhf(BaseEllahZehaf):
    """Hadhf (الحذف): Removal of the final Sabab Khafif (10) from the foot."""

    name_ar = "محذوفة (الحذف)"
    name_en = "Hadhf"
    description_ar = "إسقاط السبب الخفيف من آخر التفعيلة"

    def modify_tafeela(self) -> None:
        if len(self.tafeela.pattern) >= 2 and self.tafeela.pattern[-2:] == [1, 0]:
            self.tafeela.delete_from_pattern(len(self.tafeela.pattern) - 1)
            self.tafeela.delete_from_pattern(len(self.tafeela.pattern) - 1)


class HadhfAndKhaban(BaseEllahZehaf):
    """Hadhf + Khabn (الحذف والخبن)."""

    name_ar = "محذوفة مخبونة"
    name_en = "Hadhf and Khaban"
    description_ar = "اجتماع الحذف والخبن"

    def modify_tafeela(self) -> None:
        self.tafeela = Hadhf(self.tafeela).modified_tafeela
        self.tafeela = Khaban(self.tafeela).modified_tafeela


class Qataf(BaseEllahZehaf):
    """Qataf (القطف): Hadhf of Sabab Khafif + 'Asb (in Wafir: مفاعلتن -> مفاعل -> فعولن)."""

    name_ar = "مقطوفة (القطف)"
    name_en = "Qataf"
    description_ar = "حذف السبب الخفيف وتسكين ما قبله في مفاعلتن"

    def modify_tafeela(self) -> None:
        self.tafeela = Hadhf(self.tafeela).modified_tafeela
        self.tafeela = Asab(self.tafeela).modified_tafeela


class Qataa(BaseEllahZehaf):
    """Qat' (القطع): Removal of the Sakin of Watad Majmu' and quiescence of the preceding letter."""

    name_ar = "مقطوعة (القطع)"
    name_en = "Qataa"
    description_ar = "حذف ساكن الوتد المجموع وتسكين ما قبله"

    def modify_tafeela(self) -> None:
        if len(self.tafeela.pattern) >= 2 and self.tafeela.pattern[-2:] == [1, 0]:
            self.tafeela.delete_from_pattern(len(self.tafeela.pattern) - 1)
            self.tafeela.edit_pattern_at_index(len(self.tafeela.pattern) - 1, 0)


class KhabanAndQataa(BaseEllahZehaf):
    """Qat' + Khabn (القطع والخبن)."""

    name_ar = "مقطوعة مخبونة"
    name_en = "Khaban and Qataa"
    description_ar = "اجتماع القطع والخبن"

    def modify_tafeela(self) -> None:
        self.tafeela = Qataa(self.tafeela).modified_tafeela
        self.tafeela = Khaban(self.tafeela).modified_tafeela


class QataaAndEdmaar(BaseEllahZehaf):
    """Qat' + Idmar (القطع والإضمار)."""

    name_ar = "مقطوعة مضمرة"
    name_en = "Qataa and Edmaar"
    description_ar = "اجتماع القطع والإضمار"

    def modify_tafeela(self) -> None:
        self.tafeela = Qataa(self.tafeela).modified_tafeela
        self.tafeela = Edmaar(self.tafeela).modified_tafeela


class Hathath(BaseEllahZehaf):
    """Hathath (الحذذ): Removal of the entire Watad Majmu' (110) from the foot end."""

    name_ar = "حذاء (الحذذ)"
    name_en = "Hathath"
    description_ar = "حذف الوتد المجموع كاملاً من آخر التفعيلة"

    def modify_tafeela(self) -> None:
        if len(self.tafeela.pattern) >= 3 and self.tafeela.pattern[-3:] == [1, 1, 0]:
            for _ in range(3):
                self.tafeela.delete_from_pattern(len(self.tafeela.pattern) - 1)


class HathathAndEdmaar(BaseEllahZehaf):
    """Hathath + Idmar (الحذذ والإضمار)."""

    name_ar = "حذاء مضمرة"
    name_en = "Hathath and Edmaar"
    description_ar = "اجتماع الحذذ والإضمار"

    def modify_tafeela(self) -> None:
        self.tafeela = Hathath(self.tafeela).modified_tafeela
        self.tafeela = Edmaar(self.tafeela).modified_tafeela


class Salam(BaseEllahZehaf):
    """Salam (الصلم): Removal of the entire Watad Mafruq (101) from the end."""

    name_ar = "أصلم (الصلم)"
    name_en = "Salam"
    description_ar = "حذف الوتد المفروق كاملاً من آخر التفعيلة"

    def modify_tafeela(self) -> None:
        if len(self.tafeela.pattern) >= 3 and self.tafeela.pattern[-3:] == [1, 0, 1]:
            for _ in range(3):
                self.tafeela.delete_from_pattern(len(self.tafeela.pattern) - 1)


class Waqf(BaseEllahZehaf):
    """Waqf (الوقف): Quiescence of the 7th Mutaharrik of Watad Mafruq in Mafoolato."""

    name_ar = "موقوفة (الوقف)"
    name_en = "Waqf"
    description_ar = "تسكين السابع المتحرك في الوتد المفروق"

    def modify_tafeela(self) -> None:
        if len(self.tafeela.pattern) >= 3 and self.tafeela.pattern[-3:] == [1, 0, 1]:
            self.tafeela.edit_pattern_at_index(len(self.tafeela.pattern) - 1, 0)


class WaqfAndTay(BaseEllahZehaf):
    """Waqf + Tayy (الوقف والطي)."""

    name_ar = "موقوفة مطوية"
    name_en = "Waqf and Tay"
    description_ar = "اجتماع الوقف والطي"

    def modify_tafeela(self) -> None:
        self.tafeela = Tay(self.tafeela).modified_tafeela
        self.tafeela = Waqf(self.tafeela).modified_tafeela


class KhabalAndKasf(BaseEllahZehaf):
    """Khabal + Kasf (الخبل والكسف)."""

    name_ar = "مخبولة مكسوفة"
    name_en = "Khabal and Kasf"
    description_ar = "اجتماع الخبل والكسف"

    def modify_tafeela(self) -> None:
        self.tafeela = Khabal(self.tafeela).modified_tafeela
        k = Kasf(self.tafeela)
        k.affected_index = max(0, k.affected_index - 2)
        self.tafeela = k.modified_tafeela


class Qasar(BaseEllahZehaf):
    """Qasr (القصر): Removal of the Sakin of Sabab Khafif and quiescence of the preceding mover."""

    name_ar = "مقصورة (القصر)"
    name_en = "Qasar"
    description_ar = "حذف ساكن السبب الخفيف وتسكين متحركه"

    def modify_tafeela(self) -> None:
        if len(self.tafeela.pattern) >= 2 and self.tafeela.pattern[-2:] == [1, 0]:
            self.tafeela.delete_from_pattern(len(self.tafeela.pattern) - 1)
            self.tafeela.edit_pattern_at_index(len(self.tafeela.pattern) - 1, 0)


class ThalmAndQasar(BaseEllahZehaf):
    """Thalm + Qasr (الثلم والقصر)."""

    name_ar = "أثلم مقصور"
    name_en = "Thalm and Qasar"
    description_ar = "اجتماع الثلم والقصر"

    def modify_tafeela(self) -> None:
        self.tafeela = Thalm(self.tafeela).modified_tafeela
        self.tafeela = Qasar(self.tafeela).modified_tafeela


class Aql(BaseEllahZehaf):
    """Aql (العقل): Qataf + Khabn."""

    name_ar = "معقولة (العقل)"
    name_en = "Aql"
    description_ar = "القطف والخبن في الوافر"

    def modify_tafeela(self) -> None:
        self.tafeela = Qataf(self.tafeela).modified_tafeela
        self.tafeela = Khaban(self.tafeela).modified_tafeela


class Batr(BaseEllahZehaf):
    """Batr (البتر): Combination of Hadhf + Qat' (الحذف والقطع)."""

    name_ar = "أبتر (البتر)"
    name_en = "Batr"
    description_ar = "اجتماع الحذف والقطع"

    def modify_tafeela(self) -> None:
        self.tafeela = Hadhf(self.tafeela).modified_tafeela
        self.tafeela = Qataa(self.tafeela).modified_tafeela
