import base64
import os
import json
import sqlite3
import httpx as httpx
import uvicorn
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from icalendar import Calendar
from cryptography.fernet import Fernet
from os import path


app = FastAPI()

ACCESS_TOKEN_URL = 'https://api.srgssr.ch/oauth/v1/accesstoken?grant_type=client_credentials'
FORECAST_URL = 'https://api.srgssr.ch/srf-meteo/forecast/47.3868,8.4846'
DATABASE_PATH = 'birthdays.db'

load_dotenv()
client_id = os.environ.get('client_id')
client_secret = os.environ.get('client_secret')
db_secret = os.environ.get('db_secret')
environment = os.environ.get('environment')


@app.get('/')
async def root():
    with httpx.Client() as client:
        forecast = parse_forecast(await fetch_forecast(client))
        garbage_collections = read_garbage_collections()
        birthdays = read_birthdays()

        response = {
            'date': datetime.now().astimezone().strftime('%a, %d.%m.%Y'),
            'forecast': forecast,
            'garbage_collections': garbage_collections,
            'birthdays': birthdays,
        }

        return json.dumps(response)


async def fetch_forecast(client):
    if environment == 'production':
        userpass = client_id + ':' + client_secret
        encoded_credentials = base64.b64encode(userpass.encode()).decode()
        headers = {'Authorization': 'Basic ' + encoded_credentials}
        token_response = client.get(ACCESS_TOKEN_URL, headers=headers).json()
        access_token = token_response['access_token']

        headers = {'Authorization': 'Bearer ' + access_token}
        return client.get(FORECAST_URL, headers=headers).json()['forecast']
    else:
        example_response = open('example_forecast_response.json')
        return json.load(example_response)['forecast']


def parse_forecast(forecast_response):
    forecast = []
    for entry in forecast_response['day'][:6]:
        forecast.append({
            'day': datetime.fromisoformat(entry['local_date_time']).strftime('%a'),
            'max_temp': str(entry['TX_C']),
            'min_temp': str(entry['TN_C']),
            'icon_id': str(entry['SYMBOL_CODE']),
            'rain': str(entry['RRR_MM']) + ' mm'
        })
    return forecast


def read_garbage_collections(limit=2):
    erz_calendar = open('entsorgungskalender_2022.ics', 'rb')
    cal = Calendar.from_ical(erz_calendar.read())
    collections = []
    for component in cal.walk():
        if component.name == 'VEVENT':
            collections.append({
                'type': component.get('summary').split(': ')[1],
                # + 1 because we want to round up the day which already has begun
                'difference_in_days': (component.get('dtstart').dt.astimezone() - datetime.now().astimezone()).days + 1
            })
    erz_calendar.close()

    collections = sorted(collections, key=lambda d: d['difference_in_days'])
    for collection in collections:
        # Replace 'difference_in_days' Key by 'when' Key
        days = collection.pop('difference_in_days')
        collection['when'] = ('in ' + str(days) + ' Tagen') if days > 1 else ('in ' + str(days) + ' Tag')
    return collections[:limit]


def read_birthdays(limit=3):
    conn = sqlite3.connect(DATABASE_PATH)
    crsr = conn.cursor()
    crsr.execute('SELECT * FROM BIRTHDAY')
    rows = crsr.fetchall()
    conn.commit()
    conn.close()

    birthdays = []
    for row in rows:
        birthdays.append({
            'name': decrypt(row['name']),
            'birthdate': decrypt(row['birthdate'])
        })
    return birthdays[:limit]


def decrypt(encrypted_value):
    fer = Fernet(db_secret)
    decrypt_value = fer.decrypt(encrypted_value)
    return decrypt_value.decode()


def encrypt(raw_value):
    encoded_value = raw_value.encode()
    fer = Fernet(db_secret)
    return fer.encrypt(encoded_value)


def create_database():
    conn = sqlite3.connect(DATABASE_PATH)
    crsr = conn.cursor()
    sql_command = """CREATE TABLE BIRTHDAY(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        birthdate TEXT NOT NULL
    );"""
    crsr.execute(sql_command)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    if not path.exists(DATABASE_PATH):
        create_database()
    uvicorn.run(app, host='0.0.0.0', port=8000)
