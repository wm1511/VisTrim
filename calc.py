import numpy as np
import scipy.io.wavfile
import ui


class SoundWave:
    def __init__(self, path):
        try:
            self.sr, self.y = scipy.io.wavfile.read(path)
        except ValueError as e:
            print(e)
            ui.data_msb()
        self.wa = None
        self.na = None
        self.sa = None

    def detect_silence(self, top, silence_length):
        trim_level = np.amax(self.y) * (top / 100)
        self.reshape_array(silence_length)
        self.get_silence(trim_level)

    def reshape_array(self, silence_length):
        if len(np.shape(self.y)) == 1:
            pad_front = int((silence_length - (self.y.size % silence_length)) / 2)
            pad_end = int((silence_length - (self.y.size % silence_length)) / 2) \
                if self.y.size % 2 == 0 else int((silence_length - (self.y.size % silence_length)) / 2) + 1
            new_length = int((self.y.size + pad_front + pad_end) / silence_length)
            self.wa = np.reshape(np.pad(self.y, (pad_front, pad_end)), (new_length, silence_length))
        elif len(np.shape(self.y)) == 2:
            pad_front = int((silence_length - (self.y[:, 0].size % silence_length)) / 2)
            pad_end = int((silence_length - (self.y[:, 0].size % silence_length)) / 2) \
                if self.y[:, 0].size % 2 == 0 else int((silence_length - (self.y[:, 0].size % silence_length)) / 2) + 1
            new_length = int((self.y[:, 0].size + pad_front + pad_end) / silence_length)
            padded = np.row_stack((np.pad(self.y[:, 0], (pad_front, pad_end)),
                                   np.pad(self.y[:, 1], (pad_front, pad_end))))
            self.wa = np.reshape(padded, (len(np.shape(self.y)), new_length, silence_length))

    def get_silence(self, trim_level):
        cut_arrays = []
        silence_array = np.zeros(self.wa.shape, dtype=int)
        if len(np.shape(self.wa)) == 2:
            for i in range(self.wa.shape[0]):
                if np.abs(np.amax(self.wa[i, :])) < trim_level:
                    silence_array[i, :] = self.wa[i, :]
                else:
                    cut_arrays.append(self.wa[i, :])
            self.sa = np.reshape(silence_array, (self.wa.shape[0] * self.wa.shape[1]))
            self.na = np.reshape(np.row_stack(cut_arrays), (len(cut_arrays) * self.wa.shape[1]))
        elif len(np.shape(self.wa)) == 3:
            for i in range(self.wa.shape[1]):
                if np.abs(np.amax(self.wa[0, i, :])) < trim_level:
                    silence_array[:, i, :] = self.wa[:, i, :]
                else:
                    cut_arrays.append(self.wa[:, i, :])
            self.sa = np.rot90(np.reshape(silence_array, (self.wa.shape[0], self.wa.shape[1] * self.wa.shape[2])), k=3)
            ch1 = np.row_stack([i[0, :] for i in cut_arrays])
            ch2 = np.row_stack([i[1, :] for i in cut_arrays])
            self.na = np.rot90(np.row_stack((np.reshape(ch1, (ch1.shape[0] * ch1.shape[1])),
                                             np.reshape(ch2, (ch2.shape[0] * ch2.shape[1])))), k=3)

    def export_int16(self, path):
        if path != '':
            scipy.io.wavfile.write(path + '.wav', self.sr, self.na.astype(np.int16))

    def export_int32(self, path):
        if path != '':
            scipy.io.wavfile.write(path + '.wav', self.sr, self.na.astype(np.int32))
