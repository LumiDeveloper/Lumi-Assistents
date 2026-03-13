import json
import os

class LumiBooks:
    def __init__(self):
        # Пути к её новым личным вещам
        self.user_book = "memory/user_facts.json"
        self.research_book = "memory/world_lore.json"
        self.secret_diary = "memory/lumi_secrets.json"
        
        self._ensure_storage()

    def _ensure_storage(self):
        """Создаем папку, если её нет, чтобы Люми не 'потерялась'"""
        if not os.path.exists("memory"):
            os.makedirs("memory")
        
        # Создаем пустые блокноты, если их еще нет
        for book in [self.user_book, self.research_book, self.secret_diary]:
            if not os.path.exists(book):
                with open(book, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=4)

    def save_fact(self, book_type, key, value):
        """Метод записи, который она будет использовать незаметно"""
        paths = {
            "user": self.user_book,
            "research": self.research_book,
            "secret": self.secret_diary
        }
        path = paths.get(book_type)
        if not path: return

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data[key] = value
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)