FROM python:3.9-alpine

WORKDIR /

# Needed for MySQL client for Ubuntu
#RUN apt-get update && apt-get install -y gcc default-libmysqlclient-dev

# Needed for MySQL client for Alpine
RUN apk add gcc musl-dev mariadb-connector-c-dev

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["flask", "run"]
