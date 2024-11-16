from confluent_kafka import Producer
from bson import json_util
import json, traceback 

def delivery_report(err, msg):
  if err is not None:
    print(f"Message delivery failed: {err}")
  else:
    print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

producer = Producer({'bootstrap.servers': 'localhost:9093, localhost:9094, localhost:9095'})
message = {'key1': 'value1', 'key2': 'value2'}

try:
  producer.produce('test', key="", value=json.dumps(message, default=json_util.default).encode('utf-8'), callback=delivery_report)
  producer.flush()
except Exception as e:
  print(f"Exception occurred: {type(e).__name__}")
  print(f"Error message: {e}")
  print("Traceback:")
  traceback.print_exc()