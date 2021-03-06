import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import tkinter.filedialog
import matplotlib.pyplot as plt
from ttkthemes import ThemedTk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
import calc


def file_browse():
    path = tk.filedialog.askopenfilename(initialdir='/', title='Open file', filetypes=[('Sound files', '*.wav')])
    return path


def file_save():
    path = tk.filedialog.asksaveasfilename(initialdir='/', title='Save file', filetypes=[('Sound files', '*.wav')])
    return path


def plot(array, sr, color):
    time = np.linspace(0., array.shape[0] / sr, array.shape[0])
    if len(np.shape(array)) == 1:
        plt.plot(time, array, color=color)
    elif len(np.shape(array)) == 2:
        plt.subplot(211)
        plt.title('Left channel')
        plt.plot(time, array[:, 0], color=color)
        plt.subplot(212)
        plt.title('Right channel')
        plt.plot(time, array[:, 1], color=color)
    else:
        channel_msb()
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')


def channel_msb():
    tk.messagebox.showerror(title="File error", message="Incorrect count of audio channels!")


def data_msb():
    tk.messagebox.showerror(title="File error", message="Unsupported data format!")


class App:
    def __init__(self):
        self.wave = None
        self.root = ThemedTk(theme='arc', themebg=True)
        self.root.title('Silence trimmer')
        fig = plt.figure(figsize=(15, 5))
        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=2, columnspan=5)

        misc_frame = ttk.Frame(self.root)
        open_button = ttk.Button(misc_frame, text='Open file', command=self.open_file)
        open_button.grid(row=0, pady=5)
        save_button = ttk.Button(misc_frame, text='Save file', command=self.export_file)
        save_button.grid(row=1, pady=5)
        exit_button = ttk.Button(misc_frame, text='Exit', command=self.root.quit)
        exit_button.grid(row=2, pady=5)
        misc_frame.grid(column=0, row=4, padx=50, pady=20, sticky=tk.W)

        plot_frame = ttk.Frame(self.root)
        fresh_button = ttk.Button(plot_frame, text='Plot source wave', command=self.plot_fresh)
        fresh_button.grid(row=0, pady=5)
        cut_button = ttk.Button(plot_frame, text='Plot cut wave', command=self.cut_silence)
        cut_button.grid(row=1, pady=5)
        plot_frame.grid(column=4, row=4, padx=50, pady=20, sticky=tk.E)

        top_frame = ttk.Frame(self.root)
        top_label = ttk.Label(top_frame, text='% of sound amplitude considered as silence')
        top_label.grid()
        self.top_spinbox = ttk.Spinbox(top_frame, from_=1, to=99)
        self.top_spinbox.delete(0)
        self.top_spinbox.insert(0, 5)
        self.top_spinbox.grid(row=1, pady=5)
        top_frame.grid(column=3, row=4, padx=50, pady=20)

        detect_button = ttk.Button(self.root, text='Detect silence', command=self.initialize_detection)
        detect_button.grid(column=2, row=4, pady=5)

        chunk_frame = ttk.Frame(self.root)
        chunk_label = ttk.Label(chunk_frame, text='Minimal duration of silence chunk in ms')
        chunk_label.grid()
        self.chunk_spinbox = ttk.Spinbox(chunk_frame, from_=1, to=1000)
        self.chunk_spinbox.delete(0)
        self.chunk_spinbox.insert(0, 100)
        self.chunk_spinbox.grid(row=1, pady=5)
        chunk_frame.grid(column=1, row=4, padx=50, pady=20)

        toolbar_frame = ttk.Frame(self.root)
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
        toolbar_frame.grid(row=0, pady=20, columnspan=5)

        ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(column=0, row=1, columnspan=5, sticky='ew')
        ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(column=0, row=3, columnspan=5, sticky='ew')

        self.root.mainloop()

    def plot_fresh(self):
        try:
            self.plot_clear()
            plot(self.wave.y, self.wave.sr, 'blue')
            self.canvas.draw()
        except AttributeError:
            tk.messagebox.showerror(title="File error", message="You have to open sound file first!")

    def plot_silence(self):
        try:
            plot(self.wave.sa, self.wave.sr, 'red')
            self.canvas.draw()
        except AttributeError:
            tk.messagebox.showerror(title="File error", message="You have to open sound file first!")

    def plot_cut(self):
        try:
            self.plot_clear()
            plot(self.wave.na, self.wave.sr, 'green')
            self.canvas.draw()
        except AttributeError:
            tk.messagebox.showerror(title="File error", message="You have to cut sound first!")

    def plot_clear(self):
        plt.clf()
        self.canvas.draw()

    def initialize_detection(self):
        try:
            self.plot_clear()
            self.wave.detect_silence(int(self.top_spinbox.get()),
                                     int(int(self.chunk_spinbox.get()) * (self.wave.sr / 1000)))
            self.plot_fresh()
            self.plot_silence()
        except AttributeError as e:
            print(e)
            tk.messagebox.showerror(title="File error", message="You have to open sound file first!")

    def cut_silence(self):
        try:
            self.plot_cut()
        except AttributeError:
            tk.messagebox.showerror(title="File error", message="You have to open sound file first!")

    def open_file(self):
        try:
            self.plot_clear()
            self.wave = calc.SoundWave(file_browse())
            self.plot_fresh()
        except FileNotFoundError:
            tk.messagebox.showerror(title="File error", message="No file was selected!")

    def export_file(self):
        try:
            if np.amax(self.wave.na) > np.iinfo(np.int16).max:
                self.wave.export_int32(file_save())
            elif np.amax(self.wave.na) <= np.iinfo(np.int16).max:
                self.wave.export_int16(file_save())
            else:
                tk.messagebox.showerror(title="File error", message="Incorrect data!")
        except AttributeError:
            tk.messagebox.showerror(title="File error", message="You have to open sound file first!")
