import numpy as np
import scipy.io.wavfile


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
        self.sr, self.y = scipy.io.wavfile.read(path)
        self.sa = np.empty(np.shape(self.y))

    def detect_silence(self, top):
        trim_level = np.amax(self.y) * top

        if np.shape(self.y)[1] == 1:
            silent_indices = clear_array(np.where(abs(self.y) < trim_level)[0])
            self.sa = indices_to_values(silent_indices, self.y)

        elif np.shape(self.y)[1] == 2:
            channel1 = clear_array(np.where(abs(self.y[:, 0]) < trim_level)[0])
            channel2 = clear_array(np.where(abs(self.y[:, 1]) < trim_level)[0])
            if channel1.size > channel2.size:
                channel2 = np.pad(channel2, (int((channel1.size - channel2.size)/2),), 'symmetric')
            elif channel2.size > channel1.size:
                channel1 = np.pad(channel1, (int((channel2.size - channel1.size)/2),), 'symmetric')
            channel1_silence = indices_to_values(channel1, self.y[:, 0])
            channel2_silence = indices_to_values(channel2, self.y[:, 1])
            self.sa = np.column_stack((channel1_silence, channel2_silence))

        else:
            print("Incorrect count of audio channels")

    def cut_silence(self):
        if np.shape(self.y)[1] == 1:
            self.y = replace_arrays(self.y, self.sa)

        elif np.shape(self.y)[1] == 2:
            channel1 = replace_arrays(self.y[:, 0], self.sa[:, 0])
            channel2 = replace_arrays(self.y[:, 1], self.sa[:, 1])
            self.y = np.column_stack((channel1, channel2))

        else:
            print("Incorrect count of audio channels")

    def export(self, path):
        scipy.io.wavfile.write(path, self.sr, self.y)
