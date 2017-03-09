### Unreleased
  - Fix handling of None responses in remote call
  - Change `status_code` to `status` for SDX logging

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
