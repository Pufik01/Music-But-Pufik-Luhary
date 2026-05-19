import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import threading
import os
import json

class SoundPad:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Music Button - Sound Pad")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Инициализация pygame mixer
        pygame.mixer.init()
        
        # Хранилище звуков: {кнопка: путь_к_файлу}
        self.sounds = {}
        self.buttons = {}
        
        # Загрузка сохраненных звуков
        self.config_file = "soundpad_config.json"
        self.load_config()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Верхняя панель
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="🎵 Music Button - Sound Pad", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        ttk.Button(top_frame, text="➕ Добавить звук", 
                  command=self.add_sound).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(top_frame, text="🗑️ Очистить все", 
                  command=self.clear_all).pack(side=tk.RIGHT, padx=5)
        
        # Панель с кнопками звуков (с прокруткой)
        canvas_frame = ttk.Frame(self.root, padding="10")
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, 
                                 command=self.canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе. Добавьте звуки через кнопку 'Добавить звук'")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, padding=5)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Обновление кнопок
        self.update_buttons()
        
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def add_sound(self):
        filetypes = [
            ("Аудио файлы", "*.mp3 *.wav *.ogg *.flac"),
            ("MP3 файлы", "*.mp3"),
            ("WAV файлы", "*.wav"),
            ("Все файлы", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Выберите аудио файл",
            filetypes=filetypes
        )
        
        if filename:
            sound_name = os.path.basename(filename)
            # Убираем расширение для названия кнопки
            name_without_ext = os.path.splitext(sound_name)[0]
            
            # Проверяем, существует ли уже такой звук
            counter = 1
            original_name = name_without_ext
            while name_without_ext in self.sounds:
                name_without_ext = f"{original_name}_{counter}"
                counter += 1
            
            self.sounds[name_without_ext] = filename
            self.save_config()
            self.update_buttons()
            self.status_var.set(f"Добавлен звук: {name_without_ext}")
            
    def play_sound(self, sound_name):
        def play_thread():
            try:
                if sound_name in self.sounds:
                    sound_path = self.sounds[sound_name]
                    if os.path.exists(sound_path):
                        sound = pygame.mixer.Sound(sound_path)
                        sound.play()
                        self.status_var.set(f"Воспроизводится: {sound_name}")
                    else:
                        self.status_var.set(f"Файл не найден: {sound_name}")
                        messagebox.showerror("Ошибка", f"Файл звука '{sound_name}' не найден!")
                else:
                    self.status_var.set(f"Звук не найден: {sound_name}")
            except Exception as e:
                self.status_var.set(f"Ошибка воспроизведения: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось воспроизвести звук:\n{str(e)}")
        
        thread = threading.Thread(target=play_thread, daemon=True)
        thread.start()
        
    def remove_sound(self, sound_name):
        if sound_name in self.sounds:
            del self.sounds[sound_name]
            self.save_config()
            self.update_buttons()
            self.status_var.set(f"Удален звук: {sound_name}")
            
    def clear_all(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить все звуки?"):
            self.sounds.clear()
            self.save_config()
            self.update_buttons()
            self.status_var.set("Все звуки удалены")
            
    def update_buttons(self):
        # Очищаем существующие кнопки
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.buttons.clear()
        
        if not self.sounds:
            ttk.Label(self.scrollable_frame, 
                     text="Нет добавленных звуков.\nНажмите 'Добавить звук', чтобы добавить аудио файлы.",
                     font=("Arial", 12), justify=tk.CENTER).pack(pady=50)
            return
        
        # Создаем сетку кнопок
        columns = 3
        for i, (name, path) in enumerate(self.sounds.items()):
            row = i // columns
            col = i % columns
            
            frame = ttk.Frame(self.scrollable_frame, padding=5)
            frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            
            # Кнопка воспроизведения
            btn = ttk.Button(frame, text=f"▶️ {name}", 
                           command=lambda n=name: self.play_sound(n),
                           width=20)
            btn.pack(fill=tk.X, pady=(0, 5))
            
            # Кнопка удаления
            del_btn = ttk.Button(frame, text="🗑️ Удалить", 
                               command=lambda n=name: self.remove_sound(n))
            del_btn.pack(fill=tk.X)
            
            self.buttons[name] = {"play": btn, "delete": del_btn}
            
        # Настройка растягивания колонок
        for i in range(columns):
            self.scrollable_frame.grid_columnconfigure(i, weight=1)
            
    def save_config(self):
        try:
            config = {"sounds": self.sounds}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
            
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.sounds = config.get("sounds", {})
                    
                    # Проверяем существование файлов
                    missing_sounds = []
                    for name, path in list(self.sounds.items()):
                        if not os.path.exists(path):
                            missing_sounds.append(name)
                            
                    if missing_sounds:
                        self.status_var.set(f"Найдено {len(missing_sounds)} отсутствующих файлов")
                        # Можно удалить отсутствующие файлы из конфигурации
                        # for name in missing_sounds:
                        #     del self.sounds[name]
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            self.sounds = {}

def main():
    root = tk.Tk()
    
    # Установка стиля
    style = ttk.Style()
    style.theme_use('clam')
    
    # Настройка цветов
    style.configure("TButton", padding=10, font=("Arial", 10))
    style.configure("TLabel", font=("Arial", 10))
    
    app = SoundPad(root)
    root.mainloop()

if __name__ == "__main__":
    main()
