import sqlite3
from flask import g
from werkzeug.security import generate_password_hash, check_password_hash
import logging

DATABASE = 'user_data.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        create_users_table(db)
    return db

def create_users_table(db):
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    db.commit()

def register_user(username, password):
    db = get_db()
    hashed_password = generate_password_hash(password, method='sha256')
    try:
        db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        db.commit()
        logging.debug(f'User {username} registered successfully.')
        return True
    except sqlite3.IntegrityError:
        logging.debug(f'Username {username} already exists.')
        return False

def validate_login(username, password):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    logging.debug(f'User fetched from database: {user}')
    if user and check_password_hash(user[2], password):
        logging.debug(f'User {username} logged in successfully.')
        return True
    logging.debug(f'Invalid login attempt for username: {username}')
    return False

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
