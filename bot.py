import os
import psycopg2
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from collections import defaultdict

DATABASE_URL = os.getenv("DATABASE_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")


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
        update.message.reply_text(f"Id della chat: {chat_id}")
    else:
        update.message.reply_text(f"Id della chat: {chat_id}, id del topic: {topic_id}")


if __name__ == "__main__":
    def main():
        create_table()

        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("odg", handle_odg))
        application.add_handler(CommandHandler("chatid", get_chat_id_topic))
        application.run_polling()

    main()
