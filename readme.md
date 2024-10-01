### NOTES:
- [ ] Revisit docker-compose
- [ ] Retest one command setup
- [ ] Should be 12 factor app compliant
- [ ] Assumption made that logs fields will not be null, absense of a log field will mean rejected for processing.
- [ ] 1 million request per second, data retention 30 days
- [ ] Reduce cardinality
- [ ] use one .env.local file for docker compose, docker files and everything else like log processor, bytewax

### Thoughts : 
- Since Bytewax and Streaming is mentioned, the data will be processed in streams 
- For batch inserts postgres should be fine but this project is probably demanding stream ingestion.
- For streams (data as it is available) inserts / ingestion rate postgres will do poorly at high ingestion rates like 1 mil rows per second 
  without optimization because of increased disk space and cause slow queries, a good fit here could be a time series db store because logs have timestamps. 
- The request for the api will have customer_id and date for which we need to return stats, the calculation of p99, median and avg latency are also required.
- Looks like a influx db satisfy the log processing requirement and also the log search requirement too because it has inherent support for p99, median, avg calculations. 


### System Design :

```mermaid
sequenceDiagram
    participant LogFile as Log File (api_requests.log)
    participant Bytewax as Bytewax (Stream Processor)
    participant InfluxDB as InfluxDB (Time-Series Database)
    participant FastAPI as FastAPI (API Service)
    participant Client as API Client

    LogFile->>Bytewax: Reads logs line by line
    Bytewax->>InfluxDB: Processes log data and sends to InfluxDB
    Client->>FastAPI: Requests stats (GET /customers/:id/stats)
    FastAPI->>InfluxDB: Queries log data for customer stats
    InfluxDB-->>FastAPI: Returns stats (success/failure counts, latency)
    FastAPI-->>Client: Sends back statistics (daily metrics)

```