import threading
import pyaudio
import numpy as np

class AudioRecorderThread(threading.Thread):
    def __init__(self, chunk_size=1024, sample_rate=44100, channels=1):
        super(AudioRecorderThread, self).__init__()
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.channels = channels
        self.frames = []

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=self.channels,
                                      rate=self.sample_rate,
                                      input=True,
                                      frames_per_buffer=self.chunk_size)

    def run(self):
        while True:
            data = self.stream.read(self.chunk_size)
            self.frames.append(np.frombuffer(data, dtype=np.int16))

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

if __name__ == '__main__':
    recorder = AudioRecorderThread()
    recorder.start()

    # Do something while recording...
    while True:
        print(len(recorder.frames))










import threading
import queue
import pyaudio
import numpy as np

class AudioRecorderThread(threading.Thread):
    def __init__(self, chunk_size=1024, sample_rate=44100, channels=1):
        super(AudioRecorderThread, self).__init__()
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.channels = channels
        self.frames_queue = queue.Queue()

        self._stop_event = threading.Event()

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=self.channels,
                                      rate=self.sample_rate,
                                      input=True,
                                      frames_per_buffer=self.chunk_size)

    def run(self):
        while not self._stop_event.is_set():
            data = self.stream.read(self.chunk_size)
            self.frames_queue.put(np.frombuffer(data, dtype=np.int16))

    def stop(self):
        self._stop_event.set()
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def get_frames(self):
        frames = []
        while not self.frames_queue.empty():
            frames.append(self.frames_queue.get())
        return frames
    



import threading
import pyaudio
import numpy as np

class AudioRecorderThread(threading.Thread):
    def __init__(self, chunk_size=1024, sample_rate=44100, channels=1):
        super(AudioRecorderThread, self).__init__()
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.channels = channels
        self.frames = []
        self.lock = threading.Lock()
        self.condition = threading.Condition()

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=self.channels,
                                      rate=self.sample_rate,
                                      input=True,
                                      frames_per_buffer=self.chunk_size)

    def run(self):
        while True:
            data = self.stream.read(self.chunk_size)
            with self.lock:
                self.frames.append(np.frombuffer(data, dtype=np.int16))
                self.condition.notify()

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def get_latest_frame(self):
        with self.lock:
            if len(self.frames) > 0:
                return self.frames[-1]
            else:
                return None

    def wait_for_new_frame(self):
        with self.condition:
            self.condition.wait()

if __name__ == '__main__':
    recorder = AudioRecorderThread()
    recorder.start()

    # Do something while recording...
    while True:
        frame = recorder.get_latest_frame()
        if frame is not None:
            # Process the frame...
            pass
        else:
            recorder.wait_for_new_frame()