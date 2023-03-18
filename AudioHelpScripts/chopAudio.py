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

import AudioHelper as ah


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


if __name__ == "__main__":

    load_main_dir = sys.argv[1]
    save_main_dir = sys.argv[2]

    sample_rate = int(sys.argv[3])
    chop_duration = float(sys.argv[4])

    if not os.path.exists(load_main_dir):
        print(f"Podany folder ({load_main_dir}) nie istniej.")
        exit

    if not type(sample_rate) == int:
        print("Podane próbowanie jest niepoprawne.")
        exit

    if not type(chop_duration) == float:
        print("Podana długość cięcia jest niepoprawna.")

    if not os.path.exists(save_main_dir):
        print(f"Podany folder został utworzony.")
        os.makedirs(save_main_dir)

    files_path = glob(os.path.join(load_main_dir, '*'))

    for k, file_path in enumerate(files_path[:]):
        data = ah.load_audio(file_path, sample_rate)

        frames_per_clip = sample_rate * chop_duration
        number_of_chops = math.floor(data.__len__() / frames_per_clip)

        for i in range(0, number_of_chops):
            frame_start = int(i * frames_per_clip)
            frame_end = int((i + 1) * frames_per_clip)

            choped_data = data[frame_start: frame_end]

            file_path_new = ah.GetNewFilename(save_main_dir, file_path)

            ah.SaveAudio(file_path_new, choped_data, sample_rate)

        printProgressBar(k + 1, files_path.__len__(), prefix='Progress:', suffix='Complete', length=50)
