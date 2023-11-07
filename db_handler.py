import sqlite3
from sqlite3 import Error, IntegrityError

def db_connection():
    conn = sqlite3.connect('orianna_bot.db')
    c = conn.cursor()
    return conn, c

def create_user(discord_id, author, summoner_name, summoner_id, account_id, puu_id):
    conn, c = db_connection()
    params = (discord_id, author, summoner_name, summoner_id, account_id, puu_id)
    try:
        with conn:
            c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", params)
            return True
    except IntegrityError:
        return False


def remove_user(discord_id):
    conn, c = db_connection()
    try:
        with conn:
            c.execute("SELECT summoner_name FROM users WHERE discord_id = ?", (discord_id,))
            summoner_name = c.fetchone()[0]
            c.execute("DELETE FROM users WHERE discord_id = ?", (discord_id,))
            print(f"{discord_id} removed from user database")
            return True, summoner_name
    except TypeError:
        return False, None


def get_summoner_name(discord_id):

    # If user exists in database, return summoner name
    # If user does not exist, return False

    conn, c = db_connection()
    try:
        with conn:
            c.execute("SELECT summoner_name FROM users WHERE discord_id = ?", (discord_id,))
        return c.fetchone()[0]
    except TypeError:
        return False

def get_summoner_id(discord_id):

    # If user exists in database, return summoner id
    # If user does not exist, return False

    conn, c = db_connection()
    try:
        with conn:
            c.execute("SELECT summoner_id FROM users WHERE discord_id = ?", (discord_id,))
        return c.fetchone()[0]
    except TypeError:
        return False

def get_account_id(discord_id):

    # If user exists in database, return account id
    # If user does not exist, return False

    conn, c = db_connection()
    try:
        with conn:
            c.execute("SELECT account_id FROM users WHERE discord_id = ?", (discord_id,))
        return c.fetchone()[0]
    except TypeError:
        return False

def get_puu_id(discord_id):

    # If user exists in database, return puu id
    # If user does not exist, return False

    conn, c = db_connection()
    try:
        with conn:
            c.execute("SELECT puu_id FROM users WHERE discord_id = ?", (discord_id,))
        return c.fetchone()[0]
    except TypeError:
        return False