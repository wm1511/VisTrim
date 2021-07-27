import tkinter as tk
import matplotlib.pyplot as plt
import librosa.display
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)


def file_browse():
    path = filedialog.askopenfilename(initialdir="/", title="Trim silence from", filetypes=[("Sound files", "*.wav")])
    return path


def file_save():
    path = filedialog.asksaveasfilename(initialdir="/", title="Save trimmed file", filetypes=[("Sound files", "*.wav")])
    return path


#podzielić to trzeba ale chuj wie jak, może nie zamykać interfejsu w klasie
class UserInterface:
    def __init__(self, wave, top_silence):
        self.root = tk.Tk()
        self.root.title('Silence trimmer')
        self.root.config(background="white")
        plot_button = tk.Button(master=self.root, height=2, width=10, text="Plot", command=self.plot(wave, top_silence))
        plot_button.pack()
        self.root.mainloop()

    def plot(self, wave, top_silence):
        fig = plt.figure(figsize=(15, 5))
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        librosa.display.waveshow(wave.y, wave.sr, alpha=0.8)
        canvas.draw()
        canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(canvas, self.root)
        toolbar.update()
        canvas.get_tk_widget().pack()
        wave.detect_silence(top_silence)
        librosa.display.waveshow(wave.sa, wave.sr, alpha=0.8, color='red')
        canvas.draw()


class Graph:
    def __init__(self, wave, root):
        self.wave = wave
        self.fig = plt.figure(figsize=(15, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(self.canvas, root)
        toolbar.update()
        self.canvas.get_tk_widget().pack()

    def draw_fresh(self):
        librosa.display.waveshow(self.wave.y, self.wave.sr, alpha=0.8)
        self.canvas.draw()

    def draw_trimmed(self, top_silence):
        librosa.display.waveshow(self.wave.detect_silence(top_silence), self.wave.sr, alpha=0.8, color='red')
        self.canvas.draw()
