import pymysql

conn = pymysql.connect(host='localhost', port=3307, user='user', password='password', db='demo')
cursor = conn.cursor()

def user_count():
  cursor.execute("SELECT COUNT(*) FROM Users")
  print(cursor.fetchone()[0])

# user_count()

def user_sample():
  cursor.execute("SELECT * FROM Users LIMIT 3")
  for row in cursor.fetchall():
    print(row)

user_sample()

# cursor.execute("DROP TABLE IF EXISTS Users")

cursor.close()
conn.close()