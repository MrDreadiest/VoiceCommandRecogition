import os
import wave
from glob import glob
import matplotlib.pyplot as plt

import numpy as np

import librosa
import librosa.display
import soundfile as sf

import noisereduce as nr

LOAD_DATA_ORG = 'data_org_2'
LOAD_DATA_RED = 'data_reduce'
SR = 44100

def getLabel(path:str) -> str:
    pass

def getNewPath(current_path:str) -> str:
    path = os.path.normpath(current_path).split(os.sep)
    path[0]=SAVE_DATA_PATH
    return os.path.join(*(path))

def get_audio_time(path:str) -> float:
    obj = wave.open(path,"rb")
    samples= obj.getnframes()
    rate = obj.getframerate()
    obj.close()

    return float(samples/rate)

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



file_paths_org = glob(LOAD_DATA_ORG+'\*\*.*')
file_paths_org_length = len(file_paths_org)

file_paths_red = glob(LOAD_DATA_RED+'\*\*.*')
file_paths_red_length = len(file_paths_red)

file_paths_org_array = np.array(file_paths_org)
file_paths_red_array = np.array(file_paths_red)

random_index_array = np.random.choice(file_paths_org_length, 1, replace=False)

rows = random_index_array.__len__()
cols = 4


file_path_org =  file_paths_org_array[0]
file_path_red = file_paths_red_array[0]

samples_org, sample_rate = librosa.load(file_path_org, sr=SR)
samples_red, sample_rate = librosa.load(file_path_red, sr=SR)


n_fft = 2048
hop_length = 512
n_mels = 128

fig, ax = plt.subplots(nrows=2, ncols=1)

S = librosa.feature.melspectrogram(y=samples_red, sr=sample_rate, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels,window="hann")
S_DB = librosa.power_to_db(S, ref=np.max)
librosa.display.specshow(S_DB, sr=sample_rate, hop_length=hop_length, x_axis='time', y_axis='mel',ax=ax[0])

print(S_DB.shape)
plt.show()

