from tkinter import *
from tkinter import filedialog
import tkinter.ttk as ttk
import pathlib, os
import pygame
from PIL import Image, ImageTk
import time
from mutagen.flac import FLAC


class Application(Frame):
    """Application that loads and play music"""
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.master.title("ProMCS")
        self.master.geometry("400x310")
        self.create_menu()
        self.create_frames()
        self.files = {}
        pygame.mixer.init()
        self.paused = False

    def create_menu(self):
        """Design menu bar"""
        self.my_menu = Menu(self.master)

        # Menu that gives functions to add music
        self.add_menu = Menu(self.my_menu)
        self.add_menu.add_command(label="Add one song", command=self.add_song)
        self.add_menu.add_command(label="Add many songs", command=self.add_songs)

        # Menu that gives functions to remove one or all elements from listbox
        self.remove_menu = Menu(self.my_menu)
        self.remove_menu.add_command(label="Remove one song", command=self.remove_song)
        self.remove_menu.add_command(label="Remove all songs", command=self.remove_songs)

        # This code embeds add and remove menu
        self.my_menu.add_cascade(label="Add Songs", menu=self.add_menu)
        self.my_menu.add_cascade(label="Remove Songs", menu=self.remove_menu)

        self.master.config(menu=self.my_menu)

    def create_frames(self):
        """Create all frames and images"""
        self.list_frame = Frame(self.master)
        self.list_frame.pack(fill=X)
        self.listbox = Listbox(self.list_frame, bg='black', fg='green', selectbackground='gray', selectforeground='black', selectmode=EXTENDED)
        self.listbox.pack(fill=X, padx=20, pady=(20, 0))
        self.slider = ttk.Scale(self.list_frame, value=0, from_=0, to=100, orient=HORIZONTAL)
        self.slider.pack(fill=X, padx=20)
        self.btn_frame = Frame(self.master)
        self.btn_frame.pack(fill=X, padx=20)

        # setting images
        global img_1, img_2, img_3, img_4, img_5
        img_1 = self.create_image(f'img/next.png', 180)
        img_2 = self.create_image(f'img/play.png', 0)
        img_3 = self.create_image(f'img/pause.png', 0)
        img_4 = self.create_image(f'img/stop.png', 0)
        img_5 = self.create_image(f'img/next.png', 0)

        images = [{"file": img_1, "command": self.previous},
                  {"file": img_2, "command": self.play},
                  {"file": img_3, "command": self.pause},
                  {"file": img_4, "command": self.stop},
                  {"file": img_5, "command": self.next}]

        for index, image in enumerate(images):
            self.btn = Button(self.btn_frame, image=image["file"], command=image["command"], relief=FLAT)
            self.btn.grid(row=0, column=index, sticky=N+S+E+W, padx=8)

        self.info_frame = Frame(self.master)
        self.info_frame.pack(fill=X, side=BOTTOM)
        self.info_label = Label(self.info_frame, text="", relief=SUNKEN, anchor=E)
        self.info_label.pack(fill=X)

    @staticmethod
    def create_image(path, rotation):
        img = Image.open(path)
        img = img.rotate(rotation)
        img = img.resize((50, 50))
        img = ImageTk.PhotoImage(img)
        return img

    def play(self):
        """Play selected music"""
        selected = self.files[self.listbox.selection_get()]
        pygame.mixer.music.load(selected)
        pygame.mixer.music.play(loops=0)
        self.play_time()

    def next(self):
        """Play next music on the playlist"""
        current = self.listbox.curselection()[0]
        if current < self.listbox.size() - 1:
            self.listbox.selection_clear(current)
            self.listbox.activate(current+1)
            self.listbox.select_set(current+1)
            self.play()

    def previous(self):
        """Play previous music on the playlist"""
        current = self.listbox.curselection()[0]
        if current > 0:
            self.listbox.selection_clear(current)
            self.listbox.activate(current-1)
            self.listbox.select_set(current-1)
            selected = self.files[self.listbox.selection_get()]
            pygame.mixer.music.load(selected)
            pygame.mixer.music.play(loops=0)

    def pause(self):
        """Pause or unpause the music"""
        if not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
        else:
            pygame.mixer.music.unpause()
            self.paused = False

    def stop(self):
        """Stop music"""
        pygame.mixer.music.stop()

    def add_song(self):
        """Open dialogbox, chose one file and load it"""
        start_path = pathlib.Path().absolute()
        song = filedialog.askopenfilename(
            initialdir=start_path,
            title="Choose a song",
            filetypes=(("flac files", "*.flac"),
                       ("mp3 files", "*.mp3"),
                       ("all files", "*")))

        key = os.path.basename(song)
        self.files[key] = song
        self.listbox.insert("end", key)

    def add_songs(self):
        """Open dialogbox, chose multiple files and load them"""
        start_path = pathlib.Path().absolute()
        songs = filedialog.askopenfilenames(
            initialdir=start_path,
            title="Choose songs",
            filetypes=(("flac files", "*.flac"),
                       ("mp3 files", "*.mp3"),
                       ("all files", "*")))

        self.files.update({os.path.basename(song): song for song in songs})
        self.listbox.insert("end", *self.files.keys())

        # for song in songs:
        #     self.files.append({'index': ...,
        #                        'name': ...,
        #                        'path': ...,
        #                        'flac_object': ...,
        #                        'length': ...,
        #                        'flength': ...})

    def remove_song(self):
        """Pick a song from listbox and remove it"""
        self.listbox.delete("anchor")
        pygame.mixer.music.stop()

    def remove_songs(self):
        """Remove all songs from listbox"""
        self.listbox.delete(0, "end")
        pygame.mixer.music.stop()

    def play_time(self):
        # Get current song name
        current_song_name = self.listbox.selection_get()
        # Get current song path
        current_song_path = self.files[self.listbox.selection_get()]
        # Create current song flac object based on its path
        current_song_object = FLAC(current_song_path)
        # Get current song length
        current_song_length = current_song_object.info.length
        # Get current song length
        current_song_length_formated = time.strftime('%M:%S', time.gmtime(current_song_length))
        # Get current position of a song - rounded to seconds
        current_song_position = round(pygame.mixer.music.get_pos()/1000)
        # Convert current position to Minutes:Seconds format
        current_song_position_formated = time.strftime('%M:%S', time.gmtime(current_song_position))

        self.slider.config(to=current_song_length)
        current_song_slider_time = self.slider.get()
        self.slider.config(value=current_song_position)

        print(current_song_position, current_song_position_formated, current_song_slider_time)

        if current_song_slider_time == current_song_position:
            print(True)

        if current_song_position >= round(current_song_length):
            self.next()

        self.info_label.config(text=f"{current_song_position_formated} of {current_song_length_formated}")
        self.info_label.after(1000, self.play_time)


if __name__ == '__main__':
    root = Tk()
    app = Application(master=root)
    app.mainloop()
