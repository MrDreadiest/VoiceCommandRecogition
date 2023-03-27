import json
import os

SETTINGS_FILE = 'settings.json'

class MainSettings:
    def __init__(self):
        
        self.udp_size = 0
        self.topic = ""
        self.ip_address = ""
        self.port = 0
        self.prediciotn_rate = 0
        self.predictions_per_update = 0
        self.avg_mean = 0
        self.avg_median = 0
        self.avg_gausse_weighted = 0
        self.frames_per_buffer = 0
        self.channels = 0
        self.frame_rate = 0
        self.duration = 0
        self.frame_rate_min = 0
        self.frame_rate_max = 0
        self.n_fft = 0
        self.hop_length = 0
        self.n_mels = 0
        self.model = ""
        self.commands = []

        self.set_flag = False
        self.set_log = ""
        
        self.load_settings()

    def load_settings(self):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:

                try:
                    settings = json.load(f)
                    self.udp_size = int(settings['udp_size'])
                    self.udp_topic = settings['udp_topic']
                    self.ip_address = settings['ip_address']
                    self.port = int(settings['port'])
                    self.prediciotn_rate = int(settings['prediciotn_rate'])
                    self.predictions_per_update = int(settings['predictions_per_update'])
                    self.avg_mean = int(settings['avg_mean'])
                    self.avg_median = int(settings['avg_median'])
                    self.avg_gausse_weighted = int(settings['avg_gausse_weighted'])
                    self.frames_per_buffer = int(settings['frames_per_buffer'])
                    self.channels = int(settings['channels'])
                    self.frame_rate = int(settings['frame_rate'])
                    self.duration = int(settings['duration'])
                    self.frame_rate_min = int(settings['frame_rate_min'])
                    self.frame_rate_max = int(settings['frame_rate_max'])
                    self.n_fft = int(settings['n_fft'])
                    self.hop_length = int(settings['hop_length'])
                    self.n_mels = int(settings['n_mels'])
                    self.model = settings['model']
                    self.commands = settings['commands']

                    self.set_flag = True
                except BaseException as e:
                    self.set_log += f'Niepoprawny format pliku {SETTINGS_FILE} z e:{str(e)}.\n'
                    self.set_flag = False
                    
        except BaseException as e:
            self.set_log += f'Nieudana próba załadowania pliku {SETTINGS_FILE} z e:{str(e)}.\n'
            self.set_flag = False

    def is_ok(self):
        try:

            if  self.udp_size == 0:
                self.set_flag = False
                self.set_log += f'self.udp_size: {self.udp_size}.\n'
        
            if  self.udp_topic == "":
                self.set_flag = False
                self.set_log += f'self.udp_topic: {self.udp_topic}.\n'

            if  self.ip_address == "":
                self.set_flag = False
                self.set_log += f'self.ip_address: {self.ip_address}.\n'

            if self.port == 0:
                self.set_flag = False
                self.set_log += f'self.port: {self.port}.\n'

            if self.prediciotn_rate == 0:
                self.set_flag = False
                self.set_log += f'self.prediciotn_rate: {self.prediciotn_rate}.\n'

            if self.predictions_per_update == 0:
                self.set_flag = False
                self.set_log += f'self.predictions_per_update: {self.predictions_per_update}.\n'
            
            if  (self.avg_mean + self.avg_median + self.avg_gausse_weighted) > 1 or (self.avg_mean + self.avg_median + self.avg_gausse_weighted) == 0:
                self.set_flag = False
                self.set_log += f'self.avgs: {self.set_flag}:{self.avg_median}:{self.avg_gausse_weighted}.\n'

            if self.frames_per_buffer == 0:
                self.set_flag = False
                self.set_log += f'self.frames_per_buffer: {self.frames_per_buffer}.\n'

            if self.channels == 0:
                self.set_flag = False
                self.set_log += f'self.channels: {self.channels}.\n'

            if self.frame_rate == 0:
                self.set_flag = False
                self.set_log += f'self.frame_rate: {self.frame_rate}.\n'

            if self.duration == 0:
                self.set_flag = False
                self.set_log += f'self.duration: {self.duration}.\n'

            if self.frame_rate_min == 0:
                self.set_flag = False
                self.set_log += f'self.frame_rate_min: {self.frame_rate_min}.\n'

            if self.frame_rate_max == 0:
                self.set_flag = False
                self.set_log += f'self.frame_rate_max: {self.frame_rate_max}.\n'

            if self.n_fft == 0:
                self.set_flag = False
                self.set_log += f'self.n_fft: {self.n_fft}.\n'

            if self.hop_length == 0:
                self.set_flag = False
                self.set_log += f'self.hop_length: {self.hop_length}.\n'

            if self.n_mels == 0:
                self.set_flag = False
                self.set_log += f'self.n_mels: {self.n_mels}.\n'
            
            if self.model == "":
                self.set_flag = False
                self.set_log += f'self.model: {self.model}.\n'
            else:
                if not os.path.exists(os.path.join(os.getcwd(),self.model)):
                    self.set_flag = False
                    self.set_log += f'self.model path not exist: {os.path.join(os.getcwd(),self.model)}.\n'

            if self.commands.__len__() == 0:
                self.set_flag = False
                self.set_log += f'self.commands: {self.commands}.\n'

        except:
            self.set_flag = False
            self.set_log += "Niepoprawne parametry startowe aplikacji.\n"

        return self.set_flag
