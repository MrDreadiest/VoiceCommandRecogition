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


LOAD_DATA = '..\\DATA\\data_org_1'
SAVE_DATA = '..\\DATA\\data_test_clear'
SAMPLE_RATE_REDUCTION = 16000
FIX_TIME_DURATION = 2

attempt = 0
human = 0

if __name__ == "__main__":
    
    file_paths = glob(LOAD_DATA + '\\*\\*.wav')
    file_paths_length = len(file_paths)

    print("ROZSZERZANIE DANYCH WEJŚCIOWYCH UCZENIA MASZYNOWEGO")
    print(f"Załadowano {file_paths_length} plików audio.")

    commands = ah.get_command_labels(LOAD_DATA)
    print(f"Wykryte komendy: {commands}")

    # Przygotowanie katalogu pod zapis
    ah.prepare_save_dir(SAVE_DATA, commands)

    for i, file_path in enumerate(file_paths):
        # Update progress bar
        ah.printProgressBar(i, file_paths_length, prefix='Progress:', suffix='Complete', length=50)

        # Load data
        data, sample_rate = librosa.load(file_path, sr=SAMPLE_RATE_REDUCTION)

        data = librosa.util.fix_length(data, size=int(FIX_TIME_DURATION * sample_rate))
        data = nr.reduce_noise(data,sample_rate)

        command = ah.get_label(file_path)
        command_id = commands.index(command)

        filename = ah.get_file_name(file_path)
        ah.save_audio(os.path.join(SAVE_DATA,command,filename),data,sample_rate)