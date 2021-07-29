import tkinter as tk
from tkinter import filedialog
import tkinter.ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np


def file_browse():
    path = filedialog.askopenfilename(initialdir='/', title='Trim silence from', filetypes=[('Sound files', '*.wav')])
    return path


def file_save():
    path = filedialog.asksaveasfilename(initialdir='/', title='Save trimmed file', filetypes=[('Sound files', '*.wav')])
    return path


def plot(array, sr, color):
    time = np.linspace(0., array.shape[0] / sr, array.shape[0])
    if np.shape(array)[1] == 1:
        plt.plot(time, array, color=color)
    elif np.shape(array)[1] == 2:
        plt.subplot(211)
        plt.title('Channel 1')
        plt.plot(time, array[:, 0], color=color)
        plt.subplot(212)
        plt.title('Channel 2')
        plt.plot(time, array[:, 1], color=color)
    else:
        print('Incorrect count of audio channels')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')


def only_numbers(char):
    return char.isdigit()


class App:
    def __init__(self, wave):
        self.wave = wave
        self.root = tk.Tk()
        self.root.title('Silence trimmer')
        fig = plt.figure(figsize=(15, 5))
        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=2, columnspan=3)

        misc_frame = tk.Frame(self.root)
        save_button = tk.Button(misc_frame, text='Save file', command=self.export_file)
        save_button.pack()
        exit_button = tk.Button(misc_frame, text='Exit', command=self.root.quit)
        exit_button.pack()
        misc_frame.grid(column=2, row=4, padx=50, pady=20, sticky=tk.E)

        plot_frame = tk.Frame(self.root)
        fresh_button = tk.Button(plot_frame, text='Plot source wave', command=self.plot_fresh)
        fresh_button.pack()
        silence_button = tk.Button(plot_frame, text='Plot silence', command=self.plot_silence)
        silence_button.pack()
        cut_button = tk.Button(plot_frame, text='Cut silence', command=self.cut_silence)
        cut_button.pack()
        plot_frame.grid(column=1, row=4, padx=50, pady=20)

        top_frame = tk.Frame(self.root)
        top_label = tk.Label(top_frame, text='% of sound amplitude considered as silence')
        top_label.pack(side=tk.TOP)
        validation = top_frame.register(only_numbers)
        self.top_entry = tk.Entry(top_frame, width=5, validate='key', validatecommand=(validation, '%S'))
        self.top_entry.insert(0, 5)
        self.top_entry.pack()
        top_button = tk.Button(top_frame, text='Confirm value', command=self.initialize_detection)
        top_button.pack(side=tk.BOTTOM)
        top_frame.grid(column=0, row=4, sticky=tk.W, padx=50, pady=20)

        toolbar_frame = tk.Frame(self.root)
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
        toolbar_frame.grid(column=1, row=0, pady=20)

        tkinter.ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(column=0, row=1, columnspan=3, sticky='ew')
        tkinter.ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(column=0, row=3, columnspan=3, sticky='ew')

        self.root.mainloop()

    def plot_fresh(self):
        plot(self.wave.y, self.wave.sr, 'blue')
        self.canvas.draw()

    def plot_silence(self):
        plot(self.wave.sa, self.wave.sr, 'red')
        self.canvas.draw()

    def plot_cut(self):
        plot(self.wave.y, self.wave.sr, 'green')
        self.canvas.draw()

    def plot_clear(self):
        plt.subplot()
        self.canvas.draw()

    def initialize_detection(self):
        self.wave.detect_silence(int(self.top_entry.get()))

    def cut_silence(self):
        self.wave.cut_silence()
        self.plot_clear()
        self.plot_cut()

    def export_file(self):
        self.wave.export(file_save())
