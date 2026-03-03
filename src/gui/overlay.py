# --------------------------------- Добавляем конфигурацию для python src/gui/overlay.py ------------------------------------------ #

import sys
import os

# Добавляем родительскую директорию (src) в пути поиска
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import signal
from core.listener import SpeechWorker
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QFrame, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap

# Настройка завершения скрипта по Ctrl+C
signal.signal(signal.SIGINT, signal.SIG_DFL)


# ---------------------------------------------- Создаем кожу для нашей Люми ------------------------------------------------------- #

class LumiOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Создаем объект-слушатель. 
        # device_id — это тот ID от AudioRelay, который ты нашел.
        self.worker = SpeechWorker(device_id=1) 

        # CONNECT: Связываем сигнал из потока с методом в этом классе.
        # Это магия Qt: когда Vosk найдет текст, он "выстрелит" сигналом,
        # и выполнится метод on_speech, получив этот текст.
        self.worker.text_recognized.connect(self.on_speech)

        # START: Запускаем поток. Теперь он живет своей жизнью и не мешает окну.
        self.worker.start()

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Создаем главный вертикальный слой
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10) # Расстояние между облачком и Люми

        # 1. ОБЛАЧКО
        self.bubble = QFrame()
        self.bubble.setStyleSheet("""
            background-color: white;
            border: 2px solid #FFC0CB;
            border-radius: 15px;
            padding: 10px;
        """)
        self.bubble_layout = QVBoxLayout(self.bubble)
        self.text_label = QLabel("...")
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("color: black; font-size: 14px;")
        self.bubble_layout.addWidget(self.text_label)
        
        # Сначала прячем, чтобы не висел пустой квадрат
        self.bubble.hide()

        # 2. ЛЮМИ
        self.label = QLabel()
        self.update_sprite("assets/lumi_idle.png")

        # Добавляем в слой: сначала облачко (сверху), потом Люми (снизу)
        self.main_layout.addWidget(self.bubble, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.show()

    def update_sprite(self, path):
        pixmap = QPixmap(path)
        self.label.setPixmap(pixmap)
        # Убираем жесткий resize окна по картинке, 
        # теперь Layout сам раздвинет окно как надо
        self.adjustSize()

    # Логика перетаскивания окна по экрану
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def on_speech(self, text):
        # Этот метод сработает автоматически, как только ты что-то скажешь
        print(f"Люми услышала: {text}")
        self.text_label.setText(f"Ты сказал: {text}")
        self.bubble.show()
        self.adjustSize()


        # Этот метод сработает автоматически, он убирает облачко через 5 секунд
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(5000, self.bubble.hide)


        # Маленький интерактив: если скажешь "замри", 
        # мы можем, например, поменять картинку
        if "привет" in text.lower():
            print("Люми радуется!")
            self.update_sprite("assets/lumi_happy.png")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    lumi = LumiOverlay()
    sys.exit(app.exec())