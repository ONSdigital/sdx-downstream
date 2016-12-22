FROM onsdigital/flask-crypto

ADD app /app
ADD startup.sh /startup.sh

RUN mkdir -p /app/logs

ENTRYPOINT ./startup.sh
