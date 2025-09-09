import json

#насрал
config_data = {
    "download_folder": "C://Users//hfhtu//Music//music",
    "enabled": True,
    "COOKIE_FILE": "C:/Users/hfhtu/Desktop/Puthon/audio-player/cookies/www.youtube.com_cookies.txt"
}

config_file_name = r"C:\Users\hfhtu\Desktop\Puthon\audio-player\main-git\Config\config.json"

try:
    # Открываем файл для записи ('w' - write)
    with open(config_file_name, 'w', encoding='utf-8') as f:
        # Записываем данные в файл, используя отступы для красоты
        json.dump(config_data, f, indent=4)
    print(f"Конфигурационный файл '{config_file_name}' успешно создан.")
except IOError as e:
    print(f"Ошибка при записи файла: {e}")