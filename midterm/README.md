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

# 3. Apache Pinot

# 4. Streamlit

# 5. Docker Setup

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

### Setup Connector, Create Stream, and Populate Data
Run init.sh using Git Bash  
```bash
sh init.sh
```
`connector-config.json`
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

### Check KSQL Tables
```bash
python "./ksql/02_testing_correctness.py"
```