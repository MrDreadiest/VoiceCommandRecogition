import numpy as np
import tensorflow as tf 
import tensorflow_io as tfio
from tensorflow.keras import models
import json

SETTINGS_FILE_TF = 'tf_settings.json'

class TensorFlowHelper:
    def __init__(self):

        self.frame_rate = 16000
        self.frame_rate_min = 100
        self.frame_rate_max = 8000

        self.n_fft = int(0.05 * self.frame_rate)  #50ms
        self.hop_length = int(0.02 * self.frame_rate)  # 20 ms
        self.n_mels = 128

        self.model_name = "model"

        self.load_settings()
        
        self.model = models.load_model(self.model_name)

    def get_prediction(self,audio):
         
         spectrogram = self.preprocess_audiobuffer(audio)
         prediction = tf.nn.softmax(self.model(spectrogram))

         return prediction

    def load_settings(self): 
        # Load the UDP settings from the JSON file
        with open(SETTINGS_FILE_TF, 'r', encoding='utf-8') as f:
            try:
                settings = json.load(f)
                
                self.frame_rate = int(settings['frame_rate'])
                self.frame_rate_min = int(settings['frame_rate_min'])
                self.frame_rate_max = int(settings['frame_rate_max'])
                self.n_fft = int(settings['n_fft'])
                self.hop_length = int(settings['hop_length'])
                self.n_mels = int(settings['n_mels'])
                self.model_name = settings['model']
                self.set_flag = True

            except BaseException as e:
                print('The file contains invalid JSON')
                self.set_flag = False

    def get_spectrogram(self, audio):
            
            # Convert to spectrogram
            spectrogram = tfio.audio.spectrogram(audio, nfft=self.n_fft, window=self.n_fft, stride=self.n_mels)
            
            # Convert to mel-spectrogram
            mel_spectrogram = tfio.audio.melscale(spectrogram, rate=self.frame_rate, mels=self.n_mels, fmin=self.frame_rate_min, fmax=self.frame_rate_max)
            # Convert to db scale mel-spectrogram
            dbscale_mel_spectrogram = tfio.audio.dbscale(mel_spectrogram, top_db=80)
            # Add a `channels` dimension, so that the spectrogram can be used
            # as image-like input data with convolution layers (which expect
            # shape (`batch_size`, `height`, `width`, `channels`).
            dbscale_mel_spectrogram = dbscale_mel_spectrogram[..., tf.newaxis]
            #    spectrogram = tf.expand_dims(spectrogram, axis=2)
            
            return dbscale_mel_spectrogram

    def preprocess_audiobuffer(self, audio):
        #  normalize from [-32768, 32767] to [-1, 1]
        audio =  audio / 32768
        audio = tf.convert_to_tensor(audio, dtype=tf.float32)
        spectogram = self.get_spectrogram(audio)
        
        # add one dimension
        spectogram = tf.expand_dims(spectogram, 0)
        
        return spectogram