import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from database import Database
from gemini_api import generate_work

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================================================
# SOZLAMALAR - O'ZINGIZGA MOSLANG
# ================================================
BOT_TOKEN     = os.getenv("BOT_TOKEN")
ADMIN_ID      = int(os.getenv("ADMIN_ID", "0"))
PAYMENT_CARD  = os.getenv("PAYMENT_CARD", "8600 0000 0000 0000")
PAYMENT_NAME  = os.getenv("PAYMENT_NAME", "Ism Familiya")

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

# ================================================
# CONVERSATION STATES
# ================================================
SELECT_WORK, ENTER_TOPIC, SELECT_PAGES, CONFIRM, WAIT_PAY = range(5)

db = Database()

# ================================================
# /start
# ================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username or user.first_name)
    context.user_data.clear()

    kb = [
        [InlineKeyboardButton("📝 Mustaqil ish", callback_data="work_mustaqil"),
         InlineKeyboardButton("✍️ Yozma ish",    callback_data="work_yozma")],
        [InlineKeyboardButton("🔬 Amaliy ish",   callback_data="work_amaliy"),
         InlineKeyboardButton("🎓 Diplom ishi",  callback_data="work_diplom")],
        [InlineKeyboardButton("📋 Buyurtmalarim", callback_data="my_orders")],
        [InlineKeyboardButton("❓ Yordam",         callback_data="help")],
    ]
    await update.message.reply_text(
        f"👋 Assalomu alaykum, *{user.first_name}*!\n\n"
        "🎓 *AkademiyaBot*ga xush kelibsiz!\n\n"
        "Bu bot sizga akademik ishlarni tez va sifatli yozib beradi:\n\n"
        "📝 *Mustaqil ish* — 5/10/15 varaq\n"
        "✍️ *Yozma ish* — 10/15/20 varaq\n"
        "🔬 *Amaliy ish* — 10/15/20 varaq\n"
        "🎓 *Diplom ishi* — 50/60/70 varaq\n\n"
        "👇 Kerakli ish turini tanlang:",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

# ================================================
# ISH TURINI TANLASH
# ================================================
async def select_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    work_key  = query.data.replace("work_", "")
    work_info = WORK_TYPES[work_key]
    context.user_data["work_key"]  = work_key
    context.user_data["work_name"] = work_info["name"]

    price_lines = "\n".join(
        f"  • {p} varaq → {int(n):,} so'm"
        for p, n in work_info["prices"].items()
    )

    kb = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_start")]]
    await query.edit_message_text(
        f"{work_info['name']} tanlandi ✅\n\n"
        f"💰 *Narxlar:*\n{price_lines}\n\n"
        "✏️ *Mavzuni kiriting:*\n"
        "_Masalan: O'zbekistonda kichik biznesni rivojlantirish_",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )
    return ENTER_TOPIC

# ================================================
# MAVZU KIRITISH
# ================================================
async def enter_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text.strip()

    if len(topic) < 5:
        await update.message.reply_text(
            "❌ Mavzu juda qisqa. Iltimos, to'liqroq yozing.\n"
            "_Masalan: Moliyaviy menejment va uning ahamiyati_",
            parse_mode="Markdown"
        )
        return ENTER_TOPIC

    context.user_data["topic"] = topic
    work_key  = context.user_data["work_key"]
    work_info = WORK_TYPES[work_key]

    kb = []
    for pages, price in work_info["prices"].items():
        kb.append([InlineKeyboardButton(
            f"📄 {pages} varaq  —  {int(price):,} so'm",
            callback_data=f"pages_{pages}_{price}"
        )])
    kb.append([InlineKeyboardButton("🔙 Orqaga", callback_data=f"work_{work_key}")])

    await update.message.reply_text(
        f"✅ Mavzu qabul qilindi:\n*{topic}*\n\n"
        "📄 Necha varaqlik ish kerak?",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )
    return SELECT_PAGES

# ================================================
# VARAQ SONINI TANLASH
# ================================================
async def select_pages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")   # pages_10_30000
    pages = parts[1]
    price = int(parts[2])

    context.user_data["pages"] = pages
    context.user_data["price"] = price

    work_name = context.user_data["work_name"]
    topic     = context.user_data["topic"]

    kb = [
        [InlineKeyboardButton("✅ Tasdiqlash va to'lash", callback_data="confirm")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data=f"work_{context.user_data['work_key']}")],
    ]
    await query.edit_message_text(
        "📋 *Buyurtma tafsilotlari:*\n\n"
        f"📌 Ish turi: *{work_name}*\n"
        f"📝 Mavzu: *{topic}*\n"
        f"📄 Varaq soni: *{pages} varaq*\n"
        f"💰 Narx: *{price:,} so'm*\n\n"
        "Tasdiqlaysizmi?",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )
    return CONFIRM

