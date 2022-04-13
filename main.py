import base64
import os
import json
import httpx as httpx
import uvicorn
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from icalendar import Calendar

app = FastAPI()
access_token_url = "https://api.srgssr.ch/oauth/v1/accesstoken?grant_type=client_credentials"
forecast_url = "https://api.srgssr.ch/srf-meteo/forecast/47.3868,8.4846"

load_dotenv()
client_id = os.environ.get('client_id')
client_secret = os.environ.get('client_secret')
environment = os.environ.get('environment')


@app.get("/")
async def root():
    with httpx.Client() as client:
        forecast = parse_forecast(await fetch_forecast(client))
        garbage_collections = read_next_two_garbage_collections()
        birthdays = read_next_three_birthdays()

        response = {
            'date': datetime.now().astimezone().strftime("%a, %d.%m.%Y"),
            'forecast': forecast,
            'garbage_collections': garbage_collections,
            'birthdays': birthdays,
        }

        return json.dumps(response)
        # -> ['day'] gives an array
        # Day, Max Temp, Min Temp, Icon Id, Regen
        #      TX_C, TN_C, SYMBOL_CODE, RRR_MM


async def fetch_forecast(client):
    if environment == 'production':
        userpass = client_id + ':' + client_secret
        encoded_credentials = base64.b64encode(userpass.encode()).decode()
        headers = {'Authorization': 'Basic ' + encoded_credentials}
        token_response = client.get(access_token_url, headers=headers).json()
        access_token = token_response['access_token']

        headers = {'Authorization': 'Bearer ' + access_token}
        return client.get(forecast_url, headers=headers).json()['forecast']
    else:
        example_response = open('example_forecast_response.json')
        return json.load(example_response)['forecast']


def parse_forecast(forecast_response):
    return []


def read_next_two_garbage_collections():
    erz_calendar = open('entsorgungskalender_2022.ics', 'rb')
    cal = Calendar.from_ical(erz_calendar.read())
    collections = []
    for component in cal.walk():
        if component.name == "VEVENT":
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
    return collections[:2]


def read_next_three_birthdays():
    return []


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
