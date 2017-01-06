### Unreleased
  - Add change log
  - Remove publishing to delay queue on failure
  - Remove redundant census processor - now lives under [sdx-downstream-ctp](https://github.com/ONSdigital/sdx-downstream-ctp)
  - Update python library '_requests_': `2.10.0` -> `2.12.4`
  - Update docker base image to use [onsdigital/flask-crypto-queue](https://hub.docker.com/r/onsdigital/flask-crypto-queue/)

### 1.0.1 2016-11-10
  - Fix [#16](https://github.com/ONSdigital/sdx-downstream/issues/16) remove rabbit queue connection details from logs

### 1.0.0 2016-08-11
  - Initial release