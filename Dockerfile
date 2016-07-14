FROM onsdigital/flask-crypto

ADD app /app
ADD requirements.txt /requirements.txt

RUN mkdir -p /app/logs

# set working directory to /app/
WORKDIR /app/

RUN pip3 install --no-cache-dir -U -I -r /requirements.txt

ENTRYPOINT python3 consumer.py
