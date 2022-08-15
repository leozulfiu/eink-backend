import os
from datetime import datetime

import httpx as httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from icalendar import Calendar

from app.db import read_birthdays, enter_birthdate, update_birthdate, create_database_if_not_exists
from app.root_path import ROOT
from app.weather_api import fetch_forecast

app = FastAPI()

CALENDAR_FILE_NAME = os.path.join(ROOT, os.environ.get('CALENDAR_FILE_NAME'))


@app.get('/dashboard')
async def dashboard():
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
    upcoming = sorted(birthdays, key=lambda entry: (datetime.strptime(
        year_in_future + str(entry['birthdate'].date())[4:], '%Y-%m-%d') - now).days % 364)
    for entry in upcoming:
        # Replace 'birthdate' Key by 'date' Key
        date = entry.pop('birthdate')
        entry['date'] = str(date.day) + '.' + str(date.month) + '.'
    return upcoming[:3]


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


@app.on_event("startup")
async def startup_event():
    create_database_if_not_exists()


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=9000)
