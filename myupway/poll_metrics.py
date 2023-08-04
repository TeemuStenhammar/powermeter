import os
import re
import sys
import json
import time
import requests
import paho.mqtt.client as mqtt

TYPE_BOOLEAN_ON_OFF = 'boolean_on_off'
TYPE_BOOLEAN_YES_NO = 'boolean_yes_no'
TYPE_CURRENT = 'current'
TYPE_DIMENSIONLESS = 'dimensionless'
TYPE_ENERGY = 'energy'
TYPE_FLOW = 'flow'
TYPE_FREQUENCY = 'frequency'
TYPE_PERCENTAGE = 'percentage'
TYPE_POWER = 'power'
TYPE_TEMPERATURE = 'temperature'
TYPE_TIME = 'time_period'

UNIT_AMPERES = 'A'
UNIT_CELSIUS = 'C'
UNIT_DEGREE_MINUTES = 'DM'
UNIT_HERTZ = 'Hz'
UNIT_HOURS = 'h'
UNIT_KILOWATTS = 'kW'
UNIT_KILOWATT_HOURS = 'kWh'
UNIT_LITERS_PER_MINUTE = 'l/m'
UNIT_NONE = ''
UNIT_PERCENT = '%'


myupway_variables = {
  # Status
  40067: {'name': 'avg_outdoor_temp_BT1',   'type': TYPE_TEMPERATURE,   'unit': UNIT_CELSIUS},
  40014: {'name': 'hot_water_charging_BT6', 'type': TYPE_TEMPERATURE,   'unit': UNIT_CELSIUS},
  40013: {'name': 'hot_water_top_BT7',      'type': TYPE_TEMPERATURE,   'unit': UNIT_CELSIUS},
  40004: {'name': 'outdoor_temp_BT1',       'type': TYPE_TEMPERATURE,   'unit': UNIT_CELSIUS},
  40083: {'name': 'current_BE1',            'type': TYPE_CURRENT,       'unit': UNIT_AMPERES},
  40081: {'name': 'current_BE2',            'type': TYPE_CURRENT,       'unit': UNIT_AMPERES},
  40079: {'name': 'current_BE3',            'type': TYPE_CURRENT,       'unit': UNIT_AMPERES},
  43005: {'name': 'degree_minutes',         'type': TYPE_DIMENSIONLESS, 'unit': UNIT_DEGREE_MINUTES},

  # Compressor module
  10012: {'name': 'blocked', 'type': TYPE_BOOLEAN_YES_NO, 'unit': UNIT_NONE},
  43416: {'name': 'compressor_starts_EB100_EP14', 'type': TYPE_DIMENSIONLESS, 'unit': UNIT_NONE},
  43439: {'name': 'brine_pump_speed_EP14_GP2', 'type': TYPE_PERCENTAGE, 'unit': UNIT_PERCENT},
  43437: {'name': 'pump_speed_heating_medium_EP14', 'type': TYPE_PERCENTAGE, 'unit': UNIT_PERCENT},
  40015: {'name': 'brine_in_EB100_EP14_BT10', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},
  40016: {'name': 'brine_out_EB100_EP14_BT11', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},
  40017: {'name': 'condenser_out_EB100_EP14_BT12', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},
  40008: {'name': 'heat_medium_flow_BT2', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},
  40018: {'name': 'hot_gas_EB100_EP14_BT14', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},
  40019: {'name': 'liqu_line_EB100_EP14_BT15', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},
  40012: {'name': 'return_temp_EB100_EP14_BT3', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},
  40022: {'name': 'suction_gas_EB100_EP14_BT17', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},
  43420: {'name': 'compressor_operating_time_EB100_EP14', 'type': TYPE_TIME, 'unit': UNIT_HOURS},
  43424: {'name': 'compressor_operating_time_hot_water_EB100_EP14', 'type': TYPE_TIME, 'unit': UNIT_HOURS},
  43122: {'name': 'allowed_compr_freq_min', 'type': TYPE_FREQUENCY, 'unit': UNIT_HERTZ},
  43136: {'name': 'current_compr_frequency', 'type': TYPE_FREQUENCY, 'unit': UNIT_HERTZ},

  # Climate system 1
  43161: {'name': 'external_adjustment_S1', 'type': TYPE_BOOLEAN_YES_NO, 'unit': UNIT_NONE},
  47276: {'name': 'floor_drying_function', 'type': TYPE_BOOLEAN_ON_OFF , 'unit': UNIT_NONE},
  43009: {'name': 'calculated_flow_temp_S1', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},
  40071: {'name': 'external_flow_temp_BT25', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},
  40008: {'name': 'heat_medium_flow_BT2', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},
  40012: {'name': 'return_temp_EB100_EP14_BT3', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},
  40033: {'name': 'room_temperature_BT50', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},

  # Climate system 2
  43160: {'name': 'external_adjustment_S2', 'type': TYPE_BOOLEAN_YES_NO, 'unit': UNIT_NONE},
  43008: {'name': 'calculated_flow_temp_S2', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},
  40007: {'name': 'heat_medium_flow_EP21_BT2', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},
  40129: {'name': 'heat_medium_return_EP21_BT3', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},
  40032: {'name': 'room_temperature_EP21_BT50', 'type': TYPE_TEMPERATURE, 'unit': UNIT_CELSIUS},

  # Addition
  10033: {'name': 'blocked', 'type': TYPE_BOOLEAN_YES_NO, 'unit': UNIT_NONE},
  47214: {'name': 'fuse_size', 'type': TYPE_CURRENT, 'unit': UNIT_AMPERES},
  43081: {'name': 'time_factor', 'type': TYPE_TIME, 'unit': UNIT_HOURS},
  43084: {'name': 'electrical_addition_power', 'type': TYPE_POWER, 'unit': UNIT_KILOWATTS},
  47212: {'name': 'set_max_electrical_add', 'type': TYPE_POWER, 'unit': UNIT_KILOWATTS},

  # Heat meter
  44308: {'name': 'heating_compr_only_EP14', 'type': TYPE_ENERGY, 'unit': UNIT_KILOWATT_HOURS},
  44300: {'name': 'heating_int_add_incl_EP14', 'type': TYPE_ENERGY, 'unit': UNIT_KILOWATT_HOURS},
  44306: {'name': 'hotwater_compr_only_EP14', 'type': TYPE_ENERGY, 'unit': UNIT_KILOWATT_HOURS},
  44298: {'name': 'hw_incl_int_add_EP14', 'type': TYPE_ENERGY, 'unit': UNIT_KILOWATT_HOURS},
  44304: {'name': 'pool_compr_only_EP14', 'type': TYPE_ENERGY, 'unit': UNIT_KILOWATT_HOURS},
  40771: {'name': 'pool2_compr_only_EP14', 'type': TYPE_ENERGY, 'unit': UNIT_KILOWATT_HOURS},
  40072: {'name': 'flow_BF1', 'type': TYPE_FLOW, 'unit': UNIT_LITERS_PER_MINUTE},
}

