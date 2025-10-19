import sqlite3
from werkzeug.security import generate_password_hash
import os

DB_PATH = 'users.db'

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                device_fingerprint TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')
        conn.commit()
        conn.close()

def add_user(email, password):
    """Вы вызываете эту функцию вручную, чтобы выдать доступ"""
    from werkzeug.security import generate_password_hash
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO users (email, password_hash)
            VALUES (?, ?)
        ''', (email, generate_password_hash(password)))
        print(f"✅ Пользователь {email} добавлен")
    except sqlite3.IntegrityError:
        print(f"⚠️ Пользователь {email} уже существует")
    conn.commit()
    conn.close()

def get_user(email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, email, password_hash, device_fingerprint, is_active FROM users WHERE email = ?', (email,))
    row = c.fetchone()
    conn.close()
    if row and row[4]:  # is_active == 1
        return {
            'id': row[0],
            'email': row[1],
            'password_hash': row[2],
            'device_fingerprint': row[3]
        }
    return None

def update_device_fingerprint(user_id, fp):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET device_fingerprint = ? WHERE id = ?', (fp, user_id))
    conn.commit()
    conn.close()
