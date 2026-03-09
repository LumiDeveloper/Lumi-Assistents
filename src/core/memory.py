import sqlite3
import os


class LumiMemory:
    def __init__(self, db_path="src/core/memory/lumi_soul.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        

    def create_tables(self):
        # Таблица пользователей для v0.9 (Илья, брат, младший, сестра)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                role TEXT CHECK(role IN ('creator', 'brother', 'sister', 'junior', 'guest')),
                relation_level INTEGER DEFAULT 50 CHECK(relation_level BETWEEN 0 AND 100), -- Для v0.6 (эмоции)
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица истории диалогов для контекста
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT CHECK (role IN ('user', 'assistant')), -- 'user' или 'lumi'
                content TEXT NOT NULL,
                tokens INTEGER,
                is_important BOOLEAN DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Индексация, прописанная Люми
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_user ON chat_history(user_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_time ON chat_history(timestamp)')
        
        self.conn.commit()


    def get_or_create_user(self, name, role="guest"):
        """Находит пользователя или регистрирует нового"""
        self.cursor.execute("INSERT OR IGNORE INTO users (name, role) VALUES (?, ?)", (name, role))
        self.cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
        return self.cursor.fetchone()[0]

    def add_message(self, user_name, role, content):
        """Сохраняет реплику в базу данных"""
        user_id = self.get_or_create_user(user_name)
        self.cursor.execute("INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)", 
                           (user_id, role, content))
        self.conn.commit()

    def get_recent_context(self, user_name, limit=6):
        """Выгружает последние сообщения для 'мозга'"""
        self.cursor.execute('''
            SELECT chat_history.role, chat_history.content FROM chat_history 
            JOIN users ON chat_history.user_id = users.id 
            WHERE users.name = ? 
            ORDER BY chat_history.id DESC LIMIT ?
        ''', (user_name, limit))
        rows = self.cursor.fetchall()
        # Превращаем в формат, который понимают DeepSeek и GigaChat
        context = [{"role": r, "content": c} for r, c in rows]
        return context[::-1] # Переворачиваем, чтобы было от старых к новым