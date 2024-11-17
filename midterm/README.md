# 1. Data Source

### Source 1: PageView (stream datagen) (topic1_PageView)

`session_id`: Unique identifier for user session.  
`user_id`: Identifier for the user who triggered the view event.  
`source`: The origin of the view event. (Homepage, Inbox, External)  
`event_timestamp`: The timestamp when the view event occurred.  

### Source 2: UserSession (stream datagen) (topic2_UserSession)

`session_id`: Unique identifier for user session.  
`user_id`: Unique identifier for each user.  
`user_name`: The name of the user.  
`login_timestamp`: The timestamp when the user last logged in.  
`device`: The device used by the user for the last login.  

### Source 3: Users (relational database) (topic3_Users)

`user_id`: Unique identifier for each user.  
`age`: The age of the user.  
`gender`: The gender of the user.  
`country`: The primary location of the user.  
`subscription`: The subscription tier of the user (Platinum, Gold, Silver, Standard).  

# 2. Kafka & KSQL DB

**Kafka:** *3 Brokers, 5 Partitions, 8 Topics*  
`topic1`: PageView - *Base Stream*  
`topic2`: UserSession - *Base Stream*  
`topic3`: Users - *Base Table*  
`topic4`: CleanedUsers - *Users table without NULL values*  
`topic5`: PageView Country - *PageView joined with CleanedUsers*  
`topic6`: PageView Tumbling - *Tumbling Windows*  
`topic7`: PageView Hopping - *Hopping Windows*  
`topic8`: PageView Session - *Session Windows*  

# 3. Apache Pinot & Streamlit

Apache Pinot and Streamlit are used for real-time analytics and interactive visualization of the data streams.

### Apache Pinot
Apache Pinot is a real-time distributed OLAP datastore, which is used to deliver scalable real-time analytics with low latency. It can ingest data from batch and stream data sources (such as Kafka).

In this system, real-time tables in Pinot are created based on topic5 to topic8.
The Pinot table configurations and schemas are uploaded using REST API calls:
```
curl -X POST -H "Content-Type: application/json" -d @./config/pinot-schema-5.json http://localhost:9000/schemas
curl -X POST -H "Content-Type: application/json" -d @./config/pinot-config-5.json http://localhost:9000/tables
```

The configuration and schema files (pinot-config-5.json, pinot-schema-5.json, and so on for 6-8) define the table structure and settings in Pinot.

The created real-time tables are:
```
pageview_country_REALTIME
pageview_hopping_REALTIME
pageview_session_REALTIME
pageview_tumbling_REALTIME
```

### Streamlit
Streamlit is an open-source Python library that makes it easy to create custom web apps for machine learning and data science.

In this system, Streamlit is used to query the real-time tables in Pinot and plot the charts for each table. The charts provide visual insights into user count by country and user count by each window (grouped by source). The real-time data will be fetched every 15 seconds.


# 4. Docker Setup

### Download and Build Containers
Build image and connector  
```bash
docker build -f Dockerfile.streamlit -t streamlit-image .
docker build -f Dockerfile.kafka-connect -t kafka-connect .
docker-compose up -d
```

### Auto Executors  
`init.sql`
```sql
CREATE DATABASE IF NOT EXISTS demo;
USE demo;
DROP TABLE IF EXISTS Users;

CREATE TABLE IF NOT EXISTS Users (
  user_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  age INT,
  gender VARCHAR(10),
  country VARCHAR(200),
  subscription VARCHAR(20)
)
```
`create-topics.sh`
```bash
#!/bin/bash

topics=("topic1_PageView" "topic2_UserSession" "topic3_Users" "topic4" "topic5" "topic6" "topic7" "topic8")

for topic in "${topics[@]}"
do
  if /usr/bin/kafka-topics --bootstrap-server kafka1:9092 --topic $topic --describe > /dev/null 2>&1; then
    echo "Topic $topic already exists, skipping."
  else
    echo "Creating topic $topic."
    /usr/bin/kafka-topics --create --bootstrap-server kafka1:9092 --replication-factor 3 --partitions 5 --topic $topic
  fi
done
```

