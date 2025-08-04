import tkinter as tk
from tkinter import filedialog, ttk
import os
import pygame
import random
import shutil

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Enhanced Music Player")
        self.root.geometry("650x500")
        self.root.configure(bg="#FFFFFF")  # Vibrant purple background

        pygame.mixer.init()

        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.repeat = False
        self.shuffle = False

        # 🎶 Current Song Label
        self.label = tk.Label(root, text="Music ", font=("Segoe UI", 18, "bold"),
                              fg="black", bg="#FFFEFE", wraplength=580, justify="center")
        self.label.pack(pady=10)

        # 📋 Playlist Listbox
        self.song_listbox = tk.Listbox(root, font=("Segoe UI", 10), bg="#383838", fg="white",
                                       selectbackground="#cde45a", highlightbackground="#4a148c",
                                       borderwidth=0, height=8, width=80)
        self.song_listbox.pack(pady=5)
        self.song_listbox.bind("<ButtonRelease-1>", self.set_current_index)
        self.song_listbox.bind("<B1-Motion>", self.drag_to_reorder)

        # 🔘 Controls
        btn_frame = tk.Frame(root, bg="#e0e048")
        btn_frame.pack(pady=10)

        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 11), padding=6)

        ttk.Button(btn_frame, text="⏮️ Prev", command=self.prev_song).grid(row=0, column=0, padx=5)
        self.play_btn = ttk.Button(btn_frame, text="▶️ Play", command=self.play_pause)
        self.play_btn.grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="⏭️ Next", command=self.next_song).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="⏩ +10s", command=self.seek_forward).grid(row=0, column=3, padx=5)

        # 🔄 Shuffle / Repeat
        options_frame = tk.Frame(root, bg="#d7e727")
        options_frame.pack()

        self.shuffle_var = tk.IntVar()
        self.repeat_var = tk.IntVar()

        tk.Checkbutton(options_frame, text="🔀 Shuffle", variable=self.shuffle_var, bg="#4a148c", fg="white",
                       selectcolor="#dcef2e", activebackground="#dcef2e", command=self.toggle_shuffle).pack(side="left", padx=10)
        tk.Checkbutton(options_frame, text="🔁 Repeat", variable=self.repeat_var, bg="#4a148c", fg="white",
                       selectcolor="#dcef2e", activebackground="#dcef2e", command=self.toggle_repeat).pack(side="left", padx=10)

        # 📂 Load Button
        ttk.Button(root, text="📂 Load Songs", command=self.load_songs).pack(pady=10)

        # ⬇️ Download Button
        ttk.Button(root, text="⬇️ Download Current Song", command=self.download_song).pack(pady=5)

        # 🔊 Volume Slider
        tk.Label(root, text="🔉 Volume", bg="#ffffff", fg="black").pack()
        self.volume_slider = tk.Scale(root, from_=0, to=1, resolution=0.01, orient="horizontal",
                                      command=self.set_volume, bg="#4a148c", fg="white", troughcolor="#ab47bc")
        self.volume_slider.set(0.5)
        pygame.mixer.music.set_volume(0.5)
        self.volume_slider.pack(pady=5)

        # 🕓 Progress Bar
        self.progress = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=500)
        self.progress.pack(pady=10)
        self.update_progress()

    def load_songs(self):
        folder = filedialog.askdirectory(title="Select Music Folder")
        if not folder:
            return

        self.playlist = []
        self.song_listbox.delete(0, tk.END)

        for file in os.listdir(folder):
            if file.endswith(".mp3") or file.endswith(".wav"):
                full_path = os.path.join(folder, file)
                self.playlist.append(full_path)
                self.song_listbox.insert(tk.END, os.path.basename(full_path))

        if self.playlist:
            self.current_index = 0
            self.song_listbox.select_set(self.current_index)
            self.play_song()

    def play_song(self):
        if not self.playlist:
            return
        song = self.playlist[self.current_index]
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
        self.is_playing = True
        self.update_ui()
        self.root.after(1000, self.update_progress)

    def play_pause(self):
        if not self.playlist:
            return

        if self.is_playing:
            pygame.mixer.music.pause()
            self.play_btn.config(text="▶️ Play")
        else:
            pygame.mixer.music.unpause()
            self.play_btn.config(text="⏸️ Pause")

        self.is_playing = not self.is_playing

    def next_song(self):
        if not self.playlist:
            return

        if self.shuffle:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)

        self.song_listbox.select_clear(0, tk.END)
        self.song_listbox.select_set(self.current_index)
        self.play_song()

    def prev_song(self):
        if not self.playlist:
            return

        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.song_listbox.select_clear(0, tk.END)
        self.song_listbox.select_set(self.current_index)
        self.play_song()

    def toggle_shuffle(self):
        self.shuffle = bool(self.shuffle_var.get())

    def toggle_repeat(self):
        self.repeat = bool(self.repeat_var.get())

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val))

    def update_ui(self):
        song_path = self.playlist[self.current_index]
        song_name = os.path.basename(song_path)
        self.label.config(text=f"Now Playing:\n{song_name}")
        self.play_btn.config(text="⏸️ Pause")

    def update_progress(self):
        if not pygame.mixer.music.get_busy():
            if self.repeat:
                self.play_song()
            elif self.is_playing:
                self.next_song()
            return

        position = pygame.mixer.music.get_pos() / 1000
        try:
            duration = pygame.mixer.Sound(self.playlist[self.current_index]).get_length()
            self.progress["maximum"] = duration
            self.progress["value"] = position
        except:
            self.progress["value"] = 0

        self.root.after(1000, self.update_progress)

    def set_current_index(self, event):
        try:
            selection = self.song_listbox.curselection()
            if selection:
                self.current_index = selection[0]
                self.play_song()
        except:
            pass

    def drag_to_reorder(self, event):
        selection = self.song_listbox.curselection()
        if selection:
            index = selection[0]
            nearest = self.song_listbox.nearest(event.y)
            if index != nearest:
                self.playlist.insert(nearest, self.playlist.pop(index))
                song_name = self.song_listbox.get(index)
                self.song_listbox.delete(index)
                self.song_listbox.insert(nearest, song_name)
                self.song_listbox.select_clear(0, tk.END)
                self.song_listbox.select_set(nearest)
                self.current_index = nearest

    def seek_forward(self):
        if not self.playlist:
            return
        pos = pygame.mixer.music.get_pos() // 1000
        song = self.playlist[self.current_index]
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(start=pos + 10)

    def download_song(self):
        if not self.playlist:
            return
        song = self.playlist[self.current_index]
        download_path = os.path.join(os.path.expanduser("~"), "Downloads", os.path.basename(song))
        try:
            shutil.copy(song, download_path)
            print(f"Downloaded to {download_path}")
        except Exception as e:
            print(f"Download failed: {e}")

# 🏁 Entry Point
if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
