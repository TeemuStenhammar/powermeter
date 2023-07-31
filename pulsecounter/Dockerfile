FROM python:latest

RUN pip install RPi.GPIO
RUN pip install paho-mqtt

WORKDIR /usr/app/src
COPY pulsecounter.py ./

CMD [ "python", "./pulsecounter.py" ]
