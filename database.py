import sqlite3

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        # Create tables if they don't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_scores (
                chat_id INTEGER,
                username TEXT,
                score INTEGER,
                PRIMARY KEY (chat_id, username)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_scores (
                chat_id INTEGER,
                username TEXT,
                score INTEGER,
                PRIMARY KEY (chat_id, username)
            )
        ''')
        self.conn.commit()

    def update_score(self, chat_id, username, score):
        # Update score for a user in a chat
        self.cursor.execute('''
            INSERT INTO user_scores (chat_id, username, score)
            VALUES (?, ?, ?)
            ON CONFLICT(chat_id, username) DO UPDATE SET
                score = score + excluded.score
        ''', (chat_id, username, score))
        self.conn.commit()

    def get_user_scores(self, chat_id, username):
        try:
            # Retrieve user scores
            self.cursor.execute('''
                SELECT score FROM user_scores
                WHERE chat_id = ? AND username = ?
            ''', (chat_id, username))
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error in get_user_scores: {e}")
            return 0

    def get_top_scores(self):
        try:
            # Retrieve top scores globally
            self.cursor.execute('''
                SELECT username, SUM(score) AS total_score
                FROM user_scores
                GROUP BY username
                ORDER BY total_score DESC
                LIMIT 10
            ''')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_top_scores: {e}")
            return []

    def get_group_top_scores(self, chat_id):
        try:
            # Retrieve top scores for a specific group
            self.cursor.execute('''
                SELECT username, score
                FROM group_scores
                WHERE chat_id = ?
                ORDER BY score DESC
                LIMIT 10
            ''', (chat_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_group_top_scores: {e}")
            return []

    def close(self):
        self.conn.close()
