import librosa
import librosa.display
import numpy as np
import soundfile as sf
import scipy.io
import scipy.io.wavfile
import time


def clear_array(array):
    part_arrays = []
    begin = array[0]
    current = 0
    length = 0
    for el in array:
        if current + 1 < array.size:
            if el + 1 == array[current + 1]:
                length += 1
                if length > 220:
                    part_arrays.append(array[begin:current])
                    length = 0
                    begin = current + 1
            else:
                length = 0
                begin = current + 1
            current += 1
    return np.concatenate(part_arrays)


# def indices_to_values(index_array, value_array):
#     current = 0
#     result_array = np.zeros((value_array.size,), dtype=float)
#     for _ in value_array:
#         if current + 1 < value_array.size:
#             if current in index_array:
#                 result_array[current] = value_array[current]
#             current += 1
#     return result_array


def indices_to_values(index_array, value_array):
    result_array = np.zeros((value_array.size,), dtype=float)
    for index in index_array:
        result_array[index] = value_array[index]
    return result_array


def replace_arrays(source_array, silence_array):
    current = 0
    added = 0
    result_array = np.empty((source_array.size - np.count_nonzero(silence_array),))
    for sample in silence_array:
        if sample == 0:
            result_array[added] = source_array[current]
            added += 1
        current += 1
    return result_array


class SoundWave:
    def __init__(self, path):
        self.y, self.sr = librosa.load(path)
        print(time.perf_counter())
        self.sa = np.empty(self.y.size,)
        print(time.perf_counter())

    def detect_silence(self, top):
        silent_indices = clear_array(np.where(abs(self.y) < top)[0])
        self.sa = indices_to_values(silent_indices, self.y)

    def cut_silence(self):
        self.y = replace_arrays(self.y, self.sa)

    def export(self, path):
        sf.write(path, self.y, self.sr, subtype='PCM_24')
