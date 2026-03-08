import sqlite3


class LumiMemory:
    def __init__(self, db_name="lumi_soul.db"):
        self.db_name = db_name
        self._init_db()
        

    def _init_db(self):
        # Создаем таблицу, если её нет
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users_facts (
                    fact_key TEXT PRIMARY KEY,
                    fact_value TEXT
                )
            ''')
            conn.commit()


    # Сохранить важный факт (например: 'name', 'Илья')
    def save_fact(self, key, value):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_facts (fact_key, fact_value) 
                VALUES (?, ?)
            ''', (key, value))
            conn.commit()


    # Получить все знания об Илье одной строкой
    def get_all_facts(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT fact_key, fact_value FROM user_facts')
            rows = cursor.fetchall()
            if not rows:
                return "Пока нет данных."
            return "; ".join([f"{k}: {v}" for k, v in rows])
        


    def save_message(self, role, content):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO chat_history (role, content) VALUES (?, ?)', (role, content))
            conn.commit()


    def get_recent_history(self, limit=10):
        # Берем последние 10 сообщений для контекста
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, content FROM (
                    SELECT * FROM chat_history ORDER BY id DESC LIMIT ? 
                ) ORDER BY id ASC
            ''', (limit,))
            rows = cursor.fetchall()
            return [{"role": r, "content": c} for r, c in rows]