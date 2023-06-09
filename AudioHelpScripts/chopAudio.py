# python .\chopAudio.py ..\\DATA\\noise ..\\DATA\\data_aug_3s\\05-tlo 16000 3  

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


    files_path = glob(os.path.join(load_main_dir, '*.*'))

    print(f"Plikow: {len(files_path)}")

    for k, file_path in enumerate(files_path[:]):
        data = ah.load_audio(file_path, sample_rate)

        frames_per_clip = sample_rate * chop_duration
        number_of_chops = math.floor(data.__len__() / frames_per_clip)

        for i in range(0, number_of_chops):
            frame_start = int(i * frames_per_clip)
            frame_end = int((i + 1) * frames_per_clip)

            choped_data = data[frame_start: frame_end]

            file_path_new = ah.get_new_file_name(save_main_dir, file_path)

            choped_data = librosa.util.fix_length(choped_data, size=int(chop_duration * sample_rate))

            ah.save_audio(file_path_new, choped_data, sample_rate)

        ah.printProgressBar(k + 1, files_path.__len__(), prefix='Progress:', suffix='Complete', length=50)
