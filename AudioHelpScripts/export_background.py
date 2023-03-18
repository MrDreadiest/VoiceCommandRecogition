import os
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


def add_white_noise(data, noise_percentage_factor):
    noise = np.random.normal(0, data.std(), data.size)
    augmented_data = data + noise * noise_percentage_factor
    return augmented_data


def pitch_scale(signal, sr, semitones_factor):
    return librosa.effects.pitch_shift(y=signal, sr=sr, n_steps=semitones_factor)


def random_gain(data, gain_factor):
    augmented_data = data * gain_factor
    return augmented_data


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


def get_command_labels(load_main_dir: str):
    return os.listdir(load_main_dir)


def get_label(file_path):
    return os.path.normpath(file_path).split(os.sep)[-2]


def get_new_command_label(commands, new_label: str, separator='-') -> str:
    last_command = commands[-1]
    last_command_iter = int(last_command.split(separator)[0])
    last_command_iter += 1
    return f"{last_command_iter:02d}{separator}{new_label}"


def get_file_name(file_path: str) -> str:
    return os.path.normpath(file_path).split(os.sep)[-1].split('.')[0]


# DESCRIPTION
def get_next_path(save_main_dir: str, command_label: str, file_name: str, extension="wav", separator='-'):
    flag = False
    iterator = 0
    path_new = os.path.join(save_main_dir, command_label, file_name + '.' + extension)

    while not flag:

        path_temp = os.path.normpath(path_new).split(os.sep)
        path_temp[-1] = file_name[:-2] + f"{separator}{iterator:02d}" + '.' + extension
        path_temp = os.path.join(*path_temp)

        iterator += 1

        if not os.path.exists(path_temp):
            flag = True
            path_new = path_temp

    return path_new


# Save wav file
def save_audio(file_path: str, data, sample_rate, subtype="PCM_16"):
    head, _ = os.path.split(file_path)

    if os.path.exists(head) == False:
        os.makedirs(head)

    # Save file
    sf.write(file=file_path, data=data, samplerate=sample_rate, subtype=subtype)


LOAD_DATA = '..\\DATA\\data_org_2'
SAVE_DATA = '..\\DATA\\data_augmented_2'
LABEL_NAME = 'tlo'

SAMPLE_RATE = 44100  # HZ
SAMPLE_RATE_REDUCTION = 16000
FIX_TIME_DURATION = 3  # SECONDS

AUGM_PARAM_ORG_COPY = True
AUGM_PARAM_ORG_REDUCE = True

NEAREST_UP_DURATION = 2

SEMITONES_FACTOR_MIN = -3
SEMITONES_FACTOR_MAX = 2

GAIN_FACTOR_MIN = 1.0
GAIN_FACTOR_MAX = 2.0

NOISE_PERCENTAGE_FACTOR_MIN = 0.0
NOISE_PERCENTAGE_FACTOR_MAX = 0.03

BACKGROUND_NOISE_START = 0.0  # in sec
BACKGROUND_NOISE_END = 1.0  # in sec

if __name__ == "__main__":
    file_paths = glob(LOAD_DATA + '\*\*.*')
    file_paths_length = len(file_paths)

    commands = get_command_labels(LOAD_DATA)

    print("GENERATE BACKGROUND NOISE BASED ON DATASET")
    print(f"Loaded {file_paths_length} files.")

    for i, file_path in enumerate(file_paths[:]):

        # Load data
        data, _ = librosa.load(file_path, sr=SAMPLE_RATE)
        data = librosa.util.fix_length(data, size=FIX_TIME_DURATION * SAMPLE_RATE, mode='edge')
        data = librosa.resample(data, orig_sr=SAMPLE_RATE, target_sr=SAMPLE_RATE_REDUCTION)

        background_data = librosa.effects.time_stretch(data[
                                                       int(BACKGROUND_NOISE_START * SAMPLE_RATE_REDUCTION):
                                                       int(BACKGROUND_NOISE_END * SAMPLE_RATE_REDUCTION)
                                                       ], rate=0.5)

        background_data = librosa.util.fix_length(background_data, size=NEAREST_UP_DURATION * SAMPLE_RATE_REDUCTION,
                                                  mode='edge')

        for i in range(0, 2):

            semitone_factor = random.uniform(SEMITONES_FACTOR_MIN, SEMITONES_FACTOR_MAX)
            background_data = pitch_scale(background_data, SAMPLE_RATE_REDUCTION, semitone_factor)

            gain_factor = 0
            while gain_factor == 0:
                gain_factor = random.uniform(GAIN_FACTOR_MIN, GAIN_FACTOR_MAX)

            background_data = random_gain(background_data, gain_factor)

            noise_percentage_factor = random.uniform(NOISE_PERCENTAGE_FACTOR_MIN, NOISE_PERCENTAGE_FACTOR_MAX)
            background_data = add_white_noise(background_data, noise_percentage_factor)

            file_name = get_file_name(file_path)
            command = get_new_command_label(commands, LABEL_NAME)

            file_name_new = get_next_path(SAVE_DATA, command, file_name)

            save_audio(file_name_new, background_data, SAMPLE_RATE_REDUCTION)

        printProgressBar(i + 1, file_paths_length, prefix='Progress:', suffix='Complete', length=50)
