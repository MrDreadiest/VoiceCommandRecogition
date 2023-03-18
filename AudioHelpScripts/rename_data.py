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

LOAD_DATA = '..\\DATA\\data_org_2'

SAVE_DATA = '..\\DATA\\data_aug_2'

file_paths = glob(LOAD_DATA + '\\*\\*.wav')
file_paths_length = len(file_paths[:])


SAMPLE_RATE = 44100  # HZ
SAMPLE_RATE_REDUCTION = 16000
FIX_TIME_DURATION = 3  # SECONDS
DB_TRIM = 20

AUGM_PARAM_ORG_COPY = True
AUGM_PARAM_ORG_REDUCE = True

NEAREST_UP_DURATION = 4

SEMITONES_FACTOR_MIN = -2
SEMITONES_FACTOR_MAX = 1

GAIN_FACTOR_MIN = 1.0
GAIN_FACTOR_MAX = 10.0

NOISE_PERCENTAGE_FACTOR_MIN = 0.00
NOISE_PERCENTAGE_FACTOR_MAX = 0.02

SHIFT_PERCENTAGE_OFFSET = [0.0, 0.05, 0.10, 0.15]

for i, file_path in enumerate(file_paths):
    data, sample_rate = librosa.load(file_path, sr=SAMPLE_RATE)

    data = librosa.util.fix_length(data, size=int(NEAREST_UP_DURATION * sample_rate))

    file_name = ah.get_filename(file_path)
    _, extension = ah.split_file_name(file_name)
    command = ah.get_label(file_path)
    file_path_new = os.path.join(SAVE_DATA,command, file_name)

    path_temp = os.path.normpath(file_path_new).split(os.sep)
    path_temp[-1] = path_temp[-1].split(".")[0] + f"_c0" + "." + extension
    path_temp = os.path.join(*path_temp)

    print(path_temp)
    ah.save_audio(path_temp, data, sample_rate)
