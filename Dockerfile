FROM onsdigital/flask-crypto

ADD app.py /app/app.py
ADD example_consumer.py /app/example_consumer.py
ADD settings.py /app/settings.py
ADD requirements.txt /app/requirements.txt

RUN mkdir -p /app/logs

# set working directory to /app/
WORKDIR /app/

RUN pip3 install --no-cache-dir -U -I -r /app/requirements.txt

ENTRYPOINT python3 app.py