# ================================================
# TASDIQLASH → TO'LOV MA'LUMOTI
# ================================================
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user     = query.from_user
    price    = context.user_data["price"]
    order_id = db.create_order(
        user_id   = user.id,
        work_type = context.user_data["work_key"],
        topic     = context.user_data["topic"],
        pages     = context.user_data["pages"],
        price     = price
    )
    context.user_data["order_id"] = order_id

    kb = [
        [InlineKeyboardButton("✅ To'lov qildim", callback_data=f"paid_{order_id}")],
        [InlineKeyboardButton("❌ Bekor qilish",  callback_data="cancel")],
    ]
    await query.edit_message_text(
        "💳 *To'lov ma'lumotlari:*\n\n"
        f"💰 Summa: *{price:,} so'm*\n"
        f"🏦 Karta: `{PAYMENT_CARD}`\n"
        f"👤 Egasi: *{PAYMENT_NAME}*\n\n"
        f"📋 Buyurtma raqami: *#{order_id}*\n\n"
        "1️⃣ Yuqoridagi kartaga pul o'tkazing\n"
        "2️⃣ *«To'lov qildim»* tugmasini bosing\n"
        "3️⃣ Admin tasdiqlaydi → ish tayyor bo'ladi ✅",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )
    return WAIT_PAY

