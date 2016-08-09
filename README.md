# sdx-downstream

The sdx-downstream app is used within the Office for National Statistics (ONS) for consuming decrypted Survey Data Exchange (SDX) Surveys from sdx-store and delivering them to downstream environments e.g. Common Software.

## Installation

Using virtualenv and pip, create a new environment and install within using:

    $ pip install -r requirements.txt

To run the tests, also install the test dependencies into a virtualenv using:

    $ pip install -r test_requirements.txt

It's also possible to install within a container using docker. From the sdx-downstream directory:

    $ docker build -t sdx-downstream .

## Configuration

The following envioronment variables can be set:

`SDX_STORE_URL` - The URL of the sdx-store service, defaults to http://sdx-store:5000

`SDX_TRANSFORM_CS_URL` - The URL of the sdx-transform-cs service, defaults to http://sdx-transform-cs:5000

`SDX_SEQUENCE_URL` - The URL of the sdx-transform-cs service, defaults to http://sdx-sequence:5000

## Usage

sdx-downstream works as a single consumer which exposes no endpoints. The best way to test its behaviour is to start it within a [docker-compose](https://github.com/ONSdigital/sdx-compose) setup and trigger the consumer through the console.
