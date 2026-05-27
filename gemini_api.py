import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"


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
- Dolzarbligi, maqsadi, vazifalari

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
Topshiriq 1: shart, yechim, natija
Topshiriq 2: shart, yechim, natija
Topshiriq 3: shart, yechim, natija

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
- Dolzarbligi, maqsad, vazifalar, ob'ekt, predmet, metodologiya

I BOB: NAZARIY ASOSLAR ({pages//4} bet)
1.1. Asosiy tushunchalar
1.2. Xorijiy tajriba
1.3. O'zbekistondagi holat
I bob xulosalari

II BOB: EMPIRIK TAHLIL ({pages//4} bet)
2.1. Tadqiqot metodologiyasi
2.2. Tahlil natijalari
2.3. Muammolar diagnostikasi
II bob xulosalari

III BOB: TAVSIYALAR ({pages//5} bet)
3.1. Strategik tavsiyalar
3.2. Amaliy chora-tadbirlar
3.3. Kutilayotgan natijalar
III bob xulosalari

UMUMIY XULOSA (4-5 bet)
ADABIYOTLAR (40-50 manba)
ILOVALAR

O'zbek tilida, oliy ilmiy-akademik uslubda, {pages} varaq."""

    return f"{topic} mavzusida {pages} varaqlik akademik ish yoz. O'zbek tilida."


def generate_work(work_type: str, topic: str, pages: int) -> str:
    """Gemini REST API orqali ish yaratish"""

    if not GEMINI_KEY:
        raise ValueError("GEMINI_API_KEY topilmadi! Railway Variables ga kiriting.")

    prompt = get_prompt(work_type, topic, pages)

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192
        }
    }

    response = requests.post(
        GEMINI_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=120
    )

    if response.status_code != 200:
        raise ValueError(f"Gemini API xatolik: {response.status_code} - {response.text}")

    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]
