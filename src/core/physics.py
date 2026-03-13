from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QGuiApplication
import pywinctl as pwc

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
        default_floor = screen_rest.bottom() + 2

        char_x_center = self.window.x() + self.window.width() // 2
        char_feet_y = self.window.y() + self.window.height()

        try:
            all_windows = pwc.getAllWindows()
            potential_floors = [default_floor]

            for win in all_windows:
                if not win.title or "Lumi" in win.title or not win.isVisible or win.isMinimized:
                    continue
                if win.left - 20 <= char_x_center <= win.right + 20:
                    if win.top >= char_feet_y - 10:
                        potential_floors.append(win.top)
            return min(potential_floors)
        except Exception:
            return default_floor
        
    
    def smooth_velocity(self):
        if not self.is_falling:
            return 0
        
        self.velocity_y += self.gravity * 0.4

        if self.velocity_y > 40:
            self.velocity_y = 40

        return self.velocity_y
    
    def update_physics(self):
        if getattr(self.window, 'is_dragging', False):
            return

        floor_y = self.get_floor_y()
        curr_pos = self.window.pos()
        window_h = self.window.height()
        target_y = floor_y - window_h

        diff_y = curr_pos.y() - target_y

        if self.is_falling:
            vel = self.smooth_velocity()
            new_y =int(curr_pos.y() + vel)

            # Проверка на столкновение с панелью задач
            if new_y + window_h >= floor_y:
                new_y = floor_y - window_h
                self.velocity_y = 0
                self.is_falling = False
                # Двигаем окно
            self.window.move(curr_pos.x(), new_y)
        else:
            if 0 < abs(diff_y) <= 15:
                self.window.move(curr_pos.x(), target_y)
            elif diff_y < -15:
                self.is_falling = True

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


