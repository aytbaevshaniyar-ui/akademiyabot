import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import threading
from dotenv import load_dotenv
from database import Database
from ai_api import generate_work

load_dotenv()

BOT_TOKEN    = os.getenv("BOT_TOKEN")
ADMIN_ID     = int(os.getenv("ADMIN_ID", "0"))
PAYMENT_CARD = os.getenv("PAYMENT_CARD", "8600 0000 0000 0000")
PAYMENT_NAME = os.getenv("PAYMENT_NAME", "Ism Familiya")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
db  = Database()

WORK_TYPES = {
    "mustaqil": {
        "name": "Mustaqil ish",
        "prices": {"5": 15000, "10": 25000, "15": 35000}
    },
    "yozma": {
        "name": "Yozma ish",
        "prices": {"10": 30000, "15": 45000, "20": 60000}
    },
    "amaliy": {
        "name": "Amaliy ish",
        "prices": {"10": 35000, "15": 50000, "20": 65000}
    },
    "diplom": {
        "name": "Diplom ishi",
        "prices": {"50": 300000, "60": 350000, "70": 400000}
    },
}

user_states = {}

def main_menu():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("Mustaqil ish", callback_data="work_mustaqil"),
        InlineKeyboardButton("Yozma ish", callback_data="work_yozma")
    )
    kb.row(
        InlineKeyboardButton("Amaliy ish", callback_data="work_amaliy"),
        InlineKeyboardButton("Diplom ishi", callback_data="work_diplom")
    )
    kb.row(InlineKeyboardButton("Buyurtmalarim", callback_data="my_orders"))
    kb.row(InlineKeyboardButton("Yordam", callback_data="help"))
    return kb

# ================================================
# /start
# ================================================
@bot.message_handler(commands=["start"])
def start(msg):
    try:
        db.add_user(msg.from_user.id, msg.from_user.username or msg.from_user.first_name)
        user_states.pop(msg.from_user.id, None)
        bot.send_message(
            msg.chat.id,
            "Assalomu alaykum, " + msg.from_user.first_name + "!\n\n"
            "AkademiyaBotga xush kelibsiz!\n\n"
            "Quyidagi ishlarni yozib beramiz:\n"
            "- Mustaqil ish (5/10/15 varaq)\n"
            "- Yozma ish (10/15/20 varaq)\n"
            "- Amaliy ish (10/15/20 varaq)\n"
            "- Diplom ishi (50/60/70 varaq)\n\n"
            "Kerakli ish turini tanlang:",
            reply_markup=main_menu()
        )
    except Exception as e:
        print(f"Start xatolik: {e}")

# ================================================
# /admin
# ================================================
@bot.message_handler(commands=["admin"])
def admin_cmd(msg):
    try:
        if msg.from_user.id != ADMIN_ID:
            return
        s = db.get_stats()
        bot.send_message(
            msg.chat.id,
            "Admin panel\n\n"
            "Foydalanuvchilar: " + str(s['users']) + " ta\n"
            "Jami buyurtmalar: " + str(s['total']) + " ta\n"
            "Bajarilgan: " + str(s['completed']) + " ta\n"
            "Kutilayotgan: " + str(s['pending']) + " ta\n"
            "Daromad: " + str(s['revenue']) + " som"
        )
    except Exception as e:
        print(f"Admin xatolik: {e}")

# ================================================
# MAVZU KIRITISH
# ================================================
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("state") == "wait_topic")
def got_topic(msg):
    try:
        topic = msg.text.strip()
        if len(topic) < 5:
            bot.send_message(msg.chat.id, "Mavzu juda qisqa. Toliqroq yozing.")
            return

        uid = msg.from_user.id
        work_key = user_states[uid]["work_key"]
        work_info = WORK_TYPES[work_key]
        user_states[uid]["topic"] = topic
        user_states[uid]["state"] = "wait_pages"

        kb = InlineKeyboardMarkup()
        for pages, price in work_info["prices"].items():
            kb.add(InlineKeyboardButton(
                str(pages) + " varaq - " + str(int(price)) + " som",
                callback_data="pages_" + str(pages) + "_" + str(price)
            ))
        kb.add(InlineKeyboardButton("Orqaga", callback_data="work_" + work_key))

        bot.send_message(
            msg.chat.id,
            "Mavzu qabul qilindi:\n" + topic + "\n\nNecha varaqlik ish kerak?",
            reply_markup=kb
        )
    except Exception as e:
        print(f"Topic xatolik: {e}")
        bot.send_message(msg.chat.id, "Xatolik yuz berdi. /start bosing.")

