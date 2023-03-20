import threading, time, signal
import json
import socket
import os
import numpy as np
import random

SETTINGS_FILE_UDP = 'udp_settings.json'

class UdpSenderThread:
    def __init__(self, interval):
        self.interval = interval
        self.timer = None
        self.flag = True

        self.socket = None
        self.ip = ""
        self.port = ""

        self.set_flag = False
        self.msg = ""

        self.connnect()

    def connnect(self): 
        # Load the UDP settings from the JSON file
        with open(SETTINGS_FILE_UDP, 'r', encoding='utf-8') as f:
            try:
                settings = json.load(f)  # 👈️ parse the JSON with load()
                
                self.ip = settings['ip_address']
                self.port = settings['port']

                print(f"UDP SETTINGS: {self.ip}:{self.port}")
                self.set_flag = True

                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                new_buffer_size = 65536  # 64 KB
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, new_buffer_size)

            except BaseException as e:
                print('The file contains invalid JSON')
                self.set_flag = False

    def set_msg(self, msg):
        self.msg = msg

    def start(self):
        self.flag = True
        self.timer = threading.Timer(self.interval, self.run)
        self.timer.start()

    def stop(self):
        self.flag = False
        if self.timer:
            self.timer.cancel()
            socket.close()

    def run(self):
        try:
            if self.flag:
                self.send_udp_msg() # call the function
                self.start()
        except KeyboardInterrupt:
            self.stop()

    def send_udp_msg(self):
        if  self.set_flag :
            self.socket.sendto(bytes(f"{self.msg}", "utf-8"), (self.ip, self.port))
