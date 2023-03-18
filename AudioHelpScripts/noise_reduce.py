import os
import wave
from glob import glob
import matplotlib.pyplot as plt

import numpy as np

import librosa
import librosa.display
import soundfile as sf

import noisereduce as nr

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

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 99, fill = '█', printEnd = "\r"):
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

def reduce_noise(data, sample_rate, noisy_part_start, noisy_part_end):
    
    # perform noise reduction 
    noisy_part = data[noisy_part_start:noisy_part_end]
    data_reduced = nr.reduce_noise(y=data, y_noise=noisy_part, sr=sample_rate)

    return data_reduced

def silence_trim(data, sample_rate, db_trim):
    # Get noice reduce data
    data_reduce = reduce_noise(data,sample_rate, 0, int(sample_rate*1.0))
    data_reduce_trim , index = librosa.effects.trim(data_reduce[int(sample_rate*1.0):],frame_length=128, hop_length=32, top_db=db_trim)

    return data[int(sample_rate*1.0)+index[0]:int(sample_rate*1.0)+index[1]]

LOAD_DATA_PATH = 'data_org_1'
SAVE_DATA_PATH = 'data_reduce_1'

SR = 44100

if __name__ == "__main__":

    file_paths = glob(LOAD_DATA_PATH+'\*\*.*')
    file_paths_length = len(file_paths)

    print(f"Loaded {file_paths_length} files.")

    for i,file in enumerate(file_paths):
        
        # Load some audio
        data, sample_rate = librosa.load(file, sr=SR)

        data_fixed = librosa.util.fix_length(data, size=3*sample_rate)

        # Reduce noises
        data_reduce = reduce_noise(data_fixed, sample_rate, 0, int(sample_rate*0.2))

        # Trim Audio
        #data_trim = silence_trim(data,sample_rate,28)
        
        # Get splited new path
        new_file_path = get_new_path(file)
        head, tail = os.path.split(new_file_path)

        #print(f"{tail} Duration : {librosa.get_duration(y=data,sr=sample_rate):.5f} -> {librosa.get_duration(y=data_trim,sr=sample_rate):.5f}")

        # Check if new path exists
        if os.path.exists(head) == False:
            os.makedirs(head)

        # Save file
        sf.write(file=new_file_path, data=data_reduce, samplerate=sample_rate, subtype='PCM_16')

        #update progress bar
        printProgressBar(i + 1, file_paths_length, prefix = 'Progress:', suffix = 'Complete', length = 35)