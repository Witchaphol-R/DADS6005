sh init.sh
sh pinot.sh

### Main Commands
docker build -f Dockerfile.streamlit -t streamlit-image .
docker build -f Dockerfile.kafka-connect -t kafka-connect .
docker-compose up -d
curl -X POST -H "Content-Type: application/json" -d @./config/connector-config.json http://localhost:8083/connectors
curl -X POST -H "Content-Type: application/json" -d @./config/pinot-schema-5.json http://localhost:9000/schemas
curl -X POST -H "Content-Type: application/json" -d @./config/pinot-config-5.json http://localhost:9000/tables

### Docker Debug
docker ps
docker network inspect nx
docker exec -it kafka1 /bin/bash
/usr/bin/kafka-topics --list --bootstrap-server localhost:9092
/usr/bin/kafka-console-consumer --bootstrap-server localhost:9092 --topic test --from-beginning

### KSQL
docker-compose exec ksqldb-cli ksql http://ksqldb-server:8088
SET 'auto.offset.reset' = 'earliest';
SET 'ksql.streams.cache.max.bytes.buffering' = '0';
PRINT 'topic3_Users' FROM BEGINNING;
SELECT * FROM users_stream EMIT CHANGES LIMIT 10;
SELECT * FROM users_table EMIT CHANGES LIMIT 10;
DESCRIBE pageview_session_table;
SHOW STREAMS;

### CMD
cls
netstat -a -b | findstr 9097