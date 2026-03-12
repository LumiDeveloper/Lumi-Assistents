from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QGuiApplication

class LumiPhysics:
    def __init__(self, window):
        self.window = window     # Ссылка на наше окно (overlay)
        self.gravity = 0.8       # ----------------- Сила притяжения
        self.velocity_y = 0      # ----------------- Скорость падения
        self.is_falling = False   # ----------------- Состояние полета
        
        # Настройка таймера
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_physics)
        
    def start(self):
        self.timer.start(33) # ~30 FPS

    def stop(self):
        self.timer.stop()

    def get_floor_y(self):
        # Получаем границы всего экрана
        screen_rest = QGuiApplication.primaryScreen().availableGeometry()
        return screen_rest.bottom() + 2
    
    
    def update_physics(self):
        if getattr(self.window, 'is_dragging', False):
            return

        floor_y = self.get_floor_y()
        curr_pos = self.window.pos()
        window_h = self.window.height()

        target_y = floor_y - window_h

        if self.is_falling:
            self.velocity_y += self.gravity
            new_y = int(curr_pos.y() + self.velocity_y)
            # Проверка на столкновение с панелью задач
            if new_y + window_h >= floor_y:
                new_y = floor_y - window_h
                self.velocity_y = 0
                self.is_falling = False
                # Двигаем окно
            self.window.move(curr_pos.x(), new_y)
        else:
            if abs(curr_pos.y() - target_y) > 1:
                self.window.move(curr_pos.x(), target_y)

    def keep_on_ground(self, floor_y):
        curr_geo = self.window.geometry()
        target_y = floor_y - curr_geo.height()

        if curr_geo.y() != target_y:
            self.window.setGeometry(curr_geo.x(), target_y, curr_geo.width(), curr_geo.height())

    def force_anchor(self):
        self.window.updateGeometry()
        floor_y = self.get_floor_y()
        target_y = floor_y - self.window.height()

        self.window.setGeometry(
            self.window.x(),
            target_y,
            self.window.width(),
            self.window.height()
        )


