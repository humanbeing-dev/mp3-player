from tkinter import *
from tkinter import filedialog
import tkinter.ttk as ttk
import pathlib, os
import pygame
from PIL import Image, ImageTk
import time
from mutagen.flac import FLAC
import pickle


class MusicPlayer(Frame):
    """Application that loads and plays music"""
    def __init__(self, master):
        pygame.mixer.init()
        super().__init__(master)
        self.master.title("ProMCS")
        self.master.geometry("500x310")

        self.create_menu()
        self.create_frames()

        self.paused = False
        self.stopped = False
        self.files = {}
        self.song_index = 1
        self.song_list = []

    def create_menu(self):
        """Design menu bar"""
        self.my_menu = Menu(self.master)

        # Menu that gives functions to add music
        self.add_menu = Menu(self.my_menu)
        self.add_menu.add_command(label="Load last list", command=self.load_list)
        self.add_menu.add_separator()
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
        self.list_frame.grid(row=0, column=0)

        self.volume_frame = VolumeFrame(master=self.master, text="Volume")
        self.volume_frame.grid(row=0, column=2, rowspan=2)

        self.btn_frame = Frame(self.master)
        self.btn_frame.grid(row=1, column=0, padx=20)

        self.listbox = Listbox(self.list_frame, bg='black', fg='green', selectbackground='gray', selectforeground='black', selectmode=EXTENDED, width=48)
        self.listbox.pack(fill=X, padx=20, pady=(20, 0))
        self.slider = ttk.Scale(self.list_frame, value=0, from_=0, to=100, orient=HORIZONTAL, command=self.slide)
        self.slider.pack(fill=X, padx=20)

        # setting images
        global img_1, img_2, img_3, img_4, img_5
        img_1 = ImageConverter.create_image(f'img/next.png', 40, 180)
        img_2 = ImageConverter.create_image(f'img/play.png', 40, 0)
        img_3 = ImageConverter.create_image(f'img/pause.png', 40, 0)
        img_4 = ImageConverter.create_image(f'img/stop.png', 40, 0)
        img_5 = ImageConverter.create_image(f'img/next.png', 40, 0)

        images = [{"file": img_1, "command": self.previous},
                  {"file": img_2, "command": self.play},
                  {"file": img_3, "command": self.pause},
                  {"file": img_4, "command": self.stop},
                  {"file": img_5, "command": self.next}]

        for index, image in enumerate(images):
            self.btn = Button(self.btn_frame, image=image["file"], command=image["command"], relief=FLAT)
            self.btn.grid(row=0, column=index, sticky=N+S+E+W, padx=8)

        self.info_frame = Frame(self.master)
        self.info_frame.grid(row=2, column=0, sticky=S)
        self.info_label = Label(self.info_frame, text="", relief=SUNKEN, anchor=E, width=48)
        self.info_label.pack(fill=X)

    @staticmethod
    def create_image(path, rotation):
        img = Image.open(path)
        img = img.rotate(rotation)
        img = img.resize((50, 50))
        img = ImageTk.PhotoImage(img)
        return img

    def load_list(self):
        with open('last_list.pkl', 'rb') as f:
            self.song_list = pickle.load(f)
            self.listbox.insert("end", *[song['name'] for song in self.song_list])

    def add_song(self):
        """Open dialogbox, chose one file and load it"""
        settings = dict(initialdir=pathlib.Path().absolute(), title="Choose songs", filetypes=(
            ("flac files", "*.flac"),
            ("mp3 files", "*.mp3"),
            ("all files", "*")))

        song = filedialog.askopenfilename(**settings)

        self.update_playlist(song)
        self.listbox.insert("end", self.song_list[-1]['name'])

    def add_songs(self):
        """Open dialogbox, chose multiple files and load them"""
        settings = dict(initialdir=pathlib.Path().absolute(), title="Choose songs", filetypes=(
            ("flac files", "*.flac"),
            ("mp3 files", "*.mp3"),
            ("all files", "*")))

        songs = filedialog.askopenfilenames(**settings)

        for song in songs:
            self.update_playlist(song)

        self.listbox.insert("end", *[song['name'] for song in self.song_list])
        with open('last_list.pkl', 'wb') as f:
            pickle.dump(self.song_list, f)

    def update_playlist(self, song):
        self.song_list.append({'name': os.path.splitext(os.path.basename(song))[0],
                               'path': song,
                               'flac_object': FLAC(song),
                               'length': FLAC(song).info.length,
                               'flength': time.strftime('%M:%S', time.gmtime(round(FLAC(song).info.length)))})

    def remove_song(self):
        """Pick a song from listbox and remove it"""
        self.stop()
        self.listbox.delete("anchor")
        pygame.mixer.music.stop()

    def remove_songs(self):
        """Remove all songs from listbox"""
        self.stop()
        self.listbox.delete(0, "end")
        pygame.mixer.music.stop()

    def get_song(self):
        try:
            song_to_play_index = self.listbox.curselection()[0]
            return self.song_list[song_to_play_index]
        except IndexError:
            return None

    def play(self):
        """Play selected song"""
        self.stopped = False

        # Try to load song and play it, otherwise throw info
        try:
            song_to_play = self.get_song()
            pygame.mixer.music.load(song_to_play['path'])
            pygame.mixer.music.play(loops=0)
            self.song_time(song_to_play)
        except TypeError:
            self.info_label.config(text=f"Load list first")

    def next(self):
        """Play next song on the playlist"""
        current = self.listbox.curselection()[0]
        if current < self.listbox.size() - 1:
            self.listbox.selection_clear(current)
            self.listbox.activate(current+1)
            self.listbox.select_set(current+1)
            self.play()

    def previous(self):
        """Play previous song on the playlist"""
        current = self.listbox.curselection()[0]
        if current > 0:
            self.listbox.selection_clear(current)
            self.listbox.activate(current-1)
            self.listbox.select_set(current-1)
            selected = self.files[self.listbox.selection_get()]
            pygame.mixer.music.load(selected)
            pygame.mixer.music.play(loops=0)

    def pause(self):
        """Pause or unpause the song"""
        if not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
        else:
            pygame.mixer.music.unpause()
            self.paused = False

    def stop(self):
        """Stop song"""
        # Reset slider
        self.slider.config(value=0)
        pygame.mixer.music.stop()
        self.info_label.config(text='')

        # Set stop variable
        self.stopped = True

    def slide(self, event):
        song_to_play = self.get_song()
        pygame.mixer.music.load(song_to_play['path'])
        pygame.mixer.music.play(loops=0, start=int(self.slider.get()))

    def song_time(self, song):
        if self.stopped:
            return
        # Song parameters
        name, path, flac_object, length, flength = song.values()

        position = int(pygame.mixer.music.get_pos() / 1000)
        fposition = time.strftime('%M:%S', time.gmtime(position))

        slider_time = int(self.slider.get())

        print(slider_time, position)

        position += 1
        if slider_time == int(length):
            pass
        elif slider_time == position:
            self.slider.config(to=length, value=position)
        elif self.paused:
            pass
        else:
            self.slider.config(to=length, value=slider_time)
            fposition = time.strftime('%M:%S', time.gmtime(slider_time))
            self.info_label.config(text=f"{fposition} of {flength}")
            next_time = slider_time + 1
            self.slider.config(to=length, value=next_time)

        self.info_label.after(1000, lambda: self.song_time(song))