### Setup Connectors, Create Streams, and Populate Data
Run init.sh using Git Bash  
```bash
sh init.sh
```

Processes executed by `init.sh`:  
`Initialize Connector`
```bash
curl -X POST -H "Content-Type: application/json" -d @./config/connector-config.json http://localhost:8083/connectors
```
```json
{
  "name": "jdbc-source-connector",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
    "tasks.max": "1",
    "connection.url": "jdbc:mysql://mysql-server:3306/demo?useSSL=false",
    "connection.user": "user",
    "connection.password": "password",
    "table.whitelist": "Users",
    "mode": "incrementing",
    "key.field": "user_id",
    "incrementing.column.name": "user_id",
    "topic.prefix": "topic3_",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url": "http://schema-registry:8081",
    "value.converter.schemas.enable": "true"
  }
}
```
`Setup Realtime Tables`
```bash
curl -X POST -H "Content-Type: application/json" -d @./config/pinot-schema-$i.json http://localhost:9000/schemas
curl -X POST -H "Content-Type: application/json" -d @./config/pinot-config-$i.json http://localhost:9000/tables
```
```json
{
  "tableName": "pageview_tumbling_REALTIME",
  "tableType": "REALTIME",
  "segmentsConfig": {
    "schemaName": "pageview_tumbling",
    "timeColumnName": "window_start",
    "replication": "1",
    "replicasPerPartition": "1",
    "minimizeDataMovement": false
  },
  "tenants": {
    "broker": "DefaultTenant",
    "server": "DefaultTenant",
    "tagOverrideConfig": {}
  },
  "tableIndexConfig": {
    "invertedIndexColumns": [],
    "rangeIndexColumns": [],
    "rangeIndexVersion": 2,
    "autoGeneratedInvertedIndex": false,
    "createInvertedIndexDuringSegmentGeneration": false,
    "sortedColumn": [],
    "bloomFilterColumns": [],
    "loadMode": "MMAP",
    "streamConfigs": {
      "streamType": "kafka",
      "stream.kafka.topic.name": "topic6",
      "stream.kafka.broker.list": "kafka1:9092",
      "stream.kafka.consumer.type": "lowlevel",
      "stream.kafka.consumer.prop.auto.offset.reset": "smallest",
      "stream.kafka.consumer.factory.class.name": "org.apache.pinot.plugin.stream.kafka20.KafkaConsumerFactory",
      "stream.kafka.decoder.class.name": "org.apache.pinot.plugin.stream.kafka.KafkaJSONMessageDecoder",
      "realtime.segment.flush.threshold.rows": "0",
      "realtime.segment.flush.threshold.time": "24h",
      "realtime.segment.flush.threshold.segment.size": "100M"
    },
    "noDictionaryColumns": [],
    "onHeapDictionaryColumns": [],
    "varLengthDictionaryColumns": [],
    "enableDefaultStarTree": false,
    "enableDynamicStarTreeCreation": false,
    "aggregateMetrics": false,
    "nullHandlingEnabled": false,
    "optimizeDictionary": false,
    "optimizeDictionaryForMetrics": false,
    "noDictionarySizeRatioThreshold": 0
  },
  "metadata": {},
  "quota": {},
  "routing": {},
  "query": {},
  "ingestionConfig": {
    "continueOnError": false,
    "rowTimeValueCheck": false,
    "segmentTimeValueCheck": true
  },
  "isDimTable": false
}
```
`Run Producers`
```bash
"./producer/00_set_timestamp.py"
"./producer/01_database_producer.py"
"./ksql/01_create_stream.py"
"./producer/02_kafka_producer.py"
```

### Check KSQL Tables
```bash
python "./ksql/02_testing_correctness.py"
```
