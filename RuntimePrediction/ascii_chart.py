
import threading, time, signal
import numpy as np
import random
import udp_sender as sender
import xml.etree.ElementTree as ET

DATA = [
('Clare',0.1),
('Donegal',0.2),
('Mayo',0.3),
('Meath',0.01),
('Offaly',0.1),
('Tipperary',0.7),
('Wicklow',0.0),
]

DATA_VALUE_MIN = 0.0
DATA_VALUE_MAX = 1.0

UPDATE_TASK_MILIS = 0.1

class UpdateTask:
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
                update_data() # call the function
                self.start()
        except KeyboardInterrupt:
            self.stop()


class PeriodicTask:
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
                print_asci_bar_chart() # call the function
                self.start()
        except KeyboardInterrupt:
            self.stop()

def print_asci_bar_chart():
    max_value = max(count for _, count in DATA)
    increment = max_value / 25

    longest_label_length = max(len(label) for label, _ in DATA)

    print(f"\033[{len(DATA)+2}A\033[J")

    for label, count in DATA:

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

def update_data():
    
    if len(DATA) > 0:

        for i, touple in enumerate(DATA):
            new_value = random.uniform(DATA_VALUE_MIN,DATA_VALUE_MAX)
            DATA[i] = (touple[0], new_value)

if __name__ == "__main__":

    data = []

    sender = sender.PeriodicSender(1)
    sender.start()



    while True:
        data.clear()
        
        for i in range(0,7):
            new_value = random.uniform(DATA_VALUE_MIN,DATA_VALUE_MAX)
            data.append(new_value)
        
        root = ET.Element('prediction')
        root.set('values',data)

        xml_data = ET.tostring(root)
        
        sender.set_msg(xml_data)




