import os
import threading
import wave
import math
from glob import glob
import matplotlib.pyplot as plt

import numpy as np
import random

import librosa
import librosa.display
import soundfile as sf

import noisereduce as nr

import AudioHelper as ah


def reduce_noise(data, sample_rate, noisy_part_start=0.0, noisy_part_end=1.0):
    # perform noise reduction
    noisy_part = data[int(noisy_part_start * sample_rate):int(noisy_part_end * sample_rate)]
    data_reduced = nr.reduce_noise(y=data, y_noise=noisy_part, sr=sample_rate)

    return data_reduced


def get_red_trim(data, sample_rate, db_trim, noisy_part_start=0.0, noisy_part_end=1.0):
    # Get noice reduce data
    data_reduce = reduce_noise(data, sample_rate, int(noisy_part_start), int(sample_rate * noisy_part_end))
    data_reduce_trim, index = librosa.effects.trim(data_reduce[int(sample_rate * noisy_part_end):], frame_length=512,
                                                   hop_length=32, top_db=db_trim)

    return data_reduce[int(sample_rate * noisy_part_end) + index[0]:int(sample_rate * noisy_part_end) + index[1]]


def get_org_trim(data, sample_rate, db_trim, noisy_part_start=0.0, noisy_part_end=1.0):
    # Get noice reduce data
    data_reduce = reduce_noise(data, sample_rate, noisy_part_start, int(sample_rate * noisy_part_end))
    data_reduce_trim, index = librosa.effects.trim(data_reduce[int(sample_rate * noisy_part_end):], frame_length=128,
                                                   hop_length=32, top_db=db_trim)

    return data[int(sample_rate * noisy_part_end) + index[0]:int(sample_rate * noisy_part_end) + index[1]]


def get_trim_index(data, sample_rate, db_trim, noisy_part_start=0.0, noisy_part_end=1.0):
    # Get noice reduce data
    data_reduce = reduce_noise(data, sample_rate, int(noisy_part_start), int(sample_rate * noisy_part_end))
    _, index = librosa.effects.trim(data_reduce[int(sample_rate * noisy_part_end):], frame_length=512,
                                    hop_length=32, top_db=db_trim)

    return int(sample_rate * noisy_part_end) + index[0], int(sample_rate * noisy_part_end) + index[1]


# Print iterations progress
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


# Shift audio to the left plus assigned offset of given frame. Offset 0.0 - 0 %
def shift_trimed_audio_left(data, duration: float, sample_rate, offset_cut=0.0):
    shift_size = math.floor(data.__len__() * offset_cut)
    remain_size = data.__len__() - shift_size

    zero_padding = np.zeros((duration * sample_rate) - remain_size)
    return np.concatenate((data[shift_size:], zero_padding))


# Shift audio to the right plus assigned offset of given frame. Offset 0.0 - 0 %
def shift_trimed_audio_right(data, duration: float, sample_rate, offset_cut=0.0):
    shift_size = math.floor(data.__len__() * offset_cut)
    remain_size = data.__len__() - shift_size

    zero_padding = np.zeros((duration * sample_rate) - remain_size)
    return np.concatenate((zero_padding, data[:remain_size]))


# Shift audio to the center of given frame
def shift_trimed_audio_center(data, duration: float, sample_rate):
    output_duration = (duration * sample_rate)
    input_duration = data.__len__()

    if (output_duration - input_duration) % 2 != 0:
        zero_padding_left = np.zeros(math.floor((output_duration - input_duration) / 2))
        zero_padding_right = np.zeros(math.ceil((output_duration - input_duration) / 2))
    else:
        zero_padding_left = np.zeros(int((output_duration - input_duration) / 2))
        zero_padding_right = np.zeros(int((output_duration - input_duration) / 2))

    return np.concatenate((zero_padding_left, data, zero_padding_right))


# Shift audio to the center of given frame
def shift_audio_center(data, index_start, index_end, duration: float, sample_rate):
    # print(f"index_start: {index_start}")
    # print(f"index_end: {index_end}")
    # print(f"data: {len(data)}")

    output_duration = (duration * sample_rate)
    input_duration = data[index_start:index_end].__len__()

    output = np.zeros(output_duration)

    if (output_duration - input_duration) % 2 != 0:
        zero_padding_left = np.zeros(math.floor((output_duration - input_duration) / 2))
        zero_padding_right = np.zeros(math.ceil((output_duration - input_duration) / 2))
    else:
        zero_padding_left = np.zeros(int((output_duration - input_duration) / 2))
        zero_padding_right = np.zeros(int((output_duration - input_duration) / 2))

    # Wypełnienie lewej strony
    if zero_padding_left.__len__() > 0:

        data_left = data[:index_start]
        data_left_length = data_left.__len__()

        # print(f"data_left_length: {data_left_length}")
        # print(f"zero_padding_left: {zero_padding_left.__len__()}")

        # Dane orginalne pokryją część lub nie
        if data_left_length >= zero_padding_left.__len__():
            if zero_padding_left.__len__() > 0:
                zero_padding_left = data_left[data_left_length - zero_padding_left.__len__():]
        else:
            if zero_padding_left.__len__() > 0:
                for i in range(0, data_left_length):
                    zero_padding_left[(i + 1) * -1] = data_left[(i + 1) * -1]

    # Wypełnienie prawej strony
    if zero_padding_right.__len__() > 0:

        data_right = data[index_end:]
        data_right_length = data_right.__len__()

        # print(f"data_right_length: {data_right_length}")
        # print(f"zero_padding_right: {zero_padding_right.__len__()}")

        # Dane orginalne pokryją część lub nie
        if data_right_length >= zero_padding_right.__len__():
            if zero_padding_right.__len__() > 0:
                zero_padding_right = data_right[:data_right_length - zero_padding_right.__len__()]
        else:
            if zero_padding_right.__len__() > 0:
                for i in range(0, data_right_length):
                    zero_padding_right[i] = data_right[i]

    output = np.concatenate((zero_padding_left, data[index_start:index_end], zero_padding_right))

    return output


