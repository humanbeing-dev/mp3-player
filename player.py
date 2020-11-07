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
        pygame.mixer.init()
        super().__init__(master)
        self.master.title("ProMCS")
        self.master.geometry("400x310")

        self.create_menu()
        self.create_frames()

        self.paused = False
        self.files = {}
        self.song_index = 1
        self.song_list = []

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

        for index, song in enumerate(songs):
            self.song_list.append({'index': index,
                                   'name': os.path.splitext(os.path.basename(song))[0],
                                   'path': song,
                                   'flac_object': FLAC(song),
                                   'length': FLAC(song).info.length,
                                   'flength': time.strftime('%M:%S', time.gmtime(round(FLAC(song).info.length)))})

        self.listbox.insert("end", *[song['name'] for song in self.song_list])

    def remove_song(self):
        """Pick a song from listbox and remove it"""
        self.listbox.delete("anchor")
        pygame.mixer.music.stop()

    def remove_songs(self):
        """Remove all songs from listbox"""
        self.listbox.delete(0, "end")
        pygame.mixer.music.stop()

    def get_song(self):
        song_to_play_index = self.listbox.curselection()[0]
        return self.song_list[song_to_play_index]

    def play(self):
        """Play selected song"""
        # get active song
        song_to_play = self.get_song()

        # load and play song
        pygame.mixer.music.load(song_to_play['path'])
        pygame.mixer.music.play(loops=0)

        # set slider top value
        self.slider.config(to=song_to_play['length'])

        self.song_time(song_to_play)

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
        pygame.mixer.music.stop()

    def song_time(self, song):
        # Song parameters
        index, name, path, flac_object, length, flength = song.values()
        print(pygame.mixer.music.get_pos())
        # self.song_index += 1
        # pygame.mixer.music.load(song['path'])
        # pygame.mixer.music.play(loops=0, start=self.song_index)
        # print(pygame.mixer.music.get_pos())
        # Get song position
        # position = round(pygame.mixer.music.get_pos()/1000)
        # fposition = time.strftime('%M:%S', time.gmtime(position))
        # # Get current
        # slider_time = self.slider.get()
        # self.slider.config(value=position)
        #
        # print(position, fposition, slider_time)
        #
        # if slider_time == position:
        #     pass
        # else:
        #     pygame.mixer.music.play(loops=0, start=slider_time)
        #     position = slider_time
        #     self.slider.config(value=position)
        #
        #     fposition = time.strftime('%M:%S', time.gmtime(position))
        #
        # self.info_label.config(text=f"{fposition} of {flength}")
        self.info_label.after(1000, lambda: self.song_time(song))

        # if position >= round(length):
        #     self.next()


if __name__ == '__main__':
    root = Tk()
    app = Application(master=root)
    app.mainloop()
