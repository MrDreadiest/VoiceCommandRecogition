import numpy as np
import tensorflow as tf 
import tensorflow_io as tfio
from tensorflow.keras import models

class TensorflowHelper:
    def __init__(self, settings):

        self.frame_rate = settings.frame_rate
        self.frame_rate_min = settings.frame_rate_min
        self.frame_rate_max = settings.frame_rate_max

        self.n_fft = settings.n_fft
        self.hop_length = settings.hop_length
        self.n_mels = settings.n_mels

        self.model_name = settings.model
        self.commands = settings.commands

        self.model = models.load_model(self.model_name)

    def get_prediction(self,audio):
         
         spectrogram = self.preprocess_audiobuffer(audio)
         prediction = tf.nn.softmax(self.model(spectrogram))

         return prediction

    def get_spectrogram(self, audio):
            
            spectrogram = tfio.audio.spectrogram(audio, nfft=self.n_fft, window=self.n_fft, stride=self.n_mels)
            mel_spectrogram = tfio.audio.melscale(spectrogram, rate=self.frame_rate, mels=self.n_mels, fmin=self.frame_rate_min, fmax=self.frame_rate_max)
            dbscale_mel_spectrogram = tfio.audio.dbscale(mel_spectrogram, top_db=80)
            dbscale_mel_spectrogram = dbscale_mel_spectrogram[..., tf.newaxis]
            
            return dbscale_mel_spectrogram

    def preprocess_audiobuffer(self, audio):
        #  normalize from [-32768, 32767] to [-1, 1]
        audio =  audio / 32768
        audio = tf.convert_to_tensor(audio, dtype=tf.float32)
        spectogram = self.get_spectrogram(audio)
        
        # add one dimension
        spectogram = tf.expand_dims(spectogram, 0)
        
        return spectogram
    
    def is_ok(self):
         return self.set_flag