def shift_audio_left(data, index_start, index_end, duration: float, sample_rate, offset_cut=0.0):
    output_duration = (duration * sample_rate)
    input_duration = data[index_start:index_end].__len__()

    shift_size = math.floor(input_duration * offset_cut)
    zero_padding = np.zeros(output_duration)

    data_trimmed = data[index_start + shift_size:]

    if data_trimmed.__len__() >= zero_padding.__len__():
        for i in range(0, zero_padding.__len__()):
            zero_padding[i] = data_trimmed[i]
    else:
        for i in range(0, data_trimmed.__len__()):
            zero_padding[i] = data_trimmed[i]

    return zero_padding


def shift_audio_right(data, index_start, index_end, duration: float, sample_rate, offset_cut=0.0):
    output_duration = (duration * sample_rate)
    input_duration = data[index_start:index_end].__len__()

    shift_size = math.floor(input_duration * offset_cut)
    zero_padding = np.zeros(output_duration)

    data_trimmed = data[:index_end - shift_size]

    if data_trimmed.__len__() >= zero_padding.__len__():
        for i in range(0, zero_padding.__len__()):
            zero_padding[(i+1) * -1] = data_trimmed[(i+1) * -1]
    else:
        for i in range(0, data_trimmed.__len__()):
            zero_padding[(i+1) * -1] = data_trimmed[(i+1) * -1]

    return zero_padding


def thread_loop_task(start, end, data_set):
    print(f"Thread {threading.current_thread().name} processing {end - start} samples.")

    for i, file_path in enumerate(data_set[start:end]):
        # Load oryginal audio
        data, sample_rate = librosa.load(file_path, sr=SAMPLE_RATE_REDUCTION)

        # Get reduced audio
        data_reduced = reduce_noise(data, sample_rate)

        base_dataset = (data, data_reduced)

        # Find start, Eed position
        index_start, index_end = get_trim_index(data_reduced, sample_rate, DB_TRIM)

        for base_data in base_dataset:
            base_data_center = shift_audio_center(base_data, index_start, index_end, NEAREST_UP_DURATION, sample_rate)

            file_name = ah.get_file_name(file_path)
            command = ah.get_label(file_path)
            file_name_new = ah.get_next_path(SAVE_DATA, command, file_name)

            base_data_center = librosa.util.fix_length(base_data_center, size=int(NEAREST_UP_DURATION * sample_rate))
            ah.save_audio(file_name_new, base_data_center, sample_rate)

        percentage_offset = SHIFT_PERCENTAGE_OFFSET

        for base_data in base_dataset:

            # Shift left
            for offset in percentage_offset[:]:
                data_shift_left = shift_audio_left(base_data, index_start, index_end, NEAREST_UP_DURATION, sample_rate,
                                                   offset)

                semitone_factor = random.uniform(SEMITONES_FACTOR_MIN, SEMITONES_FACTOR_MAX)
                data_shift_left = ah.pitch_scale(data_shift_left, SAMPLE_RATE_REDUCTION, semitone_factor)

                gain_factor = 0
                while gain_factor == 0:
                    gain_factor = random.uniform(GAIN_FACTOR_MIN, GAIN_FACTOR_MAX)

                data_shift_left = ah.random_gain(data_shift_left, gain_factor)

                noise_percentage_factor = random.uniform(NOISE_PERCENTAGE_FACTOR_MIN, NOISE_PERCENTAGE_FACTOR_MAX)
                data_shift_left = ah.add_white_noise(data_shift_left, noise_percentage_factor)

                inverse_polarity_rate = random.uniform(INVERSE_POLARITY_MIN, INVERSE_POLARITY_MAX)
                if (inverse_polarity_rate >= 0.5):
                    data_shift_left = ah.invert_polarity(data_shift_left)

                file_name = ah.get_file_name(file_path)
                command = ah.get_label(file_path)
                file_name_new = ah.get_next_path(SAVE_DATA, command, file_name)

                data_shift_left = librosa.util.fix_length(data_shift_left, size=int(NEAREST_UP_DURATION * sample_rate))
                ah.save_audio(file_name_new, data_shift_left, SAMPLE_RATE_REDUCTION)

            # Shift right
            for offset in percentage_offset[:]:
                data_shift_right = shift_audio_right(base_data, index_start, index_end, NEAREST_UP_DURATION,
                                                    sample_rate,
                                                    offset)

                semitone_factor = random.uniform(SEMITONES_FACTOR_MIN, SEMITONES_FACTOR_MAX)
                data_shift_right = ah.pitch_scale(data_shift_right, SAMPLE_RATE_REDUCTION, semitone_factor)

                gain_factor = 0
                while gain_factor == 0:
                    gain_factor = random.uniform(GAIN_FACTOR_MIN, GAIN_FACTOR_MAX)

                data_shift_right = ah.random_gain(data_shift_right, gain_factor)

                noise_percentage_factor = random.uniform(NOISE_PERCENTAGE_FACTOR_MIN, NOISE_PERCENTAGE_FACTOR_MAX)
                data_shift_right = ah.add_white_noise(data_shift_right, noise_percentage_factor)

                inverse_polarity_rate = random.uniform(INVERSE_POLARITY_MIN, INVERSE_POLARITY_MAX)
                if (inverse_polarity_rate >= 0.5):
                    data_shift_right = ah.invert_polarity(data_shift_right)

                file_name = ah.get_file_name(file_path)
                command = ah.get_label(file_path)
                file_name_new = ah.get_next_path(SAVE_DATA, command, file_name)

                data_shift_right = librosa.util.fix_length(data_shift_right,
                                                          size=int(NEAREST_UP_DURATION * sample_rate))
                ah.save_audio(file_name_new, data_shift_right, SAMPLE_RATE_REDUCTION)
        


