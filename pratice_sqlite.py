import sqlite3


conn = sqlite3.connect('test.db')


cur = conn.cursor()


cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    email TEXT UNIQUE
)
''')

cur.execute("INSERT INTO users (name, age, email) VALUES ('홍길동', 25, 'hong@example.com')")


cur.execute("SELECT * FROM users")
rows = cur.fetchall()


for row in rows:
    print(row)

conn.close()