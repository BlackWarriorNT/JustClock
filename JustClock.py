import configparser
import customtkinter as ctk
from datetime import datetime, timedelta
import time
import threading
import pygame
import os
import sys

# Определение пути к папке с приложением
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# Путь к папке sounds
sounds_path = os.path.join(application_path, "sounds")

# Инициализация pygame
pygame.mixer.init()

### Блок с важными переменными
# Настройки положения
clock_position = "bottom_right"  # Варианты: "center", "top_left", "bottom_left", "top_right", "bottom_right"

# Настройки шрифта
font_name = "Tahoma"  # Варианты: "Tahoma", "Helvetica", "Terminal", "Calibri", "Arial", "Segoe UI"
font_style = "bold"  # Варианты: "normal", "italic", "bold"
font_size = 18
font_color = "#D4D4D4"
paper_color = "#1E1E1E"

# Настройки полоски секунд
seconds_bar_show = True  # Отображать полоску секунд (true или false)
seconds_bar_height = 4  # Высота полоски секунд в пикселях
seconds_bar_color = "#4C72AF"  # Цвет полоски

# Настройки воспроизведения MP3
playback_start = "06:00"  # Начало промежутка воспроизведения (часы)
playback_end = "23:00"  # Конец промежутка воспроизведения (часы)

# Настройки воспроизведения chime.mp3
chime_on_start = True  # Разрешение воспроизведения файла chime.mp3 при запуске программы
chime_before_hour = True  # Разрешение воспроизведения файла chime.mp3 перед воспроизведением mp3-файла с номером часа

# Настройки размера окна
window_width_percentage = 1.05  # Ширина окна на 5% больше размера шрифта
window_height_percentage = 1.05  # Высота окна на 5% больше размера шрифта

# Глобальная переменная для отслеживания состояния воспроизведения звука
is_playing = False
last_chime_played = None

def update_time():
    global last_chime_played
    last_second = -1
    last_hour = -1
    while True:
        current_time = datetime.now()
        current_second = current_time.second
        current_hour = current_time.hour

        if current_second != last_second:
            time_label.configure(text=current_time.strftime("%H:%M:%S"))

            if seconds_bar_show:
                bar_width = int((current_second / 59) * window_width)
                seconds_bar.configure(width=bar_width)

            last_second = current_second

        if current_hour != last_hour and is_within_playback_range(current_time):
            play_sound(current_hour)
            last_hour = current_hour

        # Переустановка флага -topmost
        root.attributes("-topmost", True)

        root.update()
        time.sleep(0.25)  # Небольшая задержка для снижения нагрузки на CPU

def on_double_click(event):
    root.destroy()

def play_sound(hour):
    global is_playing, last_chime_played
    current_time = datetime.now()
    if current_time.minute == 0 and current_time.second == 0:
        if chime_before_hour and last_chime_played != hour:
            play_chime()
            last_chime_played = hour
        sound_file = os.path.join(sounds_path, f"{hour:02}.mp3")
        if os.path.exists(sound_file):
            while is_playing:
                time.sleep(0.1)  # Ожидание завершения текущего воспроизведения
            is_playing = True
            sound_thread = threading.Thread(target=play_mp3, args=(sound_file,))
            sound_thread.start()

def play_chime():
    global is_playing
    chime_file = os.path.join(sounds_path, "chime.mp3")
    if os.path.exists(chime_file):
        while is_playing:
            time.sleep(0.1)  # Ожидание завершения текущего воспроизведения
        is_playing = True
        sound_thread = threading.Thread(target=play_mp3, args=(chime_file,))
        sound_thread.start()

def play_mp3(file_path):
    global is_playing
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except pygame.error as e:
        print(f"Error playing sound: {e}")
        print(f"Attempted to play file: {file_path}")
    finally:
        is_playing = False

