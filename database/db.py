import psycopg2
import os


DATABASE_URL = os.getenv("DATABASE_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")


# constant for the deep linking
NOME_COGNOME = "nome.cognome"


def create_table():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS odg_topics (
            id SERIAL PRIMARY KEY,
            topic_id BIGINT,
            author TEXT,
            topic_text TEXT,
            timestamp TIMESTAMPTZ DEFAULT NOW()
        )
    """
    )
    conn.commit()
    cursor.close()
    conn.close()


def create_table_ore():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ore (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            user_mail TEXT,
            timestamp TIMESTAMPTZ DEFAULT NOW()
        )
    """
    )
    conn.commit()
    cursor.close()
    conn.close()


def create_table_users():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
                   CREATE TABLE IF NOT EXISTS users (
                       id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                       name VARCHAR(100) NOT NULL,
                       surname VARCHAR(100) NOT NULL,
                       email VARCHAR (250) NOT NULL,
                       main_team_id INT NULL,
                       FOREIGN KEY (main_team_id) REFERENCES main_teams(id)
                       )
                   """
    )
    conn.commit()
    cursor.close()
    conn.close()


def create_table_teams():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
                   CREATE TABLE IF NOT EXISTS main_teams ( 
                        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        name VARCHAR(50) UNIQUE NOT NULL 
                        )
                   """
    )
    conn.commit()
    cursor.close()
    conn.close()


def create_table_workgroups():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
                   CREATE TABLE IF NOT EXISTS worgroups(
                       id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                       name VARCHAR(100) UNIQUE NOT NULL
                       )
                   """
    )
    conn.commit()
    cursor.close()
    conn.close()


def create_table_user_workgroups():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
                   CREATE TABLE IF NOT EXISTS user_workgroups(
                        user_id BIGINT NOT NULL,
                        optional_workgroups BIGINT NOT NULL,
                        PRIMARY KEY (user_id, optional_workgroups),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (optional_workgroups) REFERENCES workgroups(id) ON DELETE CASCADE
                       )
                   """
    )
    conn.commit()
    cursor.close()
    conn.close()


def user_mail_to_user_id(user_mail) -> int:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
                   SELECT id FROM users WHERE email = %(str)s
                   """,
        (user_mail,),
    )
    rows = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return rows[0][0]


def get_user_workgroups(user_mail):
    id = user_mail_to_user_id(user_mail)
    # TODO: finish this function
    # TODO: import teams from gmazzucchi/eagletrtbot and user data into the database
    # TODO: create a function also to get all the people who belong to a teams and a fn to the ones that belong to a workgroup


def add_user_to_db(user_id, user_mail):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO ore (user_id, user_mail)
        VALUES (%s, %s)
    """,
        (user_id, user_mail),
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_mail_from_id_db(user_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT user_mail FROM ore WHERE user_id = %s
    """,
        (user_id,),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows[-1][0]


def add_topic_to_db(topic_id, author, topic_text):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO odg_topics (topic_id, author, topic_text)
        VALUES (%s, %s, %s)
    """,
        (topic_id, author, topic_text),
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_topics_from_db(topic_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT topic_text, author FROM odg_topics WHERE topic_id = %s
    """,
        (topic_id,),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def reset_topics_in_db(topic_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM odg_topics WHERE topic_id = %s
    """,
        (topic_id,),
    )
    conn.commit()
    cursor.close()
    conn.close()


async def is_in_db(user_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT user_mail FROM ore WHERE user_id = %s
    """,
        (user_id,),
    )
    mail = cursor.fetchall()
    cursor.close()
    conn.close()
    if mail:
        return True
    else:
        return False
