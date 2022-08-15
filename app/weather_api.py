import os
import base64
import json

from app.root_path import ROOT

ACCESS_TOKEN_URL = 'https://api.srgssr.ch/oauth/v1/accesstoken?grant_type=client_credentials'
FORECAST_URL = 'https://api.srgssr.ch/srf-meteo/forecast/47.3868,8.4846'

SRGSSR_CLIENT_ID = os.environ.get('SRGSSR_CLIENT_ID', None)
SRGSSR_CLIENT_SECRET = os.environ.get('SRGSSR_CLIENT_SECRET', None)

env_mock = os.environ.get('MOCK_FILE_NAME', None)
MOCK_FILE_NAME = os.path.join(ROOT, env_mock) if env_mock else None


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
