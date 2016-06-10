import settings
import json
import logging
import logging.handlers
import requests
from flask import Flask, request, Response

app = Flask(__name__)

app.config['SDX_STORE_URL'] = settings.SDX_STORE_URL
app.config['SDX_TRANSFORM_CS_URL'] = settings.SDX_TRANSFORM_CS_URL

@app.route('/pck', methods=['GET'])
def do_transform():
    store_url = app.config['SDX_STORE_URL'] + "/response?surveyId=023"
    result = requests.get(store_url).json()
    stored_json = result['results'][0]['surveyResponse']

    transform_url = app.config['SDX_TRANSFORM_CS_URL'] + "/pck"
    transformed_data = requests.post(transform_url, json=stored_json)
    response = Response(response=transformed_data,
        status=200, \
        mimetype="application/json")
    return(response)

if __name__ == '__main__':
    # Startup
    logging.basicConfig(level=settings.LOGGING_LEVEL, format=settings.LOGGING_FORMAT)
    app.run(debug=True, host='0.0.0.0', port=5001)
