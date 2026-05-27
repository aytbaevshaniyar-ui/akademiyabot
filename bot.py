import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import threading
from dotenv import load_dotenv
from database import Database
from groq_api import generate_work

load_dotenv()

BOT_TOKEN    = os.getenv("BOT_TOKEN")
ADMIN_ID     = int(os.getenv("ADMIN_ID", "0"))
PAYMENT_CARD = os.getenv("PAYMENT_CARD", "8600 0000 0000 0000")
PAYMENT_NAME = os.getenv("PAYMENT_NAME", "Ism Familiya")

bot = telebot.TeleBot(BOT_TOKEN)
db  = Database()

WORK_TYPES = {
    "mustaqil": {
        "name": "📝 Mustaqil ish",
        "prices": {"5": 15000, "10": 25000, "15": 35000}
    },
    "yozma": {
        "name": "✍️ Yozma ish",
        "prices": {"10": 30000, "15": 45000, "20": 60000}
    },
    "amaliy": {
        "name": "🔬 Amaliy ish",
        "prices": {"10": 35000, "15": 50000, "20": 65000}
    },
    "diplom": {
        "name": "🎓 Diplom ishi",
        "prices": {"50": 300000, "60": 350000, "70": 400000}
    },
}

# Foydalanuvchi holatlari
user_states = {}

# ================================================
# YORDAMCHI FUNKSIYALAR
# ================================================
def main_menu():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("📝 Mustaqil ish", callback_data="work_mustaqil"),
        InlineKeyboardButton("✍️ Yozma ish",    callback_data="work_yozma")
    )
    kb.row(
        InlineKeyboardButton("🔬 Amaliy ish",  callback_data="work_amaliy"),
        InlineKeyboardButton("🎓 Diplom ishi", callback_data="work_diplom")
    )
    kb.row(InlineKeyboardButton("📋 Buyurtmalarim", callback_data="my_orders"))
    kb.row(InlineKeyboardButton("❓ Yordam",          callback_data="help"))
    return kb

def back_btn():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_start"))
    return kb

# ================================================
# /start
# ================================================
@bot.message_handler(commands=["start"])
def start(msg):
    db.add_user(msg.from_user.id, msg.from_user.username or msg.from_user.first_name)
    user_states.pop(msg.from_user.id, None)
    bot.send_message(
        msg.chat.id,
        f"👋 Assalomu alaykum, *{msg.from_user.first_name}*\\!\n\n"
        "🎓 *AkademiyaBot*ga xush kelibsiz\\!\n\n"
        "Bu bot sizga akademik ishlarni tez va sifatli yozib beradi:\n\n"
        "📝 *Mustaqil ish* — 5/10/15 varaq\n"
        "✍️ *Yozma ish* — 10/15/20 varaq\n"
        "🔬 *Amaliy ish* — 10/15/20 varaq\n"
        "🎓 *Diplom ishi* — 50/60/70 varaq\n\n"
        "👇 Kerakli ish turini tanlang:",
        reply_markup=main_menu(),
        parse_mode="MarkdownV2"
    )

