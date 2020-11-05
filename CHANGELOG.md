### Unreleased
 - Methods to get feedback from store
 - Tests for feedback automation
 
### 3.14.0 2020-09-07
  - All surveys call 'transform' endpoint

### 3.13.3 2020-05-21
  - Updated packages

### 3.13.2 2020-05-13
  - Remove Cloudfoundry deployment files

### 3.13.1 2020-01-27
  - Add python 3.8 to travis builds
  - Update structlog to 19.2.0 to support python 3.8

### 3.13.0 2019-09-04
  - Update sdc-rabbit to 1.7.0 to fix reconnection issues
  - Update various dependencies

### 3.12.0 2019-08-13
  - Changed name of the SDX Collect Rabbit queue

### 3.11.0 2019-08-1
  - removed reference to transform_cora service
  - Reverted to default heartbeat

### 3.10.0 2019-06-20
  - Remove python 3.4 and 3.5 from travis builds
  - Add python 3.7 to travis builds
  - Upgrade various packages, including sdc-rabbit, pika and tornado to allow the upgrade to python 3.7

### 3.9.2 2019-05-14
  - Fix issue where the previous submissions values (tx_id, ru_ref, user_id) were still bound at the start of a new submission
  - Upgrade urllib3 package to fix security issue

### 3.9.1 2019-02-19
  - Fix security issue and update packages

### 3.9.0 2019-01-22
  - CORA submissions now go to sdx-transform-cs. sdx-transform-cs now handles transformations for all surveys as opposed
to having separate services to handle different types.
  - Fix newline bug in reprocessing script

### 3.8.0 2018-12-12
  - Added processor to handle surveys that go to CORD (currently only e-commerce)

### 3.7.0 2018-11-13
  - Add tx_id to ftp log lines
  - Add reprocessing scripts to repo
  - Add log with version on startup

### 3.6.0 2018-06-27
  - Remove second rabbit host

### 3.5.0 2018-01-17
  - Add heartbeat interval to rabbit mq url

### 3.4.0 2018-01-04
  - Removed ability to store heartbeat in a different folder
  - Refactored cora_processor , common_software_processor and message_processor to make them dryer

### 3.3.0 2017-11-21
  - Add changes for moving to cloud foundry

### 3.2.0 2017-11-01
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
