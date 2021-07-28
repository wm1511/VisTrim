import tkinter as tk
from tkinter import filedialog
import tkinter.ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np


def file_browse():
    path = filedialog.askopenfilename(initialdir="/", title="Trim silence from", filetypes=[("Sound files", "*.wav")])
    return path


def file_save():
    path = filedialog.asksaveasfilename(initialdir="/", title="Save trimmed file", filetypes=[("Sound files", "*.wav")])
    return path


class CanvasDraw:
    def __init__(self, wave):
        self.root = tk.Tk()
        self.root.title('Silence trimmer')

        fig = plt.figure(figsize=(15, 5))
        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=2, columnspan=3)

        #naprawić przyciski, dodać otwieranie i zapisywanie z przycisku
        fresh_button = tk.Button(self.root, text='Plot fresh', command=self.plot(wave.y, wave.sr, 'blue'))
        fresh_button.grid(column=1, row=4, pady=20)

        top_frame = tk.Frame(self.root)
        top_label = tk.Label(top_frame, text="% of sound amplitude considered as silence")
        top_label.pack(side=tk.BOTTOM)
        top_entry = tk.Entry(top_frame, width=5)
        top_entry.insert(0, 5)
        top_entry.pack(side=tk.TOP)
        top_frame.grid(column=0, row=4, sticky=tk.W, padx=50, pady=20)

        wave.detect_silence(int(top_entry.get()))
        silence_button = tk.Button(self.root, text='Plot silence', command=self.plot(wave.sa, wave.sr, 'red'))
        silence_button.grid(column=2, row=4, sticky=tk.E, padx=50, pady=20)

        toolbar_frame = tk.Frame(self.root)
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
        toolbar_frame.grid(column=1, row=0, pady=20)

        tkinter.ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(column=0, row=1, columnspan=3, sticky='ew')
        tkinter.ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(column=0, row=3, columnspan=3, sticky='ew')

        self.root.mainloop()

    def plot(self, array, sr, color):
        time = np.linspace(0., array.shape[0] / sr, array.shape[0])
        if np.shape(array)[1] == 1:
            plt.plot(time, array, color=color)
        elif np.shape(array)[1] == 2:
            plt.subplot(211)
            plt.title("Channel 1")
            plt.plot(time, array[:, 0], color=color)
            plt.subplot(212)
            plt.title("Channel 2")
            plt.plot(time, array[:, 1], color=color)
        else:
            print("Incorrect count of audio channels")
        plt.xlabel('Time [s]')
        plt.ylabel('Amplitude')
        self.canvas.draw()
