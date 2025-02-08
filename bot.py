import requests
import random
import os
from user_agent import generate_user_agent
import pyfiglet
import sys
import time
from os import system, name
from ssl import CERT_NONE
from gzip import decompress
from random import choice, choices
from concurrent.futures import ThreadPoolExecutor
from json import dumps

try:
    from websocket import create_connection
except:
    system('pip install websocket-client')
    from websocket import create_connection

failed = 0
success = 0
retry = 0
accounts = []

# Telegram Bot API details
TELEGRAM_BOT_TOKEN = '6739169902:AAEjKSq3UQw0JXFY2tJTPdQsmE8Pyb77tNA'
TELEGRAM_CHAT_ID = '5207032121'

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    response = requests.post(url, data=payload)
    return response.json()

def work():
    global failed, success, retry
    username = choice('qwertyuiooasdfghjklzxcvpbnm') + ''.join(choices(list('qwertyuioasdfghjklzxcvbnpm1234567890'), k=16))
    try:
        con = create_connection("wss://195.13.182.213/Auth",
                                header={"app": "com.safeum.android", "host": None, "remoteIp": "195.13.182.213",
                                        "remotePort": str(8080), "sessionId": "b6cbb22d-06ca-41ff-8fda-c0ddeb148195",
                                        "time": "2024-04-11 11:00:00", "url": "wss://51.79.208.190/Auth"},

sslopt={"cert_reqs": CERT_NONE})
        con.send(dumps(
            {"action":"Register","subaction":"Desktop","locale":"ar_EG","gmt":"+03","password":{"m1x":"8d589ae17267d3e33301c16497ed731d92ebdd1784830abaafa12cff66703017","m1y":"6fa74a69ad0d56c74978df6916ffc1a89cd973c296aa9465e7d587776ad44b43","m2":"30cfa6e82da7889cdfeec3a95730e2305d90716e7ff2345d931167a8e777e589","iv":"47f411b7ee73e26564a4c12e6c29283d","message":"7e17a0db4bb5b145ec772ba26e3f5ff581da505d38911c317eed67a3101136cc30cab7c7a2c177c59aec21682f1a3f9b840870417f0d1d5c1327f1f4aca940a6d5f299e4b57da1556eefb12b0a7ff9cb"},"magicword":{"m1x":"db9fedd1d974b59fae2d8e677dba01a46248e6149668d79d06d83cb884c470a5","m1y":"097e0b4ef87ba0854c4712d494e722b07b84b9c7db0ba8bc2964ae37ca1a7850","m2":"d3b0b86a805b1413224619392f20b38b92ff6f1d974c4b164e97fb8c5286c17f","iv":"b3297c537192980eaae661e78c76c6a1","message":"be2961cd8ba6a57dc7014e39dce26bd8"},"magicwordhint":"0000","login":str(username),"devicename":"Android Device","softwareversion":"1.1.0.2300","nickname":"sbxkdnbwkdhfkdn","os":"AND","deviceuid":"4b81ce4e8c8208f4","devicepushuid":"*dea1cKAUQqSGUUh445-13X:APA91bG4_Bog5JK6OOGCtvpjmvYc_rznLzmKIYuUjkKJKlYbjsU4BCwL-ucmmzXyLXj-VB3sZ7w5DRBrt0AuAi7YVGKMnCLAf-u0Iy3z7_w3zW6uj5UFgUQ","osversion":"and_14.0.0","id":"1428254296"}))
        gzip = decompress(con.recv()).decode('utf-8')
        if '"status":"Success"' in gzip:
            success += 1
            accounts.append(username + ':jjjj')
            # Send the username to Telegram
            send_to_telegram(f"New account created: {username}")
        else:
            failed += 1
    except:
        retry += 1

def main():
    start = ThreadPoolExecutor(max_workers=1000)
    for _ in range(10):  # Run 10 iterations instead of an infinite loop
        start.submit(work)
        print(f'\nSuccess : {success}\nFailed : {failed}\nReTry : {retry}')
        if success >= 2990:
            print("Created Acc successfully")
            break
        if success > 0:
            print("CREATED ACCOUNTS>>\n", "\n".join(accounts))
        time.sleep(10)  # Add a delay to avoid overloading

if __name__ == "__main__":
    main()
