# Powermeter stack

This project was accomplished by using [koenvervloesem](https://github.com/koenvervloesem/ruuvitag-demo) 
nice stack from their RuuviTag Demo project, and [Jalle19 pyupway](https://github.com/Jalle19/pyupway) library. 
This Readme is mostly copied from the former with additions from what I did there.

## System requirements
The project was designed on Rasperry Pi 4 and Raspbian OS. You need a Linux system with Bluetooth Low Energy 
(BLE) adapter, so at least Bluetooth 4.0.

All instructions assume the first configuration. It should run on other Linux systems with minor adjustments, though.

### Checking your Bluetooth adapter
Your system should have a Bluetooth Low Energy adapter, as is available in all recent Raspberry Pi models. 
You can verify this with:

```shell
hciconfig -a
```

This should show a device **hci0** as **UP RUNNING** and the **LMP Version** should be at least 4.0.

### Installing Docker and Docker Compose
Docker can be installed with:

```shel
curl -sSL https://get.docker.com | sh
```

And give your user access to Docker by adding it to the `docker` group:

```shell
sudo usermod <username> -aG docker
```

Log out and then log in again, so the group permissions are applied to your session.

Then install Python's pip package manager:

```shell
sudo apt install python3-pip
```

And install Docker Compose:

```shell
sudo pip3 install docker-compose
```

## Installation
Clone the repository (you may have to `sudo apt install git` first) and enter the directory:

```shell
git clone https://https://github.com/TeemuStenhammar/powermeter.git
cd powermeter
```

Change the owner of the `grafana` directory (not sure if this is needed):

```shell
sudo chown -R 1000:1000 grafana
```

## Configuration

The project configures two pulsecounters that read S0 pulse output from electricity meter. In my case these were connected to earth-to-water and air-to-air heat pumps. These S0 outputs need to be captrured properly. [Here](https://lutpub.lut.fi/bitstream/handle/10024/158461/Toni_Naukkarinen_Kandi_lutpub.pdf?sequence=1) is a bachelors thesis that explains options to make this happen (in Finnish, sorry for that). 

The next configuration bit is to create an account to [myUpway](https://myupway.com/), if you happen to have Jämä heating device. The configuration of this most likely requires several steps:
* Navigate to Service Info https://myupway.com/System/<YourSystemId>/Status/ServiceInfo
* Capture system id from the path
* Read the page source to find codes that match values you want to pull from it
* Update /myupway/poll_metrics.py to match your selection
* Set you username and password to .env file

Add the MAC addresses of your RuuviTag sensors to the `bt-mqtt-gateway/config.yaml` file. You can find these by scanning for Bluetooth Low Energy devices in your neighborhood:

```shell
sudo hcitool lescan
```

## Getting the stack up

```shell
docker-compose up -d
```

This starts eight Docker containers:

  * [Mosquitto](https://mosquitto.org/): Receives the MQTT messages from bt-mqtt-gateway and relays them to anyone who is interested.
  * [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/): Collects MQTT messages from Mosquitto and sends the values to InfluxDB.
  * [InfluxDB](https://www.influxdata.com/): Stores all the values of the RuuviTag measurements in a time-series database.
  * [Grafana](https://grafana.com/): Shows the values of the InfluxDB database in a dashboard.
  * 2x Pulsecounter: Reads S0 pulse output from electricity meters connected to Raspberry GPIO
  * myUpway Poller: Polls myUpway for information about Jämä heat machine
  * Spot Price: Uses [this API](https://www.porssisahko.net/api) to fetch the current price and price 10h into future for electricity and publishes those values to MQTT
  * [bt-mqtt-gateway](https://github.com/zewelor/bt-mqtt-gateway): Reads RuuviTag sensor measurements using Bluetooth Low Energy and forwards them to a MQTT broker.* [bt-mqtt-gateway](https://github.com/zewelor/bt-mqtt-gateway): Reads RuuviTag sensor measurements using Bluetooth Low Energy and forwards them to a MQTT broker.

You have access to:

  * The Grafana dashboard on http://localhost:3000

## Tearing the stack down

```shell
docker-compose down
```

## License
This program is provided as open source software with the MIT license.# Powermeter stack

This project was accomplished by using [koenvervloesem](https://github.com/koenvervloesem/ruuvitag-demo) nice stack from their RuuviTag Demo project, and [Jalle19 pyupway](https://github.com/Jalle19/pyupway) library. This Readme is mostly copied from the former with additions from what I did there.

## System requirements
The project was designed on Rasperry Pi 4 and Raspbian OS.

All instructions assume the first configuration. It should run on other Linux systems with minor adjustments, though.

### Installing Docker and Docker Compose
Docker can be installed with:

```shel
curl -sSL https://get.docker.com | sh
```

And give your user access to Docker by adding it to the `docker` group:

```shell
sudo usermod <username> -aG docker
```

Log out and then log in again, so the group permissions are applied to your session.

Then install Python's pip package manager:

```shell
sudo apt install python3-pip
```

And install Docker Compose:

```shell
sudo pip3 install docker-compose
```

## Installation
Clone the repository (you may have to `sudo apt install git` first) and enter the directory:

```shell
git clone https://https://github.com/TeemuStenhammar/powermeter.git
cd powermeter
```

Change the owner of the `grafana` directory (not sure if this is needed):

```shell
sudo chown -R 1000:1000 grafana
```

## Configuration

The project configures two pulsecounters that read S0 pulse output from electricity meter. In my case these were connected to earth-to-water and air-to-air heat pumps. These S0 outputs need to be captrured properly. [Here](https://lutpub.lut.fi/bitstream/handle/10024/158461/Toni_Naukkarinen_Kandi_lutpub.pdf?sequence=1) is a bachelors thesis that explains options to make this happen (in Finnish, sorry for that). 

The next configuration bit is to create an account to [myUpway](https://myupway.com/), if you happen to have Jämä heating device. The configuration of this most likely requires several steps:
* Navigate to Service Info https://myupway.com/System/<YourSystemId>/Status/ServiceInfo
* Capture system id from the path
* Read the page source to find codes that match values you want to pull from it
* Update /myupway/poll_metrics.py to match your selection
* Set you username and password to .env file


## Getting the stack up

```shell
docker-compose up -d
```

This starts eight Docker containers:

  * [Mosquitto](https://mosquitto.org/): Receives the MQTT messages from bt-mqtt-gateway and relays them to anyone who is interested.
  * [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/): Collects MQTT messages from Mosquitto and sends the values to InfluxDB.
  * [InfluxDB](https://www.influxdata.com/): Stores all the values of the RuuviTag measurements in a time-series database.
  * [Grafana](https://grafana.com/): Shows the values of the InfluxDB database in a dashboard.
  * 2x Pulsecounter: Reads S0 pulse output from electricity meters connected to Raspberry GPIO
  * myUpway Poller: Polls myUpway for information about Jämä heat machine
  * Spot Price: Uses [this API](https://www.porssisahko.net/api) to fetch the current price and price 10h into future for electricity and publishes those values to MQTT

You have access to:

  * The Grafana dashboard on http://localhost:3000

## Tiering the stack down

```shell
docker-compose down
```

## License
This program is provided as open source software with the MIT license.
