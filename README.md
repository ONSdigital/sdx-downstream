# sdx-downstream

The sdx-downstream app is used within the Office National of Statistics (ONS) for consuming decrypted Survey Data Exchange (SDX) Surveys from sdx-store and delivering them to downstream environments e.g. Common Software.

## Installation

Using virtualenv and pip, create a new environment and install within using:

    $ pip install -r requirements.txt

It's also possible to install within a container using docker. From the sdx-downstream directory:

    $ docker build -t sdx-downstream .

## Configuration

The following envioronment variables can be set:

`SDX_STORE_URL` - The URL of the sdx-store service, defaults to http://localhost:8080

`SDX_TRANSFORM_CS_URL` - The URL of the sdx-transform-cs service, defaults to http://localhost:5000

## Usage

Start sdx-downstream service using the following command:

    python server.py

sdx-downstream exposes a single endpoint - /pck - for transforming to the pck format and by default binds to port 5001 on localhost. It returns a response formatted in the type requested.

### Example
```
curl http://localhost:5001/pck
```
```
FBFV03000112/03/16
FV
RSI7B:12345678901A:0216
0001 00000000002
0011 00000010416
0012 00000311016
0020 00001800000
0021 00000060000
0022 00000705000
0023 00000000900
0024 00000000074
0025 00000000050
0026 00000000100
0146 00000000001
```

