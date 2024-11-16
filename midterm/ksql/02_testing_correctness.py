import subprocess

ksql_statements = """
SET 'auto.offset.reset' = 'earliest';
SET 'ksql.streams.cache.max.bytes.buffering' = '0';

SELECT * FROM cleaned_users_stream EMIT CHANGES LIMIT 10;
SELECT * FROM pageview_country EMIT CHANGES LIMIT 10;
SELECT * FROM pageview_tumbling_table EMIT CHANGES LIMIT 10;
SELECT * FROM pageview_hopping_table EMIT CHANGES LIMIT 10;
SELECT * FROM pageview_session_table EMIT CHANGES LIMIT 10;
"""

result = subprocess.run('docker exec -i ksqldb-cli ksql http://ksqldb-server:8088', input=ksql_statements, text=True, capture_output=True)

if result.returncode != 0:
  print(f'Execution failed, error: {result.stderr}')

print(result.stdout)