variables_to_fetch = [40067, 40014, 40013, 40004, 43084, 47212]

SYSTEM_ID = os.environ.get('SYSTEM_ID')
EMAIL = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')
NAME = os.environ.get('CLIENT')
TOPIC_PREFIX = os.environ.get('TOPIC_PREFIX')
INTERVAL = int(os.environ.get('INTERVAL'))

print(f'Starting metric poll client {NAME} to post metrics to {TOPIC_PREFIX}/#')

connected = False


def on_connect(client, userdata, flags, rc):
  if rc == 0:
    print('Connected to broker')

    global connected
    connected = True
  else:
    print('Connection failed')
    client.loop_stop()


client = mqtt.Client(f'MyUpway-Metric-Poller-{NAME}-Pub')
client.on_connect = on_connect
client.connect('mosquitto')
client.loop_start()

while connected != True:
  time.sleep(0.1)


def parse_raw_value(raw_value, type, unit):
    if raw_value == "--":
        return None

    if unit == UNIT_CELSIUS:
        return float(re.sub(r'^([-\d.]+)([°º])C$', r'\1', raw_value, flags=re.UNICODE))
    elif unit == UNIT_AMPERES or unit == UNIT_HOURS:
        return float(raw_value[:-1])
    elif unit == UNIT_DEGREE_MINUTES or unit == UNIT_HERTZ:
        return int(raw_value[:-2])
    elif unit == UNIT_KILOWATTS:
        return float(raw_value[:-2])
    elif type == TYPE_BOOLEAN_YES_NO:
        return raw_value == "yes"
    elif type == TYPE_BOOLEAN_ON_OFF:
        return raw_value == "on"
    elif unit == UNIT_KILOWATT_HOURS or unit == UNIT_LITERS_PER_MINUTE:
        return float(raw_value[:-3])
    elif unit == UNIT_PERCENT:
        return int(raw_value[:-1])

    return raw_value


while True:
  session = requests.session()
  auth_response = session.post('https://myupway.com/LogIn', {
    'returnUrl': f'/System/{SYSTEM_ID}/Status/Overview',
    'Email': EMAIL,
    'Password': PASSWORD
  })

  # The login endpoint doesn't use HTTP 4XX status codes, so we check that it
  # redirects to the "returnUrl" we requested
  redirect = auth_response.history.pop()
  if redirect.headers.get('Location') != f'/System/{SYSTEM_ID}/Status/Overview':
    client.publish(f'{TOPIC_PREFIX}/failed_to_fetch_metrics', 1)
  else:
    # Fetch values
    values_response = session.post("https://myupway.com/PrivateAPI/Values", {
      "hpid": SYSTEM_ID,
      "variables": variables_to_fetch
    })
    values = values_response.json()

    # Post each value to MQTT
    for v in values.get('Values', []):
      variable_id = v.get('VariableId', 0)
      if variable_id not in myupway_variables:
        print(f'Variable {variable_id} not in MyUpway variables')
        continue

      myupway_variable = myupway_variables[variable_id]

      real_value = parse_raw_value(v['CurrentValue'], myupway_variable['type'], myupway_variable['unit'])
      if real_value:
        client.publish(f'{TOPIC_PREFIX}/{myupway_variable["name"]}', real_value)
      #print(f'{myupway_variable["name"]} : {real_value}')

  time.sleep(INTERVAL)
