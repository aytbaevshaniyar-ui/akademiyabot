# 🎓 AkademiyaBot V4

Telegram bot — O'zbek tilida akademik ishlar yozib beruvchi bot (Groq AI asosida).

## ⚙️ Muhit o'zgaruvchilari (Environment Variables)

Railway, Render yoki boshqa hostingda quyidagi o'zgaruvchilarni kiriting:

| Kalit | Tavsif |
|-------|--------|
| `BOT_TOKEN` | [@BotFather](https://t.me/BotFather) dan olingan Telegram bot token |
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) dan olingan API key (bepul) |
| `ADMIN_ID` | Adminning Telegram ID raqami |
| `PAYMENT_CARD` | To'lov qabul qiluvchi karta raqami |
| `PAYMENT_NAME` | Karta egasining ismi |

## 🚀 Ishga tushirish

```bash
pip install -r requirements.txt
python bot.py
```

## 📁 Fayl tuzilmasi

```
├── bot.py          # Asosiy bot kodi
├── groq_api.py     # Groq AI integratsiyasi
├── database.py     # SQLite bazasi
├── requirements.txt
└── .gitignore
```
