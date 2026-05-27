import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


def get_prompt(work_type: str, topic: str, pages: int) -> str:

    if work_type == "mustaqil":
        return f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
{topic} mavzusida {pages} varaqlik MUSTAQIL ISH yoz.

Quyidagi tuzilmada yoz:

MUNDARIJA

KIRISH
- Mavzuning dolzarbligi
- Tadqiqotning maqsadi
- Tadqiqotning vazifalari
- Foydalanilgan metodlar

I BO'LIM: NAZARIY ASOSLAR
- Asosiy tushunchalar
- Ilmiy qarashlar
- Xorijiy tajriba

II BO'LIM: TAHLIL VA MUHOKAMA
- Hozirgi holat tahlili
- Muammolar va yechimlar
- Misollar va faktlar

III BO'LIM: TAVSIYALAR
- Amaliy tavsiyalar
- Istiqbol yo'llari

XULOSA
- Asosiy natijalar (5-7 ta)

ADABIYOTLAR RO'YXATI (8-10 manba)

O'zbek tilida, akademik uslubda, jami {pages} varaq hajmda yoz."""

    elif work_type == "yozma":
        return f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
{topic} mavzusida {pages} varaqlik YOZMA ISH yoz.

Tuzilma:

MUNDARIJA

KIRISH ({max(2, pages//10)} bet)
- Dolzarbligi, maqsadi, vazifalari, ob'ekti, predmeti

I BOB: NAZARIY ASOSLAR ({pages//3} bet)
1.1. Asosiy tushunchalar tahlili
1.2. Xorijiy tajriba
1.3. O'zbekistondagi holat
I bob xulosasi

II BOB: TAHLIL ({pages//3} bet)
2.1. Joriy holat tahlili
2.2. Muammolar
2.3. Yechim variantlari
II bob xulosasi

III BOB: TAVSIYALAR ({pages//4} bet)
3.1. Amaliy tavsiyalar
3.2. Samaradorlik
III bob xulosasi

XULOSA
ADABIYOTLAR (12-15 manba)

O'zbek tilida, akademik uslubda, {pages} varaq."""

    elif work_type == "amaliy":
        return f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
{topic} mavzusida {pages} varaqlik AMALIY ISH yoz.

Tuzilma:

MUNDARIJA

KIRISH
- Maqsad, vazifalar, metodlar

NAZARIY QISM ({pages//4} bet)
- Nazariy asos, tushunchalar

AMALIY QISM ({pages//2} bet)
Topshiriq 1:
- Shart va ma'lumotlar
- Yechim jarayoni
- Natija

Topshiriq 2:
- Shart va ma'lumotlar
- Yechim jarayoni
- Natija

Topshiriq 3:
- Shart va ma'lumotlar
- Yechim jarayoni
- Natija

NATIJALAR TAHLILI
XULOSA
ADABIYOTLAR (6-8 manba)

O'zbek tilida, {pages} varaq."""

    elif work_type == "diplom":
        return f"""Sen O'zbek tilida yuqori malakali diplom ishi yozuvchi ekspertsan.
{topic} mavzusida {pages} varaqlik DIPLOM ISHI yoz.

To'liq tuzilma:

MUNDARIJA
ANNOTATSIYA (o'zbek va ingliz tilida)

KIRISH (4-5 bet)
- Tadqiqot dolzarbligi
- O'rganilganlik darajasi
- Maqsad, vazifalar (5-6 ta)
- Ob'ekt va predmet
- Gipoteza
- Metodologiya
- Ilmiy yangilik
- Amaliy ahamiyat
- Ishning tuzilishi

I BOB: NAZARIY ASOSLAR ({pages//4} bet)
1.1. Asosiy tushunchalar va kategoriyalar (8-10 bet)
1.2. Xorijiy ilm-fan tajribasi (8-10 bet)
1.3. O'zbekistondagi rivojlanish (6-8 bet)
I bob xulosalari

II BOB: EMPIRIK TAHLIL ({pages//4} bet)
2.1. Tadqiqot metodologiyasi (8-10 bet)
2.2. Tahlil natijalari, statistika (8-10 bet)
2.3. Muammolar diagnostikasi (6-8 bet)
II bob xulosalari

III BOB: TAVSIYALAR ({pages//5} bet)
3.1. Strategik tavsiyalar (6-8 bet)
3.2. Amaliy chora-tadbirlar (6-8 bet)
3.3. Kutilayotgan natijalar (4-6 bet)
III bob xulosalari

UMUMIY XULOSA (4-5 bet)
ADABIYOTLAR (40-50 manba)
ILOVALAR

O'zbek tilida, oliy ilmiy-akademik uslubda, {pages} varaq."""

    return f"{topic} mavzusida {pages} varaqlik akademik ish yoz. O'zbek tilida."


def generate_work(work_type: str, topic: str, pages: int) -> str:
    """Gemini AI orqali ish yaratish (sync)"""
    prompt = get_prompt(work_type, topic, pages)
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=8192,
        )
    )
    return response.text
