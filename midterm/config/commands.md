docker build -f Dockerfile.streamlit -t streamlit-image .
docker build -f Dockerfile.kafka-connect -t kafka-connect .
docker-compose up -d
curl -X POST -H "Content-Type: application/json" --data @./config/connector-config.json http://localhost:8083/connectors

cls
docker ps
docker network inspect nx
docker exec -it kafka1 /bin/bash
/usr/bin/kafka-topics --list --bootstrap-server localhost:9092
/usr/bin/kafka-console-consumer --bootstrap-server localhost:9092 --topic test --from-beginning
netstat -a -b | findstr 9097
docker-compose exec ksqldb-cli ksql http://ksqldb-server:8088


SET 'auto.offset.reset' = 'earliest';
SET 'ksql.streams.cache.max.bytes.buffering' = '0';
PRINT 'topic2_UserSession' FROM BEGINNING;
SELECT * FROM usersession_stream EMIT CHANGES LIMIT 10;
DESCRIBE users_table;
PRINT 'topic3_Users' FROM BEGINNING;
SELECT * FROM users_stream EMIT CHANGES LIMIT 10;
SELECT * FROM users_table EMIT CHANGES LIMIT 10;
SHOW STREAMS;