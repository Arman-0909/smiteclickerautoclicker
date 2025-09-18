import sqlite3
import json

class DatabaseManager:
    def __init__(self, db_name="autoclicker.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                settings TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT,
                end_time TEXT,
                duration_seconds REAL,
                total_clicks INTEGER
            )
        """)
        self.conn.commit()

    def save_profile(self, name, settings_dict):
        settings_json = json.dumps(settings_dict)
        try:
            self.cursor.execute("INSERT INTO profiles (name, settings) VALUES (?, ?)", (name, settings_json))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_profiles(self):
        self.cursor.execute("SELECT id, name FROM profiles")
        return self.cursor.fetchall()

    def get_profile(self, profile_id):
        self.cursor.execute("SELECT name, settings FROM profiles WHERE id = ?", (profile_id,))
        row = self.cursor.fetchone()
        if row:
            name, settings_json = row
            return name, json.loads(settings_json)
        return None, None

    def delete_profile(self, profile_id):
        self.cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        self.conn.commit()

    def add_log(self, start_time, end_time, duration, clicks):
        self.cursor.execute(
            "INSERT INTO logs (start_time, end_time, duration_seconds, total_clicks) VALUES (?, ?, ?, ?)",
            (start_time, end_time, duration, clicks)
        )
        self.conn.commit()

    def get_all_logs(self):
        self.cursor.execute("SELECT id, start_time, end_time, duration_seconds, total_clicks FROM logs ORDER BY id DESC")
        return self.cursor.fetchall()

    def clear_logs(self):
        self.cursor.execute("DELETE FROM logs")
        self.conn.commit()

    def delete_log(self, log_id):
        self.cursor.execute("DELETE FROM logs WHERE id = ?", (log_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()