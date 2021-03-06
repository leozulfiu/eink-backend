import base64
import os
import json
import sqlite3
import httpx as httpx
import uvicorn
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from icalendar import Calendar
from cryptography.fernet import Fernet
from os import path

app = FastAPI()

ACCESS_TOKEN_URL = 'https://api.srgssr.ch/oauth/v1/accesstoken?grant_type=client_credentials'
FORECAST_URL = 'https://api.srgssr.ch/srf-meteo/forecast/47.3868,8.4846'

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
SRGSSR_CLIENT_ID = os.environ.get('SRGSSR_CLIENT_ID', None)
SRGSSR_CLIENT_SECRET = os.environ.get('SRGSSR_CLIENT_SECRET', None)
DATABASE_FILE_NAME = os.path.join(ROOT, os.environ.get('DATABASE_FILE_NAME'))
CALENDAR_FILE_NAME = os.path.join(ROOT, os.environ.get('CALENDAR_FILE_NAME'))
env_mock = os.environ.get('MOCK_FILE_NAME', None)
MOCK_FILE_NAME = os.path.join(ROOT, env_mock) if env_mock else None
DB_SECRET = os.environ.get('DB_SECRET')


@app.get('/')
async def root():
    with httpx.Client() as client:
        forecast = parse_forecast(await fetch_forecast(client))
        garbage_collections = read_garbage_collections()
        birthdays = read_upcoming_birthdays()

        response = {
            'date': datetime.now().astimezone().strftime('%a, %d.%m.%Y'),
            'forecast': forecast,
            'garbage_collections': garbage_collections,
            'birthdays': birthdays,
        }

        return response


async def fetch_forecast(client):
    if MOCK_FILE_NAME:
        example_response = open(MOCK_FILE_NAME)
        return json.load(example_response)['forecast']
    else:
        userpass = SRGSSR_CLIENT_ID + ':' + SRGSSR_CLIENT_SECRET
        encoded_credentials = base64.b64encode(userpass.encode()).decode()
        headers = {'Authorization': 'Basic ' + encoded_credentials}
        token_response = client.get(ACCESS_TOKEN_URL, headers=headers).json()
        access_token = token_response['access_token']

        headers = {'Authorization': 'Bearer ' + access_token}
        return client.get(FORECAST_URL, headers=headers).json()['forecast']


def parse_forecast(forecast_response):
    forecast = []
    forecast_for_days = 6
    for entry in forecast_response['day'][:forecast_for_days]:
        forecast.append({
            'day': datetime.fromisoformat(entry['local_date_time']).strftime('%a'),
            'max_temp': str(entry['TX_C']),
            'min_temp': str(entry['TN_C']),
            'icon_id': str(entry['SYMBOL_CODE']),
            'rain': str(entry['RRR_MM']) + ' mm',
            'rain_probability': str(entry['PROBPCP_PERCENT']) + '%'
        })
    return forecast


def read_garbage_collections(limit=2):
    erz_calendar = open(CALENDAR_FILE_NAME, 'rb')
    cal = Calendar.from_ical(erz_calendar.read())
    collections = []
    for component in cal.walk():
        if component.name == 'VEVENT':
            collections.append({
                # ditch the beginning of the summary
                'type': component.get('summary').split(': ')[1],
                # + 1 because we want to round up the day which already has begun
                'difference_in_days': (component.get('dtstart').dt.astimezone() - datetime.now().astimezone()).days + 1
            })
    erz_calendar.close()

    collections = sorted(collections, key=lambda d: d['difference_in_days'])
    collections = list(filter(lambda x: (x['difference_in_days'] >= 0), collections))
    for collection in collections:
        # Replace 'difference_in_days' Key by 'when' Key
        days = collection.pop('difference_in_days')
        if days == 0:
            collection['when'] = 'heute'
        elif days == 1:
            collection['when'] = ('in ' + str(days) + ' Tag')
        else:
            collection['when'] = ('in ' + str(days) + ' Tagen')
    return collections[:limit]


def read_upcoming_birthdays():
    birthdays = read_birthdays()
    now = datetime.now()
    year_in_future = str(now.year + 1)
    upcoming = sorted(birthdays, key=lambda entry: (datetime.strptime(year_in_future + str(entry['birthdate'].date())[4:], '%Y-%m-%d') - now).days % 364)
    for entry in upcoming:
        # Replace 'birthdate' Key by 'date' Key
        date = entry.pop('birthdate')
        entry['date'] = str(date.day) + '.' + str(date.month) + '.'
    return upcoming[:3]


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


@app.get('/api/new')
async def new(name, birthdate):
    try:
        parsed_birthdate = datetime.strptime(birthdate, '%d.%m.%Y').date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Could not parse birthdate. Specify in dd.mm.yyyy format.")

    if len(name) < 30:
        parsed_name = name
    else:
        raise HTTPException(status_code=400, detail="name is too long. It must be less than 30 characters long.")

    birthdays = read_birthdays()
    match = list(filter(lambda birthday: birthday['name'] == parsed_name, birthdays))
    if len(match) == 0:
        id = enter_birthdate(parsed_name, parsed_birthdate.isoformat())
    else:
        id = update_birthdate(match[0]['id'], parsed_birthdate.isoformat())

    return {
        'id': id
    }


@app.get('/api/birthdays')
async def birthdays():
    return read_birthdays()


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


def update_birthdate(id, birthdate):
    conn = sqlite3.connect(DATABASE_FILE_NAME)
    crsr = conn.cursor()
    sql_command = """UPDATE BIRTHDAY SET birthdate = ? WHERE id = ?;"""
    enc_date = encrypt(str(birthdate))
    crsr.execute(sql_command, (enc_date, id))

    conn.commit()
    conn.close()
    return id


def decrypt(encrypted_value):
    fer = Fernet(DB_SECRET)
    decrypt_value = fer.decrypt(encrypted_value)
    return decrypt_value.decode()


def encrypt(raw_value):
    encoded_value = raw_value.encode()
    fer = Fernet(DB_SECRET)
    return fer.encrypt(encoded_value)


def create_database():
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


@app.on_event("startup")
async def startup_event():
    if not path.exists(DATABASE_FILE_NAME):
        create_database()

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=9000)
