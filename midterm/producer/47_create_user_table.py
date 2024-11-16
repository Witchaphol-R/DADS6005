import pymysql

conn = pymysql.connect(host='localhost', port=3307, user='user', password='password', db='demo')
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS Users")
cursor.execute("""
  CREATE TABLE IF NOT EXISTS Users (
    user_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    age INT,
    gender VARCHAR(10),
    country VARCHAR(200),
    subscription VARCHAR(20)
  )
""")

cursor.close()
conn.close()
print('Created')