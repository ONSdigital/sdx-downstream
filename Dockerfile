FROM onsdigital/flask-crypto-queue

RUN mkdir -p /app/logs

COPY app /app
COPY requirements.txt /requirements.txt
COPY startup.sh /startup.sh
COPY Makefile /Makefile

RUN make build

ENTRYPOINT ./startup.sh
