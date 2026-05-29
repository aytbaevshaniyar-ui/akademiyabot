import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def ask_groq(prompt: str, max_tokens: int = 6000) -> str:
    """Groq API ga bitta so'rov yuborish"""
    import time
    if not GROQ_KEY:
        raise ValueError("GROQ_API_KEY topilmadi!")
    time.sleep(35)  # Rate limit: 12000 TPM, har so'rov orasida kutish

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": max_tokens
    }
    response = requests.post(GROQ_URL, json=payload, headers=headers, timeout=120)
    if response.status_code != 200:
        raise ValueError(f"Groq xatolik: {response.status_code} - {response.text}")
    return response.json()["choices"][0]["message"]["content"]


# ================================================
# MUSTAQIL ISH
# ================================================
def gen_mustaqil(topic: str, pages: int) -> str:
    parts = []

    parts.append(ask_groq(f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
"{topic}" mavzusida mustaqil ish uchun KIRISH qismini yoz (2-3 bet).

Quyidagilarni to'liq yoz:
- Mavzuning dolzarbligi (2-3 abzats, har biri 5-7 gap)
- Tadqiqotning maqsadi
- Tadqiqotning vazifalari (5-6 ta, har biri tushuntirilgan)
- Foydalanilgan metodlar
- Ishning tuzilishi

O'zbek tilida, akademik uslubda, to'liq va batafsil yoz."""))

    parts.append(ask_groq(f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
"{topic}" mavzusida mustaqil ish uchun I BO'LIM: NAZARIY ASOSLAR qismini yoz ({pages//3} bet).

Quyidagilarni to'liq yoz:
1.1. Asosiy tushunchalar va ta'riflar
- Kamida 8-10 ta asosiy tushuncha, har biri batafsil tushuntirilgan
- Ilmiy ta'riflar va ularning tahlili

1.2. Ilmiy qarashlar va nazariyalar
- Xorijiy olimlarning qarashlari (kamida 5-7 ta)
- Mahalliy olimlarning ishlari
- Turli yondashuvlarning taqqoslamasi

1.3. Xorijiy tajriba
- Rivojlangan mamlakatlar tajribasi (3-4 ta mamlakat)
- Eng yaxshi amaliyotlar
- O'zbekiston uchun saboqlar

O'zbek tilida, akademik uslubda, har bir bo'lim kamida 3-4 sahifa hajmida yoz."""))

    parts.append(ask_groq(f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
"{topic}" mavzusida mustaqil ish uchun II BO'LIM: TAHLIL VA MUHOKAMA qismini yoz ({pages//3} bet).

Quyidagilarni to'liq yoz:
2.1. Hozirgi holat tahlili
- Mavzuning O'zbekistondagi joriy ahvoli
- Statistik ma'lumotlar va faktlar
- Muammolar va kamchiliklar

2.2. Qiyosiy tahlil
- Xorijiy mamlakatlar bilan taqqoslash
- Afzalliklar va kamchiliklar jadvali
- Sabab-oqibat aloqalari

2.3. Rivojlantirish imkoniyatlari
- Mavjud resurslar va imkoniyatlar
- To'siqlar va ularni bartaraf etish yo'llari
- Istiqbolli yo'nalishlar

O'zbek tilida, akademik uslubda, har bir bo'lim kamida 3-4 sahifa hajmida yoz."""))

    parts.append(ask_groq(f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
"{topic}" mavzusida mustaqil ish uchun III BO'LIM: TAVSIYALAR va XULOSA qismlarini yoz.

III BO'LIM: TAVSIYALAR ({pages//4} bet):
3.1. Qisqa muddatli tavsiyalar (1-2 yilga)
- Kamida 5-7 ta aniq tavsiya, har biri batafsil asoslangan
- Amalga oshirish mexanizmlari

3.2. Uzoq muddatli tavsiyalar (3-5 yilga)
- Kamida 5-7 ta strategik tavsiya
- Kutilayotgan natijalar

XULOSA (1-2 bet):
- Barcha boblar bo'yicha asosiy xulosalar (7-10 ta)
- Tadqiqotning ahamiyati
- Kelajak istiqboli

ADABIYOTLAR RO'YXATI:
(Kamida 10 ta manba, to'g'ri akademik formatda)

O'zbek tilida, akademik uslubda yoz."""))

    mundarija = f"""MUNDARIJA

KIRISH....................................................................3
I BO'LIM: NAZARIY ASOSLAR..............................................5
  1.1. Asosiy tushunchalar va ta'riflar................................5
  1.2. Ilmiy qarashlar va nazariyalar.................................8
  1.3. Xorijiy tajriba...............................................11
II BO'LIM: TAHLIL VA MUHOKAMA.........................................14
  2.1. Hozirgi holat tahlili.........................................14
  2.2. Qiyosiy tahlil...............................................17
  2.3. Rivojlantirish imkoniyatlari..................................20
III BO'LIM: TAVSIYALAR...............................................23
  3.1. Qisqa muddatli tavsiyalar....................................23
  3.2. Uzoq muddatli tavsiyalar.....................................26
XULOSA..................................................................28
ADABIYOTLAR RO'YXATI...................................................30

"""
    return mundarija + "\n\n".join(parts)


