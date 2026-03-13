# --------------------------------- Добавляем конфигурацию для python src/gui/overlay.py ------------------------------------------ #

import sys
import os

# Добавляем родительскую директорию (src) в пути поиска
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import signal
from core.listener import SpeechWorker
from PyQt6.QtWidgets import QApplication, QLayout, QWidget, QVBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap

from core.brain import BrainWorker, LumiBrain
from core.physics import LumiPhysics


# Настройка завершения скрипта по Ctrl+C
signal.signal(signal.SIGINT, signal.SIG_DFL)


# ---------------------------------------------- Создаем кожу для нашей Люми ------------------------------------------------------- #

class LumiWorker(QThread):
    result_received = pyqtSignal(str)

    def __init__(self, brain, text):
        super().__init__()
        self.brain = brain
        self.text = text

    def run(self):
        answer = self.brain.ask(self.text)
        self.result_received.emit(answer)


class LumiOverlay(QWidget):
    def __init__(self, brain=None):
        super().__init__()

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

        self.brain_worker = BrainWorker(self.brain)
        self.brain_worker.finished.connect(self.show_lumi_answer)

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


        # 3. ЛЮМИ
        self.sprite_label = QLabel()
        self.update_sprite("assets/lumi_idle.png")

        self.main_layout.addWidget(self.bubble_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(self.input_field, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(self.sprite_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        

        self.show()

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



    def send_message(self):
        text = self.input_field.text()
        if text:
            # old_bottom = self.geometry().bottom()
            # self.move(self.x(), self.y() - 500)

            self.input_field.clear()
            self.bubble_label.setText("<i>Люми думает...</i>")
            self.bubble_label.show()

            self.worker = LumiWorker(self.brain, text)
            self.worker.result_received.connect(self.display_answer)
            self.worker.start()
    
    def display_answer(self, answer):
        self.bubble_label.setText(f"Люми: {answer}")
        self.adjustSize()

        self.is_thinking = False

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

# ---------------------------------------------- Создаем мозг для нашей Люми ------------------------------------------------------- #

    def handle_user_speech(self, text):
        if not text.strip():
            return
            
        print(f"Илья сказал: {text}")
        
        # Меняем текст в облачке на "..." чтобы было видно, что Люми думает
        self.bubble_label.show()
        self.bubble_label.setText("<i>Думаю...</i>")
        
        # Запускаем фоновый запрос к GigaChat
        self.brain_worker.prepare(text)
        self.brain_worker.start()

    def show_lumi_answer(self, answer):
        print(f"Люми ответила: {answer}")
        self.bubble_label.setText(answer)
        self.bubble_label.show()
        self.adjustSize()
        self.is_thinking = False
        # Здесь в будущем мы будем менять спрайт Люми на радостный/грустный


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

        self.worker = LumiWorker(self.brain, text)
        self.worker.result_received.connect(self.display_answer)
        self.worker.finished.connect(self.reset_thinking_state)
        self.worker.start()
        
    
    def reset_thinking_state(self):
        self.is_thinking = False

        if hasattr(self, 'physics'):
            QTimer.singleShot(20, self.physics.force_anchor)
        print("Система: Люми снова может вас услышать. Говорите")


# ------------------------------------------- Включение/выключение нашей Люми ------------------------------------------------------- #

if __name__ == "__main__":
    app = QApplication(sys.argv)
    lumi = LumiOverlay()
    sys.exit(app.exec())