# ================================================
# /admin
# ================================================
@bot.message_handler(commands=["admin"])
def admin_cmd(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    s = db.get_stats()
    bot.send_message(
        msg.chat.id,
        f"👨‍💼 *Admin panel*\n\n"
        f"👥 Foydalanuvchilar: *{s['users']}* ta\n"
        f"📋 Jami buyurtmalar: *{s['total']}* ta\n"
        f"✅ Bajarilgan: *{s['completed']}* ta\n"
        f"⏳ Kutilayotgan: *{s['pending']}* ta\n"
        f"❌ Rad etilgan: *{s['rejected']}* ta\n"
        f"💰 Jami daromad: *{s['revenue']:,} so'm*",
        parse_mode="Markdown"
    )

# ================================================
# MAVZU KIRITISH (matn xabarlari)
# ================================================
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("state") == "wait_topic")
def got_topic(msg):
    topic = msg.text.strip()
    if len(topic) < 5:
        bot.send_message(msg.chat.id, "❌ Mavzu juda qisqa. To'liqroq yozing.")
        return

    uid      = msg.from_user.id
    work_key = user_states[uid]["work_key"]
    work_info = WORK_TYPES[work_key]
    user_states[uid]["topic"] = topic
    user_states[uid]["state"] = "wait_pages"

    kb = InlineKeyboardMarkup()
    for pages, price in work_info["prices"].items():
        kb.add(InlineKeyboardButton(
            f"📄 {pages} varaq  —  {int(price):,} so'm",
            callback_data=f"pages_{pages}_{price}"
        ))
    kb.add(InlineKeyboardButton("🔙 Orqaga", callback_data=f"work_{work_key}"))

    bot.send_message(
        msg.chat.id,
        f"✅ Mavzu qabul qilindi:\n*{topic}*\n\n📄 Necha varaqlik ish kerak?",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ================================================
# CALLBACK HANDLER
# ================================================
@bot.callback_query_handler(func=lambda c: True)
def callback(call):
    uid  = call.from_user.id
    data = call.data

    # ── Bosh menu ──────────────────────────────
    if data == "back_start":
        user_states.pop(uid, None)
        bot.edit_message_text(
            "🏠 *Bosh menyu*\n\nKerakli ish turini tanlang:",
            call.message.chat.id, call.message.message_id,
            reply_markup=main_menu(), parse_mode="Markdown"
        )

    # ── Ish turi ───────────────────────────────
    elif data.startswith("work_"):
        work_key  = data.replace("work_", "")
        work_info = WORK_TYPES[work_key]
        user_states[uid] = {"state": "wait_topic", "work_key": work_key,
                             "work_name": work_info["name"]}
        price_lines = "\n".join(
            f"  • {p} varaq → {int(n):,} so'm"
            for p, n in work_info["prices"].items()
        )
        bot.edit_message_text(
            f"{work_info['name']} tanlandi ✅\n\n"
            f"💰 *Narxlar:*\n{price_lines}\n\n"
            "✏️ *Mavzuni kiriting:*\n"
            "_Masalan: O'zbekistonda kichik biznes_",
            call.message.chat.id, call.message.message_id,
            reply_markup=back_btn(), parse_mode="Markdown"
        )

    # ── Varaq soni ─────────────────────────────
    elif data.startswith("pages_"):
        if uid not in user_states or "topic" not in user_states.get(uid, {}):
            bot.answer_callback_query(call.id, "Iltimos qaytadan boshlang")
            return
        parts = data.split("_")
        pages = parts[1]
        price = int(parts[2])
        user_states[uid]["pages"] = pages
        user_states[uid]["price"] = price

        work_name = user_states[uid]["work_name"]
        topic     = user_states[uid]["topic"]

        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("✅ Tasdiqlash va to'lash", callback_data="confirm"))
        kb.add(InlineKeyboardButton("🔙 Orqaga", callback_data=f"work_{user_states[uid]['work_key']}"))

        bot.edit_message_text(
            "📋 *Buyurtma tafsilotlari:*\n\n"
            f"📌 Ish turi: *{work_name}*\n"
            f"📝 Mavzu: *{topic}*\n"
            f"📄 Varaq soni: *{pages} varaq*\n"
            f"💰 Narx: *{price:,} so'm*\n\n"
            "Tasdiqlaysizmi?",
            call.message.chat.id, call.message.message_id,
            reply_markup=kb, parse_mode="Markdown"
        )

    # ── Tasdiqlash ─────────────────────────────
    elif data == "confirm":
        if uid not in user_states:
            bot.answer_callback_query(call.id, "Iltimos qaytadan boshlang")
            return
        st    = user_states[uid]
        price = st["price"]
        order_id = db.create_order(uid, st["work_key"], st["topic"], st["pages"], price)
        user_states[uid]["order_id"] = order_id

        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("✅ To'lov qildim", callback_data=f"paid_{order_id}"))
        kb.add(InlineKeyboardButton("❌ Bekor qilish",  callback_data="cancel"))

        bot.edit_message_text(
            "💳 *To'lov ma'lumotlari:*\n\n"
            f"💰 Summa: *{price:,} so'm*\n"
            f"🏦 Karta: `{PAYMENT_CARD}`\n"
            f"👤 Egasi: *{PAYMENT_NAME}*\n\n"
            f"📋 Buyurtma raqami: *#{order_id}*\n\n"
            "1️⃣ Kartaga pul o'tkazing\n"
            "2️⃣ *«To'lov qildim»* tugmasini bosing\n"
            "3️⃣ Admin tasdiqlaydi → ish yuboriladi ✅",
            call.message.chat.id, call.message.message_id,
            reply_markup=kb, parse_mode="Markdown"
        )

    # ── To'lov qilindi ─────────────────────────
    elif data.startswith("paid_"):
        order_id = int(data.split("_")[1])
        order    = db.get_order(order_id)
        db.update_status(order_id, "waiting")

        admin_kb = InlineKeyboardMarkup()
        admin_kb.row(
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"adm_ok_{order_id}"),
            InlineKeyboardButton("❌ Rad etish",  callback_data=f"adm_no_{order_id}")
        )
        try:
            bot.send_message(
                ADMIN_ID,
                f"🔔 *Yangi to'lov!*\n\n"
                f"👤 @{call.from_user.username or call.from_user.first_name} (ID: `{uid}`)\n"
                f"📋 Buyurtma: *#{order_id}*\n"
                f"📌 Tur: {WORK_TYPES[order['work_type']]['name']}\n"
                f"📝 Mavzu: {order['topic']}\n"
                f"📄 Varaq: {order['pages']} ta\n"
                f"💰 Summa: *{order['price']:,} so'm*",
                reply_markup=admin_kb,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Admin xabar xatolik: {e}")

        bot.edit_message_text(
            "✅ *To'lov ma'lumoti yuborildi!*\n\n"
            "⏳ Admin to'lovingizni tekshirmoqda...\n"
            "Tasdiqlangach, ish avtomatik tayyorlanib yuboriladi.\n\n"
            f"📋 Buyurtma raqamingiz: *#{order_id}*",
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown"
        )
        user_states.pop(uid, None)

    # ── Bekor qilish ───────────────────────────
    elif data == "cancel":
        user_states.pop(uid, None)
        bot.edit_message_text(
            "❌ Bekor qilindi.\n\n/start — qayta boshlash",
            call.message.chat.id, call.message.message_id
        )

    # ── Mening buyurtmalarim ───────────────────
    elif data == "my_orders":
        orders = db.get_user_orders(uid)
        if not orders:
            bot.edit_message_text(
                "📋 Sizda hali buyurtmalar yo'q.\n\nYangi ish buyurtma qiling!",
                call.message.chat.id, call.message.message_id,
                reply_markup=back_btn()
            )
            return
        STATUS = {
            "pending": "⏳ To'lov kutilmoqda",
            "waiting": "🔄 Tasdiqlanmoqda",
            "generating": "⚙️ Tayyorlanmoqda",
            "completed": "✅ Bajarildi",
            "rejected": "❌ Rad etildi",
            "error": "⚠️ Xatolik",
        }
        text = "📋 *Sizning buyurtmalaringiz:*\n\n"
        for o in orders[-8:]:
            st = STATUS.get(o["status"], o["status"])
            text += (
                f"{st}\n"
                f"  #{o['id']} — {WORK_TYPES[o['work_type']]['name']}\n"
                f"  📝 {o['topic'][:35]}\n"
                f"  📄 {o['pages']} varaq | 💰 {o['price']:,} so'm\n\n"
            )
        bot.edit_message_text(
            text, call.message.chat.id, call.message.message_id,
            reply_markup=back_btn(), parse_mode="Markdown"
        )

    # ── Yordam ─────────────────────────────────
    elif data == "help":
        bot.edit_message_text(
            "❓ *Yordam*\n\n"
            "*Qanday ishlaydi?*\n"
            "1️⃣ Ish turini tanlang\n"
            "2️⃣ Mavzuni kiriting\n"
            "3️⃣ Varaq sonini tanlang\n"
            "4️⃣ Kartaga pul o'tkering\n"
            "5️⃣ «To'lov qildim» tugmasini bosing\n"
            "6️⃣ Admin tasdiqlaydi → ish yuboriladi ✅\n\n"
            "*Muammo bo'lsa:*\n"
            "Admin: @SIZNING_USERNAME",
            call.message.chat.id, call.message.message_id,
            reply_markup=back_btn(), parse_mode="Markdown"
        )

    # ── Admin: Tasdiqlash ──────────────────────
    elif data.startswith("adm_ok_"):
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Ruxsat yo'q!")
            return
        order_id = int(data.split("_")[2])
        order    = db.get_order(order_id)
        db.update_status(order_id, "generating")

        bot.edit_message_text(
            f"⚙️ Buyurtma #{order_id} tayyorlanmoqda...",
            call.message.chat.id, call.message.message_id
        )
        bot.send_message(
            order["user_id"],
            f"✅ *To'lovingiz tasdiqlandi!*\n\n"
            f"⚙️ Ish tayyorlanmoqda, biroz kuting...\n"
            f"📋 Buyurtma #{order_id}",
            parse_mode="Markdown"
        )

        # Alohida threadda generate qilish
        def gen():
            try:
                work_text = generate_work(order["work_type"], order["topic"], int(order["pages"]))
                safe      = order["topic"][:40].replace(" ", "_").replace("/", "-")
                filename  = f"{order['work_type']}_{safe}.txt"
                filepath  = f"/tmp/{filename}"
                with open(filepath, "w", encoding="utf-8") as f:
                    header = (
                        f"ISH TURI: {WORK_TYPES[order['work_type']]['name']}\n"
                        f"MAVZU: {order['topic']}\n"
                        f"VARAQ SONI: {order['pages']} varaq\n"
                        f"{'='*60}\n\n"
                    )
                    f.write(header + work_text)

                with open(filepath, "rb") as f:
                    bot.send_document(
                        order["user_id"], f,
                        visible_file_name=filename,
                        caption=f"🎉 *{WORK_TYPES[order['work_type']]['name']}* tayyor!\n\n"
                                f"📝 Mavzu: {order['topic']}\n"
                                f"📄 {order['pages']} varaq\n\n"
                                "✅ Muvaffaqiyatli tayyorlandi!\n"
                                "Botdan foydalanganingiz uchun rahmat 🙏",
                        parse_mode="Markdown"
                    )
                db.update_status(order_id, "completed")
                bot.send_message(ADMIN_ID, f"✅ Buyurtma #{order_id} bajarildi!")
            except Exception as e:
                db.update_status(order_id, "error")
                bot.send_message(order["user_id"], "❌ Xatolik yuz berdi. Admin bilan bog'laning.")
                bot.send_message(ADMIN_ID, f"❌ Buyurtma #{order_id} xatolik: {str(e)}")

        threading.Thread(target=gen).start()

    # ── Admin: Rad etish ───────────────────────
    elif data.startswith("adm_no_"):
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Ruxsat yo'q!")
            return
        order_id = int(data.split("_")[2])
        order    = db.get_order(order_id)
        db.update_status(order_id, "rejected")
        bot.send_message(
            order["user_id"],
            f"❌ *Buyurtma #{order_id} rad etildi.*\n\n"
            "To'lov tasdiqlanmadi. Admin bilan bog'laning.",
            parse_mode="Markdown"
        )
        bot.edit_message_text(
            f"❌ Buyurtma #{order_id} rad etildi.",
            call.message.chat.id, call.message.message_id
        )

    bot.answer_callback_query(call.id)

# ================================================
# ISHGA TUSHIRISH
# ================================================
if __name__ == "__main__":
    print("✅ Bot muvaffaqiyatli ishga tushdi!")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
