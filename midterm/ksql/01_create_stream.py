import subprocess

ksql_statements = """
SET 'auto.offset.reset' = 'earliest';
SET 'ksql.streams.cache.max.bytes.buffering' = '0';

-- DROP STREAM/TABLE --
DROP STREAM IF EXISTS test;
DROP TABLE IF EXISTS pageview_country;
DROP TABLE IF EXISTS cleaned_users_table;
DROP STREAM IF EXISTS cleaned_users_stream;
DROP TABLE IF EXISTS pageview_tumbling_table;
DROP TABLE IF EXISTS pageview_hopping_table;
DROP TABLE IF EXISTS pageview_session_table;

DROP STREAM IF EXISTS pageview_stream;
DROP STREAM IF EXISTS usersession_stream;
DROP TABLE IF EXISTS users_table;
DROP STREAM IF EXISTS users_stream;

-- CREATE BASE STREAM/TABLE --

CREATE STREAM pageview_stream (session_id VARCHAR, user_id INT, source VARCHAR, event_timestamp VARCHAR)
  WITH (
    KAFKA_TOPIC='topic1_PageView'
    , VALUE_FORMAT='JSON'
    , PARTITIONS=5
    , TIMESTAMP='event_timestamp'
    , TIMESTAMP_FORMAT='yyyy-MM-dd HH:mm:ss'
  );

CREATE STREAM usersession_stream (session_id VARCHAR, user_id INT, user_name VARCHAR, login_timestamp VARCHAR, device VARCHAR)
  WITH (
    KAFKA_TOPIC='topic2_UserSession'
    , VALUE_FORMAT='JSON'
    , PARTITIONS=5
    , TIMESTAMP='login_timestamp'
    , TIMESTAMP_FORMAT='yyyy-MM-dd HH:mm:ss'
  );

CREATE STREAM users_stream (user_id BIGINT, age INT, gender VARCHAR, country VARCHAR, subscription VARCHAR)
WITH (
    KAFKA_TOPIC='topic3_Users'
    , VALUE_FORMAT='AVRO'
    , PARTITIONS=5
  );
CREATE TABLE users_table AS
  SELECT
    user_id
    , LATEST_BY_OFFSET(age) AS age
    , LATEST_BY_OFFSET(gender) AS gender
    , LATEST_BY_OFFSET(country) AS country
    , LATEST_BY_OFFSET(subscription) AS subscription
  FROM users_stream
  GROUP BY user_id;

-- CLEAN & AGGREGATE --

CREATE STREAM cleaned_users_stream
  WITH (
    KAFKA_TOPIC='topic4'
    , PARTITIONS=5
    , VALUE_FORMAT='AVRO'
  ) AS
    SELECT user_id, age, gender, country, subscription 
    FROM users_stream
    WHERE user_id IS NOT NULL
      AND age IS NOT NULL
      AND gender IS NOT NULL
      AND country IS NOT NULL
      AND subscription IS NOT NULL;
CREATE TABLE cleaned_users_table AS
  SELECT
    user_id
    , LATEST_BY_OFFSET(age) AS age
    , LATEST_BY_OFFSET(gender) AS gender
    , LATEST_BY_OFFSET(country) AS country
    , LATEST_BY_OFFSET(subscription) AS subscription
  FROM cleaned_users_stream
  GROUP BY user_id;

CREATE TABLE pageview_country
  WITH (
    KAFKA_TOPIC='topic5'
    , PARTITIONS=5
    , VALUE_FORMAT='AVRO'
  ) AS
    SELECT cleaned_users_table.country, COUNT(*) AS pageview_count
    FROM pageview_stream
    JOIN cleaned_users_table
      ON CAST(pageview_stream.user_id AS BIGINT) = cleaned_users_table.user_id
    GROUP BY cleaned_users_table.country;

-- WINDOWS --

CREATE TABLE pageview_tumbling_table
  WITH (
    KAFKA_TOPIC='topic6'
    , PARTITIONS=5
    , VALUE_FORMAT='JSON'
  ) AS
    SELECT source, COUNT(*) AS pageview_count
    FROM pageview_stream
    WINDOW TUMBLING (SIZE 30 SECONDS)
    GROUP BY source;

CREATE TABLE pageview_hopping_table
  WITH (
    KAFKA_TOPIC='topic7'
    , PARTITIONS=5
    , VALUE_FORMAT='JSON'
  ) AS
    SELECT source, COUNT(*) AS pageview_count
    FROM pageview_stream
    WINDOW HOPPING (SIZE 60 SECONDS, ADVANCE BY 30 SECONDS)
    GROUP BY source;

CREATE TABLE pageview_session_table
  WITH (
    KAFKA_TOPIC='topic8'
    , PARTITIONS=5
    , VALUE_FORMAT='JSON'
  ) AS
    SELECT source, COUNT(*) AS pageview_count
    FROM pageview_stream
    WINDOW SESSION (5 MINUTES)
    GROUP BY source;
"""

result = subprocess.run('docker exec -i ksqldb-cli ksql http://ksqldb-server:8088', input=ksql_statements, text=True, capture_output=True)

if result.returncode != 0:
  print(f'Execution failed, error: {result.stderr}')

print(result.stdout)