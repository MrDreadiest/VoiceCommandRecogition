import os
import wave
from glob import glob
import matplotlib.pyplot as plt

import numpy as np

import librosa
import librosa.display
import soundfile as sf


LOAD_DATA_PATH = 'data_long'
SAVE_DATA_PATH = 'data_short'


def get_new_path(current_path:str):
    path = os.path.normpath(current_path).split(os.sep)
    path[0]=SAVE_DATA_PATH
    return os.path.join(*(path))

def get_audio_time(path:str) -> float:
    obj = wave.open(path,"rb")
    samples= obj.getnframes()
    rate = obj.getframerate()
    obj.close()

    return float(samples/rate)


file_paths = glob(LOAD_DATA_PATH+'\*\*.*')

print(f"Załączonych plików {len(file_paths)}")

lengths = []

data0, sr0 = librosa.load("WindowApp\\data\\00-odrzuc_bron\\f_0002_0_0_w.wav", sr=44100)

for file in file_paths:
    # Load some audio
    data, sr = librosa.load(file, sr=44100)
    
    new_file_path = get_new_path(file)
    head, tail = os.path.split(new_file_path)

    if os.path.exists(head) == False:
        os.makedirs(head)
    data_fix = librosa.util.fix_length(data=data, size=data0.__len__())        
    sf.write(file=new_file_path,data=data_fix,samplerate=sr, subtype='PCM_32')


