import threading
import pyaudio
import numpy as np
import json

SETTINGS_FILE_UDP = 'audio_settings.json'

class AudioListenerThread:
    def __init__(self, interval):
        self.interval = interval
        self.timer = None
        self.flag = True

        self.frames = []
        

        self.pyaudio = pyaudio.PyAudio()
        self.stream = None

        self.format = pyaudio.paInt16
        self.channels = None
        self.frame_rate = None
        self.frames_per_buffer = None
        self.duration = None

        self.set_flag = False

        self.load_settings()

        # initialize empty numpy array to store recorded audio
        self.buffer = np.zeros(int(self.frame_rate * self.duration))

    def load_settings(self): 
        # Load the UDP settings from the JSON file
        with open(SETTINGS_FILE_UDP, 'r', encoding='utf-8') as f:
            try:
                settings = json.load(f)
                
                self.frames_per_buffer = int(settings['frames_per_buffer'])
                self.channels = int(settings['channels'])
                #self.format = int(settings['format'])
                self.frame_rate = int(settings['frame_rate'])
                self.duration = float(settings['duration'])

                self.set_flag = True

            except BaseException as e:
                print('The file contains invalid JSON')
                self.set_flag = False

    def get_data(self):
        return self.buffer

    def start(self):
        self.flag = True
        self.timer = threading.Timer(self.interval, self.run)
        self.timer.start()

    def stop(self):
        self.flag = False
        if self.timer:
            self.timer.cancel()
            
            self.stream.stop_stream()
            self.stream.close()
            self.pyaudio.terminate()

    def run(self):
        try:
            if self.flag:
                self.record_audio() # call the function
                self.start()
        except KeyboardInterrupt:
            self.stop()

    def record_audio(self):
        if  self.set_flag :

            print("listening")

            self.stream = self.pyaudio.open(
                format=self.format,
                channels=self.channels,
                rate=self.frame_rate,
                input=True,
                frames_per_buffer=self.frames_per_buffer
            )

            while self.flag:
                self.framesframes = []
                self.frames.append(self.stream.read(self.frames_per_buffer))

                frames_np = np.frombuffer(b''.join(self.frames), dtype=np.int16)

                if frames_np.__len__() >= self.buffer.__len__():
                    self.buffer = frames_np[ frames_np.__len__() - self.buffer.__len__():]
                    self.frames = self.frames[1:]



