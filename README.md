# sdx-downstream

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/bf44060d82ee41f49d73729b9150eb99)](https://www.codacy.com/app/ons-sdc/sdx-downstream?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ONSdigital/sdx-downstream&amp;utm_campaign=Badge_Grade) [![codecov](https://codecov.io/gh/ONSdigital/sdx-downstream/branch/master/graph/badge.svg)](https://codecov.io/gh/ONSdigital/sdx-downstream)

The sdx-downstream app is used within the Office for National Statistics (ONS) for consuming decrypted Survey Data Exchange (SDX) Surveys from sdx-store and delivering them to downstream environments e.g. Common Software.

## Installation

Using virtualenv and pip, create a new environment and install within using:

    $ pip install -r requirements.txt

To run the tests, also install the test dependencies into a virtualenv using:

    $ pip install -r test_requirements.txt

It's also possible to install within a container using docker. From the sdx-downstream directory:

    $ docker build -t sdx-downstream .

## Configuration

The following environment variables can be set:

| Environment Variable    | Default                               | Description
|-------------------------|---------------------------------------|----------------
| SDX_STORE_URL           | `http://sdx-store:5000`               | The URL of the `sdx-store` service
| SDX_TRANSFORM_CS_URL    | `http://sdx-transform-cs:5000`        | The URL of the `sdx-transform-cs` service
| SDX_SEQUENCE_URL        | `http://sdx-sequence:5000`            | The URL of the `sdx-sequence` service
| FTP_HOST                | `pure-ftpd`                           | FTP to monitor
| FTP_USER                | _none_                                | User for FTP account if required
| FTP_PASS                | _none_                                | Password for FTP account if required
| FTP_FOLDER              | `/`                                   | FTP folder
| RABBIT_QUEUE            | `sdx-cs-survey-notifications`         | Rabbit queue name
| RABBIT_EXCHANGE         | `message`                             | RabbitMQ exchange to use

## Usage

sdx-downstream works as a single consumer which exposes no endpoints. The best way to test its behaviour is to start it within a [docker-compose](https://github.com/ONSdigital/sdx-compose) setup and trigger the consumer through the console.

### License

Copyright (c) 2016 Crown Copyright (Office for National Statistics)

Released under MIT license, see [LICENSE](LICENSE) for details.
