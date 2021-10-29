import numpy as np
import scipy.io.wavfile
import ui


def clear_array(array, silence_length):
    part_arrays = []
    begin = array[0]
    current = 0
    length = 0
    for el in array:
        if current + 1 < array.size:
            if el + 1 == array[current + 1]:
                length += 1
                if length > silence_length:
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
        try:
            self.sr, self.y = scipy.io.wavfile.read(path)
        except ValueError as e:
            print(e)
            ui.data_msb()
        self.sa = np.empty(np.shape(self.y))

    def detect_silence(self, top, silence_length):
        trim_level = np.amax(self.y) * (top / 100)

        if len(np.shape(self.y)) == 1:
            silent_indices = clear_array(np.where(abs(self.y) < trim_level)[0], silence_length)
            self.sa = indices_to_values(silent_indices, self.y)

        elif len(np.shape(self.y)) == 2:
            # self.reshape_array(silence_length)
            # self.get_silence(trim_level)
            channel1 = clear_array(np.where(abs(self.y[:, 0]) < trim_level)[0], silence_length)
            channel2 = clear_array(np.where(abs(self.y[:, 1]) < trim_level)[0], silence_length)
            if channel1.size > channel2.size:
                delta = channel1.size - channel2.size
                channel2 = np.pad(channel2, (0, int(delta)), 'symmetric')
            elif channel2.size > channel1.size:
                delta = channel2.size - channel1.size
                channel1 = np.pad(channel1, (0, int(delta)), 'symmetric')
            channel1_silence = indices_to_values(channel1, self.y[:, 0])
            channel2_silence = indices_to_values(channel2, self.y[:, 1])
            self.sa = np.column_stack((channel1_silence, channel2_silence))

        else:
            ui.channel_msb()

    def cut_silence(self):
        if len(np.shape(self.y)) == 1:
            self.y = replace_arrays(self.y, self.sa)

        elif len(np.shape(self.y)) == 2:
            channel1 = replace_arrays(self.y[:, 0], self.sa[:, 0])
            channel2 = replace_arrays(self.y[:, 1], self.sa[:, 1])
            if channel1.size > channel2.size:
                delta = channel1.size - channel2.size
                channel2 = np.pad(channel2, (0, int(delta)), 'symmetric')
            elif channel2.size > channel1.size:
                delta = channel2.size - channel1.size
                channel1 = np.pad(channel1, (0, int(delta)), 'symmetric')
            self.y = np.column_stack((channel1, channel2))

        else:
            ui.channel_msb()

    def export_int16(self, path):
        if path != '':
            scipy.io.wavfile.write(path + '.wav', self.sr, self.y.astype(np.int16))

    def export_int32(self, path):
        if path != '':
            scipy.io.wavfile.write(path + '.wav', self.sr, self.y.astype(np.int32))

    def reshape_array(self, silence_length):
        pad_front = int((silence_length - (self.y[:, 0].size % silence_length)) / 2)
        pad_end = int((silence_length - (self.y[:, 0].size % silence_length)) / 2) \
            if self.y[:, 0].size % 2 == 0 else int((silence_length - (self.y[:, 0].size % silence_length)) / 2) + 1
        new_length = int((self.y[:, 0].size + pad_front + pad_end) / silence_length)

        if len(np.shape(self.y)) == 1:
            self.y = np.reshape(np.pad(self.y, (pad_front, pad_end)), (new_length, silence_length))
        elif len(np.shape(self.y)) == 2:
            self.y = np.row_stack((np.pad(self.y[:, 0], (pad_front, pad_end)),
                                   np.pad(self.y[:, 1], (pad_front, pad_end))))
            self.y = np.reshape(self.y, (2, new_length, silence_length))

    def get_silence(self, trim_level):
        silence_array = np.zeros(self.y.shape)
        for i in range(self.y.shape[1]):
            if np.abs(np.amax(self.y[0, i, :])) < trim_level:
                silence_array[:, i, :] = self.y[:, i, :]
        print(silence_array)
        # TODO If z ilością kanałów, zapisać jako self.sa
