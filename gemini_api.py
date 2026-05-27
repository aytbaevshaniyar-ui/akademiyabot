import google.generativeai as genai
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# ================================================
# PROMPTLAR - Har bir ish turi uchun
# ================================================

def get_prompt(work_type: str, topic: str, pages: int) -> str:

    if work_type == "mustaqil":
        return f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
Quyidagi mavzu bo'yicha {pages} varaqlik MUSTAQIL ISH yoz.

Mavzu: {topic}

TUZILMA (quyidagi tartibda yoz):

MUNDARIJA
(Barcha bo'limlar va sahifa raqamlari)

KIRISH
- Mavzuning dolzarbligi (2-3 abzats)
- Tadqiqotning maqsadi
- Tadqiqotning vazifalari (3-4 ta)
- Foydalanilgan metodlar

ASOSIY QISM
1-bo'lim: Nazariy asoslar
- Asosiy tushunchalar va ta'riflar
- Mavzu bo'yicha ilmiy qarashlar
- Xorijiy va mahalliy tajriba

2-bo'lim: Tahlil va muhokama  
- Mavzuning hozirgi holati
- Muammolar va yechimlar
- Misollar va faktlar bilan asoslash

3-bo'lim: Tavsiyalar
- Amaliy tavsiyalar
- Istiqbol va rivojlanish yo'llari

XULOSA
- Barcha xulosalar (5-7 ta)
- Asosiy natijalar

ADABIYOTLAR RO'YXATI
(Kamida 8-10 ta manba, to'g'ri formatda)

MUHIM:
- O'zbek tilida yoz
- Professional akademik uslub
- Har bir bo'lim to'liq va batafsil bo'lsin
- Jami hajm taxminan {pages} varaq bo'lsin (1 varaq = 250 so'z)
- Aniq faktlar, raqamlar va misollar keltir"""

    elif work_type == "yozma":
        return f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
Quyidagi mavzu bo'yicha {pages} varaqlik YOZMA ISH yoz.

Mavzu: {topic}

TUZILMA:

MUNDARIJA

KIRISH ({max(2, pages//10)} bet)
- Mavzuning dolzarbligi va ahamiyati
- Tadqiqotning maqsadi va vazifalari
- Ob'ekt va predmet
- Ishning metodologik asosi
- Ishning tuzilishi

I BOB: NAZARIY-METODOLOGIK ASOSLAR ({pages//3} bet)
1.1. Asosiy tushunchalar tahlili
1.2. Xorijiy ilm-fan tajribasi
1.3. O'zbekistondagi holat
I bob xulosasi

II BOB: EMPIRIK TAHLIL VA NATIJALAR ({pages//3} bet)
2.1. Mavzu bo'yicha joriy holat tahlili
2.2. Muammolar va cheklovlar
2.3. Yechim variantlari taqqoslamasi
II bob xulosasi

III BOB: TAVSIYALAR VA ISTIQBOL ({pages//4} bet)
3.1. Amaliy tavsiyalar
3.2. Samaradorlikni oshirish yo'llari
3.3. Kelajak istiqboli
III bob xulosasi

UMUMIY XULOSA ({max(2, pages//12)} bet)
ADABIYOTLAR RO'YXATI (12-15 manba)

MUHIM:
- O'zbek tilida, akademik uslubda
- Har bob to'liq va batafsil
- Jami {pages} varaq hajmda
- Konkret misollar va statistika keltir"""

    elif work_type == "amaliy":
        return f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
Quyidagi mavzu bo'yicha {pages} varaqlik AMALIY ISH yoz.

Mavzu: {topic}

TUZILMA:

MUNDARIJA

KIRISH (1-2 bet)
- Ishning maqsadi va vazifalari
- Qo'llaniladigan usullar
- Kutilayotgan natija

