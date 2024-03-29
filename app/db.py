import sqlite3
import sys
from datetime import datetime
from os import path
import os

from cryptography.fernet import Fernet

from root_path import ROOT

DB_ENV = os.environ.get('DATABASE_FILE_NAME')
if not DB_ENV:
    sys.exit('env variable DATABASE_FILE_NAME was not set!')
DATABASE_FILE_NAME = os.path.join(ROOT, DB_ENV)
DB_SECRET = os.environ.get('DB_SECRET')


def read_birthdays():
    conn = sqlite3.connect(DATABASE_FILE_NAME)
    crsr = conn.cursor()
    crsr.execute('SELECT * FROM BIRTHDAY')
    rows = crsr.fetchall()
    conn.commit()
    conn.close()

    birthdays = []
    for row in rows:
        birthdays.append({
            'id': row[0],
            'name': decrypt(row[1]),
            'birthdate': datetime.fromisoformat(decrypt(row[2]))
        })
    return birthdays


def enter_birthdate(name, birthdate):
    conn = sqlite3.connect(DATABASE_FILE_NAME)
    crsr = conn.cursor()
    sql_command = """INSERT INTO BIRTHDAY(name,birthdate) VALUES (?,?);"""
    enc_name = encrypt(name)
    enc_date = encrypt(str(birthdate))

    crsr.execute(sql_command, (enc_name, enc_date))

    conn.commit()
    conn.close()
    return crsr.lastrowid


def delete_birthdate(id):
    conn = sqlite3.connect(DATABASE_FILE_NAME)
    crsr = conn.cursor()
    sql_command = """DELETE FROM BIRTHDAY WHERE id = ?;"""
    crsr.execute(sql_command, (id,))

    conn.commit()
    conn.close()


def decrypt(encrypted_value):
    fer = Fernet(DB_SECRET)
    decrypt_value = fer.decrypt(encrypted_value)
    return decrypt_value.decode()


def encrypt(raw_value):
    encoded_value = raw_value.encode()
    fer = Fernet(DB_SECRET)
    return fer.encrypt(encoded_value)


def create_database_if_not_exists():
    print('Checking if database exists in: ' + DATABASE_FILE_NAME)
    if path.exists(DATABASE_FILE_NAME):
        print('Database file exists and will be used')
        return
    print("Database file doesn't exist and will be created")

    conn = sqlite3.connect(DATABASE_FILE_NAME)
    crsr = conn.cursor()
    sql_command = """CREATE TABLE BIRTHDAY(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        birthdate TEXT NOT NULL
    );"""
    crsr.execute(sql_command)
    conn.commit()
    conn.close()
