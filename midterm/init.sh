#!/bin/bash

cd "$(dirname "$0")" || exit 1 # current directory

echo "Starting the connector setup..."
curl -X POST -H "Content-Type: application/json" -d @./config/connector-config.json http://localhost:8083/connectors
if [ $? -ne 0 ]; then
  echo "Error: Failed to configure the connector. Exiting."
  exit 1
fi
echo ""
echo "Connector setup completed successfully."

sleep 1

for i in {5..8}
do
  echo ""
  echo "Executing schema and config for topic$i"
  curl -X POST -H "Content-Type: application/json" -d @./config/pinot-schema-$i.json http://localhost:9000/schemas
  curl -X POST -H "Content-Type: application/json" -d @./config/pinot-config-$i.json http://localhost:9000/tables
done
echo ""
echo "Realtime setup completed successfully."

sleep 1

python_scripts=(
  "./producer/00_set_timestamp.py"
  "./producer/01_database_producer.py"
  "./ksql/01_create_stream.py"
  "./producer/02_kafka_producer.py"
)

for script in "${python_scripts[@]}"; do
  echo "Running $script..."
  python "$script"
  if [ $? -ne 0 ]; then
    echo "Error: $script failed. Exiting."
    exit 1
  fi
  echo "$script completed successfully."
done

echo "All tasks completed successfully."