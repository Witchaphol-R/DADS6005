import subprocess

ksql_statements = """
SET 'auto.offset.reset' = 'earliest';
SET 'ksql.streams.cache.max.bytes.buffering' = '0';

-- DROP STREAM/TABLE --
DROP STREAM IF EXISTS test;
DROP TABLE IF EXISTS pageview_country_table;
DROP TABLE IF EXISTS cleaned_pageview_stream;
DROP STREAM IF EXISTS cleaned_users_table;
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

CREATE TABLE cleaned_users_table
  WITH (
    KAFKA_TOPIC='topic4'
    , PARTITIONS=5
    , VALUE_FORMAT='JSON'
  ) AS
    SELECT 
      user_id
      , LATEST_BY_OFFSET(age) AS age
      , LATEST_BY_OFFSET(country) AS country
      , LATEST_BY_OFFSET(subscription) AS subscription
    FROM users_stream
    WHERE user_id IS NOT NULL
      AND age IS NOT NULL
      AND gender IS NOT NULL
      AND country IS NOT NULL
      AND subscription IS NOT NULL
    GROUP BY user_id;

CREATE STREAM cleaned_pageview_stream
  WITH (VALUE_FORMAT='JSON') AS
    SELECT
      cleaned_users_table.user_id
      , age
      , country
      , subscription
      , event_timestamp 
    FROM pageview_stream
    LEFT JOIN cleaned_users_table
      ON CAST(pageview_stream.user_id AS BIGINT) = cleaned_users_table.user_id;

CREATE TABLE pageview_country_table
  WITH (
    KAFKA_TOPIC='topic5'
    , PARTITIONS=5
    , VALUE_FORMAT='JSON'
  ) AS
    SELECT
      country
      , FORMAT_TIMESTAMP(FROM_UNIXTIME(WINDOWSTART),'yyyy-MM-dd HH:mm:ss', 'UTC') AS window_start
      , AVG(age) AS average_age
      , COUNT(*) AS pageview_count
    FROM cleaned_pageview_stream
    WINDOW TUMBLING (SIZE 5 MINUTES)
    GROUP BY country;

-- WINDOWS --

CREATE TABLE pageview_tumbling_table
  WITH (
    KAFKA_TOPIC='topic6'
    , PARTITIONS=5
    , VALUE_FORMAT='JSON'
  ) AS
    SELECT
      source
      , FORMAT_TIMESTAMP(FROM_UNIXTIME(WINDOWSTART),'yyyy-MM-dd HH:mm:ss', 'UTC') AS window_start
      , FORMAT_TIMESTAMP(FROM_UNIXTIME(WINDOWEND),'yyyy-MM-dd HH:mm:ss', 'UTC') AS window_end
      , COUNT(*) AS pageview_count
    FROM pageview_stream
    WINDOW TUMBLING (SIZE 5 MINUTES)
    GROUP BY source;

CREATE TABLE pageview_hopping_table
  WITH (
    KAFKA_TOPIC='topic7'
    , PARTITIONS=5
    , VALUE_FORMAT='JSON'
  ) AS
    SELECT
      source
      , FORMAT_TIMESTAMP(FROM_UNIXTIME(WINDOWSTART),'yyyy-MM-dd HH:mm:ss', 'UTC') AS window_start
      , FORMAT_TIMESTAMP(FROM_UNIXTIME(WINDOWEND),'yyyy-MM-dd HH:mm:ss', 'UTC') AS window_end
      , COUNT(*) AS pageview_count
    FROM pageview_stream
    WINDOW HOPPING (SIZE 5 MINUTES, ADVANCE BY 1 MINUTES)
    GROUP BY source;

CREATE TABLE pageview_session_table
  WITH (
    KAFKA_TOPIC='topic8'
    , PARTITIONS=5
    , VALUE_FORMAT='JSON'
  ) AS
    SELECT
      source
      , FORMAT_TIMESTAMP(FROM_UNIXTIME(WINDOWSTART),'yyyy-MM-dd HH:mm:ss', 'UTC') AS window_start
      , FORMAT_TIMESTAMP(FROM_UNIXTIME(WINDOWEND),'yyyy-MM-dd HH:mm:ss', 'UTC') AS window_end
      , COUNT(*) AS pageview_count
    FROM pageview_stream
    WINDOW SESSION (5 MINUTES)
    GROUP BY source;
"""

result = subprocess.run('docker exec -i ksqldb-cli ksql http://ksqldb-server:8088', input=ksql_statements, text=True, capture_output=True)

if result.returncode != 0:
  print(f'Execution failed, error: {result.stderr}')

print(result.stdout)