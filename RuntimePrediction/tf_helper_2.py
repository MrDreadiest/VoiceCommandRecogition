import numpy as np
import tensorflow as tf 
import tensorflow_io as tfio

# Set the seed value for experiment reproducibility.
seed = 42
tf.random.set_seed(seed)
np.random.seed(seed)

SR = 16000
F_MIN = 100
F_MAX = 8000

N_FFT = int(0.05 * SR)  # 25 ms, 50ms
HOP_LENGTH = int(0.02 * SR)  # 10 ms
N_MELS = 128

def get_spectrogram(waveform):
    
    n_fft = N_FFT
    hop_length = HOP_LENGTH
    n_mels = N_MELS

    f_min = F_MIN
    f_max = F_MAX
    
    # Convert to spectrogram
    spectrogram = tfio.audio.spectrogram(waveform, nfft=n_fft, window=n_fft, stride=n_mels)
      
    # Convert to mel-spectrogram
    mel_spectrogram = tfio.audio.melscale(spectrogram, rate=SR, mels=n_mels, fmin=f_min, fmax=f_max)
    # Convert to db scale mel-spectrogram
    dbscale_mel_spectrogram = tfio.audio.dbscale(mel_spectrogram, top_db=80)
    # Add a `channels` dimension, so that the spectrogram can be used
    # as image-like input data with convolution layers (which expect
    # shape (`batch_size`, `height`, `width`, `channels`).
    dbscale_mel_spectrogram = dbscale_mel_spectrogram[..., tf.newaxis]
    #    spectrogram = tf.expand_dims(spectrogram, axis=2)
    
    return dbscale_mel_spectrogram


def preprocess_audiobuffer(waveform):
    #  normalize from [-32768, 32767] to [-1, 1]
    waveform =  waveform / 32768
    waveform = tf.convert_to_tensor(waveform, dtype=tf.float32)
    spectogram = get_spectrogram(waveform)
    
    # add one dimension
    spectogram = tf.expand_dims(spectogram, 0)
    
    return spectogram