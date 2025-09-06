#Компилирование вместе с консолью pyinstaller --onefile main.py
import os
import glob
import yt_dlp
import subprocess
import xml.etree.ElementTree as ET

DOWNLOAD_FOLDER = "C:/Users/hfhtu/Music/music"
files = glob.glob(os.path.join(DOWNLOAD_FOLDER, '*'))
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

print("(◕‿◕) Vinerdowld может скачивать видео и клипы с youtube, в формате mp3 или mp4.")

save_format = input("Выберите формат сохранения видео(mp3 or mp4): ").strip()

if save_format == "mp3":
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
        "cookiefile": "C:/Users/hfhtu/Desktop/Puthon/audio-player/cookies/www.youtube.com_cookies.txt",
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
        ],
    }
elif save_format == "mp4":
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
        "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
        "cookiefile": "C:/Users/hfhtu/Desktop/Puthon/audio-player/cookies/www.youtube.com_cookies.txt",
        "merge_output_format": "mp4",
    }
else:
    print("Выбран неправильный формат")
    exit()

query = input("Введите ссылку на YouTube или название трека: ").strip()

def open_folder():
    """
    Открывает папку и выделяет в ней последний созданный файл.
    """
    
    # Получаем список файлов в папке
    try:
        files = [os.path.join(DOWNLOAD_FOLDER, f) for f in os.listdir(DOWNLOAD_FOLDER) if os.path.isfile(os.path.join(DOWNLOAD_FOLDER, f))]
    except FileNotFoundError:
        print(f"Ошибка: Папка не найдена по пути '{DOWNLOAD_FOLDER}'")
        return

    if not files:
        print("Файлов в папке нет.")
        return

    # Находим файл с самой последней датой создания (getctime)
    latest_file = max(files, key=os.path.getctime)

    # Нормализация пути к файлу
    normalized_path = os.path.normpath(latest_file)

    # Формирование команды для explorer'a 
    command = f'explorer /select,"{normalized_path}"'
    
    # Запускаем команду
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError:
        pass


if "youtube.com" in query or "youtu.be" in query:
    download_url = query
else:
    download_url = f"ytsearch1:{query}"

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    print(f"⏳ Начинаю скачивание: {download_url}")
    ydl.download([download_url])
    print(f"✅ Скачивание завершено. Файлы в папке '{DOWNLOAD_FOLDER}'")
    open_folder()

