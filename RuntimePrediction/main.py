import numpy as np

import tensorflow as tf
from tensorflow.keras import models

import record_helper as rh
from tf_helper import preprocess_audiobuffer

# Avoid OOM errors by setting GPU Memory Consumption Growth
# physical_devices = tf.config.experimental.list_physical_devices('GPU')
# if len(physical_devices) > 0:
#     tf.config.experimental.set_memory_growth(physical_devices[0], True)

COMMANDS = ['00-odrzuc_bron', '01-obroc_sie', '02-na_kolana', '03-gleba', '04-rece_na_glowe']

loaded_model = models.load_model("model-61")


def predict_mic():
    audio = rh.record_audio()
    spectrogram = preprocess_audiobuffer(audio)
    prediction = loaded_model(spectrogram)
    print(prediction.numpy())
    label_prediction = np.argmax(prediction, axis=1)
    command = COMMANDS[label_prediction[0]]
    print("Pred label:", command)
    return command


if __name__ == "__main__":

    while True:
        command = predict_mic()
