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