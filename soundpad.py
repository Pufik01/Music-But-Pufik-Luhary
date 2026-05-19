import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os

try:
    import sounddevice as sd
    import numpy as np
    from pydub import AudioSegment
except ImportError as e:
    print(f"Ошибка импорта библиотек: {e}")
    print("Пожалуйста, установите зависимости: pip install sounddevice numpy pydub")
    exit(1)

class SoundPadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Button - Sound Pad")
        self.root.geometry("600x400")
        
        # Хранилище загруженных звуков: {button_id: {"name": str, "data": numpy_array, "sr": int}}
        self.sounds = {}
        self.button_widgets = []
        
        # Настройка устройства вывода (по умолчанию системное, можно выбрать виртуальный кабель)
        self.output_device = None
        self.setup_device_menu()
        
        # Фрейм для кнопок
        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Кнопка добавления звука
        self.add_btn = tk.Button(root, text="+ Добавить звук (MP3/WAV)", command=self.add_sound, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        self.add_btn.pack(pady=10, ipadx=10, ipady=5)
        
        # Статус бар
        self.status_label = tk.Label(root, text="Готов к работе", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_device_menu(self):
        """Создает меню выбора устройства вывода"""
        menu_frame = tk.Frame(self.root)
        menu_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(menu_frame, text="Устройство вывода:").pack(side=tk.LEFT)
        
        devices = sd.query_devices()
        device_names = ["Системное по умолчанию"]
        for i, dev in enumerate(devices):
            if dev['max_output_channels'] > 0:
                device_names.append(f"{dev['name']} (ID: {dev['index']})")
        
        self.device_var = tk.StringVar(value=device_names[0])
        self.device_menu = tk.OptionMenu(menu_frame, self.device_var, *device_names, command=self.change_device)
        self.device_menu.pack(side=tk.LEFT, padx=5)
        
        # Инструкция
        info_label = tk.Label(menu_frame, text="(Выберите 'Виртуальный кабель' для трансляции в Discord/VK)", font=("Arial", 8), fg="gray")
        info_label.pack(side=tk.RIGHT)

    def change_device(self, selection):
        if selection == "Системное по умолчанию":
            self.output_device = None
        else:
            # Извлекаем ID устройства из строки
            try:
                device_id_str = selection.split("(ID: ")[1].replace(")", "")
                self.output_device = int(device_id_str)
            except:
                self.output_device = None
        self.status_label.config(text=f"Устройство изменено: {selection}")

    def load_audio_file(self, filepath):
        """Загружает аудиофайл и конвертирует в numpy массив"""
        try:
            audio = AudioSegment.from_file(filepath)
            # Конвертируем в формат, понятный sounddevice (float32, нормализованный)
            samples = np.array(audio.get_array_of_samples())
            
            # Если стерео, разделяем каналы или берем один, но лучше миксовать в моно для простоты
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
                # Превращаем в моно для упрощения (среднее арифметическое)
                samples = samples.mean(axis=1)
            
            # Нормализация
            samples = samples.astype(np.float32)
            max_val = np.max(np.abs(samples))
            if max_val > 0:
                samples = samples / max_val
            
            return samples, audio.frame_rate
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")
            return None, None

    def add_sound(self):
        filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
        if not filepath:
            return
            
        filename = os.path.basename(filepath)
        data, sr = self.load_audio_file(filepath)
        
        if data is None:
            return
            
        sound_id = len(self.sounds)
        self.sounds[sound_id] = {"name": filename, "data": data, "sr": sr}
        
        # Создаем кнопку
        btn = tk.Button(self.buttons_frame, text=filename[:20] + ("..." if len(filename) > 20 else ""), 
                        command=lambda sid=sound_id: self.play_sound(sid),
                        height=3, width=40, bg="#2196F3", fg="white", font=("Arial", 10))
        btn.pack(pady=5, padx=10)
        self.button_widgets.append(btn)
        
        self.status_label.config(text=f"Добавлен: {filename}")

    def play_sound(self, sound_id):
        if sound_id not in self.sounds:
            return
            
        sound_data = self.sounds[sound_id]["data"]
        sample_rate = self.sounds[sound_id]["sr"]
        
        def play_thread():
            try:
                self.status_label.config(text=f"Воспроизведение: {self.sounds[sound_id]['name']}")
                sd.play(sound_data, samplerate=sample_rate, device=self.output_device)
                sd.wait() # Ждем окончания воспроизведения
                self.status_label.config(text="Готов к работе")
            except Exception as e:
                self.status_label.config(text=f"Ошибка воспроизведения: {e}")
                messagebox.showerror("Ошибка", f"Не удалось воспроизвести звук: {e}")
        
        # Запускаем в отдельном потоке, чтобы не блокировать интерфейс
        threading.Thread(target=play_thread, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = SoundPadApp(root)
    root.mainloop()
