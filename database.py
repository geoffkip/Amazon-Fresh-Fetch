import sqlite3
import json
from datetime import datetime

class DBManager:
    def __init__(self, db_name="agent_data.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS settings 
                     (key TEXT PRIMARY KEY, value TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS meal_plans 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      date TEXT, 
                      prompt TEXT, 
                      plan_json TEXT, 
                      shopping_list TEXT)''')
        self.conn.commit()

    def save_setting(self, key, value):
        c = self.conn.cursor()
        c.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    def get_setting(self, key, default=""):
        c = self.conn.cursor()
        c.execute("SELECT value FROM settings WHERE key=?", (key,))
        result = c.fetchone()
        return result[0] if result else default

    def save_plan(self, prompt, plan_json, shopping_list):
        c = self.conn.cursor()
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        list_str = json.dumps(shopping_list)
        c.execute("INSERT INTO meal_plans (date, prompt, plan_json, shopping_list) VALUES (?, ?, ?, ?)",
                  (date_str, prompt, plan_json, list_str))
        self.conn.commit()

    def get_recent_plans(self, limit=5):
        c = self.conn.cursor()
        c.execute("SELECT id, date, prompt, plan_json, shopping_list FROM meal_plans ORDER BY id DESC LIMIT ?", (limit,))
        return [{"id": r[0], "date": r[1], "prompt": r[2], "json": r[3], "list": json.loads(r[4])} for r in c.fetchall()]

    def delete_all_plans(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM meal_plans")
        self.conn.commit()

    # --- PREFERENCE LEARNING ---
    def get_all_past_items(self):
        c = self.conn.cursor()
        c.execute("SELECT shopping_list FROM meal_plans")
        rows = c.fetchall()
        all_items = set()
        for r in rows:
            try:
                items = json.loads(r[0])
                for i in items: all_items.add(i.strip())
            except: pass
        return ", ".join(list(all_items))

db = DBManager()
