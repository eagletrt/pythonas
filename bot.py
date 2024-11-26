from database import db
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
from commands import commands

BOT_TOKEN = os.getenv("BOT_TOKEN")

# constant for the deep linking
NOME_COGNOME = "nome.cognome"


async def get_chat_id_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    topic_id = update.message.message_thread_id

    if topic_id is None:
        await update.message.reply_text(f"Id della chat: {chat_id}")
    else:
        await update.message.reply_text(f"Id della chat: {chat_id}, id del topic: {topic_id}")


async def deep_linked_level_1(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_mail = ""
    user_id = update.message.chat_id
    if context.args:
        user_mail = f"{context.args[0]}"
        user_mail = user_mail.replace("___", ".")
        await update.message.reply_text(f"Sei autenticat*. La tua email è {user_mail}@eagletrt.it!")
    else:
        await update.message.reply_text("Attenzione: utilizza il comando /ore altrimenti contatta lo staff IT")
        return
    db.add_user_to_db(user_id, user_mail)


if __name__ == "__main__":
    def main():
        db.create_table()
        db.create_table_ore()

        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", deep_linked_level_1))
        application.add_handler(CommandHandler("odg", commands.handle_odg))
        application.add_handler(CommandHandler("chatid", get_chat_id_topic))
        application.add_handler(CommandHandler("ore", commands.ore))
        application.add_handler(CommandHandler("start", commands.start))
        application.run_polling()

    main()
