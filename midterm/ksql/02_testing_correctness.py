import subprocess
from tabulate import tabulate

ksql_statements = """
SET 'auto.offset.reset' = 'earliest';
SET 'ksql.streams.cache.max.bytes.buffering' = '0';

SELECT * FROM cleaned_users_stream EMIT CHANGES LIMIT 10;
SELECT * FROM pageview_country_table EMIT CHANGES LIMIT 10;
SELECT * FROM pageview_tumbling_table EMIT CHANGES LIMIT 10;
SELECT * FROM pageview_hopping_table EMIT CHANGES LIMIT 10;
SELECT * FROM pageview_session_table EMIT CHANGES LIMIT 10;
"""

result = subprocess.run('docker exec -i ksqldb-cli ksql http://ksqldb-server:8088', input=ksql_statements, text=True, capture_output=True)

if result.returncode != 0:
  print(f'Execution failed, error: {result.stderr}')
else:
  lines = result.stdout.splitlines()
  table_data = []
  header_line = None

  for line in lines:
    if line.startswith("+"):
      continue
    elif line.startswith("|"):
      row = [cell.strip() for cell in line.split("|")[1:-1]]
      if header_line is None:
        header_line = row
      else:
        table_data.append(row)

  if table_data:
    print(tabulate(table_data, headers=header_line, tablefmt="grid"))
  else:
    print(result.stdout)