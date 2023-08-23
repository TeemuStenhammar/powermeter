import os
import sys
import time
import requests
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

TOPIC_PREFIX = os.getenv('TOPIC_PREFIX')
NAME = os.getenv('CLIENT')
URL = 'https://api.porssisahko.net/v1/price.json'

session = requests.session()

# Get the current spot price
now = datetime.now()
now_date = now.strftime('%Y-%m-%d')
now_hour = now.strftime('%H')
now_response = session.get(f'{URL}?date={now_date}&hour={now_hour}')
if now_response.status_code >= 300:
  print(f'Getting spot price failed with {now_response.status_code}')
  sys.exit(1)
now_price = now_response.json()['price']
print(f'Price {now_date} at {now_hour} is {now_price}')

# Get the price in 10h future
future = now + timedelta(hours=10)
future_date = future.strftime('%Y-%m-%d')
future_hour = future.strftime('%H')
future_response = session.get(f'{URL}?date={future_date}&hour={future_hour}')
if now_response.status_code >= 300:
  print(f'Getting spot future price failed with {future_response.status_code}')
  sys.exit(1)
future_price = future_response.json()['price']
print(f'Price {future_date} at {future_hour} is {future_price}')

# Connect to MQTT broker
connected = False
def on_connect(client, userdata, flags, rc):
  if rc == 0:
    print('Connected to broker')
    global connected
    connected = True
  else:
    print('Connection failed')
    client.loop_stop()
    sys.exit(1)

client = mqtt.Client(f'Spot-price-{NAME}-Pub')
client.on_connect = on_connect
client.connect('mosquitto')
client.loop_start()

while connected != True:
  time.sleep(0.1)

# Publish price to MQTT
client.publish(f'{TOPIC_PREFIX}/price', now_price)
client.publish(f'{TOPIC_PREFIX}/future', f'{{"value": {future_price}, "timestamp": {int(future.timestamp() * 1000)}}}')
time.sleep(1)
