import psycopg2
import os


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
    return rows[-1][0]


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
