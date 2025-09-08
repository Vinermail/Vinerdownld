# Компилирование вместе с консолью: pyinstaller --onefile main.py
# TODO: Сделать конфиг с настройками
# Если папка с загруженным видео уже открыта, просто выделять скачанный файл

import os
import yt_dlp
import subprocess

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
    """Открывает папку и выделяет последний созданный файл"""
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
    command = f'explorer /select,"{normalized_path}"'

    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError:
        pass

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
