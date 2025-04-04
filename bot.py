import os
from telegram import Update, ChatJoinRequest
from telegram.helpers import escape_markdown
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ChatJoinRequestHandler,
    ContextTypes,
    filters
)

# === تنظیمات اصلی ===

TOKEN = "7979279592:AAFhvKPjrrDoR0WaRpFQGjNE3PB1NBIWxYg"  # 🔐 توکن ربات
VALID_GROUP_ID = -1001698161225  # 🏠 آیدی عددی گروه اصلی

ADMIN_IDS = [5420061063, 287579078]  # 🧑‍💻 آیدی عددی ادمین‌هایی که پیام خصوصی بگیرن

# 🟢 کاربران تأیید شده از طریق Join Request
approved_users = set()

# === هندلر /start برای تست دستی در پیوی ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ ربات امنیتی فعال است.")
    await update.message.reply_text(f"Chat ID: `{update.effective_chat.id}`", parse_mode="MarkdownV2")

# ✅ اگر کاربر با join request وارد شد → ثبتش کن
async def handle_join_request(update: ChatJoinRequest, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    approved_users.add(user.id)
    print(f"📥 کاربر مجاز شد از طریق join-request: {user.id}")

# 🧹 اگر کاربر مجاز نیست → حذفش کن
async def handle_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != VALID_GROUP_ID:
        return

    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await update.message.reply_text("سلام! 👋")
            return

        user_id = str(member.id)
        full_name = member.full_name
        username_raw = f"@{member.username}" if member.username else full_name
        username = escape_markdown(username_raw, version=2)

        print(f"\n👤 کاربر وارد شد: {username_raw} ({user_id})")

        if member.id not in approved_users:
            print("❌ کاربر در لیست مجاز نیست → تلاش برای حذف...")

            try:
                result = await context.bot.ban_chat_member(chat_id=VALID_GROUP_ID, user_id=member.id)
                await context.bot.unban_chat_member(chat_id=VALID_GROUP_ID, user_id=member.id)
                print(f"✅ حذف با موفقیت انجام شد (ریسپانس تلگرام: {result})")

                report = (
                    "🚨 *کاربر غیرمجاز حذف شد:*\n\n"
                    f"👤 نام: {username}\n"
                    f"🆔 آی‌دی: `{user_id}`"
                )
                for admin_id in ADMIN_IDS:
                    try:
                        await context.bot.send_message(chat_id=admin_id, text=report, parse_mode="MarkdownV2")
                    except Exception as e:
                        print(f"❌ خطا در ارسال گزارش به {admin_id}: {e}")

            except Exception as e:
                print(f"⛔️ خطا در عملیات ban/unban → {e}")
        else:
            print("✅ کاربر در لیست مجاز بود. باقی می‌مونه.")
            approved_users.remove(member.id)

# === اجرای ربات ===
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(ChatJoinRequestHandler(handle_join_request))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_members))

print("🤖 ربات امنیتی پیشرفته در حال اجراست...")
app.run_polling()
