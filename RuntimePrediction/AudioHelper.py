import os
from glob import glob
import matplotlib.pyplot as plt

import numpy as np

import librosa
import librosa.display
import soundfile as sf

#
#   Modyfikacja audio
#

def add_white_noise(data, noise_percentage_factor):
    noise = np.random.normal(0, data.std(), data.size)
    augmented_data = data + noise * noise_percentage_factor
    return augmented_data

def pitch_scale(data, sr, semitones_factor):
    return librosa.effects.pitch_shift(y=data, sr=sr, n_steps=semitones_factor)


def random_gain(data, gain_factor):
    return data * gain_factor


def invert_polarity(data):
    return data * -1


def time_stretch(data, rate):
    return librosa.effects.time_stretch(y=data, rate=rate)

#
#   Operacje na nazwie i ścieżce pliku
#

def get_command_labels(load_main_dir: str):
    return os.listdir(load_main_dir)


def get_label(file_path):
    return os.path.normpath(file_path).split(os.sep)[-2]


def get_new_command_label(commands, new_label: str, separator='-') -> str:
    last_command = commands[-1]
    last_command_iter = int(last_command.split(separator)[0])
    last_command_iter += 1
    return f"{last_command_iter:02d}{separator}{new_label}"


# Zwraca nazwę pliku ze ścieżki wraz z rozszerzeniem
def get_file_name(file_path):
    _, file_name = os.path.split(file_path)
    return file_name


# Zwraca krotkę nazwa , rozszerzenie na podstawie nazwy
def split_file_name(file_name):
    return get_file_name(file_name).split(".")[0], get_file_name(file_name).split(".")[-1]


# Zwraca nową następną w kolejności nazwę pliku
def get_new_file_name(mian_save_dir, file_path):
    file_name = get_file_name(file_path)
    _, extension = split_file_name(file_name)

    file_path_new = os.path.join(mian_save_dir, file_name)

    flag = False
    iterator = 0

    while flag == False:

        path_temp = os.path.normpath(file_path_new).split(os.sep)
        path_temp[-1] = path_temp[-1].split(".")[0] + f"_{iterator:02d}" + "." + extension
        path_temp = os.path.join(*path_temp)

        iterator += 1

        if os.path.exists(path_temp) == False:
            flag = True
            file_path_new = path_temp

    return file_path_new


# DESCRIPTION
def get_next_path(save_main_dir: str, command_label: str, file_name: str, extension="wav", separator='_'):
    flag = False
    iterator = 0
    path_new = os.path.join(save_main_dir, command_label, file_name + '.' + extension)

    while not flag:

        path_temp = os.path.normpath(path_new).split(os.sep)
        path_temp[-1] = file_name[:] + f"{separator}{iterator:02d}" + '.' + extension
        path_temp = os.path.join(*path_temp)

        iterator += 1

        if not os.path.exists(path_temp):
            flag = True
            path_new = path_temp

    return path_new

# Zapis pliku
def save_audio(file_path: str, data, sample_rate, subtype="PCM_16"):
    head, _ = os.path.split(file_path)

    if os.path.exists(head) == False:
        try:
            os.makedirs(head)
        except:
            pass

    # Save file
    sf.write(file=file_path, data=data, samplerate=sample_rate, subtype=subtype)


def prepare_save_dir(mian_save_dir, commands):

    for command in commands:
        path = os.path.join(mian_save_dir,command)

        if os.path.exists(path) == False:
            try:
                os.makedirs(path)
            except:
                pass

# Ładowanie pliku audio
def load_audio(file_path, sample_rate):
    data, _ = librosa.load(file_path, sr=sample_rate)
    return data

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
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()
