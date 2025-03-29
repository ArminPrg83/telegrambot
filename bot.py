import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes
)

# توکن ربات از متغیر محیطی
TOKEN = os.environ["BOT_TOKEN"]

# فقط این لینک مجاز است
VALID_INVITE_LINK = "https://t.me/+1DS_plQTweM3YmY0"

# لیست یوزرنیم ادمین‌ها (بدون @)
ADMIN_USERNAMES = [
    "armin_mahn",
    "SoleimaniS",
    "NavidSatt"
]

# ⬇️ /start → فقط برای ادمین‌ها
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    full_name = update.effective_user.full_name

    if username in ADMIN_USERNAMES:
        await update.message.reply_text(
            f"سلام {full_name}! 👋\n"
            f"به ربات امنیتی ما خوش اومدی 🤖🔥"
        )
    else:
        await update.message.reply_text("⛔️ شما ادمین این ربات نیستید!")

# ⬇️ وقتی کسی عضو گروه می‌شه
async def handle_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        # اگه خود ربات وارد گروه شده → فقط سلام بده
        if member.id == context.bot.id:
            await update.message.reply_text("سلام 👋")
            return

        # بررسی لینک دعوت
        invite_link = update.message.invite_link
        if invite_link is None or invite_link.invite_link != VALID_INVITE_LINK:
            # حذف کاربر
            await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=member.id)
            await context.bot.unban_chat_member(chat_id=update.effective_chat.id, user_id=member.id)

            # گزارش به ادمین‌ها
            report = (
                f"🚨 حذف خودکار کاربر غیرمجاز:\n"
                f"• نام: @{member.username or member.first_name}\n"
                f"• آی‌دی: `{member.id}`\n"
                f"• گروه: {update.effective_chat.title}\n"
                f"• وضعیت: بدون لینک دعوت وارد شد و حذف شد ✅"
            )

            for username in ADMIN_USERNAMES:
                try:
                    chat = await context.bot.get_chat(username)
                    await context.bot.send_message(chat_id=chat.id, text=report, parse_mode="Markdown")
                except Exception as e:
                    print(f"❗ خطا در ارسال گزارش به {username}: {e}")

# راه‌اندازی ربات
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_members))

print("🤖 ربات در حال اجراست...")
app.run_polling()
