import threading
import pyaudio
import numpy as np
import noisereduce as nr

class AudioListenerThread:
    def __init__(self, interval, settings):
        self.interval = interval
        self.timer = None
        self.flag = True

        self.frames = []
        

        self.pyaudio = pyaudio.PyAudio()
        self.stream = None

        self.format = pyaudio.paInt16
        self.channels = settings.channels
        self.frame_rate = settings.frame_rate
        self.frames_per_buffer = settings.frames_per_buffer
        self.duration = settings.duration

        # initialize empty numpy array to store recorded audio
        self.buffer = np.zeros(int(self.frame_rate * self.duration))

    def get_audio(self):
        return self.buffer
    
    def get_audio_clear(self):
        return nr.reduce_noise(y=self.buffer, sr=self.frame_rate)

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

        self.stream = self.pyaudio.open(
            format=self.format,
            channels=self.channels,
            rate=self.frame_rate,
            input=True,
            frames_per_buffer=self.frames_per_buffer
        )

        while self.flag:

            self.frames.append(self.stream.read(self.frames_per_buffer))

            frames_np = np.frombuffer(b''.join(self.frames), dtype=np.int16)

            if frames_np.__len__() >= self.buffer.__len__():
                self.buffer = frames_np[ frames_np.__len__() - self.buffer.__len__():]
                self.frames = self.frames[1:]
