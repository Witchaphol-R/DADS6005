import random, pymysql

conn = pymysql.connect(host='localhost', port=3307, user='user', password='password', db='demo')
cursor = conn.cursor()

for _ in range(200):
  age = random.randint(20, 60)
  gender = random.choice(['Male', 'Female'])
  country = random.choice(['Thailand', 'Singapore', 'Vietnam'])
  subscription = random.choice(['Platinum', 'Gold', 'Silver', 'Standard'])
  cursor.execute("INSERT INTO Users (age, gender, country, subscription) VALUES (%s, %s, %s, %s)", (age, gender, country, subscription))
  conn.commit()

cursor.execute("SELECT COUNT(*) FROM Users")
total_users = cursor.fetchone()[0]

cursor.close()
conn.close()
print(f"Total Users: {total_users}")