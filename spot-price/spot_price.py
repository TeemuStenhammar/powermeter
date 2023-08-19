import os
import sys
import time
import requests
import paho.mqtt.client as mqtt
from datetime import datetime

TOPIC = 'spot/price'
NAME = 'spot-client'
URL = 'https://api.porssisahko.net/v1/price.json'

# Get current date and hour
now = datetime.now()
date = now.strftime('%Y-%m-%d')
hour = now.strftime('%H')

# Get the current spot price
session = requests.session()
response = session.get(f'{URL}?date={date}&hour={hour}')
if response.status_code >= 300:
  print(f'Getting spot price failed with {response.status_code}')
  sys.exit(1)

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
print(f'Price {date} at {hour} is {response.json()["price"]}')
client.publish(TOPIC, response.json()['price'])
time.sleep(1)
