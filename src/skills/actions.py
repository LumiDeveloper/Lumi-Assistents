import os
import subprocess
import shutil

class LumiActions:
    def __init__(self):
        # Список сокращений для удобства
        self.aliases = {
            "калькулятор": "calc",
            "ms-calculator": "calc",
            "блокнот": "notepad",
            "браузер": "start firefox",
            "код": "code"
        }

    def run_app(self, app_name):
        app_name = app_name.lower().strip()
        
        # Расширяем алиасы для вредной Windows
        aliases = {
            "firefox": "start firefox",
            "браузер": "start firefox",
            "калькулятор": "calc",
            "calc": "calc",
            "notepad": "notepad",
            "блокнот": "notepad"
        }
        
        target = aliases.get(app_name, app_name)
        
        # Если в команде нет 'start' и это не системный calc/notepad, 
        # добавим 'start' для подстраховки
        if " " not in target and target not in ["calc", "notepad"]:
            command = f"start {target}"
        else:
            command = target

        try:
            import subprocess
            # shell=True обязателен для работы команды 'start'
            subprocess.Popen(command, shell=True)
            return f"Выполнено: {command}"
        except Exception as e:
            print(f"Ошибка OS: {e}")
            return f"Ошибка: {e}"