LOAD_DATA = '..\\DATA\\data_org_23'

SAVE_DATA = '..\\DATA\\data_aug_23'

NUM_THREADS = 16

SAMPLE_RATE = 44100  # HZ
SAMPLE_RATE_REDUCTION = 16000
FIX_TIME_DURATION = 3  # SECONDS
DB_TRIM = 15

AUGM_PARAM_ORG_COPY = True
AUGM_PARAM_ORG_REDUCE = True

NEAREST_UP_DURATION = 0

SEMITONES_FACTOR_MIN = -2
SEMITONES_FACTOR_MAX = 1

GAIN_FACTOR_MIN = 1.0
GAIN_FACTOR_MAX = 10.0

NOISE_PERCENTAGE_FACTOR_MIN = 0.00
NOISE_PERCENTAGE_FACTOR_MAX = 0.01

TIME_STRETCH_RATE_MIN = 0.5
TIME_STRETCH_RATE_MAX = 1.5

INVERSE_POLARITY_MIN = 0
INVERSE_POLARITY_MAX = 1

SHIFT_PERCENTAGE_OFFSET = [0.0, 0.075, 0.15]

if __name__ == "__main__":

    file_paths = glob(LOAD_DATA + '\\*\\*.wav')
    file_paths_length = len(file_paths[:])

    print("DATASET AUGMENTATION")
    print(f"Loaded {file_paths_length} files.")

    commands = ah.get_command_labels(LOAD_DATA)
    print(f"Commands: {commands}")

    print(f"Calculate sample lengths ...")
    lengths_array = np.zeros(file_paths_length)

    for i, file_path in enumerate(file_paths[:]):
        # Update progress bar
        printProgressBar(i, file_paths_length, prefix='Progress:', suffix='Complete', length=50)
    
        # Load data
        data, sample_rate = librosa.load(file_path, sr=SAMPLE_RATE_REDUCTION)
    
        # Trim Audio
        data_red_trim = get_red_trim(data, sample_rate, DB_TRIM)
    
        lengths_array[i] = librosa.get_duration(y=data_red_trim, sr=sample_rate)
    
    print("Duration  min: " + str(lengths_array.min()) + file_paths[np.argmin(lengths_array)])
    print("Duration  max: " + str(lengths_array.max()) + file_paths[np.argmax(lengths_array)])
    print("Duration mean: " + str(lengths_array.mean()))


    for i, len in enumerate(lengths_array):
        if len >= 2.0 :
            print(f"{len}   {file_paths[i]}")
    #Get nearest upper duration in seconds
    #NEAREST_UP_DURATION = math.ceil(lengths_array.max()*100)/100
    NEAREST_UP_DURATION = math.ceil(lengths_array.max())

    #NEAREST_UP_DURATION = 3

    # NEAREST_UP_DURATION = 2
    print(f"NEAREST_UP_DURATION : {NEAREST_UP_DURATION} seconds")

    # Przygotowanie katalogu pod zapis
    ah.prepare_save_dir(SAVE_DATA, commands)

    threads = []
    total_tasks = file_paths_length
    tasks_per_thread = total_tasks // NUM_THREADS

    for i in range(NUM_THREADS):
        start = i * tasks_per_thread
        end = (i + 1) * tasks_per_thread if i < NUM_THREADS - 1 else total_tasks
        t = threading.Thread(target=thread_loop_task, args=(start, end, file_paths))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
