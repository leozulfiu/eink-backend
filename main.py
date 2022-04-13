import base64
import os

import httpx as httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

app = FastAPI()
access_token_url = "https://api.srgssr.ch/oauth/v1/accesstoken?grant_type=client_credentials"
forecast_url = "https://api.srgssr.ch/srf-meteo/forecast/47.3868,8.4846"

load_dotenv()
client_id = os.environ.get('client_id')
client_secret = os.environ.get('client_secret')


@app.get("/")
async def root():
    with httpx.Client() as client:
        userpass = client_id + ':' + client_secret
        encoded_credentials = base64.b64encode(userpass.encode()).decode()
        headers = {'Authorization': 'Basic ' + encoded_credentials}
        token_response = client.get(access_token_url, headers=headers).json()
        access_token = token_response['access_token']

        headers = {'Authorization': 'Bearer ' + access_token}
        forecast_response = client.get(forecast_url, headers=headers).json()['forecast']


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
