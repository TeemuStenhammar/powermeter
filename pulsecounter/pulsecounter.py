import os
import sys
import time
import RPi.GPIO as GPIO
import traceback
import paho.mqtt.client as mqtt

NAME = os.environ['CLIENT_NAME']
TOPIC = os.environ['TOPIC']
GPIO_PIN = int(os.environ['GPIO_PIN'])

print(f'Client name: {NAME}')
print(f'Topic: {TOPIC}')
print(f'GPIO PIN: {GPIO_PIN}')

connected = False

def on_connect(client, userdata, flags, rc):
  if rc == 0:
    print('Connected to broker')

    global connected
    connected = True
  else:
    print('Connection failed')
    client.loop_stop()

client = mqtt.Client(f'PulseCounter-{NAME}-Pub')
client.on_connect = on_connect
client.connect('mosquitto')
client.loop_start()

while connected != True:
  time.sleep(0.1)


GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

while True:
  try:
    GPIO.wait_for_edge(GPIO_PIN, GPIO.RISING)
    client.publish(TOPIC, 1)
  except Exception:
    print(traceback.format_exc())
    break

GPIO.cleanup()
