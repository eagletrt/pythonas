from database import db
from telegram import Update
from telegram.ext import ContextTypes
import requests
from telegram.constants import ParseMode
from utils import utils


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
        topics = db.get_topics_from_db(topic_id)
        if topics:
            topics_text = ""
            for topic_text, author in topics:
                topics_text += f"📋{topic_text}\n👤 {author}\n\n"
            await update.message.reply_text("Contenuto Ordine Del Giorno:\n\n" + topics_text.strip())
        else:
            await update.message.reply_text("Niente in programma, cara")
    elif context.args[0] == "reset":
        db.reset_topics_in_db(topic_id)  # Reset dei topics nel database
        await update.message.reply_text("odg reset effettuato")
    else:
        topic_text = ' '.join(context.args)
        db.add_topic_to_db(topic_id, author, topic_text)
        await update.message.reply_text(f"Aggiunto all'odg: {topic_text}")


async def ore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    in_db = await db.is_in_db(user_id)
    if in_db is not True:
        url = "https://api.eagletrt.it/api/v2/tecsLinkOre"
        text = f"Clicca su <a href='{url}'>questo link</a> per le ore"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    email = str(db.get_mail_from_id_db(user_id))
    url = f"https://api.eagletrt.it/api/v2/lab/ore?username={email}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        ore = round(float(data.get("ore")), 2)
        inlab = data.get("inlab")
        answer_text = ""
        if ore is None:
            await update.message.reply_text("Errore, contatta lo staff IT.\n Codice errore: in ore function: ore is None")
            return
        if inlab is False:
            answer_text = "Ciao! Non sei in lab 😿 \n"
        elif inlab is True:
            answer_text = "Ciao! Sei in lab 🐱\n"
        else:
            await update.message.reply_text(f"Errore, contatta lo staff IT.\n Codice errore: in ore function: inlab is {inlab}")
            print(inlab)
            return
        ore = utils.prettify_minutes(ore)
        reply_ore = answer_text + f"Mi risulta che finora tu abbia trascorso {ore} nel laboratorio di E-Agle TRT questo mese"
        await update.message.reply_text(reply_ore)
    else:
        status_code = response.status_code
        await update.message.reply_text(f"Errore, contatta lo staff IT.\n Codice errore: in ore function, response status code is {status_code}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.message.reply_text("Welcome to pyThonasBot!")