# ================================================
# CALLBACK HANDLER
# ================================================
@bot.callback_query_handler(func=lambda c: True)
def callback(call):
    uid = call.from_user.id
    data = call.data

    try:
        bot.answer_callback_query(call.id)

        if data == "back_start":
            user_states.pop(uid, None)
            bot.edit_message_text(
                "Bosh menyu\n\nKerakli ish turini tanlang:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=main_menu()
            )

        elif data.startswith("work_"):
            work_key = data.replace("work_", "")
            work_info = WORK_TYPES[work_key]
            user_states[uid] = {
                "state": "wait_topic",
                "work_key": work_key,
                "work_name": work_info["name"]
            }
            price_lines = ""
            for p, n in work_info["prices"].items():
                price_lines += "  " + str(p) + " varaq = " + str(int(n)) + " som\n"

            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("Orqaga", callback_data="back_start"))

            bot.edit_message_text(
                work_info["name"] + " tanlandi\n\n"
                "Narxlar:\n" + price_lines + "\n"
                "Mavzuni kiriting:\n"
                "Masalan: O'zbekistonda kichik biznes",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=kb
            )

        elif data.startswith("pages_"):
            if uid not in user_states or "topic" not in user_states.get(uid, {}):
                bot.send_message(call.message.chat.id, "Iltimos /start bosib qaytadan boshlang.")
                return

            parts = data.split("_")
            pages = parts[1]
            price = int(parts[2])
            user_states[uid]["pages"] = pages
            user_states[uid]["price"] = price

            work_name = user_states[uid]["work_name"]
            topic = user_states[uid]["topic"]

            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("Tasdiqlash va tolash", callback_data="confirm"))
            kb.add(InlineKeyboardButton("Orqaga", callback_data="work_" + user_states[uid]["work_key"]))

            bot.edit_message_text(
                "Buyurtma tafsilotlari:\n\n"
                "Ish turi: " + work_name + "\n"
                "Mavzu: " + topic + "\n"
                "Varaq soni: " + pages + " varaq\n"
                "Narx: " + str(price) + " som\n\n"
                "Tasdiqlaysizmi?",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=kb
            )

        elif data == "confirm":
            if uid not in user_states:
                bot.send_message(call.message.chat.id, "Iltimos /start bosib qaytadan boshlang.")
                return

            st = user_states[uid]
            price = st["price"]
            order_id = db.create_order(uid, st["work_key"], st["topic"], st["pages"], price)
            user_states[uid]["order_id"] = order_id

            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("Tolov qildim", callback_data="paid_" + str(order_id)))
            kb.add(InlineKeyboardButton("Bekor qilish", callback_data="cancel"))

            bot.edit_message_text(
                "Tolov malumotlari:\n\n"
                "Summa: " + str(price) + " som\n"
                "Karta: " + PAYMENT_CARD + "\n"
                "Egasi: " + PAYMENT_NAME + "\n\n"
                "Buyurtma raqami: #" + str(order_id) + "\n\n"
                "1. Kartaga pul otkering\n"
                "2. Tolov qildim tugmasini bosing\n"
                "3. Admin tasdiqlaydi va ish yuboriladi",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=kb
            )

        elif data.startswith("paid_"):
            order_id = int(data.split("_")[1])
            order = db.get_order(order_id)
            db.update_status(order_id, "waiting")

            admin_kb = InlineKeyboardMarkup()
            admin_kb.row(
                InlineKeyboardButton("Tasdiqlash", callback_data="adm_ok_" + str(order_id)),
                InlineKeyboardButton("Rad etish", callback_data="adm_no_" + str(order_id))
            )

            try:
                bot.send_message(
                    ADMIN_ID,
                    "Yangi tolov!\n\n"
                    "Foydalanuvchi: " + str(call.from_user.username or call.from_user.first_name) + "\n"
                    "ID: " + str(uid) + "\n"
                    "Buyurtma: #" + str(order_id) + "\n"
                    "Tur: " + WORK_TYPES[order["work_type"]]["name"] + "\n"
                    "Mavzu: " + order["topic"] + "\n"
                    "Varaq: " + str(order["pages"]) + " ta\n"
                    "Summa: " + str(order["price"]) + " som",
                    reply_markup=admin_kb
                )
            except Exception as e:
                print("Admin xabar xatolik: " + str(e))

            bot.edit_message_text(
                "Tolov malumoti yuborildi!\n\n"
                "Admin tolovingizni tekshirmoqda...\n"
                "Tasdiqlangach ish yuboriladi.\n\n"
                "Buyurtma raqamingiz: #" + str(order_id),
                call.message.chat.id,
                call.message.message_id
            )
            user_states.pop(uid, None)

        elif data == "cancel":
            user_states.pop(uid, None)
            bot.edit_message_text(
                "Bekor qilindi.\n\n/start - qayta boshlash",
                call.message.chat.id,
                call.message.message_id
            )

        elif data == "my_orders":
            orders = db.get_user_orders(uid)
            if not orders:
                kb = InlineKeyboardMarkup()
                kb.add(InlineKeyboardButton("Bosh menu", callback_data="back_start"))
                bot.edit_message_text(
                    "Sizda hali buyurtmalar yoq.",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=kb
                )
                return

            STATUS = {
                "pending": "Tolov kutilmoqda",
                "waiting": "Tasdiqlanmoqda",
                "generating": "Tayyorlanmoqda",
                "completed": "Bajarildi",
                "rejected": "Rad etildi",
                "error": "Xatolik",
            }
            text = "Sizning buyurtmalaringiz:\n\n"
            for o in orders[-8:]:
                st = STATUS.get(o["status"], o["status"])
                text += (
                    "#" + str(o["id"]) + " - " + WORK_TYPES[o["work_type"]]["name"] + "\n"
                    "Mavzu: " + o["topic"][:35] + "\n"
                    "Varaq: " + str(o["pages"]) + " | Narx: " + str(o["price"]) + " som\n"
                    "Holat: " + st + "\n\n"
                )

            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("Bosh menu", callback_data="back_start"))
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=kb
            )

        elif data == "help":
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("Bosh menu", callback_data="back_start"))
            bot.edit_message_text(
                "Yordam\n\n"
                "Qanday ishlaydi?\n"
                "1. Ish turini tanlang\n"
                "2. Mavzuni kiriting\n"
                "3. Varaq sonini tanlang\n"
                "4. Kartaga pul otkering\n"
                "5. Tolov qildim tugmasini bosing\n"
                "6. Admin tasdiqlaydi va ish yuboriladi\n\n"
                "Muammo bolsa admin bilan boganing:\n"
                "@SIZNING_USERNAME",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=kb
            )

        elif data.startswith("adm_ok_"):
            if uid != ADMIN_ID:
                return
            order_id = int(data.split("_")[2])
            order = db.get_order(order_id)
            db.update_status(order_id, "generating")

            bot.edit_message_text(
                "Buyurtma #" + str(order_id) + " tayyorlanmoqda...",
                call.message.chat.id,
                call.message.message_id
            )
            bot.send_message(
                order["user_id"],
                "Tolovingiz tasdiqlandi!\n\n"
                "Ish tayyorlanmoqda, biroz kuting...\n"
                "Buyurtma #" + str(order_id)
            )

            def gen():
                try:
                    work_text = generate_work(order["work_type"], order["topic"], int(order["pages"]))
                    safe = order["topic"][:40].replace(" ", "_").replace("/", "-")
                    filename = order["work_type"] + "_" + safe + ".txt"
                    filepath = "/tmp/" + filename
                    with open(filepath, "w", encoding="utf-8") as f:
                        header = (
                            "ISH TURI: " + WORK_TYPES[order["work_type"]]["name"] + "\n"
                            "MAVZU: " + order["topic"] + "\n"
                            "VARAQ SONI: " + str(order["pages"]) + " varaq\n"
                            + "="*60 + "\n\n"
                        )
                        f.write(header + work_text)

                    with open(filepath, "rb") as f:
                        bot.send_document(
                            order["user_id"],
                            f,
                            visible_file_name=filename,
                            caption=(
                                WORK_TYPES[order["work_type"]]["name"] + " tayyor!\n\n"
                                "Mavzu: " + order["topic"] + "\n"
                                + str(order["pages"]) + " varaq\n\n"
                                "Muvaffaqiyatli tayyorlandi!\n"
                                "Botdan foydalanganingiz uchun rahmat!"
                            )
                        )
                    db.update_status(order_id, "completed")
                    bot.send_message(ADMIN_ID, "Buyurtma #" + str(order_id) + " bajarildi!")
                except Exception as e:
                    db.update_status(order_id, "error")
                    bot.send_message(order["user_id"], "Xatolik yuz berdi. Admin bilan boganing.")
                    bot.send_message(ADMIN_ID, "Buyurtma #" + str(order_id) + " xatolik: " + str(e))

            threading.Thread(target=gen).start()

        elif data.startswith("adm_no_"):
            if uid != ADMIN_ID:
                return
            order_id = int(data.split("_")[2])
            order = db.get_order(order_id)
            db.update_status(order_id, "rejected")
            bot.send_message(
                order["user_id"],
                "Buyurtma #" + str(order_id) + " rad etildi.\n\n"
                "Tolov tasdiqlanmadi. Admin bilan boganing."
            )
            bot.edit_message_text(
                "Buyurtma #" + str(order_id) + " rad etildi.",
                call.message.chat.id,
                call.message.message_id
            )

    except Exception as e:
        print(f"Callback xatolik [{data}]: {e}")
        try:
            bot.send_message(call.message.chat.id, "Xatolik yuz berdi. /start bosing.")
        except:
            pass

# ================================================
# ISHGA TUSHIRISH
# ================================================
if __name__ == "__main__":
    print("Webhook ochirilyapti...")
    bot.remove_webhook()
    import time
    time.sleep(2)
    print("Bot ishga tushdi!")
    bot.infinity_polling(
        timeout=60,
        long_polling_timeout=60,
        allowed_updates=["message", "callback_query"],
        skip_pending=True
    )
