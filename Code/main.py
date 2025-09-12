# Компилирование вместе с консолью: pyinstaller --onefile main.py

import os
import sys
import json
import yt_dlp
import subprocess
import pythoncom
import win32com.client

if getattr(sys, 'frozen', False):  
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

config_file_name = os.path.join(ROOT_DIR, "config.json")

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QRadioButton, QLineEdit

class DownloaderUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vinerdowld Downloader")
        self.setFixedSize(500, 300)

        layout = QVBoxLayout()

        # Радиокнопки
        self.video_btn = QRadioButton("Видео")
        self.audio_btn = QRadioButton("Аудио")
        layout.addWidget(self.video_btn)
        layout.addWidget(self.audio_btn)

        # Выбор папки
        self.folder_label = QLabel("Папка для сохранения:")
        self.folder_path = QLineEdit()
        self.folder_btn = QPushButton("Выбрать папку")
        self.folder_btn.clicked.connect(self.choose_folder)

        layout.addWidget(self.folder_label)
        layout.addWidget(self.folder_path)
        layout.addWidget(self.folder_btn)

        # Кнопка запуска
        self.start_btn = QPushButton("⏬ Скачать")
        layout.addWidget(self.start_btn)

        self.setLayout(layout)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if folder:
            self.folder_path.setText(folder)

def load_config():
    """
    Загружает конфигурацию из JSON-файла.
    Если файла нет, спрашивает у пользователя и создает новый.
    """
    default_config = {
        "download_folder": "",
        "cookie_file": "",
        "first_start": True
    }

    # Если файл есть — пробуем загрузить
    try:
        with open(config_file_name, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠ Конфигурационный файл '{config_file_name}' не найден.")
        
        # Спрашиваем у пользователя настройки
        download_folder = input("Введите путь к папке для сохранения скачанных видео: ").strip()
        os.makedirs(download_folder, exist_ok=True)  # создаем папку, если её нет

        cookie_file = input("Введите путь к cookies-файлу (или оставьте пустым, если не нужен): ").strip()

        # Формируем новый конфиг
        config = {
            "download_folder": download_folder,
            "cookie_file": cookie_file,
            "first_start": True
        }

        # Сохраняем в файл
        try:
            with open(config_file_name, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f"✅ Конфиг создан: {config_file_name}")
        except IOError as e:
            print(f"Ошибка при создании файла: {e}")
            return default_config

        return config

    except json.JSONDecodeError:
        print(f"Ошибка: Файл '{config_file_name}' содержит неверный JSON.")
        return default_config

config = load_config()

if config:
    # Присваиваем значения из конфига
    DOWNLOAD_FOLDER = config.get("download_folder")
    COOKIE_FILE = config.get("cookie_file")
    first_start = config.get("first_start")

    
    # Теперь ваши переменные готовы к использованию
    print(f"Папка для загрузок: {DOWNLOAD_FOLDER}")
    print(f"Файл куки: {COOKIE_FILE}")
    print(f"Первый запуск: {first_start}")

else:
    # Если файл не загружен, можно либо выйти из программы, либо использовать значения по умолчанию.
    print("Не удалось загрузить конфигурацию. Программа будет использовать стандартные значения.")
    # Используем стандартные значения, чтобы программа могла работать.
    DOWNLOAD_FOLDER = "C:/Users/hfhtu/Music/music"
    COOKIE_FILE = "C:/Users/hfhtu/Desktop/Puthon/audio-player/cookies/www.youtube.com_cookies.txt"
    first_start = True

DOWNLOAD_FOLDER = "C:/Users/hfhtu/Music/music"
COOKIE_FILE = "C:/Users/hfhtu/Desktop/Puthon/audio-player/cookies/www.youtube.com_cookies.txt"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

first_start = True

def choose_format():
    #Запрос формата
    while True:
        save_format = input("Выберите формат сохранения (mp3/mp4): ").strip().lower()

        if "3" in save_format:  # mp3
            return {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
                "cookiefile": COOKIE_FILE,
                "postprocessors": [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
                ],
            }
        
        elif save_format == "":  # mp4
            return {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
                "cookiefile": COOKIE_FILE,
                "merge_output_format": "mp4",
            }

        elif "4" in save_format:  # mp4
            return {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
                "cookiefile": COOKIE_FILE,
                "merge_output_format": "mp4",
            }

        else:
            print("❌ Неверный формат. Попробуйте ещё раз (mp3/mp4).")


def get_query():
    """Запрашивает у пользователя ссылку или название видео"""
    query = input("Введите ссылку на YouTube или название видео: ").strip()
    if "youtube.com" in query or "youtu.be" in query:
        return query
    else:
        return f"ytsearch1:{query}"


def open_folder():
    """
    Открывает папку и выделяет последний созданный файл.
    Если папка уже открыта, выделяет файл в существующем окне.
    """
    try:
        files = [os.path.join(DOWNLOAD_FOLDER, f) for f in os.listdir(DOWNLOAD_FOLDER)
                 if os.path.isfile(os.path.join(DOWNLOAD_FOLDER, f))]
    except FileNotFoundError:
        print(f"Ошибка: Папка не найдена по пути '{DOWNLOAD_FOLDER}'")
        return

    if not files:
        print("Файлов в папке нет.")
        return

    latest_file = max(files, key=os.path.getctime)
    normalized_path = os.path.normpath(latest_file)

    # Инициализация COM-объектов
    try:
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("Shell.Application")
    except Exception as e:
        print(f"Ошибка инициализации COM: {e}")
        # Если COM не работает, переходим к запасному варианту
        subprocess.Popen(f'explorer /select,"{normalized_path}"', shell=True)
        return

    folder_found = False

    # Проверяем все открытые окна Проводника
    for window in shell.Windows():
        try:
            folder_path = window.Document.Folder.Self.Path
            # Сравниваем пути, игнорируя регистр
            if os.path.normcase(folder_path) == os.path.normcase(DOWNLOAD_FOLDER):
                # Найдено существующее окно с нужной папкой
                folder_found = True
                
                # Попытка выделить файл
                window.Document.SelectItem(normalized_path, 0)
                
                # Если окно было свернуто, разворачиваем его и делаем активным
                window.Visible = True
                window.Top = 0
                
                print(f"Файл успешно выделен в существующем окне: {normalized_path}")
                break
        except Exception:
            
            continue

    if not folder_found:
        
        try:
            subprocess.run(f'explorer /select,"{normalized_path}"', shell=True, check=True)
            print(f"Открыто новое окно и выделен файл: {normalized_path}")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при запуске explorer: {e}")


def main():
    global first_start

    if first_start:
        print("(◕‿◕) Vinerdowld может скачивать видео и клипы с YouTube, в формате mp3 или mp4.")
        print(ROOT_DIR, "пенис")
        first_start = False

    while True:
        ydl_opts = choose_format()
        download_url = get_query()

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"⏳ Начинаю скачивание: {download_url}")
                ydl.download([download_url])
                print(f"✅ Скачивание завершено. Файлы в папке '{DOWNLOAD_FOLDER}' \nОткрываю папку с файлом...")
                open_folder()

        except KeyboardInterrupt:
            print("\n⛔ Загрузка отменена. Возврат в меню...\n")
            continue

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DownloaderUI()
    window.show()
    sys.exit(app.exec_())
    main()
