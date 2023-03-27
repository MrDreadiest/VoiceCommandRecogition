import TensorflowHelper as tensorflow
import UdpSender as sender

import AudioHelper as audio_h
import AudioListener as audio_l
import MainSettings as settings

import time
import threading

import os

import numpy as np

if __name__ == "__main__":

    main_settings = settings.MainSettings()

    if not main_settings.is_ok():
        print(main_settings.set_log)
        exit()

    udp_sender = sender.UdpSender(main_settings)
    tensor_flow_helper = tensorflow.TensorflowHelper(main_settings)
    audio_listener = audio_l.AudioListenerThread(1,main_settings)
    audio_listener.start()

    # Ustawienie czasu pomiędzy próbkami
    sampling = 1 / main_settings.prediciotn_rate

    #
    predictions = []

    try:
        while True:
            time_start = time.time()

            #audio = audio_listener.get_audio_clear()
            audio = audio_listener.get_audio()
            
            prediction = tensor_flow_helper.get_prediction(audio).numpy()[0].tolist()

            if main_settings.predictions_per_update != 1:
                if  predictions.__len__() < main_settings.predictions_per_update:
                    predictions.append(prediction)
                else:
                    if main_settings.avg_mean == 1:
                        output = np.mean(np.array(predictions),axis=0)
                    elif main_settings.avg_median == 1:
                        output = np.median(np.array(predictions),axis=0)

                    threading.Thread(target=udp_sender.send, args=(output,)).start()
                    predictions.clear()
            else:
                threading.Thread(target=udp_sender.send, args=(prediction,)).start()
            
            time_elapsed = time.time() - time_start
            
            # Wyczekanie do końca zadanego czasu
            if  ( sampling > time_elapsed):
                #print(sampling - time_elapsed)
                time.sleep(sampling - time_elapsed)
            else:
                print("KUTANG KLAN")

    except KeyboardInterrupt:
        udp_sender.close()
        audio_listener.stop()
        exit()           
