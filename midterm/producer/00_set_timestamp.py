import os

script_dir = os.path.dirname(os.path.realpath(__file__))
timestamp_file = os.path.join(script_dir, 'timestamp.txt')

with open(timestamp_file, 'w') as f:
  f.write('2024-01-01 00:00:01')