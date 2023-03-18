import pyaudio
import numpy as np

FRAMES_PER_BUFFER = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
FRAME_RATE = 16000
DURATION = 2

p = pyaudio.PyAudio()

def record_audio():
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=FRAME_RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER
    )

    #print("start recording...")

    frames = []
    for i in range(0, int(FRAME_RATE / FRAMES_PER_BUFFER * DURATION)):
        data = stream.read(FRAMES_PER_BUFFER)
        frames.append(data)

    # print("recording stopped")

    stream.stop_stream()
    stream.close()
    
    audio = np.frombuffer(b''.join(frames), dtype=np.int16)
    zero_padding = np.zeros((DURATION * FRAME_RATE) - audio.__len__())
    
    return np.concatenate((audio, zero_padding))


def terminate():
    p.terminate()