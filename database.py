# database.py
import sqlite3

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS users
        (id INTEGER PRIMARY KEY, username TEXT, score INTEGER)
        ''')
        self.conn.commit()

    def update_score(self, user_id, username, score):
        self.cur.execute('''
        INSERT OR REPLACE INTO users (id, username, score)
        VALUES (?, ?, COALESCE((SELECT score FROM users WHERE id = ?), 0) + ?)
        ''', (user_id, username, user_id, score))
        self.conn.commit()

    def get_top_players(self, limit=10):
        self.cur.execute('SELECT username, score FROM users ORDER BY score DESC LIMIT ?', (limit,))
        return self.cur.fetchall()

    def close(self):
        self.conn.close()