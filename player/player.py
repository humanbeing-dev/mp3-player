from tkinter import *
from tkinter import filedialog
import tkinter.ttk as ttk
import pathlib, os
import pygame
from PIL import Image, ImageTk
import time
from mutagen.flac import FLAC


class Application(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.create_menu()
        self.create_frames()
        self.files = {}
        pygame.mixer.init()
        self.paused = False
        # self.scroll_value = IntVar()
        self.scroll_value = 0

    def create_menu(self):
        self.my_menu = Menu(self.master)

        self.add_menu = Menu(self.my_menu)
        self.add_menu.add_command(label="Add one song", command=self.add_song)
        self.add_menu.add_command(label="Add many songs", command=self.add_songs)

        self.remove_menu = Menu(self.my_menu)
        self.remove_menu.add_command(label="Remove one song", command=self.remove_song)
        self.remove_menu.add_command(label="Remove all songs", command=self.remove_songs)

        self.my_menu.add_cascade(label="Add Songs", menu=self.add_menu)
        self.my_menu.add_cascade(label="Remove Songs", menu=self.remove_menu)

        self.master.config(menu=self.my_menu)

    def create_frames(self):
        self.list_frame = Frame(self.master)
        self.list_frame.pack(fill=X)

        self.listbox = Listbox(self.list_frame, bg='black', fg='green', selectbackground='gray', selectforeground='black', selectmode=EXTENDED)
        self.listbox.pack(fill=X, padx=20, pady=(20, 0))


        # self.slider = Scale(self.list_frame, showvalue=0, from_=0, to=100, orient=HORIZONTAL, command=self.set_song)
        # self.slider.pack(fill=X, padx=20)
        self.slider = ttk.Scale(self.list_frame, value=0, from_=0, to=100, orient=HORIZONTAL, command=self.set_song)
        self.slider.pack(fill=X, padx=20)
        # my_label = Label(self.list_frame, text=self.slider.get()).pack()

        # def slide():
        #     my_label = Label(root, text=horizontal.get()).pack()
        #     root.geometry(f"{horizontal.get()}x{vertical.get()}")


        self.btn_frame = Frame(self.master)
        self.btn_frame.pack(fill=X, padx=20)

        global img_1
        img_1 = Image.open(f'img/next.png')
        img_1 = img_1.rotate(180)
        img_1 = img_1.resize((50, 50))
        img_1 = ImageTk.PhotoImage(img_1)

        global img_2
        img_2 = Image.open(f'img/play.png')
        img_2 = img_2.rotate(0)
        img_2 = img_2.resize((50, 50))
        img_2 = ImageTk.PhotoImage(img_2)

        global img_3
        img_3 = Image.open(f'img/pause.png')
        img_3 = img_3.rotate(0)
        img_3 = img_3.resize((50, 50))
        img_3 = ImageTk.PhotoImage(img_3)

        global img_4
        img_4 = Image.open(f'img/stop.png')
        img_4 = img_4.rotate(0)
        img_4 = img_4.resize((50, 50))
        img_4 = ImageTk.PhotoImage(img_4)

        global img_5
        img_5 = Image.open(f'img/next.png')
        img_5 = img_5.rotate(0)
        img_5 = img_5.resize((50, 50))
        img_5 = ImageTk.PhotoImage(img_5)

        images = [{"name": "previous", "rotate": 180, "file": img_1, "command": self.previous},
                  {"name": "play", "rotate": 0, "file": img_2, "command": self.play},
                  {"name": "pause", "rotate": 0, "file": img_3, "command": self.pause},
                  {"name": "stop", "rotate": 0, "file": img_4, "command": self.stop},
                  {"name": "next", "rotate": 0, "file": img_5, "command": self.next}]

        for index, image in enumerate(images):
            self.btn = Button(self.btn_frame, image=image["file"], command=image["command"], relief=FLAT)
            self.btn.grid(row=0, column=index, sticky=N+S+E+W, padx=8)

        self.info_frame = Frame(self.master)
        self.info_frame.pack(fill=X, side=BOTTOM)
        self.info_label = Label(self.info_frame, text="", relief=SUNKEN, anchor=E)
        self.info_label.pack(fill=X)

    def play(self):
        selected = self.files[self.listbox.selection_get()]
        pygame.mixer.music.load(selected)
        pygame.mixer.music.play(loops=0)
        self.play_time()

    def next(self):
        current = self.listbox.curselection()[0]
        if current < self.listbox.size() - 1:
            self.listbox.selection_clear(current)
            self.listbox.activate(current+1)
            self.listbox.select_set(current+1)
            selected = self.files[self.listbox.selection_get()]
            pygame.mixer.music.load(selected)
            pygame.mixer.music.play(loops=0)

    def previous(self):
        current = self.listbox.curselection()[0]
        if current > 0:
            self.listbox.selection_clear(current)
            self.listbox.activate(current-1)
            self.listbox.select_set(current-1)
            selected = self.files[self.listbox.selection_get()]
            pygame.mixer.music.load(selected)
            pygame.mixer.music.play(loops=0)

    def pause(self):
        if not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
        else:
            pygame.mixer.music.unpause()
            self.paused = False

    def stop(self):
        pygame.mixer.music.stop()

    def add_song(self):
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
        start_path = pathlib.Path().absolute()
        songs = filedialog.askopenfilenames(
            initialdir=start_path,
            title="Choose songs",
            filetypes=(("flac files", "*.flac"),
                       ("mp3 files", "*.mp3"),
                       ("all files", "*")))

        self.files.update({os.path.basename(song): song for song in songs})
        self.listbox.insert("end", *self.files.keys())

    def remove_song(self):
        self.listbox.delete("anchor")
        pygame.mixer.music.stop()

    def remove_songs(self):
        self.listbox.delete(0, "end")
        pygame.mixer.music.stop()

    def play_time(self):
        get_time = round(pygame.mixer.music.get_pos()/1000)
        converted_time = time.strftime('%M:%S', time.gmtime(get_time))

        current_song_path = self.files[self.listbox.selection_get()]
        song_time = FLAC(current_song_path)
        converted_song_time = time.strftime('%M:%S', time.gmtime(song_time.info.length))

        self.scroll_value = round((abs(get_time)/song_time.info.length) * 100)

        if get_time >= song_time.info.length:
            self.next()

        self.info_label.config(text=f"{converted_time} of {converted_song_time}")
        self.info_label.after(1000, self.play_time)
        self.slider.set(self.scroll_value)

    def set_song(self, event):
        print(int(self.slider.get()))
        # current_song_path = self.files[self.listbox.selection_get()]
        # song = FLAC(current_song_path)
        # song_time = song.info.length
        # self.scroll_value = (self.slider.get())/100 * song_time
        #
        # pygame.mixer.music.set_pos(self.scroll_value)
        # self.play_time()


root = Tk()
root.title("ProMCS")
root.geometry("400x310")
app = Application(master=root)
app.mainloop()
