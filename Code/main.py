# Компилирование вместе с консолью: pyinstaller --onefile main.py
# TODO: Сделать конфиг с настройками
# Если папка с загруженным видео уже открыта, просто выделять скачанный файл

import os
import yt_dlp
import subprocess
import pythoncom
import win32com.client

DOWNLOAD_FOLDER = "C:/Users/hfhtu/Music/music"
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
                "cookiefile": "C:/Users/hfhtu/Desktop/Puthon/audio-player/cookies/www.youtube.com_cookies.txt",
                "postprocessors": [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
                ],
            }

        elif "4" in save_format:  # mp4
            return {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
                "cookiefile": "C:/Users/hfhtu/Desktop/Puthon/audio-player/cookies/www.youtube.com_cookies.txt",
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
            # Игнорируем ошибки, если окно не является папкой (например, "Этот компьютер")
            continue

    if not folder_found:
        # Если папка не была найдена, открываем новое окно
        try:
            subprocess.run(f'explorer /select,"{normalized_path}"', shell=True, check=True)
            print(f"Открыто новое окно и выделен файл: {normalized_path}")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при запуске explorer: {e}")


def main():
    global first_start
    if first_start:
        print("(◕‿◕) Vinerdowld может скачивать видео и клипы с YouTube, в формате mp3 или mp4.")
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
    main()