NAZARIY QISM ({pages//4} bet)
- Mavzuning nazariy asosi
- Asosiy tushunchalar va formulalar/usullar
- Standartlar va me'yorlar

AMALIY QISM ({pages//2} bet)
Topshiriq 1: [Birinchi amaliy topshiriq]
- Shartlar va ma'lumotlar
- Yechim jarayoni (bosqichma-bosqich)
- Natija va tahlil

Topshiriq 2: [Ikkinchi amaliy topshiriq]
- Shartlar va ma'lumotlar
- Yechim jarayoni
- Natija va tahlil

Topshiriq 3: [Uchinchi amaliy topshiriq]
- Shartlar va ma'lumotlar
- Yechim jarayoni
- Natija va tahlil

NATIJALAR TAHLILI ({pages//5} bet)
- Olingan natijalar muhokamasi
- Xatolar va ularning sabablari
- Takomillashtirish yo'llari

XULOSA (1 bet)
FOYDALANILGAN ADABIYOTLAR (6-8 manba)

MUHIM:
- O'zbek tilida
- Amaliy va aniq misollar bilan
- Har bir topshiriq to'liq yechilgan
- Jami {pages} varaq"""

    elif work_type == "diplom":
        ch1 = pages // 4
        ch2 = pages // 4
        ch3 = pages // 5
        return f"""Sen O'zbek tilida oliy malakali diplom ishi yozuvchi ekspertsan.
Quyidagi mavzu bo'yicha {pages} varaqlik DIPLOM ISHI (Bitiruv malakaviy ishi) yoz.

Mavzu: {topic}

TO'LIQ TUZILMA:

MUNDARIJA
ANNOTATSIYA (o'zbek va ingliz tilida)
KIRISH (4-5 bet)
- Tadqiqot mavzusining dolzarbligi
- Muammoning o'rganilganlik darajasi
- Tadqiqotning maqsadi
- Tadqiqotning vazifalari (5-6 ta)
- Tadqiqotning ob'ekti
- Tadqiqotning predmeti
- Tadqiqotning gipotezasi
- Tadqiqotning metodologik asosi
- Tadqiqotning ilmiy yangiligi
- Tadqiqotning amaliy ahamiyati
- Ishning tuzilishi va hajmi

I BOB: [NAZARIY BOB NOMI] ({ch1} bet)
1.1. [Paragrof nomi] (8-10 bet)
    - Asosiy tushunchalar va kategoriyalar
    - Ilmiy adabiyotlar tahlili
1.2. [Paragrof nomi] (8-10 bet)
    - Xorijiy ilm-fan va amaliyot tajribasi
    - Taqqoslama tahlil
1.3. [Paragrof nomi] (6-8 bet)
    - O'zbekistondagi holat va rivojlanish tendensiyalari
I bob xulosalari (1-2 bet)

II BOB: [TAHLIL BOB NOMI] ({ch2} bet)
2.1. [Paragrof nomi] (8-10 bet)
    - Empirik tadqiqot metodologiyasi
    - Ma'lumotlar manbasi va to'plash usullari
2.2. [Paragrof nomi] (8-10 bet)
    - Kontent-tahlil natijalari
    - Statistik ma'lumotlar va jadvallar
2.3. [Paragrof nomi] (6-8 bet)
    - Muammolar diagnostikasi
    - Omillar tahlili
II bob xulosalari (1-2 bet)

III BOB: [TAVSIYALAR BOB NOMI] ({ch3} bet)
3.1. [Paragrof nomi] (6-8 bet)
    - Konseptual yondashuvlar
    - Strategik tavsiyalar
3.2. [Paragrof nomi] (6-8 bet)
    - Amaliy chora-tadbirlar
    - Mexanizmlar va vositalar
3.3. [Paragrof nomi] (4-6 bet)
    - Samaradorlikni baholash
    - Kutilayotgan natijalar
III bob xulosalari (1-2 bet)

UMUMIY XULOSA VA TAVSIYALAR (4-5 bet)
FOYDALANILGAN ADABIYOTLAR VA MANBALAR (4-5 bet, 40-50 ta manba)
ILOVALAR

MUHIM TALABLAR:
- O'zbek tilida, yuqori ilmiy-akademik uslubda
- Jami {pages} varaq
- Har bir paragrof chuqur va to'liq tahlil
- Aniq statistika, faktlar va misollar
- Jadvallar va sxemalar tavsifi
- Xorijiy tadqiqotlarga havolalar"""

    return f"Mavzu bo'yicha {pages} varaqlik akademik ish yoz: {topic}"


# ================================================
# ISH GENERATSIYA QILISH
# ================================================
async def generate_work(work_type: str, topic: str, pages: int) -> str:
    """Gemini AI orqali akademik ish yaratish"""
    prompt = get_prompt(work_type, topic, pages)

    loop = asyncio.get_event_loop()

    def call_gemini():
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=8192,
            )
        )
        return response.text

    # Gemini sync → async wrapper
    result = await loop.run_in_executor(None, call_gemini)
    return result
