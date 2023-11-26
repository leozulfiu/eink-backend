import os
import httpx as httpx
import random


ACCESS_TOKEN_URL = 'https://matrix.lzlf.ch/_matrix/client/r0/login'
SEND_URL = 'https://matrix.lzlf.ch/_matrix/client/r0/rooms/{}/send/m.room.message/'

BOT_USERNAME = os.environ.get('BOT_USERNAME', "birthday-bot")
BOT_PASSWORD = os.environ.get('BOT_PASSWORD', None)
ROOM_ID = os.environ.get('ROOM_ID', None)


async def send_chat_message(todays_birthdays):
    if not BOT_USERNAME or not BOT_PASSWORD or not ROOM_ID:
        return
    if len(todays_birthdays) == 0:
        return
    with httpx.Client() as client:
        token_response = client.post(ACCESS_TOKEN_URL, json={
            "type": "m.login.password",
            "user": BOT_USERNAME,
            "password": BOT_PASSWORD
        }).json()
        access_token = token_response['access_token']

        params = {
            'access_token': access_token
        }

        send_response = client.put(SEND_URL.format(ROOM_ID), params=params, json={
            "msgtype": "m.text",
            "body": "Happy birthday toooo:\n\n" + '\n'.join(['- ' + bday["name"] + ' ' + get_random_happy_emoji() for bday in todays_birthdays])
        })
        print("Successfully send message, response code: " + str(send_response.status_code))


def get_random_happy_emoji():
    emojis = ['🥳', '🎉', '🎉', '🍾', '🎂', '🎈', '🎁']
    return random.choice(emojis)
