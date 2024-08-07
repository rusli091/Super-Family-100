import sqlite3

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS user_scores (
                                    username TEXT PRIMARY KEY,
                                    score INTEGER
                                )''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS group_scores (
                                    chat_id INTEGER,
                                    username TEXT,
                                    score INTEGER,
                                    PRIMARY KEY (chat_id, username)
                                )''')

    def update_score(self, chat_id, username, score):
        with self.conn:
            self.conn.execute('INSERT OR REPLACE INTO user_scores (username, score) VALUES (?, COALESCE((SELECT score FROM user_scores WHERE username = ?), 0) + ?)', (username, username, score))
            self.conn.execute('INSERT OR REPLACE INTO group_scores (chat_id, username, score) VALUES (?, ?, COALESCE((SELECT score FROM group_scores WHERE chat_id = ? AND username = ?), 0) + ?)', (chat_id, username, chat_id, username, score))

    def get_user_score(self, username):
        with self.conn:
            result = self.conn.execute('SELECT score FROM user_scores WHERE username = ?', (username,)).fetchone()
            return result[0] if result else 0

    def get_group_scores(self, chat_id):
        with self.conn:
            return self.conn.execute('SELECT username, score FROM group_scores WHERE chat_id = ? ORDER BY score DESC', (chat_id,)).fetchall()

    def get_top_users(self, limit=10):
        with self.conn:
            return self.conn.execute('SELECT username, score FROM user_scores ORDER BY score DESC LIMIT ?', (limit,)).fetchall()

    def close(self):
        self.conn.close()