def is_within_playback_range(current_time):
    start_hour, start_minute = map(int, playback_start.split(":"))
    end_hour, end_minute = map(int, playback_end.split(":"))
    current_hour = current_time.hour
    current_minute = current_time.minute

    start_time = datetime.now().replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
    end_time = datetime.now().replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)

    if end_time < start_time:
        end_time += timedelta(days=1)

    return start_time <= current_time <= end_time

def read_config():
    config = configparser.ConfigParser()
    config_file = os.path.join(application_path, "JustClock.ini")
    if not os.path.exists(config_file):
        create_default_config(config_file)
    config.read(config_file)
    return config

def create_default_config(config_file):
    config = configparser.ConfigParser()
    config["General"] = {
        "clock_position": "bottom_right",
        "font_name": "Tahoma",
        "font_style": "bold",
        "font_size": 18,
        "font_color": "#D4D4D4",
        "paper_color": "#1E1E1E",
        "seconds_bar_show": True,
        "seconds_bar_height": 4,
        "seconds_bar_color": "#4C72AF",
        "playback_start": "06:00",
        "playback_end": "23:00",
        "chime_on_start": True,
        "chime_before_hour": True,
    }
    with open(config_file, "w") as f:
        config.write(f)

# Чтение настроек из файла
config = read_config()

# Применение настроек из файла
clock_position = config["General"]["clock_position"]
font_name = config["General"]["font_name"]
font_style = config["General"]["font_style"]
font_size = int(config["General"]["font_size"])
font_color = config["General"]["font_color"]
paper_color = config["General"]["paper_color"]
seconds_bar_show = config.getboolean("General", "seconds_bar_show")
seconds_bar_height = int(config["General"]["seconds_bar_height"])
seconds_bar_color = config["General"]["seconds_bar_color"]
playback_start = config["General"]["playback_start"]
playback_end = config["General"]["playback_end"]
chime_on_start = config.getboolean("General", "chime_on_start")
chime_before_hour = config.getboolean("General", "chime_before_hour")

ctk.set_appearance_mode("dark")  # Установить режим внешнего вида в темный
ctk.set_default_color_theme("blue")  # Установить тему цвета по умолчанию

root = ctk.CTk()
root.title("")
root.overrideredirect(True)  # Удалить стандартную строку заголовка окна и элементы управления
root.attributes("-topmost", True)  # Держать окно всегда поверх
root.configure(fg_color=paper_color)  # Установить цвет фона

# Получить ширину и высоту экрана
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Установить размер окна (на 5% больше чем размер шрифта)
window_width = int(font_size * 6 * window_width_percentage)  # 6 символов для времени (HH:MM:SS)
window_height = int(font_size * 1.5 * window_height_percentage)

# Рассчитать позицию окна на основе clock_position
if clock_position == "center":
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
elif clock_position == "top_left":
    x = 0
    y = 0
elif clock_position == "bottom_left":
    x = 0
    y = screen_height - window_height
elif clock_position == "top_right":
    x = screen_width - window_width
    y = 0
elif clock_position == "bottom_right":
    x = screen_width - window_width
    y = screen_height - window_height
else:
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Установить стиль шрифта
font_settings = (font_name, font_size, font_style)

time_label = ctk.CTkLabel(root, text="", font=font_settings, text_color=font_color)
time_label.pack(anchor="center", expand=True)

# Создать полоску секунд
seconds_bar = ctk.CTkFrame(root, fg_color=seconds_bar_color, bg_color=seconds_bar_color, height=seconds_bar_height)
seconds_bar.place(x=0, y=window_height - seconds_bar_height)

# Привязать событие двойного щелчка для закрытия окна ко всей площади окна
root.bind("<Double-1>", on_double_click)

# Воспроизведение chime.mp3 при запуске программы
if chime_on_start:
    play_chime()

# Создаем и запускаем поток для обновления времени
update_thread = threading.Thread(target=update_time, daemon=True)
update_thread.start()

root.mainloop()
