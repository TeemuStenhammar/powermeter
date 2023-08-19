FROM python:3.6.12-alpine3.12

RUN pip install paho-mqtt
RUN pip install requests
RUN pip install python-dotenv

COPY spot_price.py ./
COPY crontab ./

RUN crontab crontab

CMD env > /.env && crond -f
