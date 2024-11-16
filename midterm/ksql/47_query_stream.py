import subprocess

ksql_statements = """
SET 'auto.offset.reset' = 'earliest';
SET 'ksql.streams.cache.max.bytes.buffering' = '0';
SELECT * FROM usersession_stream EMIT CHANGES;
"""

result = subprocess.run([
  'docker', 'exec', '-i',
  'ksqldb-cli',
  'ksql', 'http://ksqldb-server:8088',
], input=ksql_statements, text=True, capture_output=True)

if result.returncode != 0:
  print(f'Execution failed, error: {result.stderr.strip()}')

print(result.stdout)