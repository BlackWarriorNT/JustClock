import customtkinter
from ctypes import windll
from PIL import Image, ImageTk
import os
import configparser
import sys

# Определение пути к папке с приложением
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# Настройки окна приложения
WINDOW_WIDTH = 440
WINDOW_HEIGHT = 780
APP_TITLE = "Просто Часы. Настройки"
APP_TITLE_COLOR_BG = "#00121F"  # Цвет фона заголовка
APP_TITLE_COLOR_FG = "#E0E0E0"  # Цвет шрифта заголовка
APP_TITLE_COLOR_FONT = "Helvetica"  # Шрифт заголовка
APP_TITLE_COLOR_FONT_STYLE = "bold"  # Стиль шрифта заголовка
APP_TRANSPARENCY = 0.97  # Прозрачность окна приложения

# Словарь для перевода значений параметров
TRANSLATIONS = {
    "center": "центр",
    "top_left": "верхний левый угол",
    "bottom_left": "нижний левый угол",
    "top_right": "верхний правый угол",
    "bottom_right": "нижний правый угол",
    "normal": "обычный",
    "bold": "жирный",
    "italic": "курсив",
    "true": "да",
    "false": "нет"
}

# Default settings
default_settings = {
    'General': {
        'clock_position': 'bottom_right',
        'font_name': 'Tahoma',
        'font_style': 'bold',
        'font_size': '18',
        'font_color': '#D4D4D4',
        'paper_color': '#1E1E1E',
        'seconds_bar_show': 'True',
        'seconds_bar_height': '4',
        'seconds_bar_color': '#4C72AF',
        'playback_start': '06:00',
        'playback_end': '23:00',
        'chime_on_start': 'True',
        'chime_before_hour': 'True'
    }
}

