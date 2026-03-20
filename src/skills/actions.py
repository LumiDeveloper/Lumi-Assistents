import os
import subprocess
import shutil
import sys

class LumiActions:
    def __init__(self):
        # Единый словарь алиасов
        self.aliases = {
            # Русские названия
            "калькулятор": "calc",
            "кальк": "calc",
            "блокнот": "notepad",
            "блокнотик": "notepad",
            "браузер": "firefox",
            "интернет": "firefox",
            "код": "code",
            "редактор кода": "code",
            "проводник": "explorer",
            "папки": "explorer",
            "корзина": "recycle_bin",  # Специальная команда
            "мусорка": "recycle_bin",
            "ютуб": "youtube",  # Будет открывать YouTube в браузере
            "ютюб": "youtube",
            "ютьюб": "youtube",
            "youtube": "youtube",
            
            # Мультимедиа и видео
            "vlc": "vlc",
            "вилси": "vlc",
            "виэлси": "vlc",
            "obs": "obs",
            "obs studio": "obs",
            "обс": "obs",
            "обс студио": "obs",
            
            # Игры
            "геншин": "genshin",
            "геншин импакт": "genshin",
            "genshin": "genshin",
            "genshin impact": "genshin",
            "steam": "steam",
            "стим": "steam",
            "стим": "steam",
            "hoyoplay": "hoyoplay",
            "хоёплей": "hoyoplay",
            "хоё плэй": "hoyoplay",
            
            # Торренты
            "qbittorrent": "qbittorrent",
            "кьюбитторрент": "qbittorrent",
            "кюбит": "qbittorrent",
            "торрент": "qbittorrent",
            "битторрент": "qbittorrent",
            "qbit": "qbittorrent",
            
            # Файловые менеджеры
            "total commander": "totalcmd",
            "totalcmd": "totalcmd",
            "тотал командер": "totalcmd",
            "тотал": "totalcmd",
            "коммандер": "totalcmd",
            "фар": "far",
            "far manager": "far",
            
            # Графика и редакторы
            "fl studio": "flstudio",
            "fl": "flstudio",
            "фл студио": "flstudio",
            "фл": "flstudio",
            "fl studio 2024": "flstudio",
            "faststone": "faststone",
            "фастстоун": "faststone",
            "faststone image viewer": "faststone",
            "просмотрщик картинок": "faststone",
            "просмотр фото": "faststone",
            
            # Английские/системные названия
            "calc": "calc",
            "calculator": "calc",
            "notepad": "notepad",
            "firefox": "firefox",
            "chrome": "chrome",
            "google chrome": "chrome",
            "opera": "opera",
            "yandex": "yandex",
            "яндекс": "yandex",
            "edge": "edge",
            "microsoft edge": "edge",
            "code": "code",
            "vscode": "code",
            "visual studio code": "code",
            "explorer": "explorer",
            "cmd": "cmd",
            "command prompt": "cmd",
            "powershell": "powershell",
        }
        
        # Кэш для найденных программ
        self.program_cache = {}
        
        # Специальные URL для открытия в браузере
        self.urls = {
            "youtube": "https://youtube.com",
            "ютуб": "https://youtube.com",
            "ютюб": "https://youtube.com",
            "ютьюб": "https://youtube.com",
        }

    def find_program(self, program_name):
        """Ищет исполняемый файл программы в системе"""
        if program_name in self.program_cache:
            return self.program_cache[program_name]
        
        # Специальные случаи для системных программ Windows
        system_programs = {
            "calc": "calc.exe",
            "notepad": "notepad.exe",
            "explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
        }
        
        if program_name in system_programs:
            # Эти программы есть в system32
            system32 = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32')
            full_path = os.path.join(system32, system_programs[program_name])
            if os.path.exists(full_path):
                self.program_cache[program_name] = full_path
                return full_path
        
        # Поиск через where/which
        try:
            if sys.platform == "win32":
                result = subprocess.run(['where', program_name], 
                                      capture_output=True, text=True, timeout=2)
            else:
                result = subprocess.run(['which', program_name], 
                                      capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                path = result.stdout.strip().split('\n')[0]
                self.program_cache[program_name] = path
                return path
        except:
            pass
        
        # Проверка стандартных путей для популярных программ
        common_paths = {
            "firefox": [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            ],
            "chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ],
            "opera": [
                r"C:\Program Files\Opera\launcher.exe",
                r"C:\Program Files (x86)\Opera\launcher.exe",
            ],
            "yandex": [
                r"C:\Users\%USERNAME%\AppData\Local\Yandex\YandexBrowser\Application\browser.exe",
                r"C:\Program Files (x86)\Yandex\YandexBrowser\Application\browser.exe",
            ],
            "edge": [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            ],
            "code": [
                r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
                r"C:\Program Files\Microsoft VS Code\Code.exe",
                r"D:\programms\Microsoft VS Code\Code.exe",
            ],
            "vlc": [
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
            ],
            "obs": [
                r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
                r"C:\Program Files (x86)\obs-studio\bin\64bit\obs64.exe",
                r"D:\programms\obs-studio\bin\64bit\obs64.exe",
            ],
            "steam": [
                r"C:\Program Files (x86)\Steam\Steam.exe",
                r"D:\programms\Steam\Steam.exe",
            ],
            "genshin": [
                r"C:\Program Files\Genshin Impact\launcher.exe",
                r"C:\Program Files (x86)\Genshin Impact\launcher.exe",
                r"C:\Users\%USERNAME%\AppData\Local\Programs\Genshin Impact\launcher.exe",
                r"D:\Games\Genshin Impact game\GenshinImpact.exe"
            ],
            "hoyoplay": [
                r"C:\Program Files\HoYoPlay\launcher.exe",
                r"C:\Program Files (x86)\HoYoPlay\launcher.exe",
                r"C:\Users\%USERNAME%\AppData\Local\Programs\HoYoPlay\launcher.exe",
                r"D:\HoYoPlay\launcher.exe"
            ],
            "qbittorrent": [
                r"C:\Program Files\qBittorrent\qbittorrent.exe",
                r"C:\Program Files (x86)\qBittorrent\qbittorrent.exe",
            ],
            "totalcmd": [
                r"C:\totalcmd\TOTALCMD64.EXE",
                r"C:\Program Files\totalcmd\TOTALCMD64.EXE",
                r"C:\Program Files (x86)\totalcmd\TOTALCMD64.EXE",
            ],
            "flstudio": [
                r"C:\Program Files\Image-Line\FL Studio 2024\FL64.exe",
                r"C:\Program Files\Image-Line\FL Studio 20\FL64.exe",
                r"C:\Program Files (x86)\Image-Line\FL Studio 20\FL64.exe",
            ],
            "faststone": [
                r"C:\Program Files\FastStone Image Viewer\FSViewer.exe",
                r"C:\Program Files (x86)\FastStone Image Viewer\FSViewer.exe",
                r"D:\programms\FastStone Image Viewer\FSViewer.exe"
            ],
        }
        
        if program_name in common_paths:
            for path_template in common_paths[program_name]:
                path = path_template.replace('%USERNAME%', os.environ.get('USERNAME', ''))
                if os.path.exists(path):
                    self.program_cache[program_name] = path
                    return path
        
        return None

    def run_app(self, app_name):
        """Запускает приложение по имени"""
        if not app_name:
            return "Не указано имя программы"
        
        app_name = app_name.lower().strip()
        
        # Проверяем специальные URL
        if app_name in self.urls:
            url = self.urls[app_name]
            try:
                import webbrowser
                webbrowser.open(url)
                return f"Открываю {original_name if 'original_name' in locals() else app_name} в браузере"
            except Exception as e:
                return f"Не могу открыть браузер: {e}"
        
        # Проверка на корзину (специальная команда)
        if app_name == "recycle_bin":
            try:
                # Открываем корзину через explorer
                os.startfile("shell:RecycleBinFolder")
                return "Открываю корзину"
            except Exception as e:
                return f"Не могу открыть корзину: {e}"
        
        # Сохраняем оригинальное имя для вывода
        original_name = app_name
        
        # Проверяем алиасы
        app_name = self.aliases.get(app_name, app_name)
        
        if original_name != app_name:
            print(f"Система: Алиас '{original_name}' -> '{app_name}'")
        
        try:
            # Специальная обработка для OBS Studio
            if app_name == "obs":
                # Ищем путь к OBS
                program_path = self.find_program("obs")
                if program_path:
                    # Получаем директорию OBS
                    obs_dir = os.path.dirname(os.path.dirname(program_path))  # Поднимаемся на уровень выше
                    # Проверяем, есть ли папка data/locale
                    locale_dir = os.path.join(obs_dir, "data", "obs-studio", "locale")
                    if os.path.exists(locale_dir):
                        # Запускаем из правильной директории
                        print(f"Система: Запуск OBS из {obs_dir}")
                        subprocess.Popen([program_path], cwd=obs_dir, shell=False)
                        return f"Запускаю OBS Studio"
                    else:
                        # Пробуем другой вариант структуры папок
                        obs_bin_dir = os.path.dirname(program_path)
                        obs_root = os.path.dirname(obs_bin_dir)
                        locale_dir = os.path.join(obs_root, "data", "locale")
                        if os.path.exists(locale_dir):
                            subprocess.Popen([program_path], cwd=obs_root, shell=False)
                            return f"Запускаю OBS Studio"
                        else:
                            # Если не нашли локаль, пробуем с переменной окружения
                            env = os.environ.copy()
                            env['OBS_DATA_PATH'] = os.path.join(obs_dir, "data")
                            subprocess.Popen([program_path], env=env, shell=False)
                            return f"Запускаю OBS Studio (с переменными окружения)"
                else:
                    return "Не могу найти OBS Studio. Проверь, установлен ли он в C:\\Program Files\\obs-studio\\"
            
            # Специальная обработка для cmd и powershell
            elif app_name in ["cmd", "powershell"]:
                subprocess.Popen(app_name, shell=True)
                return f"Запускаю {original_name}"
            
            # Для всех остальных программ
            else:
                # Ищем программу
                program_path = self.find_program(app_name)
                
                if program_path:
                    # Запускаем найденную программу
                    subprocess.Popen([program_path], shell=False)
                    print(f"Система: Запущен {app_name} по пути {program_path}")
                    return f"Запускаю {original_name if original_name != app_name else app_name}"
                else:
                    # Если не нашли, пробуем через start (Windows)
                    if sys.platform == "win32":
                        try:
                            subprocess.Popen(f"start {app_name}", shell=True)
                            print(f"Система: Попытка запуска через start {app_name}")
                            return f"Пробую запустить {original_name}..."
                        except:
                            pass
                    
                    # Последняя попытка - просто по имени
                    try:
                        subprocess.Popen(app_name, shell=True)
                        print(f"Система: Прямой запуск {app_name}")
                        return f"Пытаюсь запустить {original_name}..."
                    except Exception as e:
                        return f"Не могу найти программу '{original_name}'. Попробуй указать полный путь или установи её."
                        
        except Exception as e:
            print(f"Система: Ошибка запуска: {e}")
            return f"Ошибка при запуске: {str(e)}"

    def get_available_programs(self):
        """Возвращает список доступных программ (для автодополнения)"""
        return list(self.aliases.keys())