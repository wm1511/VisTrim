import tkinter as tk
from tkinter import filedialog
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
        self.root.config(background="white")

        fig = plt.figure(figsize=(15, 5))
        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.get_tk_widget().pack()

        #interfejs do zrobienia
        plot_button = tk.Button(self.root, text='Plot', command=self.plot(wave.y, wave.sr, 'blue'))
        plot_button.pack()
        wave.detect_silence(0.05)
        silence_button = tk.Button(self.root, text='Plot', command=self.plot(wave.sa, wave.sr, 'red'))
        silence_button.pack()

        toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        toolbar.update()
        self.canvas.get_tk_widget().pack()

        self.root.mainloop()

    def plot(self, array, sr, color):
        time = np.linspace(0., array.shape[0] / sr, array.shape[0])
        if np.shape(array)[1] == 1:
            plt.plot(time, array, color=color)
        elif np.shape(array)[1] == 2:
            plt.subplot(211)
            plt.plot(time, array[:, 0], color=color)
            plt.subplot(212)
            plt.plot(time, array[:, 1], color=color)
        else:
            print("Incorrect count of audio channels")
        plt.xlabel('Time [s]')
        plt.ylabel('Amplitude')
        self.canvas.draw()
