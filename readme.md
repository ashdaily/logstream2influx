### Logs -> Bytewax -> InfluxDB :

```mermaid
sequenceDiagram
    actor Client/Users
    participant FastAPI
    participant InfluxDB Storage
    participant LogGenerator
    participant api_requests.log
    participant Bytewax.SimplePollingSource
    participant ByteWax.DataFlow
    participant LogProcessor
    
    Client/Users->>FastAPI: Sends API Requests
    FastAPI->>InfluxDB Storage: Queries for log data

    LogGenerator->>api_requests.log: Generates api_requests.logs (growing over time)
    Note over LogGenerator,api_requests.log: LogGenerator simulating growing log file<br>based on a rate <br> that can be set in .env.local to facilitate streaming
    
    Bytewax.SimplePollingSource ->>api_requests.log: Polls to seek to EOF
    Bytewax.SimplePollingSource->>ByteWax.DataFlow: newly seeked logs
    ByteWax.DataFlow-->>LogProcessor : log stream handling
    LogProcessor->>InfluxDB Storage: Store logs in InfluxDB
```

## Run the project
```bash
chmod +x ./start.sh && ./start.sh
```
- Simulates the end to end flow, runs `log_generator`, `log_processor`, `influx_db`, `api`  

### Log Generator
- Log Generator (`src/log_generator`) : Responsible for ingesting logs in `api_requests.log` at a rate. This rate is basically `LOG_BATCH_SIZE` per `LOG_INTERVAL_SECONDS`. 
- For example : `LOG_BATCH_SIZE=1` and `LOG_INTERVAL_SECONDS=60` means Log Generator will ingest one log line per `60` seconds. You can increase or decrease it but to understand the flow it's recommended to keep it at low as possible. 

### Log Processor
- LogProcessor uses `ByteWax.SimplePollingSource` to poll the log file Log Generator creates and seeks to the EOF and hands over the log line to `ByteWax.DataFlow` which hands it over to Log Handler which does some simple string to dict transformation and dumps it in the InfluxDB
- LogProcessor has some unit tests and some integration test that test against the InfluxDB docker instance.

### Api
- Available once project starts on `http://127.0.0.1:8000/docs`
- Sample request
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/customers/cust_1/stats?from_date=2024-10-01' \
  -H 'accept: application/json'
```

### Run Tests
```bash
chmod +x ./run_tests.sh && run_tests.sh
```

### Clean up setup
```bash
chmod +x ./cleanup.sh && ./cleanup.sh
```

- <p style="color: red">Note: that <code>`chmod`</code> command is required only the first time.</p>