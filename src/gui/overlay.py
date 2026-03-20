# --------------------------------- Добавляем конфигурацию для python src/gui/overlay.py ------------------------------------------ #
import re
import sys
import os

# Добавляем родительскую директорию (src) в пути поиска
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import signal
import pyperclip
from core.listener import SpeechWorker
from PyQt6.QtWidgets import QApplication, QLayout, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap

from core.brain import BrainWorker, LumiBrain
from core.physics import LumiPhysics
from skills.actions import LumiActions



# Настройка завершения скрипта по Ctrl+C
signal.signal(signal.SIGINT, signal.SIG_DFL)


# ---------------------------------------------- Создаем кожу для нашей Люми ------------------------------------------------------- #

class LumiOverlay(QWidget):
    def __init__(self, brain, books):
        super().__init__()
        self.brain = brain
        self.books = books

        from skills.actions import LumiActions
        self.actions = LumiActions() 

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.NoDropShadowWindowHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setFixedWidth(400)
        self.setFixedHeight(800)

        self.brain = brain if brain else LumiBrain()
        self.init_ui()
        
        # Создаем объект-слушатель. # device_id — это тот ID от AudioRelay.
        self.worker = SpeechWorker(device_id=1) 
        self.worker.text_recognized.connect(self.on_speech)
        self.worker.start()
        self.is_thinking = False
        self.is_dragging = False

        # СОЗДАЕМ ОДИН BrainWorker на всё время жизни программы
        self.brain_worker = BrainWorker(self.brain)
        # Подключаем к методу, который обрабатывает ВСЁ (и память, и EXEC)
        self.brain_worker.finished.connect(self.display_answer)
        self.brain_worker.finished.connect(self.reset_thinking_state)

        self.physics = LumiPhysics(self)
        self.physics.start()
        

    def init_ui(self):

        # Создаем главный вертикальный слой
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addStretch(1)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10) # Расстояние между облачком и Люми

        # 1. ОБЛАЧКО
        self.bubble_label = QLabel("Люми: Привет! Я готова.")
        self.bubble_label.setStyleSheet("""
            color: #00FF00;
            background: rgba(0, 0, 0, 150);
            border: 1px solid #00FF00;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Courier New';
        """)
        self.bubble_label.setWordWrap(True)
        self.bubble_label.setFixedWidth(300)
        self.bubble_label.hide()


        # 2. ПОЛЕ ВВОДА
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Скажи что-нибудь...")
        self.input_field.setStyleSheet("background: rgba(30,30,30,200); color: white; border: 1px solid #444;")
        self.input_field.setFixedWidth(300)
        self.input_field.returnPressed.connect(self.send_message)

        # --- ДОБАВЛЯЕМ КНОПКУ КОПИРОВАНИЯ ---
        self.copy_btn = QPushButton("📋 Копировать ответ")
        self.copy_btn.setFixedWidth(300)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background: rgba(50, 50, 50, 200);
                color: #00FF00;
                border: 1px solid #00FF00;
                border-radius: 5px;
                padding: 5px;
                font-family: 'Courier New';
            }
            QPushButton:hover {
                background: rgba(70, 70, 70, 255);
            }
        """)
        self.copy_btn.clicked.connect(self.copy_answer)


        # Кнопка сканирования экрана
        self.btn_scan = QPushButton("👁️", self)
        self.btn_scan.setFixedSize(35, 35)
        self.btn_scan.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 60, 70, 200);
                color: #00ffcc;
                border: 1px solid #00ffcc;
                border-radius: 17px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(0, 255, 204, 50);
                border: 2px solid #00ffcc;
            }
        """)
        self.btn_scan.setToolTip("Люми посмотрит на твой экран")
        self.btn_scan.clicked.connect(self.manual_look)


        # 3. ЛЮМИ
        self.sprite_label = QLabel()
        self.update_sprite("assets/lumi_idle.png")

        self.main_layout.addWidget(self.bubble_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(self.input_field, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(self.copy_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(self.btn_scan, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(self.sprite_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        

        self.show()
    
    def copy_answer(self):
        # Берем текст из облачка
        text = self.bubble_label.text()
        # Убираем HTML-теги (типа <i>), если они там есть
        clean_text = re.sub(r'<.*?>', '', text)
        
        if clean_text and clean_text != "..." and "Думаю" not in clean_text:
            pyperclip.copy(clean_text)
            self.copy_btn.setText("✅ Скопировано!")
            # Возвращаем текст кнопки через 2 секунды
            QTimer.singleShot(2000, lambda: self.copy_btn.setText("📋 Копировать ответ"))

    def update_sprite(self, path):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        full_path = os.path.join(base_path, path)

        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)
            self.sprite_label.setPixmap(pixmap)
            self.adjustSize()
        else:
            self.sprite_label.setText(f"Ошибка: Люми... А именно {path} не найдена! Поищите в другом месте.")
            self.sprite_label.setStyleSheet("background: red; color: white;")


 # ---------------------------------------------- Создаем мозг и память для нашей Люми ------------------------------------------------------- #

    def process_memory_tags(self, text):
        """Метод обработки памяти"""
        import re
        # Регулярка для поиска тегов [SAVE_...]
        pattern = r"\[SAVE_(\w+)\s*:\s*(.*?)\]"
        tags = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        
        book_map = {
            "USER": "user",
            "RESEARCH": "research",
            "SECRET": "secret"
        }
        
        for b_type_raw, content in tags:
            b_type = b_type_raw.strip().upper()
            target_book = book_map.get(b_type)
            
            if target_book:
                clean_content = content.replace('\n', ' ').strip()
                pairs = clean_content.split(';')
                for pair in pairs:
                    if '=' in pair:
                        k, v = pair.split('=', 1)
                        self.books.save_fact(target_book, k.strip(), v.strip())
                        print(f"✅ Система: {target_book} -> {k.strip()} сохранено!")
                    elif '-' in pair: # На случай если Люми поставит тире
                        k, v = pair.split('-', 1)
                        self.books.save_fact(target_book, k.strip(), v.strip())

        # Удаляем все теги из текста для вывода на экран
        clean_text = re.sub(r"\[SAVE_.*?\]", "", text, flags=re.DOTALL).strip()
        return clean_text if clean_text else "..."
    

    def handle_user_speech(self, text):
        if not text.strip():
            return
            
        print(f"Илья сказал: {text}")
        
        # Меняем текст в облачке на "..." чтобы было видно, что Люми думает
        self.bubble_label.show()
        self.bubble_label.setText("<i>Думаю...</i>")
        
        # Запускаем фоновый запрос
        self.brain_worker.prepare(text)
        self.brain_worker.start()

    def show_lumi_answer(self, answer):
        # Сначала магия сохранения и очистки
        clean_text = self.process_memory_tags(answer)

        # Теперь выводим ТОЛЬКО чистый текст
        self.bubble_label.setText(clean_text)

        self.bubble_label.show()
        self.adjustSize()
        self.is_thinking = False



    def send_message(self):
        text = self.input_field.text()
        if text:
            self.input_field.clear()
            self.bubble_label.setText("<i>Люми думает...</i>")
            self.bubble_label.show()
            # Используем brain_worker
            self.brain_worker.prepare(text)
            self.brain_worker.start()
    
    def display_answer(self, answer):
        """ЕДИНСТВЕННЫЙ метод обработки ответов"""
        
        # 1. Сначала чистим текст и сохраняем факты в JSON
        text_after_memory = self.process_memory_tags(answer)
        
        # 2. Теперь ищем и выполняем системные команды
        import re
        
        # Ищем теги в разных форматах: [EXEC: ...], [exec: ...], [Exec: ...]
        action_pattern = r"\[(?:EXEC|exec|Exec):\s*(.*?)\]"
        
        # Находим список всех программ для запуска
        apps_to_run = re.findall(action_pattern, text_after_memory)
        
        for app in apps_to_run:
            print(f"⚙️ Система: Попытка запуска '{app}'...")
            result = self.actions.run_app(app)
            print(f"Результат запуска: {result}")
            
        # 3. Убираем все варианты тегов EXEC из финального текста
        clean_text = re.sub(r"\[(?:EXEC|exec|Exec):.*?\]", "", text_after_memory).strip()

        # 4. Выводим чистый текст
        self.bubble_label.setText(clean_text)
        self.bubble_label.show()

        print(f"--- [DEBUG v0.5] ---")
        print(f"Оригинал: {answer}")
        print(f"Итог: {clean_text}")

        self.adjustSize()
        self.is_thinking = False

# ---------------------------------------------- Создаем физику для нашей Люми ------------------------------------------------------- #

    # Логика перетаскивания окна по экрану
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.old_pos = event.globalPosition().toPoint() 

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.physics.is_falling = True
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'physics') and not self.physics.is_falling:
            self.physics.force_anchor()

# ---------------------------------------------- Создаем руки для нашей Люми ------------------------------------------------------- #

    def manual_look(self):
        import pyautogui
        import os
        
        path = "lumi_scan.jpg"
        screenshot = pyautogui.screenshot()
        screenshot = screenshot.resize((1024, 576))
        screenshot.convert("RGB").save(path, "JPEG", quality=50)
        
        description = self.brain.get_vision_description(path)
        
        if not description or "Ошибка" in description:
            self.show_lumi_answer("Илья, я пытаюсь открыть глаза, но вокруг всё застлано цифровым туманом...")
            return

        # Модифицированный промпт с инструкцией по сохранению
        surprise_prompt = (
            f"Ты только что открыла глаза и увидела на экране Ильи: {description}. "
            "Это твой новый визуальный опыт. Твоя живая реакция? "
            "\n\nВажно: Обязательно сохрани описание увиденного в свой блокнот, используя формат: "
            "[SAVE_RESEARCH: зрение=активировано; объект_на_экране=краткое описание]"
        )
        
        # Запускаем через brain_worker, который умеет вызывать display_answer
        self.brain_worker.prepare(surprise_prompt)
        self.brain_worker.start()


# ---------------------------------------------- Разговор для нашей Люми ------------------------------------------------------- #

    def on_speech(self, text):
        if self.is_thinking:
            return
        
        if not text.strip():
            return
        
        print(f'Люми услышала голос: {text}')

        self.bubble_label.show()
        self.bubble_label.setText(f'<i>Слушаю: {text}</i>')
        self.adjustSize()

        # Маленький интерактив: если скажешь "замри", 
        # мы можем, например, поменять картинку
        if "привет" in text.lower():
            print("Люми радуется!")
            self.update_sprite("assets/lumi_happy.png")

        self.process_thought(text)


    def process_thought(self, text):
        self.is_thinking = True
        self.bubble_label.setText(f'<i>Думаю... </i>')
        self.adjustSize()

        if hasattr(self, 'physics'):
            QTimer.singleShot(20, self.physics.force_anchor)

        # ИСПРАВЛЕНО: используем существующий brain_worker, а не создаем новый!
        self.brain_worker.prepare(text)
        self.brain_worker.start()
        
    
    def reset_thinking_state(self):
        self.is_thinking = False

        if hasattr(self, 'physics'):
            QTimer.singleShot(20, self.physics.force_anchor)
        print("Система: Люми снова может вас услышать. Говорите")


# ------------------------------------------- Включение/выключение нашей Люми ------------------------------------------------------- #

if __name__ == "__main__":
    app = QApplication(sys.argv)
    brain = LumiBrain()
    # Предположим, у тебя есть объект памяти (books/memory)
    # Если нет отдельного объекта, передай None или создай его
    from memory import LumiMemory 
    memory = LumiMemory()
    lumi = LumiOverlay(brain, memory)
    sys.exit(app.exec())