# ================================================
# YOZMA ISH
# ================================================
def gen_yozma(topic: str, pages: int) -> str:
    parts = []

    parts.append(ask_groq(f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
"{topic}" mavzusida yozma ish uchun KIRISH qismini yoz (2-3 bet).

To'liq yoz:
- Mavzuning dolzarbligi va ahamiyati (3-4 abzats)
- Tadqiqotning maqsadi
- Tadqiqotning vazifalari (5-6 ta)
- Ob'ekt va predmet
- Metodologik asos
- Ishning tuzilishi

O'zbek tilida, akademik uslubda."""))

    parts.append(ask_groq(f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
"{topic}" mavzusida yozma ish uchun I BOB: NAZARIY-METODOLOGIK ASOSLAR qismini yoz ({pages//3} bet).

1.1. Asosiy tushunchalar tahlili (batafsil, kamida 4-5 bet)
1.2. Xorijiy ilm-fan tajribasi (kamida 4-5 bet)
1.3. O'zbekistondagi holat va muammolar (kamida 4-5 bet)
I bob xulosasi

Har bir qism to'liq va batafsil, O'zbek tilida, akademik uslubda."""))

    parts.append(ask_groq(f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
"{topic}" mavzusida yozma ish uchun II BOB: TAHLIL VA NATIJALAR qismini yoz ({pages//3} bet).

2.1. Tadqiqot metodologiyasi va ma'lumotlar tahlili (kamida 4-5 bet)
2.2. Asosiy muammolar va ularning sabablari (kamida 4-5 bet)
2.3. Yechim variantlarining qiyosiy tahlili (kamida 4-5 bet)
II bob xulosasi

Har bir qism to'liq va batafsil, O'zbek tilida, akademik uslubda."""))

    parts.append(ask_groq(f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
"{topic}" mavzusida yozma ish uchun III BOB: TAVSIYALAR va XULOSA qismlarini yoz.

III BOB: TAVSIYALAR ({pages//4} bet):
3.1. Amaliy tavsiyalar (kamida 5-6 bet, har bir tavsiya batafsil)
3.2. Samaradorlikni oshirish yo'llari (kamida 3-4 bet)
III bob xulosasi

UMUMIY XULOSA (2 bet):
- Har bob bo'yicha 2-3 ta xulosa
- Umumiy natijalar

ADABIYOTLAR (kamida 12-15 manba, to'g'ri formatda)

O'zbek tilida, akademik uslubda."""))

    mundarija = f"""MUNDARIJA

KIRISH....................................................................3
I BOB: NAZARIY-METODOLOGIK ASOSLAR.....................................5
  1.1. Asosiy tushunchalar tahlili....................................5
  1.2. Xorijiy ilm-fan tajribasi.....................................9
  1.3. O'zbekistondagi holat.........................................13
II BOB: TAHLIL VA NATIJALAR...........................................17
  2.1. Tadqiqot metodologiyasi.......................................17
  2.2. Asosiy muammolar.............................................21
  2.3. Yechim variantlari...........................................25
III BOB: TAVSIYALAR..................................................29
  3.1. Amaliy tavsiyalar............................................29
  3.2. Samaradorlikni oshirish......................................33
XULOSA..................................................................36
ADABIYOTLAR............................................................38

"""
    return mundarija + "\n\n".join(parts)


# ================================================
# AMALIY ISH
# ================================================
def gen_amaliy(topic: str, pages: int) -> str:
    parts = []

    parts.append(ask_groq(f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
"{topic}" mavzusida amaliy ish uchun KIRISH va NAZARIY QISM ni yoz ({pages//4} bet).

KIRISH:
- Ishning maqsadi va vazifalari
- Qo'llaniladigan usullar

NAZARIY QISM:
- Asosiy tushunchalar va ta'riflar (batafsil)
- Standartlar va me'yorlar
- Nazariy asos

O'zbek tilida, aniq va batafsil."""))

    parts.append(ask_groq(f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
"{topic}" mavzusida amaliy ish uchun AMALIY QISM ning birinchi yarmini yoz ({pages//3} bet).

Topshiriq 1: (mavzuga oid birinchi amaliy masala)
- Masalaning shartlari va ma'lumotlari (batafsil)
- Yechim algoritmi (bosqichma-bosqich)
- Hisob-kitoblar (formulalar bilan)
- Natija va tahlil

Topshiriq 2: (mavzuga oid ikkinchi amaliy masala)
- Masalaning shartlari va ma'lumotlari
- Yechim jarayoni
- Natija va tahlil

O'zbek tilida, amaliy va aniq yoz."""))

    parts.append(ask_groq(f"""Sen O'zbek tilida akademik ish yozuvchi mutaxassissan.
"{topic}" mavzusida amaliy ish uchun AMALIY QISM ning ikkinchi yarmi, NATIJALAR va XULOSAni yoz.

Topshiriq 3: (mavzuga oid uchinchi amaliy masala)
- Masalaning shartlari
- Yechim jarayoni
- Natija

NATIJALAR TAHLILI ({pages//5} bet):
- Olingan natijalarning muhokamasi
- Xatolar tahlili
- Takomillashtirish yo'llari

XULOSA:
- Asosiy xulosalar
- Tavsiyalar

ADABIYOTLAR (6-8 manba)

O'zbek tilida."""))

    mundarija = f"""MUNDARIJA

KIRISH....................................................................3
NAZARIY QISM..............................................................4
AMALIY QISM..............................................................8
  Topshiriq 1...........................................................8
  Topshiriq 2..........................................................13
  Topshiriq 3..........................................................17
NATIJALAR TAHLILI......................................................20
XULOSA..................................................................22
ADABIYOTLAR............................................................23

"""
    return mundarija + "\n\n".join(parts)


# ================================================
# DIPLOM ISHI
# ================================================
def gen_diplom(topic: str, pages: int) -> str:
    parts = []

    # ANNOTATSIYA + KIRISH
    parts.append(ask_groq(f"""Sen O'zbek tilida yuqori malakali diplom ishi yozuvchi ekspertsan.
"{topic}" mavzusida diplom ishi uchun ANNOTATSIYA va KIRISH qismlarini yoz (6-7 bet).

ANNOTATSIYA (o'zbek tilida, 150-200 so'z):
- Ishning maqsadi, metodlari, natijalari

ANNOTATSIYA (ingliz tilida, 150-200 so'z):
- Xuddi shuni inglizcha

KIRISH (4-5 bet):
- Tadqiqot mavzusining dolzarbligi (3-4 abzats, har biri 5-7 gap)
- Muammoning o'rganilganlik darajasi (kim nimalar qilgan)
- Tadqiqotning maqsadi
- Tadqiqotning vazifalari (6 ta, har biri tushuntirilgan)
- Tadqiqotning ob'ekti
- Tadqiqotning predmeti
- Tadqiqotning gipotezasi
- Tadqiqotning metodologik asosi
- Tadqiqotning ilmiy yangiligi
- Tadqiqotning amaliy ahamiyati
- Ishning tuzilishi va hajmi

O'zbek tilida, oliy ilmiy-akademik uslubda, to'liq va batafsil."""))

    # I BOB
    parts.append(ask_groq(f"""Sen O'zbek tilida yuqori malakali diplom ishi yozuvchi ekspertsan.
"{topic}" mavzusida diplom ishi uchun I BOB: NAZARIY ASOSLAR qismini yoz ({pages//4} bet, kamida 12-13 sahifa).

1.1. {topic} ning asosiy tushunchalari va kategoriyalari (4-5 bet)
- Kamida 10-12 ta asosiy tushuncha va ta'rif
- Har bir tushunchaning ilmiy asosi
- Turli mualliflarning ta'riflari taqqoslamasi

1.2. Xorijiy ilm-fan va amaliyot tajribasi (4-5 bet)
- AQSh, Yevropa, Osiyo tajribasi
- Eng yaxshi amaliyotlar (best practices)
- Xorijiy tadqiqotlar tahlili (kamida 7-8 ta tadqiqot)

1.3. O'zbekistonda {topic} ning rivojlanish tendensiyalari (3-4 bet)
- Tarixiy rivojlanish
- Hozirgi holat
- Muammolar va imkoniyatlar

I bob xulosalari (1 bet):
- 5-6 ta xulosa

O'zbek tilida, oliy ilmiy-akademik uslubda, har qism to'liq va batafsil."""))

    # II BOB
    parts.append(ask_groq(f"""Sen O'zbek tilida yuqori malakali diplom ishi yozuvchi ekspertsan.
"{topic}" mavzusida diplom ishi uchun II BOB: EMPIRIK TAHLIL qismini yoz ({pages//4} bet, kamida 12-13 sahifa).

2.1. Tadqiqot metodologiyasi va ma'lumotlar to'plash (4-5 bet)
- Qo'llangan tadqiqot metodlari (sifatiy va miqdoriy)
- Ma'lumotlar manbasi
- Tadqiqot bazasi
- Ma'lumotlar to'plash jarayoni

2.2. Empirik tahlil natijalari va statistik ma'lumotlar (4-5 bet)
- Asosiy ko'rsatkichlar tahlili
- Jadvallar va grafiklar tavsifi
- Raqamli ma'lumotlar va ularning talqini
- Dinamika tahlili

2.3. Muammolar diagnostikasi va omillar tahlili (3-4 bet)
- Asosiy muammolar
- Sabab-oqibat aloqalari
- Omillar tahlili
- Rivojlanishga to'sqinlik qiluvchi sabablar

II bob xulosalari (1 bet):
- 5-6 ta xulosa

O'zbek tilida, oliy ilmiy-akademik uslubda, to'liq yoz."""))

    # III BOB
    parts.append(ask_groq(f"""Sen O'zbek tilida yuqori malakali diplom ishi yozuvchi ekspertsan.
"{topic}" mavzusida diplom ishi uchun III BOB: TAVSIYALAR qismini yoz ({pages//5} bet, kamida 10-11 sahifa).

3.1. Konseptual yondashuvlar va strategik tavsiyalar (4-5 bet)
- Yangi kontseptsiya yoki model taklifi
- Strategik yo'nalishlar (kamida 6-7 ta)
- Har bir tavsiyaning asoslanishi
- Amalga oshirish bosqichlari

3.2. Amaliy chora-tadbirlar va mexanizmlar (3-4 bet)
- Qisqa muddatli chora-tadbirlar (1-2 yil)
- O'rta muddatli chora-tadbirlar (3-5 yil)
- Mas'ul tashkilotlar
- Moliyalashtirish manbalari

3.3. Samaradorlikni baholash va kutilayotgan natijalar (2-3 bet)
- Kutilayotgan iqtisodiy samara
- Kutilayotgan ijtimoiy samara
- Baholash ko'rsatkichlari (KPI)
- Xavf-xatarlar tahlili

III bob xulosalari (1 bet):
- 5-6 ta xulosa

O'zbek tilida, oliy ilmiy-akademik uslubda."""))

    # XULOSA + ADABIYOTLAR
    parts.append(ask_groq(f"""Sen O'zbek tilida yuqori malakali diplom ishi yozuvchi ekspertsan.
"{topic}" mavzusida diplom ishi uchun UMUMIY XULOSA va ADABIYOTLAR ni yoz.

UMUMIY XULOSA VA TAVSIYALAR (4-5 bet):
- I bob bo'yicha 3-4 ta xulosa
- II bob bo'yicha 3-4 ta xulosa
- III bob bo'yicha 3-4 ta xulosa
- Ilmiy yangilik
- Amaliy ahamiyat
- Kelajak tadqiqotlar uchun tavsiyalar

FOYDALANILGAN ADABIYOTLAR VA MANBALAR (kamida 40 ta manba):
Quyidagi formatda:
1. O'zbek tilidagi kitoblar (kamida 10 ta)
2. Rus tilidagi adabiyotlar (kamida 8 ta)
3. Ingliz tilidagi adabiyotlar (kamida 12 ta)
4. Internet manbalar (kamida 5 ta)
5. Me'yoriy hujjatlar (kamida 5 ta)

Har bir manba to'g'ri bibliografik formatda yozilsin.

O'zbek tilida, akademik uslubda."""))

    mundarija = f"""MUNDARIJA

ANNOTATSIYA..............................................................3
KIRISH....................................................................5
I BOB: NAZARIY ASOSLAR..................................................9
  1.1. Asosiy tushunchalar va kategoriyalar.............................9
  1.2. Xorijiy ilm-fan va amaliyot tajribasi..........................13
  1.3. O'zbekistonda rivojlanish tendensiyalari........................17
  I bob xulosalari.....................................................20
II BOB: EMPIRIK TAHLIL.................................................21
  2.1. Tadqiqot metodologiyasi.........................................21
  2.2. Empirik tahlil natijalari.......................................25
  2.3. Muammolar diagnostikasi.........................................29
  II bob xulosalari....................................................32
III BOB: TAVSIYALAR....................................................33
  3.1. Strategik tavsiyalar............................................33
  3.2. Amaliy chora-tadbirlar..........................................37
  3.3. Kutilayotgan natijalar..........................................40
  III bob xulosalari...................................................43
UMUMIY XULOSA VA TAVSIYALAR...........................................44
FOYDALANILGAN ADABIYOTLAR.............................................48
ILOVALAR.................................................................55

"""
    return mundarija + "\n\n".join(parts)


# ================================================
# ASOSIY FUNKSIYA
# ================================================
def generate_work(work_type: str, topic: str, pages: int) -> str:
    if work_type == "mustaqil":
        return gen_mustaqil(topic, pages)
    elif work_type == "yozma":
        return gen_yozma(topic, pages)
    elif work_type == "amaliy":
        return gen_amaliy(topic, pages)
    elif work_type == "diplom":
        return gen_diplom(topic, pages)
    else:
        return ask_groq(f"{topic} mavzusida {pages} varaqlik akademik ish yoz. O'zbek tilida.")
