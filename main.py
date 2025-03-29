from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# لینک دعوت معتبر فقط اینه
VALID_INVITE_LINK = "https://t.me/+1DS_plQTweM3YmY0"

async def handle_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        invite_link = update.message.invite_link
        if invite_link is None or invite_link.invite_link != VALID_INVITE_LINK:
            await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=member.id)
            await context.bot.unban_chat_member(chat_id=update.effective_chat.id, user_id=member.id)
            await update.message.reply_text(
                f"⛔️ @{member.username or member.first_name} بدون لینک مجاز عضو شده و حذف شد."
            )
        else:
            await update.message.reply_text(
                f"🎉 خوش اومدی @{member.username or member.first_name}!"
            )

app = ApplicationBuilder().token("7294768971:AAERr79xQZwCkXCOTZ9bCMyQ27IbKwXx8jc").build()
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_members))
print("ربات ضد نفوذ فعال شد ✅")
app.run_polling()
