import sys
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


def get_command_labels(load_main_dir: str):
    return os.listdir(load_main_dir)


def get_label(file_path):
    return os.path.normpath(file_path).split(os.sep)[-2]

# Zwraca nazwę pliku ze ścieżki wraz z rozszerzeniem
def get_filename(file_path):
    _, file_name = os.path.split(file_path)
    return file_name


# Zwraca krotkę nazwa , rozszerzenie na podstawie nazwy
def split_filename(file_name):
    return get_filename(file_name).split(".")[0], get_filename(file_name).split(".")[-1]


# Zwraca nową następną w kolejności nazwę pliku
def get_new_filename(mian_save_dir, file_path):
    file_name = get_filename(file_path)
    _, extension = split_filename(file_name)

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