# ================================================
# TO'LOV QILINDI → ADMINGA XABAR
# ================================================
async def payment_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split("_")[1])
    user     = query.from_user
    order    = db.get_order(order_id)

    db.update_status(order_id, "waiting")

    # Adminga xabar
    admin_kb = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"adm_ok_{order_id}"),
            InlineKeyboardButton("❌ Rad etish",  callback_data=f"adm_no_{order_id}"),
        ]
    ]
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔔 *Yangi to'lov!*\n\n"
                 f"👤 @{user.username or user.first_name} (ID: `{user.id}`)\n"
                 f"📋 Buyurtma: *#{order_id}*\n"
                 f"📌 Tur: {WORK_TYPES[order['work_type']]['name']}\n"
                 f"📝 Mavzu: {order['topic']}\n"
                 f"📄 Varaq: {order['pages']} ta\n"
                 f"💰 Summa: *{order['price']:,} so'm*",
            reply_markup=InlineKeyboardMarkup(admin_kb),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Admin xabarda xatolik: {e}")

    await query.edit_message_text(
        "✅ *To'lov ma'lumoti yuborildi!*\n\n"
        "⏳ Admin to'lovingizni tekshirmoqda...\n"
        "Tasdiqlangach, ish avtomatik tayyorlanib yuboriladi.\n\n"
        f"📋 Buyurtma raqamingiz: *#{order_id}*\n\n"
        "🕐 Odatda 5-15 daqiqa ichida tayyor bo'ladi.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# ================================================
# ADMIN: TASDIQLASH → ISH GENERATSIYA
# ================================================
async def admin_ok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    order_id = int(query.data.split("_")[2])
    order    = db.get_order(order_id)

    if not order:
        await query.edit_message_text("❌ Buyurtma topilmadi.")
        return

    db.update_status(order_id, "generating")
    await query.edit_message_text(f"⚙️ Buyurtma #{order_id} uchun ish tayyorlanmoqda...")

    # Foydalanuvchiga xabar
    await context.bot.send_message(
        chat_id=order["user_id"],
        text=f"✅ *To'lovingiz tasdiqlandi!*\n\n"
             f"⚙️ Ish tayyorlanmoqda...\n"
             f"📋 Buyurtma #{order_id}\n\n"
             "Biroz kuting, tez orada yuboriladi 🚀",
        parse_mode="Markdown"
    )

    try:
        # AI orqali ish yaratish
        work_text = await generate_work(
            work_type = order["work_type"],
            topic     = order["topic"],
            pages     = int(order["pages"])
        )

        # Faylga yozish
        safe_topic = order["topic"][:40].replace(" ", "_").replace("/", "-")
        filename   = f"{order['work_type']}_{safe_topic}.txt"
        filepath   = f"/tmp/{filename}"

        with open(filepath, "w", encoding="utf-8") as f:
            header = (
                f"ISH TURI: {WORK_TYPES[order['work_type']]['name']}\n"
                f"MAVZU: {order['topic']}\n"
                f"VARAQ SONI: {order['pages']} varaq\n"
                f"{'='*60}\n\n"
            )
            f.write(header + work_text)

        # Foydalanuvchiga yuborish
        with open(filepath, "rb") as f:
            await context.bot.send_document(
                chat_id  = order["user_id"],
                document = f,
                filename = filename,
                caption  = f"🎉 *{WORK_TYPES[order['work_type']]['name']}* tayyor!\n\n"
                           f"📝 Mavzu: {order['topic']}\n"
                           f"📄 {order['pages']} varaq\n\n"
                           "✅ Muvaffaqiyatli tayyorlandi!\n"
                           "Botdan foydalanganingiz uchun rahmat 🙏",
                parse_mode="Markdown"
            )

        db.update_status(order_id, "completed")
        await query.edit_message_text(
            f"✅ Buyurtma #{order_id} bajarildi!\n"
            f"📤 Foydalanuvchiga yuborildi."
        )

    except Exception as e:
        logger.error(f"Generatsiya xatoligi: {e}")
        db.update_status(order_id, "error")
        await context.bot.send_message(
            chat_id=order["user_id"],
            text="❌ Texnik xatolik yuz berdi.\nIltimos, admin bilan bog'laning."
        )
        await query.edit_message_text(f"❌ Xatolik yuz berdi: {str(e)}")

# ================================================
# ADMIN: RAD ETISH
# ================================================
async def admin_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    order_id = int(query.data.split("_")[2])
    order    = db.get_order(order_id)

    db.update_status(order_id, "rejected")

    await context.bot.send_message(
        chat_id=order["user_id"],
        text=f"❌ *Buyurtma #{order_id} rad etildi.*\n\n"
             "To'lov tasdiqlanmadi.\n"
             "Savol bo'lsa admin bilan bog'laning.",
        parse_mode="Markdown"
    )
    await query.edit_message_text(f"❌ Buyurtma #{order_id} rad etildi.")

# ================================================
# MENING BUYURTMALARIM
# ================================================
async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    orders = db.get_user_orders(query.from_user.id)

    if not orders:
        kb = [[InlineKeyboardButton("🏠 Bosh menu", callback_data="back_start")]]
        await query.edit_message_text(
            "📋 Sizda hali buyurtmalar yo'q.\n\nYangi ish buyurtma qiling!",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    STATUS = {
        "pending":    "⏳ To'lov kutilmoqda",
        "waiting":    "🔄 Tasdiqlanmoqda",
        "generating": "⚙️ Tayyorlanmoqda",
        "completed":  "✅ Bajarildi",
        "rejected":   "❌ Rad etildi",
        "error":      "⚠️ Xatolik",
    }

    text = "📋 *Sizning buyurtmalaringiz:*\n\n"
    for o in orders[-8:]:
        st = STATUS.get(o["status"], o["status"])
        text += (
            f"{st}\n"
            f"  #{o['id']} — {WORK_TYPES[o['work_type']]['name']}\n"
            f"  📝 {o['topic'][:35]}...\n"
            f"  📄 {o['pages']} varaq | 💰 {o['price']:,} so'm\n\n"
        )

    kb = [[InlineKeyboardButton("🏠 Bosh menu", callback_data="back_start")]]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

# ================================================
# YORDAM
# ================================================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    kb = [[InlineKeyboardButton("🏠 Bosh menu", callback_data="back_start")]]
    await query.edit_message_text(
        "❓ *Yordam*\n\n"
        "*Qanday ishlaydi?*\n"
        "1️⃣ Ish turini tanlang\n"
        "2️⃣ Mavzuni kiriting\n"
        "3️⃣ Varaq sonini tanlang\n"
        "4️⃣ Kartaga pul o'tkering\n"
        "5️⃣ «To'lov qildim» tugmasini bosing\n"
        "6️⃣ Admin tasdiqlaydi → ish .txt faylda yuboriladi ✅\n\n"
        "*Qancha vaqt ketadi?*\n"
        "To'lov tasdiqlanib, 2-5 daqiqada tayyor bo'ladi.\n\n"
        "*Muammo bo'lsa:*\n"
        "Admin: @SIZNING_USERNAME",  # ← O'zingizning Telegram username yozing
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

# ================================================
# ORQAGA / BEKOR QILISH
# ================================================
async def back_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()

    kb = [
        [InlineKeyboardButton("📝 Mustaqil ish", callback_data="work_mustaqil"),
         InlineKeyboardButton("✍️ Yozma ish",    callback_data="work_yozma")],
        [InlineKeyboardButton("🔬 Amaliy ish",   callback_data="work_amaliy"),
         InlineKeyboardButton("🎓 Diplom ishi",  callback_data="work_diplom")],
        [InlineKeyboardButton("📋 Buyurtmalarim", callback_data="my_orders")],
        [InlineKeyboardButton("❓ Yordam",         callback_data="help")],
    ]
    await query.edit_message_text(
        "🏠 *Bosh menyu*\n\nKerakli ish turini tanlang:",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    kb = [[InlineKeyboardButton("🏠 Bosh menu", callback_data="back_start")]]
    await query.edit_message_text(
        "❌ Bekor qilindi.",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return ConversationHandler.END

async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Bekor qilindi. /start — qayta boshlash")
    return ConversationHandler.END

# ================================================
# ADMIN PANEL
# ================================================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    stats = db.get_stats()
    await update.message.reply_text(
        "👨‍💼 *Admin panel*\n\n"
        f"👥 Foydalanuvchilar: *{stats['users']}* ta\n"
        f"📋 Jami buyurtmalar: *{stats['total']}* ta\n"
        f"✅ Bajarilgan: *{stats['completed']}* ta\n"
        f"⏳ Kutilayotgan: *{stats['pending']}* ta\n"
        f"❌ Rad etilgan: *{stats['rejected']}* ta\n"
        f"💰 Jami daromad: *{stats['revenue']:,} so'm*",
        parse_mode="Markdown"
    )

# ================================================
# MAIN
# ================================================
def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN .env faylida topilmadi!")

    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(select_work, pattern="^work_")
        ],
        states={
            ENTER_TOPIC:  [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_topic)],
            SELECT_PAGES: [CallbackQueryHandler(select_pages, pattern="^pages_")],
            CONFIRM:      [CallbackQueryHandler(confirm_order, pattern="^confirm$")],
            WAIT_PAY:     [CallbackQueryHandler(payment_done, pattern="^paid_")],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_cmd),
            CallbackQueryHandler(cancel, pattern="^cancel$"),
            CallbackQueryHandler(back_start, pattern="^back_start$"),
            CallbackQueryHandler(select_work, pattern="^work_"),
        ],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("admin",  admin_panel))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(back_start, pattern="^back_start$"))
    app.add_handler(CallbackQueryHandler(my_orders,  pattern="^my_orders$"))
    app.add_handler(CallbackQueryHandler(help_cmd,   pattern="^help$"))
    app.add_handler(CallbackQueryHandler(admin_ok,   pattern="^adm_ok_"))
    app.add_handler(CallbackQueryHandler(admin_no,   pattern="^adm_no_"))

    logger.info("✅ Bot muvaffaqiyatli ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
