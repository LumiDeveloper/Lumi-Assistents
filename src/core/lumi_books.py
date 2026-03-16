import json
import os
import difflib # Для поиска похожих ключей

class LumiBooks:
    def __init__(self):
        self.user_book = "memory/user_facts.json"
        self.research_book = "memory/world_lore.json"
        self.secret_diary = "memory/lumi_secrets.json"
        self._ensure_storage()

    def _ensure_storage(self):
        if not os.path.exists("memory"):
            os.makedirs("memory")
        for book in [self.user_book, self.research_book, self.secret_diary]:
            if not os.path.exists(book):
                with open(book, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=4)

    def save_fact(self, book_type, key, value):
        """Умное сохранение с защитой от точных дублей"""
        paths = {"user": self.user_book, "research": self.research_book, "secret": self.secret_diary}
        path = paths.get(book_type)
        if not path: return

        key = key.strip().lower()
        value = value.strip()

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. Если такой ключ уже есть
        if key in data:
            # Если значение то же самое - игнорируем
            if data[key].lower() == value.lower():
                return
            # Если значение новое - обновляем (или можно дописывать через запятую)
            print(f"🔄 Обновляю: {key} -> {value}")
        else:
            print(f"✅ Новый факт: {key} = {value}")

        data[key] = value

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        uncertain_words = ["не знаю", "не уверена", "может быть", "неизвестно", "забыла"]
        if any(word in value.lower() for word in uncertain_words):
            print(f"⚠️ Попытка стереть факт '{key}' отклонена. Люми пытается 'забыть' данные.")
            return

        # Если ключ уже есть, и мы пытаемся записать что-то менее информативное
        if key in data and len(value) < 3: # защита от записи пустых строк
            return

    def maintenance(self):
        """Метод 'уборки': объединяет похожие ключи (имя/имя_пользователя)"""
        print("🧹 Люми наводит порядок в чертогах разума...")
        for book_path in [self.user_book, self.research_book, self.secret_diary]:
            with open(book_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            keys = list(data.keys())
            new_data = {}
            
            skip_keys = set()
            for i, key in enumerate(keys):
                if key in skip_keys: continue
                
                # Ищем похожие ключи среди оставшихся
                matches = difflib.get_close_matches(key, keys[i+1:], n=1, cutoff=0.8)
                
                if matches:
                    similar_key = matches[0]
                    print(f"🔗 Объединяю '{similar_key}' с основным ключом '{key}'")
                    # Соединяем значения, если они разные
                    if data[key] != data[similar_key]:
                        new_data[key] = f"{data[key]}; {data[similar_key]}"
                    else:
                        new_data[key] = data[key]
                    skip_keys.add(similar_key)
                else:
                    new_data[key] = data[key]
            
            with open(book_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=4)