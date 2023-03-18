import os
import wave
from glob import glob
import matplotlib.pyplot as plt

import numpy as np
import random

import librosa
import librosa.display
import soundfile as sf

def add_white_noise(signal, noise_percentage_factor):
    noise = np.random.normal(0, signal.std(), signal.size)
    augmented_signal = signal + noise * noise_percentage_factor
    return augmented_signal


def time_stretch(signal, time_stretch_rate):
    """Time stretching implemented with librosa:
    https://librosa.org/doc/main/generated/librosa.effects.pitch_shift.html?highlight=pitch%20shift#librosa.effects.pitch_shift
    """
    return librosa.effects.time_stretch(signal, time_stretch_rate)


def pitch_scale(signal, sr, num_semitones):
    """Pitch scaling implemented with librosa:
    https://librosa.org/doc/main/generated/librosa.effects.pitch_shift.html?highlight=pitch%20shift#librosa.effects.pitch_shift
    """
    return librosa.effects.pitch_shift(y=signal, sr=sr, n_steps=num_semitones)


def random_gain(signal, min_factor=-4, max_factor=4):
    gain_rate = random.uniform(min_factor, max_factor)
    augmented_signal = signal * gain_rate
    return augmented_signal


def invert_polarity(signal):
    return signal * -1


# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
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
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

# Genereate and save spectrogram
def get_spectrogram(data, sample_rate):

    n_fft = 2048
    hop_length = 512
    n_mels = 256

    MS = librosa.feature.melspectrogram(y=data, sr=sample_rate, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels, window="hann")
    MS_DB = librosa.power_to_db(MS, ref=np.max)
    
    return MS_DB

# Save spectrogram as image
def save_spectrogram(spectrogram, file_path):
    fig = plt.Figure()
    ax = fig.add_subplot(111)
    p = librosa.display.specshow(librosa.amplitude_to_db(spectrogram, ref=np.max), ax=ax, cmap='gray_r')

    # Get splited new path
    head, tail = os.path.split(file_path)

    # Check if new path exists
    if os.path.exists(head) == False:
        os.makedirs(head)   

    # Save file    
    fig.savefig(file_path)

def get_new_path(current_path:str, save_main_dir:str, estension:str):
    path = os.path.normpath(current_path).split(os.sep)
    
    path[0] = save_main_dir
    path[-1] = path[-1].split(".")[0] +"."+ estension
    
    return os.path.join(*(path))


# Load audio
def load_audio(file_path, sample_rate=44100):
    data, sample_rate = librosa.load(file_path, sr=sample_rate)
    return data, sample_rate

LOAD_DATA_PATH = 'data_augmented'
SAVE_DATA_PATH = 'data_spectograms'

SR = 44100

if __name__ == "__main__":
    print("Export augmented files as spectrograms.")

    # Get files path
    file_paths_augm = glob(LOAD_DATA_PATH + '\*\*.*')
    file_paths_augm_length = len(file_paths_augm)

    print(f"Loaded {file_paths_augm_length} files.")

    # Iterate over all files
    for i,file_path in enumerate(file_paths_augm):
        
        data, sample_rate = load_audio(file_path)
        spectrogram = get_spectrogram(data, sample_rate)

        file_path_new = get_new_path(file_path,SAVE_DATA_PATH,"png")

        save_spectrogram(spectrogram, file_path_new)

        # Update progress bar
        printProgressBar(i + 1, file_paths_augm_length, prefix = 'Progress:', suffix = 'Complete', length = 35)


        