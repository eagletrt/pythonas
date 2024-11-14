import os
import psycopg2
from telegram import Update, helpers
from telegram.ext import Application, CommandHandler, ContextTypes
from collections import defaultdict
import requests
import json
from telegram.constants import ParseMode

DATABASE_URL = os.getenv("DATABASE_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")


# constant for the deep linking
NOME_COGNOME = "nome.cognome"


def create_table():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS odg_topics (
            id SERIAL PRIMARY KEY,
            topic_id BIGINT,
            author TEXT,
            topic_text TEXT,
            timestamp TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


def create_table_ore():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ore (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            user_mail TEXT,
            timestamp TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


def add_user_to_db(user_id, user_mail):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ore (user_id, user_mail)
        VALUES (%s, %s)
    """, (user_id, user_mail))
    conn.commit()
    cursor.close()
    conn.close()


def get_mail_from_id_db(user_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_mail FROM ore WHERE user_id = %s
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def add_topic_to_db(topic_id, author, topic_text):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO odg_topics (topic_id, author, topic_text)
        VALUES (%s, %s, %s)
    """, (topic_id, author, topic_text))
    conn.commit()
    cursor.close()
    conn.close()


def get_topics_from_db(topic_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT topic_text, author FROM odg_topics WHERE topic_id = %s
    """, (topic_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def reset_topics_in_db(topic_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM odg_topics WHERE topic_id = %s
    """, (topic_id,))
    conn.commit()
    cursor.close()
    conn.close()


# Funzione per gestire i comandi /odg
async def handle_odg(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        # Verifica se 'message_thread_id' esiste, altrimenti usa 'chat.id'
        topic_id = update.message.message_thread_id if update.message.message_thread_id else update.message.chat.id
    except AttributeError:
        # Logga l'errore o gestisci il caso in cui 'update.message' sia None
        print("Errore: 'update.message' è None")
        await update.message.reply_text("Errore con l'id della chat attuale")

    author = update.message.from_user.full_name

    if len(context.args) == 0:
        topics = get_topics_from_db(topic_id)
        if topics:
            topics_text = ""
            for topic_text, author in topics:
                topics_text += f"📋{topic_text}\n👤 {author}\n\n"
            await update.message.reply_text("Contenuto Ordine Del Giorno:\n\n" + topics_text.strip())
        else:
            await update.message.reply_text("Niente in programma, cara")
    elif context.args[0] == "reset":
        reset_topics_in_db(topic_id)  # Reset dei topics nel database
        await update.message.reply_text("odg reset effettuato")
    else:
        topic_text = ' '.join(context.args)
        add_topic_to_db(topic_id, author, topic_text)
        await update.message.reply_text(f"Aggiunto all'odg: {topic_text}")


async def get_chat_id_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    topic_id = update.message.message_thread_id

    if topic_id is None:
        await update.message.reply_text(f"Id della chat: {chat_id}")
    else:
        await update.message.reply_text(f"Id della chat: {chat_id}, id del topic: {topic_id}")


async def is_in_db(user_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_mail FROM ore WHERE user_id = %s
    """, (user_id,))
    mail = cursor.fetchall()
    cursor.close()
    conn.close()
    if mail:
        return True
    else:
        return False


async def deep_linked_level_1(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_mail = ""
    user_id = update.message.chat_id
    if context.args:
        print("Il context arg è " + str(context.args))
        user_mail = f"{context.args[0]}"
        await update.message.reply_text(f"Sei autenticat*. La tua email è {user_mail}@eagletrt.it!")
    else:
        await update.message.reply_text("Attenzione: non sei autenticat*. Contatta lo staff IT")
        return
    add_user_to_db(user_id, user_mail)


async def ore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    in_db = await is_in_db(user_id)
    if in_db is not True:
        url = "https://api.eagletrt.it/api/v2/tecsLinkOre"
        bot = context.bot
        deep_link = helpers.create_deep_linked_url(bot.username)
        text = f"Clicca su <a href='{url}'>questo link</a> per le ore"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    email = get_mail_from_id_db(user_id) 
    url = f"https://api.eagletrt.it/api/v2/oreLab?username={email}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        ore = data.get("ore")
        if ore is None:
            await update.message.reply_text("Errore, contatta lo staff IT.\n Codice errore: in ore function: ore is None")                
            return
        reply_ore = f"Mi risulta che finora tu abbia trascorso {ore} ore nel laboratorio di E-Agle TRT questo mese"
        await update.message.reply_text(reply_ore)
    else:
        status_code = response.status_code
        await update.message.reply_text(f"Errore, contatta lo staff IT.\n Codice errore: in ore function, response status code is {status_code}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.message.reply_text("Welcome to pyThonasBot!")

if __name__ == "__main__":
    def main():
        create_table()
        create_table_ore()

        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", deep_linked_level_1))
        application.add_handler(CommandHandler("odg", handle_odg))
        application.add_handler(CommandHandler("chatid", get_chat_id_topic))
        application.add_handler(CommandHandler("ore", ore))
        application.add_handler(CommandHandler("start", start))
        application.run_polling()

    main()
