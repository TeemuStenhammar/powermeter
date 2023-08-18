FROM python:latest

RUN pip install paho-mqtt
RUN pip install requests

WORKDIR /usr/app/src
COPY poll_metrics.py ./

CMD [ "python", "-u", "./poll_metrics.py" ]
