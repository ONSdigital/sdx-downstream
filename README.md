# sdx-downstream

[![Build Status](https://github.com/ONSdigital/sdx-downstream/workflows/Build/badge.svg)](https://github.com/ONSdigital/sdx-downstream) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/bf44060d82ee41f49d73729b9150eb99)](https://www.codacy.com/app/ons-sdc/sdx-downstream?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ONSdigital/sdx-downstream&amp;utm_campaign=Badge_Grade)

The sdx-downstream app is used within the Office for National Statistics (ONS) for consuming decrypted Survey Data Exchange (SDX) Surveys from sdx-store and delivering them to downstream environments e.g. Common Software.

## Installation
This application presently installs required packages from requirements files:
- `requirements.txt`: packages for the application, with hashes for all packages: see https://pypi.org/project/hashin/
- `test-requirements.txt`: packages for testing and linting

It's also best to use `pyenv` and `pyenv-virtualenv`, to build in a virtual environment with the currently recommended version of Python.  To install these, see:
- https://github.com/pyenv/pyenv
- https://github.com/pyenv/pyenv-virtualenv
- (Note that the homebrew version of `pyenv` is easiest to install, but can lag behind the latest release of Python.)

### Getting started
Once your virtual environment is set, install the requirements:
```shell
$ make build
```

To test, first run `make build` as above, then run:
```shell
$ make test
```

It's also possible to install within a container using docker. From the sdx-downstream directory:
```shell
$ docker build -t sdx-downstream .
```

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
