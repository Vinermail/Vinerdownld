import sys
import os
import json
import yt_dlp
import subprocess
import pythoncom
import win32com.client
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QFileDialog, QRadioButton, 
    QTextEdit, QProgressBar, QMessageBox, QGroupBox, QButtonGroup
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont, QIcon

if getattr(sys, 'frozen', False):  
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

config_file_name = os.path.join(ROOT_DIR, "config.json")


class DownloadWorker(QThread):
    """Поток для скачивания, чтобы не блокировать GUI"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, ydl_opts, download_url):
        super().__init__()
        self.ydl_opts = ydl_opts
        self.download_url = download_url

    def run(self):
        try:
            self.progress.emit(f"⏳ Начинаю скачивание: {self.download_url}")
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([self.download_url])
            
            self.finished.emit("✅ Скачивание завершено!")
            
        except Exception as e:
            self.error.emit(f"❌ Ошибка скачивания: {str(e)}")


class YouTubeDownloaderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.download_folder = self.config.get("download_folder", "")
        self.cookie_file = self.config.get("cookie_file", "")
        self.worker = None
        
        self.init_ui()
        self.setup_first_start()

    def load_config(self):
        """Загружает конфигурацию из JSON-файла"""
        default_config = {
            "download_folder": "",
            "cookie_file": "",
            "first_start": True
        }

        try:
            with open(config_file_name, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default_config

    def save_config(self):
        """Сохраняет текущую конфигурацию"""
        config = {
            "download_folder": self.download_folder,
            "cookie_file": self.cookie_file,
            "first_start": False
        }
        
        try:
            with open(config_file_name, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить конфиг: {e}")

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("Vinerdowld")
        self.setGeometry(100, 100, 600, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: Arial;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #555;
                border-radius: 5px;
                background-color: #404040;
                font-size: 12px;
            }
            QPushButton {
                padding: 10px;
                background-color: #4CAF50;
                border: none;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QRadioButton {
                font-size: 12px;
                padding: 5px;
            }
            QTextEdit {
                border: 2px solid #555;
                border-radius: 5px;
                background-color: #404040;
                font-family: Consolas;
                font-size: 11px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin: 10px 0;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        # Основной layout
        main_layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("YouTube Downloader")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Группа настроек
        settings_group = QGroupBox("Настройки")
        settings_layout = QVBoxLayout()

        # Выбор папки скачивания
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Папка загрузок:"))
        self.folder_input = QLineEdit(self.download_folder)
        self.folder_input.setPlaceholderText("Выберите папку для сохранения файлов...")
        folder_layout.addWidget(self.folder_input)
        
        self.folder_btn = QPushButton("Обзор")
        self.folder_btn.clicked.connect(self.choose_download_folder)
        folder_layout.addWidget(self.folder_btn)
        
        settings_layout.addLayout(folder_layout)

        # Файл cookies
        cookie_layout = QHBoxLayout()
        cookie_layout.addWidget(QLabel("Файл cookies:"))
        self.cookie_input = QLineEdit(self.cookie_file)
        self.cookie_input.setPlaceholderText("Необязательно - для доступа к приватным видео...")
        cookie_layout.addWidget(self.cookie_input)
        
        self.cookie_btn = QPushButton("Обзор")
        self.cookie_btn.clicked.connect(self.choose_cookie_file)
        cookie_layout.addWidget(self.cookie_btn)
        
        settings_layout.addLayout(cookie_layout)
        
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # Группа загрузки
        download_group = QGroupBox("Скачивание")
        download_layout = QVBoxLayout()

        # Поле ввода URL или названия
        url_layout = QVBoxLayout()
        url_layout.addWidget(QLabel("YouTube ссылка или название видео:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Введите ссылку на YouTube или название видео...")
        url_layout.addWidget(self.url_input)
        download_layout.addLayout(url_layout)

        # Выбор формата
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Формат:"))
        
        self.format_group = QButtonGroup()
        self.mp3_radio = QRadioButton("MP3 (только аудио)")
        self.mp4_radio = QRadioButton("MP4 (видео)")
        self.mp4_radio.setChecked(True)  # По умолчанию MP4
        
        self.format_group.addButton(self.mp3_radio, 0)
        self.format_group.addButton(self.mp4_radio, 1)
        
        format_layout.addWidget(self.mp3_radio)
        format_layout.addWidget(self.mp4_radio)
        format_layout.addStretch()
        
        download_layout.addLayout(format_layout)

        # Кнопки
        button_layout = QHBoxLayout()
        
        self.download_btn = QPushButton("📥 Скачать")
        self.download_btn.clicked.connect(self.start_download)
        button_layout.addWidget(self.download_btn)
        
        self.open_folder_btn = QPushButton("📁 Открыть папку")
        self.open_folder_btn.clicked.connect(self.open_folder)
        button_layout.addWidget(self.open_folder_btn)
        
        download_layout.addLayout(button_layout)
        
        download_group.setLayout(download_layout)
        main_layout.addWidget(download_group)

        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Лог
        log_layout = QVBoxLayout()
        log_layout.addWidget(QLabel("Журнал событий:"))
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        main_layout.addLayout(log_layout)

        self.setLayout(main_layout)

    def setup_first_start(self):
        """Настройка при первом запуске"""
        if self.config.get("first_start", True):
            self.log("(◕‿◕) Добро пожаловать в Vinerdowld!")
            self.log("Приложение может скачивать видео и клипы с YouTube в формате MP3 или MP4.")
            
            if not self.download_folder:
                QMessageBox.information(
                    self, 
                    "Первый запуск", 
                    "Добро пожаловать в Vinerdowld!\n\nПожалуйста, выберите папку для сохранения скачанных файлов."
                )
                self.choose_download_folder()

    def log(self, message):
        """Добавляет сообщение в лог"""
        self.log_text.append(message)
        self.log_text.ensureCursorVisible()

    def choose_download_folder(self):
        """Выбор папки для загрузок"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Выберите папку для загрузок",
            self.download_folder or os.path.expanduser("~/Downloads")
        )
        
        if folder:
            self.download_folder = folder
            self.folder_input.setText(folder)
            os.makedirs(folder, exist_ok=True)
            self.save_config()
            self.log(f"📁 Папка загрузок установлена: {folder}")

    def choose_cookie_file(self):
        """Выбор файла cookies"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите файл cookies",
            self.cookie_file or "",
            "Text files (*.txt);;All files (*.*)"
        )
        
        if file_path:
            self.cookie_file = file_path
            self.cookie_input.setText(file_path)
            self.save_config()
            self.log(f"🍪 Файл cookies установлен: {file_path}")

    def get_ydl_options(self):
        """Получает опции для yt-dlp в зависимости от выбранного формата"""
        if not self.download_folder:
            raise ValueError("Не выбрана папка для загрузок!")

        base_opts = {
            "outtmpl": os.path.join(self.download_folder, "%(title)s.%(ext)s"),
        }

        # Добавляем cookies если указан файл
        if self.cookie_file and os.path.exists(self.cookie_file):
            base_opts["cookiefile"] = self.cookie_file

        if self.mp3_radio.isChecked():
            # MP3 формат
            base_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
                ],
            })
        else:
            # MP4 формат
            base_opts.update({
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                "merge_output_format": "mp4",
            })

        return base_opts

    def get_download_url(self, query):
        """Обрабатывает введенный запрос"""
        query = query.strip()
        if "youtube.com" in query or "youtu.be" in query:
            return query
        else:
            return f"ytsearch1:{query}"

    def start_download(self):
        """Запускает процесс загрузки"""
        if not self.url_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите ссылку или название видео!")
            return

        if not self.download_folder:
            QMessageBox.warning(self, "Ошибка", "Выберите папку для загрузок!")
            return

        try:
            ydl_opts = self.get_ydl_options()
            download_url = self.get_download_url(self.url_input.text())

            # Отключаем кнопку и показываем прогресс
            self.download_btn.setText("⏳ Скачивание...")
            self.download_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Бесконечный прогресс

            # Создаем и запускаем поток загрузки
            self.worker = DownloadWorker(ydl_opts, download_url)
            self.worker.progress.connect(self.log)
            self.worker.finished.connect(self.download_finished)
            self.worker.error.connect(self.download_error)
            self.worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при настройке загрузки: {e}")
            self.reset_download_button()

    def download_finished(self, message):
        """Обработка успешного завершения загрузки"""
        self.log(message)
        self.log(f"📁 Файлы сохранены в: {self.download_folder}")
        self.reset_download_button()
        
        # Автоматически открываем папку
        self.open_folder()

    def download_error(self, error_message):
        """Обработка ошибки загрузки"""
        self.log(error_message)
        QMessageBox.critical(self, "Ошибка загрузки", error_message)
        self.reset_download_button()

    def reset_download_button(self):
        """Восстанавливает состояние кнопки загрузки"""
        self.download_btn.setText("📥 Скачать")
        self.download_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def open_folder(self):
        """Открывает папку с загрузками и выделяет последний файл"""
        if not self.download_folder or not os.path.exists(self.download_folder):
            QMessageBox.warning(self, "Ошибка", "Папка загрузок не найдена!")
            return

        try:
            files = [os.path.join(self.download_folder, f) 
                    for f in os.listdir(self.download_folder)
                    if os.path.isfile(os.path.join(self.download_folder, f))]

            folder_path = os.path.normpath(self.download_folder)

            if not files:
                # Папка пустая - просто открываем её
                self.log("📁 Открываю пустую папку загрузок...")
                os.startfile(folder_path)
                return

            # Есть файлы - пробуем выделить последний
            latest_file = max(files, key=os.path.getctime)
            normalized_path = os.path.normpath(latest_file)
            
            # Пробуем выделить файл, если не получается - открываем просто папку
            try:
                subprocess.run(['explorer', '/select,', normalized_path], check=True, timeout=3)
                self.log(f"📁 Файл выделен: {os.path.basename(latest_file)}")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                # Если команда не сработала, открываем обычную папку
                self.log("📁 Папка не найдена")

        except Exception as e:
            # В случае любой ошибки просто открываем папку
            try:
                os.startfile(self.download_folder)
                self.log("📁 Папка не найдена")
            except Exception as e2:
                self.log(f"❌ Не удалось открыть папку: {e2}")

    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        # Останавливаем поток загрузки если он запущен
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        self.save_config()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    app.setWindowIcon(QIcon("icon.ico"))
    
    downloader = YouTubeDownloaderGUI()
    downloader.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()