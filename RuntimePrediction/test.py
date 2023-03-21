import audio_listener as al
import udp_sender as sender
import tensorflow_helper as tf

import time

import xml.etree.ElementTree as ET
import time
import threading

import AudioHelper as ah

import numpy as np

class UpdateTask:
    def __init__(self, interval):
        self.interval = interval
        self.timer = None
        self.flag = True

        self.prediction = []
        self.avg_prediction = []

        self.udp_sender = sender.UdpSenderThread(1)
        self.udp_sender.start()

        self.audio_listener = al.AudioListenerThread(0)
        self.audio_listener.start()

        self.tf_helper = tf.TensorFlowHelper()

    def start(self):
        self.flag = True
        self.timer = threading.Timer(self.interval, self.run)
        self.timer.start()

    def stop(self):
        self.flag = False
        if self.timer:
            self.audio_listener.stop()
            self.timer.cancel()

    def run(self):
        try:
            if self.flag:
                self.update_data() # call the function
                self.start()
        except KeyboardInterrupt:
            self.stop()

    def update_data(self):
        audio = self.audio_listener.get_audio()

        path = ah.get_new_file_name("data","test.wav")
        ah.save_audio(path, audio, 16000)

        prediction = self.tf_helper.get_prediction(audio).numpy().tolist()
        print(prediction)

        root = ET.Element('prediction')
        root.set('values',prediction)
        xml_data = ET.tostring(root)
        self.udp_sender.set_msg(xml_data)


class GraphUpdateThread:
    def __init__(self, interval):
        self.interval = interval
        self.timer = None
        self.flag = True



    def start(self):
        self.flag = True
        self.timer = threading.Timer(self.interval, self.run)
        self.timer.start()

    def stop(self):
        self.flag = False
        if self.timer:
            self.timer.cancel()

    def run(self):
        try:
            if self.flag:
                self.update_graph() # call the function
                self.start()
        except KeyboardInterrupt:
            self.stop()

    def update_graph(self):
        pass



def print_asci_bar_chart():
    max_value = max(count for _, count in DATA)
    increment = max_value / 25

    longest_label_length = max(len(label) for label, _ in DATA)

    print(f"\033[{len(DATA)*2 + 1}A\033[J")

    for label, count in DATA:

        try:
            # The ASCII block elements come in chunks of 8, so we work out how
            # many fractions of 8 we need.
            # https://en.wikipedia.org/wiki/Block_Elements
            bar_chunks, remainder = divmod(int(count * 8 / increment), 8)

            # First draw the full width chunks
            bar = '█' * bar_chunks

            # Then add the fractional part.  The Unicode code points for
            # block elements are (8/8), (7/8), (6/8), ... , so we need to
            # work backwards.
            if remainder > 0:
                bar += chr(ord('█') + (8 - remainder))

            # If the bar is empty, add a left one-eighth block
            bar = bar or  '▏'

            print(f'{label.rjust(longest_label_length)} ▏ {count:.04f} {bar}')
        except:
            pass


if __name__ == "__main__":
    
    DATA = [
        ('Odrzuć broń',0.0),
        ('Obróć się',0.0),
        ('Na kolana',0.0),
        ('Gleba',0.0),
        ('Ręce na głowę',0.0),
        ('Tło',0.0),
    ]

    frequency = 5 #hz

    udp_sender = sender.UdpSenderThread( 1 )
    udp_sender.start()

    audio_listener = al.AudioListenerThread(0)
    audio_listener.start()

    tf_helper = tf.TensorFlowHelper()
    predictions = []
    
    

    try:
        while True:
            time.sleep(0.05)
            audio = audio_listener.get_audio()

            prediction = tf_helper.get_prediction(audio).numpy()[0].tolist()

            for i,(label,value) in enumerate(DATA):
                DATA[i] = (label,prediction[i])

            print_asci_bar_chart()

            # predictions.append(prediction)

            # if(predictions.__len__() == frequency):
                
            #     output = np.array(predictions)
            #     output = np.mean(output,axis=0)

            #     for i,(label,value) in enumerate(DATA):
            #         DATA[i] = (label,output[i])
                
            #     print_asci_bar_chart()

            #     root = ET.Element('prediction')
            #     root.set('values',output)
            #     xml_data = ET.tostring(root)
            #     udp_sender.set_msg(xml_data)

            #     predictions.clear()
            

 

    except KeyboardInterrupt:
        udp_sender.stop()
        audio_listener.stop()
        exit()

    udp_sender.stop()
    audio_listener.stop()
    exit()





