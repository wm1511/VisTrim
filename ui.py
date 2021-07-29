import tkinter as tk
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog
import matplotlib.pyplot as plt
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
        print('Incorrect count of audio channels')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')


def only_numbers(char):
    return char.isdigit()


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Silence trimmer')
        fig = plt.figure(figsize=(15, 5))
        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=2, columnspan=3)

        misc_frame = tk.Frame(self.root)
        open_button = tk.Button(misc_frame, text='Open file', command=self.open_file)
        open_button.grid(row=0, pady=5)
        save_button = tk.Button(misc_frame, text='Save file', command=self.export_file)
        save_button.grid(row=1, pady=5)
        exit_button = tk.Button(misc_frame, text='Exit', command=self.root.quit)
        exit_button.grid(row=2, pady=5)
        misc_frame.grid(column=0, row=4, padx=50, pady=20, sticky=tk.W)

        plot_frame = tk.Frame(self.root)
        fresh_button = tk.Button(plot_frame, text='Plot source wave', command=self.plot_fresh)
        fresh_button.grid(row=0, pady=5)
        silence_button = tk.Button(plot_frame, text='Plot silence', command=self.plot_silence)
        silence_button.grid(row=1, pady=5)
        cut_button = tk.Button(plot_frame, text='Cut silence', command=self.cut_silence)
        cut_button.grid(row=2, pady=5)
        plot_frame.grid(column=2, row=4, padx=50, pady=20, sticky=tk.E)

        top_frame = tk.Frame(self.root)
        top_label = tk.Label(top_frame, text='% of sound amplitude considered as silence')
        top_label.grid()
        validation = top_frame.register(only_numbers)
        self.top_entry = tk.Entry(top_frame, width=5, validate='key', validatecommand=(validation, '%S'))
        self.top_entry.grid(row=1, pady=5)
        top_button = tk.Button(top_frame, text='Confirm value', command=self.initialize_detection)
        top_button.grid(row=2, pady=5)
        top_frame.grid(column=1, row=4, padx=50, pady=20)

        toolbar_frame = tk.Frame(self.root)
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
        toolbar_frame.grid(column=1, row=0, pady=20)

        tkinter.ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(column=0, row=1, columnspan=3, sticky='ew')
        tkinter.ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(column=0, row=3, columnspan=3, sticky='ew')

        self.root.mainloop()

    def plot_fresh(self):
        try:
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
        plot(self.wave.y, self.wave.sr, 'green')
        self.canvas.draw()

    def plot_clear(self):
        plt.clf()
        self.canvas.draw()

    def initialize_detection(self):
        try:
            self.wave.detect_silence(int(self.top_entry.get()))
        except AttributeError:
            tk.messagebox.showerror(title="File error", message="You have to open sound file first!")

    def cut_silence(self):
        try:
            self.wave.cut_silence()
            self.plot_clear()
            self.plot_cut()
        except AttributeError:
            tk.messagebox.showerror(title="File error", message="You have to open sound file first!")

    def open_file(self):
        self.plot_clear()
        self.wave = calc.SoundWave(file_browse())
        self.plot_fresh()

    def export_file(self):
        try:
            if np.amax(self.wave.y) > np.iinfo(np.int16).max:
                self.wave.export_int32(file_save())
            elif np.amax(self.wave.y) <= np.iinfo(np.int16).max:
                self.wave.export_int16(file_save())
            else:
                print('Incorrect data')
        except AttributeError:
            tk.messagebox.showerror(title="File error", message="You have to open sound file first!")
