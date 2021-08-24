FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine

COPY ./app /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

WORKDIR /app

ENV FLASK_APP=main

EXPOSE 80