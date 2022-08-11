FROM python:3.9-slim-buster

WORKDIR /

# Needed for MySQL client
RUN apt-get update && apt-get install -y gcc default-libmysqlclient-dev

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["flask", "run"]
