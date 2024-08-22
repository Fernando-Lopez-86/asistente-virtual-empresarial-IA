import sqlite3
from hashlib import sha256

def create_database():
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(username, password, role):
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    hashed_password = sha256(password.encode()).hexdigest()
    c.execute("INSERT INTO users (user, password, role) VALUES (?, ?, ?)", 
              (username, hashed_password, role))
    conn.commit()
    conn.close()