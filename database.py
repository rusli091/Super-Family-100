import sqlite3

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                chat_id INTEGER,
                user_name TEXT,
                score INTEGER
            )
            """)
    
    def update_score(self, chat_id, user_name, score):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT score FROM scores WHERE chat_id=? AND user_name=?", (chat_id, user_name))
            row = cur.fetchone()
            if row:
                new_score = row[0] + score
                cur.execute("UPDATE scores SET score=? WHERE chat_id=? AND user_name=?", (new_score, chat_id, user_name))
            else:
                cur.execute("INSERT INTO scores (chat_id, user_name, score) VALUES (?, ?, ?)", (chat_id, user_name, score))
            self.conn.commit()

    def get_user_score(self, chat_id, user_name):
        cur = self.conn.cursor()
        cur.execute("SELECT score FROM scores WHERE chat_id=? AND user_name=?", (chat_id, user_name))
        row = cur.fetchone()
        return row[0] if row else 0

    def get_top_users(self):
        cur = self.conn.cursor()
        cur.execute("SELECT user_name, score FROM scores ORDER BY score DESC LIMIT 10")
        return cur.fetchall()

    def get_top_groups(self):
        cur = self.conn.cursor()
        cur.execute("SELECT chat_id, SUM(score) as total_score FROM scores GROUP BY chat_id ORDER BY total_score DESC LIMIT 10")
        return cur.fetchall()

    def close(self):
        self.conn.close()
