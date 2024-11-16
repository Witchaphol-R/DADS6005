import os, json
import random, pymysql
from datetime import datetime, timedelta
from confluent_kafka import Producer
from bson import json_util
from faker import Faker

fake = Faker()
conn = pymysql.connect(host='localhost', port=3307, user='user', password='password', db='demo')
cursor = conn.cursor()
producer = Producer({'bootstrap.servers': 'localhost:9093, localhost:9094, localhost:9095'})

script_dir = os.path.dirname(os.path.realpath(__file__))
timestamp_file = os.path.join(script_dir, 'timestamp.txt')

# 2024-01-01 00:00:01
if os.path.exists(timestamp_file):
  with open(timestamp_file, 'r') as f:
    start_timestamp = datetime.strptime(f.read(), '%Y-%m-%d %H:%M:%S')
else:
  start_timestamp = datetime.now()

start_timestamp = start_timestamp + timedelta(minutes=15)
last_timestamp = start_timestamp
cursor.execute("SELECT user_id FROM Users")
users = cursor.fetchall()

for user in users:
  user_id = user[0]
  unique_number = str(fake.unique.random_number(digits=4)).zfill(4)
  user_name = fake.name()
  device = random.choice(['Mobile', 'Desktop', 'Tablet'])
  login_timestamp = start_timestamp + timedelta(minutes=random.randint(1, 120))
  session_id = f"{login_timestamp.strftime('%Y%m%d-%H%M%S')}-{unique_number}"

  user_session = {
    'session_id': session_id,
    'user_id': user_id,
    'user_name': user_name,
    'login_timestamp': login_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
    'device': device
  }
  try:
    producer.produce('topic2_UserSession', key=session_id, value=json.dumps(user_session, default=json_util.default).encode('utf-8'))
  except Exception as e:
    print(f"Exception occurred: {e}")
  
  for _ in range(100):
    source = random.choice(['Homepage', 'Inbox', 'External'])
    event_timestamp = login_timestamp + timedelta(minutes=random.randint(1, 15))

    page_view = {
      'session_id': session_id,
      'user_id': user_id,
      'source': source,
      'event_timestamp': event_timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }
    try:
      producer.produce('topic1_PageView', key=session_id, value=json.dumps(page_view, default=json_util.default).encode('utf-8'))
    except Exception as e:
      print(f"Exception occurred: {e}")

    if event_timestamp > last_timestamp:
      last_timestamp = event_timestamp

with open(timestamp_file, 'w') as f:
  f.write(last_timestamp.strftime('%Y-%m-%d %H:%M:%S'))

producer.flush()
cursor.close()
conn.close()
print('Created')