### Unreleased
  - Add service config to application config file
  - Begin using PyTest as default test runner
  - Remove sdx-common from requirements

### 3.1.0 2017-10-16
  - Hardcode unchanging variables in settings.py to make configuration management simpler

### 3.0.1 2017-09-25
  - Tag release against correct branch

### 3.0.0 2017-09-25
  - Add ability to handle cora submissions
  - Remove clone of sdx-common in docker

### 2.3.0 2017-09-11
  - Ensure integrity and version of library dependencies
  - Correctly handle error responses from dependent services
  - Integrate with sdc-rabbit library

### 2.2.0 2017-07-25
  - Change all instances of ADD to COPY in Dockerfile
  - Remove use of SDX_HOME variable in makefile

### 2.1.0 2017-07-10
  - Log tx_id for FTP successes and failures
  - Add environment variables to README
  - Add codacy badge
  - Correct license attribution
  - Add support for codecov to see unit test coverage
  - Addings sdx-common functionality
  - updating timezoning
  - Update and pin version of sdx-common to 0.7.0
  - Add additional logging

### 2.0.1 2017-03-15
  - Log version number on startup
  - Fix handling of None responses in remote call
  - Change `status_code` to `status` for SDX logging
  - Change logging messages to add the service called or returned from

### 2.0.0 2017-02-16
  - Add explicit ack/nack for messages based on processing success
  - Add persistent ftp connection
  - Make queue durable
  - Add change log
  - Remove publishing to delay queue on failure
  - Fix [#23](https://github.com/ONSdigital/sdx-downstream/issues/23) by removing redundant census processor - now lives under [sdx-downstream-ctp](https://github.com/ONSdigital/sdx-downstream-ctp)
  - Update python library '_requests_': `2.10.0` -> `2.12.4`
  - Update docker base image to use [onsdigital/flask-crypto-queue](https://hub.docker.com/r/onsdigital/flask-crypto-queue/)
  - Remove reject on max retries. Stops message being rejected if endpoint is down for prolonged period
  - Add queue name to log message and remove dump of payload
  - Add `prefetch` to rabbit consumer to address '104 Socket' errors
  - Update env var for queue name

### 1.0.1 2016-11-10
  - Fix [#16](https://github.com/ONSdigital/sdx-downstream/issues/16) remove rabbit queue connection details from logs

### 1.0.0 2016-08-11
  - Initial release
