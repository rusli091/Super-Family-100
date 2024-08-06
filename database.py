import sqlite3

class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def update_score(self, chat_id, username, score):
        self.cursor.execute(
            "INSERT OR IGNORE INTO scores (chat_id, username, score) VALUES (?, ?, ?)",
            (chat_id, username, score)
        )
        self.cursor.execute(
            "UPDATE scores SET score = score + ? WHERE chat_id = ? AND username = ?",
            (score, chat_id, username)
        )
        self.connection.commit()

    def close(self):
        self.connection.close()
