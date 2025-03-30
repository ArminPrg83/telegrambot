from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes
)

TOKEN = "7979279592:AAHt2FMV1Uh0sp12VVjcOIvLGUtLSEx2Ev0"
VALID_GROUP_ID = -1002619416296
VALID_INVITE_LINK = "https://t.me/+1DS_plQTweM3YmY0"
ADMIN_USERNAMES = ["armin_mahn", "SoleimaniS", "NavidSatt"]

# خوش‌آمد به ادمین
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    full_name = update.effective_user.full_name
    if username in ADMIN_USERNAMES:
        await update.message.reply_text(
            f"سلام {full_name}! 👋\nبه ربات امنیتی ما خوش اومدی 🤖🔥"
        )
    else:
        await update.message.reply_text("⛔️ شما ادمین این ربات نیستید!")

# بررسی اعضای جدید
async def handle_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != VALID_GROUP_ID:
        print("📭 عضو جدید توی گروه اشتباه → نادیده گرفته شد")
        return

    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await update.message.reply_text("سلام 👋")
            return

        # بررسی invite_link
        invite_link = update.message.invite_link
        invite_link_str = invite_link.invite_link if invite_link else "None"

        print("👤 عضو جدید:", member.username or member.first_name)
        print("📎 invite_link:", invite_link_str)

        # ارسال گزارش به گروه (برای تست)
        await context.bot.send_message(
            chat_id=VALID_GROUP_ID,
            text=(
                f"👤 عضو جدید: @{member.username or member.first_name}\n"
                f"🆔 ID: {member.id}\n"
                f"📎 Link: {invite_link_str}"
            )
        )

        # اگر invite_link نداشت یا اشتباه بود → حذفش کن
        if invite_link is None or invite_link.invite_link != VALID_INVITE_LINK:
            try:
                await context.bot.ban_chat_member(chat_id=VALID_GROUP_ID, user_id=member.id)
                await context.bot.unban_chat_member(chat_id=VALID_GROUP_ID, user_id=member.id)

                report = (
                    f"🚨 حذف کاربر غیرمجاز:\n"
                    f"• نام: @{member.username or member.first_name}\n"
                    f"• آی‌دی: `{member.id}`\n"
                    f"• لینک دعوت: {invite_link_str}\n"
                    f"• دلیل: لینک نداشت یا اشتباه بود"
                )

                print("✅ حذف شد:", member.id)

                for username in ADMIN_USERNAMES:
                    try:
                        chat = await context.bot.get_chat(username)
                        await context.bot.send_message(chat_id=chat.id, text=report, parse_mode="Markdown")
                    except Exception as e:
                        print(f"❗ خطا در ارسال گزارش به {username}: {e}")

            except Exception as e:
                err = f"❌ خطا در حذف کاربر @{member.username or member.first_name}:\n{e}"
                await context.bot.send_message(chat_id=VALID_GROUP_ID, text=err)
                print(err)
        else:
            print("🟢 عضو مجاز بود → حذف نشد")

# اجرای ربات
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_members))

print("🤖 ربات دیباگ‌شده با موفقیت اجرا شد!")
app.run_polling()