class VolumeFrame(LabelFrame):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.create_images()
        self.create_elements()

    def create_elements(self):
        self.slider = ttk.Scale(self, value=.25, from_=1, to=0, orient=VERTICAL, command=self.volume,length=200)
        self.slider.grid(row=1, column=0)
        self.label = Label(self, text=f"{(self.slider.get()):.02f}", anchor='center')
        self.label.grid(row=0, column=0)
        self.image = Label(self, image=vol_img_5, anchor=S)
        self.image.grid(row=2, column=0, sticky=S)

    @staticmethod
    def create_images():
        global vol_img_1, vol_img_2, vol_img_3, vol_img_4, vol_img_5
        vol_img_1 = ImageConverter.create_image(f'img/volume1.png', 50)
        vol_img_2 = ImageConverter.create_image(f'img/volume2.png', 50)
        vol_img_3 = ImageConverter.create_image(f'img/volume3.png', 50)
        vol_img_4 = ImageConverter.create_image(f'img/volume4.png', 50)
        vol_img_5 = ImageConverter.create_image(f'img/volume5.png', 50)

    def volume(self, volume_level):
        volume_level = float(volume_level)
        pygame.mixer.music.set_volume(volume_level)
        self.label.config(text=f"{volume_level:.02f}")

        if volume_level == 0: self.image.config(image=vol_img_1)
        elif volume_level <= .25: self.image.config(image=vol_img_2)
        elif volume_level <= .50: self.image.config(image=vol_img_3)
        elif volume_level <= .75: self.image.config(image=vol_img_4)
        elif volume_level <= 1: self.image.config(image=vol_img_5)


class ImageConverter:
    @staticmethod
    def create_image(path, size, rotation=0):
        img = Image.open(path)
        img = img.rotate(rotation)
        img = img.resize((size, size))
        return ImageTk.PhotoImage(img)


if __name__ == '__main__':
    root = Tk()
    app = MusicPlayer(master=root)
    app.mainloop()