# Template Options
class CTkWindow(customtkinter.CTk):
    def __init__(self,
                app_title = APP_TITLE, # Application name
                geometry = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}", # Enter window geometry
                titlebar_color = "default", # Specify the color of top bar
                title_color = "default", # Title label color
                fg_color = "default", # fg_color of window
                resizable = True, # Resize window dynamically
                round_corner = 12, # corner_radius
                icon = None, # icon path
                justify = "left", # title justify
                style = "classic" # style
                ):

        super().__init__()
        self.overrideredirect(1)
        transparent_color = self._apply_appearance_mode(['#f2f2f2','#000001'])
        self.config(background=transparent_color)
        self.attributes("-transparentcolor", transparent_color) # transparent_color will be the transparent color
        self.attributes("-alpha", APP_TRANSPARENCY)  # Set window transparency
        self.geometry(geometry)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Center the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

        self.x = self.winfo_x()
        self.y = self.winfo_y()
        self.fullscreen = False
        self.GWL_EXSTYLE = -20
        self.WS_EX_APPWINDOW = 0x00040000
        self.WS_EX_TOOLWINDOW = 0x00000080
        self.titlebar_color = [APP_TITLE_COLOR_BG, APP_TITLE_COLOR_BG] if titlebar_color=="default" else titlebar_color
        title_color = [APP_TITLE_COLOR_FG, APP_TITLE_COLOR_FG] if title_color=="default" else title_color
        self.header = customtkinter.CTkFrame(self, corner_radius=round_corner, fg_color=self.titlebar_color,
                                           background_corner_colors=(transparent_color,transparent_color,None,None))
        self.header.grid(sticky="nwe", row=0)
        self.header.grid_columnconfigure(0, weight=1)
        self.header.grid_rowconfigure(0, weight=1)
        self.header.bind("<ButtonPress-1>", self.oldxyset)
        self.header.bind("<B1-Motion>",  self.move_window)
        self.header.bind("<Double-1>",  lambda e: self.max_window())

        fg_color = customtkinter.ThemeManager.theme["CTk"]["fg_color"] if fg_color=="default" else fg_color

        self.app = customtkinter.CTkFrame(self, corner_radius=round_corner, bg_color=transparent_color, fg_color=fg_color,
                                     background_corner_colors=(fg_color,fg_color,None,None))
        self.app.grid(sticky="nsew", row=0,pady=(29,0))
        self.app.bind("<Map>", self.frame_mapped)

        if resizable==True:
            self.app.bind("<Motion>", self.change_cursor)
            self.app.bind("<B1-Motion>", self.resize)

        self.resizable = resizable
        self.ctkimage = customtkinter.CTkImage(Image.open(os.path.join(os.path.dirname(customtkinter.__file__),"assets","icons","CustomTkinter_icon_Windows.ico")), size=(16,16))
        self.icon = self.ctkimage if icon is None else customtkinter.CTkImage(Image.open(icon), size=(16,16))
        self.title_label = customtkinter.CTkLabel(self.header, width=10, image=self.icon, compound="left", text=f"  {app_title}", anchor="n", text_color=title_color, font=(APP_TITLE_COLOR_FONT, 12, APP_TITLE_COLOR_FONT_STYLE))
        if justify=="center":
            self.title_label.grid(row=0, sticky="we", padx=(30,0), pady=7)
        else:
            self.title_label.grid(row=0, sticky="w", padx=8, pady=7)

        self.title_label.bind("<ButtonPress-1>", self.oldxyset)
        self.title_label._label.bind("<ButtonPress-1>", self.oldxyset)
        self.title_label.bind("<B1-Motion>", self.move_window)
        self.title_label.bind("<Double-1>",  lambda e: self.max_window())
        self.minmize = False
        self.style = style

        self.button_close = customtkinter.CTkButton(self.header, corner_radius=round_corner, width=40, height=30, text="✕",
                                                   hover_color="#c42b1c", fg_color="transparent", text_color=["black","white"],
                                                   background_corner_colors=(None,transparent_color,None,None), command=self.close_window)
        self.button_close.grid(row=0, column=2, sticky="ne", padx=0, pady=0)
        self.button_close.configure(cursor="arrow")
        self.button_close.bind("<Enter>", lambda e: self.change_bg(transparent_color, 1), add="+")
        self.button_close.bind("<Leave>", lambda e: self.change_bg(transparent_color, 0), add="+")

        # Load settings from JustClock.ini
        self.settings_config = configparser.ConfigParser()
        config_path = os.path.join(application_path, 'JustClock.ini')
        if not os.path.exists(config_path):
            self.create_default_config(config_path)
        self.settings_config.read(config_path)

        # General Settings
        self.general_frame = customtkinter.CTkFrame(self.app, corner_radius=round_corner, fg_color=fg_color)
        self.general_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.general_frame.grid_columnconfigure(1, weight=1)

        self.clock_position_label = customtkinter.CTkLabel(self.general_frame, text="Положение часов:")
        self.clock_position_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.clock_position_combobox = customtkinter.CTkComboBox(self.general_frame, values=["центр", "верхний левый угол", "нижний левый угол", "верхний правый угол", "нижний правый угол"])
        self.clock_position_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.clock_position_combobox.set(TRANSLATIONS[self.settings_config.get('General', 'clock_position')])

        self.font_name_label = customtkinter.CTkLabel(self.general_frame, text="Шрифт:")
        self.font_name_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.font_name_combobox = customtkinter.CTkComboBox(self.general_frame, values=["Arial", "Calibri", "Helvetica", "Segoe UI", "Tahoma", "Terminal"])
        self.font_name_combobox.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.font_name_combobox.set(self.settings_config.get('General', 'font_name'))

        self.font_style_label = customtkinter.CTkLabel(self.general_frame, text="Стиль шрифта:")
        self.font_style_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.font_style_combobox = customtkinter.CTkComboBox(self.general_frame, values=["обычный", "жирный", "курсив"])
        self.font_style_combobox.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.font_style_combobox.set(TRANSLATIONS[self.settings_config.get('General', 'font_style')])

        self.font_size_label = customtkinter.CTkLabel(self.general_frame, text="Размер шрифта:")
        self.font_size_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.font_size_frame = customtkinter.CTkFrame(self.general_frame, fg_color="transparent")
        self.font_size_frame.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        self.font_size_scale = customtkinter.CTkSlider(self.font_size_frame, from_=10, to=50, number_of_steps=40, width=100, command=self.update_font_size)
        self.font_size_scale.pack(side="left", padx=(0, 10))

        self.font_size_value_label = customtkinter.CTkLabel(self.font_size_frame, text=str(int(float(self.settings_config.get('General', 'font_size')))))
        self.font_size_value_label.pack(side="left")

        self.font_size_scale.set(int(float(self.settings_config.get('General', 'font_size'))))

        self.font_color_label = customtkinter.CTkLabel(self.general_frame, text="Цвет шрифта:")
        self.font_color_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.font_color_entry = customtkinter.CTkEntry(self.general_frame)
        self.font_color_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        self.font_color_entry.insert(0, self.settings_config.get('General', 'font_color'))

        self.paper_color_label = customtkinter.CTkLabel(self.general_frame, text="Цвет фона:")
        self.paper_color_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.paper_color_entry = customtkinter.CTkEntry(self.general_frame)
        self.paper_color_entry.grid(row=5, column=1, padx=10, pady=10, sticky="ew")
        self.paper_color_entry.insert(0, self.settings_config.get('General', 'paper_color'))

        self.seconds_bar_show_label = customtkinter.CTkLabel(self.general_frame, text="Секундная полоска:")
        self.seconds_bar_show_label.grid(row=6, column=0, padx=10, pady=10, sticky="w")
        self.seconds_bar_show_frame = customtkinter.CTkFrame(self.general_frame, fg_color="transparent")
        self.seconds_bar_show_frame.grid(row=6, column=1, padx=10, pady=10, sticky="ew")

        self.seconds_bar_show_switch = customtkinter.CTkSwitch(self.seconds_bar_show_frame, text="", onvalue="True", offvalue="False", command=self.update_seconds_bar_show_label)
        self.seconds_bar_show_switch.pack(side="left", padx=(0,5))
        self.seconds_bar_show_switch.select() if self.settings_config.get('General', 'seconds_bar_show') == "True" else self.seconds_bar_show_switch.deselect()

        self.seconds_bar_show_state_label = customtkinter.CTkLabel(self.seconds_bar_show_frame, text=TRANSLATIONS[self.settings_config.get('General', 'seconds_bar_show').lower()])
        self.seconds_bar_show_state_label.pack(side="left")

        self.seconds_bar_height_label = customtkinter.CTkLabel(self.general_frame, text="Высота секундной полоски:")
        self.seconds_bar_height_label.grid(row=7, column=0, padx=10, pady=10, sticky="w")

        self.seconds_bar_height_frame = customtkinter.CTkFrame(self.general_frame, fg_color="transparent")
        self.seconds_bar_height_frame.grid(row=7, column=1, padx=10, pady=10, sticky="ew")

        self.seconds_bar_height_scale = customtkinter.CTkSlider(self.seconds_bar_height_frame, from_=1, to=10, number_of_steps=9, width=100, command=self.update_seconds_bar_height)
        self.seconds_bar_height_scale.pack(side="left", padx=(0, 10))

        self.seconds_bar_height_value_label = customtkinter.CTkLabel(self.seconds_bar_height_frame, text=self.settings_config.get('General', 'seconds_bar_height'))
        self.seconds_bar_height_value_label.pack(side="left")

        self.seconds_bar_height_scale.set(int(self.settings_config.get('General', 'seconds_bar_height')))

        self.seconds_bar_color_label = customtkinter.CTkLabel(self.general_frame, text="Цвет секундной полоски:")
        self.seconds_bar_color_label.grid(row=8, column=0, padx=10, pady=10, sticky="w")
        self.seconds_bar_color_entry = customtkinter.CTkEntry(self.general_frame)
        self.seconds_bar_color_entry.grid(row=8, column=1, padx=10, pady=10, sticky="ew")
        self.seconds_bar_color_entry.insert(0, self.settings_config.get('General', 'seconds_bar_color'))

        self.playback_start_label = customtkinter.CTkLabel(self.general_frame, text="Время начала проигрывания звука:")
        self.playback_start_label.grid(row=9, column=0, padx=10, pady=10, sticky="w")
        self.playback_start_entry = customtkinter.CTkEntry(self.general_frame)
        self.playback_start_entry.grid(row=9, column=1, padx=10, pady=10, sticky="ew")
        self.playback_start_entry.insert(0, self.settings_config.get('General', 'playback_start'))

        self.playback_end_label = customtkinter.CTkLabel(self.general_frame, text="Время окончания проигрывания звука:")
        self.playback_end_label.grid(row=10, column=0, padx=10, pady=10, sticky="w")
        self.playback_end_entry = customtkinter.CTkEntry(self.general_frame)
        self.playback_end_entry.grid(row=10, column=1, padx=10, pady=10, sticky="ew")
        self.playback_end_entry.insert(0, self.settings_config.get('General', 'playback_end'))

        self.chime_on_start_label = customtkinter.CTkLabel(self.general_frame, text="Воспроизводить звук при запуске:")
        self.chime_on_start_label.grid(row=11, column=0, padx=10, pady=10, sticky="w")
        self.chime_on_start_frame = customtkinter.CTkFrame(self.general_frame, fg_color="transparent")
        self.chime_on_start_frame.grid(row=11, column=1, padx=10, pady=10, sticky="ew")

        self.chime_on_start_switch = customtkinter.CTkSwitch(self.chime_on_start_frame, text="", onvalue="True", offvalue="False", command=self.update_chime_on_start_label)
        self.chime_on_start_switch.pack(side="left", padx=(0,5))
        self.chime_on_start_switch.select() if self.settings_config.get('General', 'chime_on_start') == "True" else self.chime_on_start_switch.deselect()

        self.chime_on_start_state_label = customtkinter.CTkLabel(self.chime_on_start_frame, text=TRANSLATIONS[self.settings_config.get('General', 'chime_on_start').lower()])
        self.chime_on_start_state_label.pack(side="left")

        self.chime_before_hour_label = customtkinter.CTkLabel(self.general_frame, text="Воспроизводить звук перед временем:")
        self.chime_before_hour_label.grid(row=12, column=0, padx=10, pady=10, sticky="w")
        self.chime_before_hour_frame = customtkinter.CTkFrame(self.general_frame, fg_color="transparent")
        self.chime_before_hour_frame.grid(row=12, column=1, padx=10, pady=10, sticky="ew")

        self.chime_before_hour_switch = customtkinter.CTkSwitch(self.chime_before_hour_frame, text="", onvalue="True", offvalue="False", command=self.update_chime_before_hour_label)
        self.chime_before_hour_switch.pack(side="left", padx=(0,5))
        self.chime_before_hour_switch.select() if self.settings_config.get('General', 'chime_before_hour') == "True" else self.chime_before_hour_switch.deselect()

        self.chime_before_hour_state_label = customtkinter.CTkLabel(self.chime_before_hour_frame, text=TRANSLATIONS[self.settings_config.get('General', 'chime_before_hour').lower()])
        self.chime_before_hour_state_label.pack(side="left")

        # Restore Defaults Button
        self.restore_defaults_button = customtkinter.CTkButton(self.app, text="Восстановить настройки по умолчанию", command=self.restore_defaults)
        self.restore_defaults_button.grid(row=13, column=0, padx=10, pady=10, sticky="ew")

        # Save Button
        self.save_button = customtkinter.CTkButton(self.app, text="Сохранить настройки", command=self.save_settings)
        self.save_button.grid(row=14, column=0, padx=10, pady=10, sticky="ew")

    def update_font_size(self, value):
        self.font_size_scale.set(int(value))
        self.font_size_value_label.configure(text=str(int(value)))

    def update_seconds_bar_show_label(self):
        current_state = self.seconds_bar_show_switch.get()
        self.seconds_bar_show_state_label.configure(text=TRANSLATIONS[current_state.lower()])

    def update_seconds_bar_height(self, value):
        self.seconds_bar_height_scale.set(int(value))
        self.seconds_bar_height_value_label.configure(text=str(int(value)))

    def update_chime_on_start_label(self):
        current_state = self.chime_on_start_switch.get()
        self.chime_on_start_state_label.configure(text=TRANSLATIONS[current_state.lower()])

    def update_chime_before_hour_label(self):
        current_state = self.chime_before_hour_switch.get()
        self.chime_before_hour_state_label.configure(text=TRANSLATIONS[current_state.lower()])

    def create_default_config(self, config_path):
        if self.settings_config.has_section('General'):
            self.settings_config.remove_section('General')
        self.settings_config.add_section('General')
        for key, value in default_settings['General'].items():
            self.settings_config.set('General', key, value)
        with open(config_path, 'w') as configfile:
            self.settings_config.write(configfile)

    def save_settings(self):
        self.settings_config.set('General', 'clock_position', self.translate_back(self.clock_position_combobox.get()))
        self.settings_config.set('General', 'font_name', self.font_name_combobox.get())
        self.settings_config.set('General', 'font_style', self.translate_back(self.font_style_combobox.get()))
        self.settings_config.set('General', 'font_size', str(int(self.font_size_scale.get())))
        self.settings_config.set('General', 'font_color', self.font_color_entry.get())
        self.settings_config.set('General', 'paper_color', self.paper_color_entry.get())
        self.settings_config.set('General', 'seconds_bar_show', self.seconds_bar_show_switch.get())
        self.settings_config.set('General', 'seconds_bar_height', str(int(self.seconds_bar_height_scale.get())))
        self.settings_config.set('General', 'seconds_bar_color', self.seconds_bar_color_entry.get())
        self.settings_config.set('General', 'playback_start', self.playback_start_entry.get())
        self.settings_config.set('General', 'playback_end', self.playback_end_entry.get())
        self.settings_config.set('General', 'chime_on_start', self.chime_on_start_switch.get())
        self.settings_config.set('General', 'chime_before_hour', self.chime_before_hour_switch.get())

        config_path = os.path.join(application_path, 'JustClock.ini')
        with open(config_path, 'w') as configfile:
            self.settings_config.write(configfile)

    def restore_defaults(self):
        self.create_default_config(os.path.join(application_path, 'JustClock.ini'))
        self.settings_config.read(os.path.join(application_path, 'JustClock.ini'))
        self.update_ui_with_defaults()

    def update_ui_with_defaults(self):
        self.clock_position_combobox.set(TRANSLATIONS[default_settings['General']['clock_position']])
        self.font_name_combobox.set(default_settings['General']['font_name'])
        self.font_style_combobox.set(TRANSLATIONS[default_settings['General']['font_style']])
        self.font_size_scale.set(int(default_settings['General']['font_size']))
        self.font_size_value_label.configure(text=str(int(default_settings['General']['font_size'])))
        self.font_color_entry.delete(0, customtkinter.END)
        self.font_color_entry.insert(0, default_settings['General']['font_color'])
        self.paper_color_entry.delete(0, customtkinter.END)
        self.paper_color_entry.insert(0, default_settings['General']['paper_color'])
        self.seconds_bar_show_switch.select() if default_settings['General']['seconds_bar_show'] == "True" else self.seconds_bar_show_switch.deselect()
        self.seconds_bar_show_state_label.configure(text=TRANSLATIONS[default_settings['General']['seconds_bar_show'].lower()])
        self.seconds_bar_height_scale.set(int(default_settings['General']['seconds_bar_height']))
        self.seconds_bar_height_value_label.configure(text=default_settings['General']['seconds_bar_height'])
        self.seconds_bar_color_entry.delete(0, customtkinter.END)
        self.seconds_bar_color_entry.insert(0, default_settings['General']['seconds_bar_color'])
        self.playback_start_entry.delete(0, customtkinter.END)
        self.playback_start_entry.insert(0, default_settings['General']['playback_start'])
        self.playback_end_entry.delete(0, customtkinter.END)
        self.playback_end_entry.insert(0, default_settings['General']['playback_end'])
        self.chime_on_start_switch.select() if default_settings['General']['chime_on_start'] == "True" else self.chime_on_start_switch.deselect()
        self.chime_on_start_state_label.configure(text=TRANSLATIONS[default_settings['General']['chime_on_start'].lower()])
        self.chime_before_hour_switch.select() if default_settings['General']['chime_before_hour'] == "True" else self.chime_before_hour_switch.deselect()
        self.chime_before_hour_state_label.configure(text=TRANSLATIONS[default_settings['General']['chime_before_hour'].lower()])

    def translate_back(self, value):
        reverse_translations = {v: k for k, v in TRANSLATIONS.items()}
        return reverse_translations.get(value, value)

    def change_bg(self, transparent_color, hover):
        if hover:
            self.button_close.configure(background_corner_colors=("#c42b1c",transparent_color,"#c42b1c","#c42b1c"), fg_color="#c42b1c")
        else:
            self.button_close.configure(background_corner_colors=(self.titlebar_color,transparent_color,self.titlebar_color,self.titlebar_color),
                                        fg_color=self.titlebar_color)

    def geometry(self, geometry):
        super().geometry(geometry)

    def iconbitmap(self, icon):
        self.icon = customtkinter.CTkImage(Image.open(icon), size=(16,16))
        self.title_label.configure(image=self.icon)

    def oldxyset(self, event):
        self.oldx = event.x
        self.oldy = event.y

    def move_window(self, event):
        if self.fullscreen==False:
            self.y = event.y_root - self.oldy
            self.x = event.x_root - self.oldx
            self.geometry(f'+{self.x}+{self.y}')

    def close_window(self):
        super().destroy()

    def frame_mapped(self, e):
        self.update_idletasks()
        self.overrideredirect(True)
        self.state('normal')
        if self.minmize:
            self.fullscreen = False
            self.max_window()
        self.minmize = False

    def min_window(self):
        self.update_idletasks()
        self.overrideredirect(False)
        self.withdraw()
        self.state('iconic')
        if self.fullscreen:
            self.minmize = True

    def set_appwindow(self):
        hwnd = windll.user32.GetParent(self.winfo_id())
        style = windll.user32.GetWindowLongW(hwnd, self.GWL_EXSTYLE)
        style = style & ~self.WS_EX_TOOLWINDOW
        style = style | self.WS_EX_APPWINDOW
        res = windll.user32.SetWindowLongW(hwnd, self.GWL_EXSTYLE, style)
        self.wm_withdraw()
        self.after(10, lambda: self.wm_deiconify())

    def max_window(self):
        if self.resizable==True:
            if self.fullscreen==False:
                self.update_idletasks()
                self.overrideredirect(False)
                self.wm_state('zoomed')
                self.overrideredirect(True)
                self.after(10, lambda: self.set_appwindow())
                self.state('normal')
                self.fullscreen=True
            else:
                self.geometry(f'+{self.x}+{self.y}')
                self.fullscreen=False

    def change_cursor(self, event):
        if (event.x in range(self.app.winfo_width()-10, self.app.winfo_width())
            and event.y in range(self.app.winfo_height()-10, self.app.winfo_height())):
            self.config(cursor="size_nw_se")
            return
        else:
            self.config(cursor="")

        if (event.x in range(self.app.winfo_width()-5, self.app.winfo_width())
            and event.y in range(0, self.app.winfo_height())):
            self.config(cursor="sb_h_double_arrow")
            return
        else:
            self.config(cursor="")

        if (event.x in range(0, self.app.winfo_width())
            and event.y in range(self.app.winfo_height()-5, self.app.winfo_height())):
            self.config(cursor="sb_v_double_arrow")
            return
        else:
            self.config(cursor="")

    def resize(self, event):
        if self.cget('cursor')=="size_nw_se":
            if event.x>100 and event.y>100:
                self.geometry(f"{event.x_root-self.x}x{event.y_root-self.y}")
        elif self.cget('cursor')=="sb_h_double_arrow":
            self.geometry(f"{event.x_root-self.x}x{self.winfo_height()}")
        elif self.cget('cursor')=="sb_v_double_arrow":
            self.geometry(f"{self.winfo_width()}x{event.y_root-self.y}")

    def configure(self, **kwargs):
        if "titlebar_color" in kwargs:
            self.titlebar_color = kwargs["titlebar_color"]
            self.header.configure(fg_color=self.titlebar_color)
        if "title" in kwargs:
            self.title_label.configure(text=f"  {kwargs['title']}")
        if "icon" in kwargs:
            self.icon = customtkinter.CTkImage(Image.open(kwargs["icon"]), size=(32,32))
            self.title_label.configure(image=self.icon)
        if "fg_color" in kwargs:
            self.app.configure(fg_color=fg_color)
        if "title_color" in kwargs:
            self.title_label.configure(text_color=kwargs['title_color'])

if __name__=="__main__":
    window = CTkWindow(app_title=APP_TITLE)
    window.mainloop()
