import os
import wave
from glob import glob
import matplotlib.pyplot as plt

import numpy as np

import librosa
import librosa.display
import soundfile as sf

import noisereduce as nr

LOAD_DATA_PATH = 'data_org'
SAVE_DATA_PATH = 'data_reduce'


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

for file in file_paths:
    # Load some audio
    data, sr = librosa.load(file, sr=44100)
    
    # perform noise reduction 
    noisy_part = data[0:int(sr*1.0)]
    data_reduced_noise = nr.reduce_noise(y=data, y_noise=noisy_part, sr=sr)

    #rmse = librosa.feature.rms(y=data_reduced_noise, frame_length=256, hop_length=64)[0]
    #db = np.abs(librosa.power_to_db(rmse**2, ref=np.max).mean())

    #data_reduce_trim , index = librosa.effects.trim(data_reduced_noise,frame_length=256, hop_length=64, top_db=26)
    
    new_file_path = get_new_path(file)
    head, tail = os.path.split(new_file_path)

    #print(f"{60-db}_ {tail} Duration : {librosa.get_duration(y=data_reduced_noise,sr=sr)} -> {librosa.get_duration(y=data_reduce_trim,sr=sr)}")

    if os.path.exists(head) == False:
        os.makedirs(head)

    sf.write(file=new_file_path,data=data_reduced_noise,samplerate=sr, subtype='PCM_32')

    lengths.append(librosa.get_duration(y=data_reduce_trim,sr=sr))

lengths_array = np.array(lengths)
print(lengths_array.max())