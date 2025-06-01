# App worker
A service in charge of performing operations remotelly and async.

## How it works?
Connected via websockets to the main server, will receive tasks

## Configuration parameters
Worker
- `SERVER_URL`: Base URL of the server
- `AUTH_TOKEN`: Token to identify against the server
- `LOG_FORMAT`: Log formatting (plain by default, can be set to `json`)
