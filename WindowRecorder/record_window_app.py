import pyaudio
import wave
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time

import customtkinter as ctk
import os
from unidecode import unidecode
import threading


# Set mode and theme
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.initialize_variable()
        self.initialize_gui()

    # Set initial startup data
    def initialize_variable(self):

        self.rec_param_frames_per_buffer :int = 
        
        self.rec_param_frame_rate = 44100
        self.rec_param_channels = 1
        self.rec_param_format = pyaudio.paInt32
        self.rec_param_recording_flag = False

        self.rec_data_0_frames = [] # type : bytes

        self.input_device_list = self.get_input_devices()
        self.input_device_0_index = -1 # indeks z listy mikrofonów dla urządzenia nr 1

        # 'input_device_0_selected' is ...
        self.input_device_0_selected = False # type :bool

        self.speaker_sex_type_list = ["Male", "Female"]
        self.speaker_sex_type_index = 0 # 0 - M, 1 - F
        self.speaker_number = 0

        self.command_list = ["00-Odrzuć broń", "01-Obróć się", "02-Na kolana","03-Gleba", "04-Ręce na głowę" ]
        self.command_index = 0
        self.command_attempt = 0

        self.record_type_list = ["Free", "Window"]
        self.record_type_index = 0 # 0 - zwykłe, 1 - oknem czasowym
        self.record_type_time = 2000 # czas nagrywania oknem w milisekundach

        self.record_time = 0 # final time in milis
        self.record_main_directory = "data"
        self.record_temp_directory = "temp"
        self.record_file_name = self.get_file_name()
        self.record_file_path = self.get_file_path()     

        self.record_countdown = 3
        self.record_countdown_end = False

    # Create window and widgest with initialized variables
    def initialize_gui(self):
        self.gui_window_width = 1600
        self.gui_window_height = 800

        # configure window
        self.title("Record App")
        self.geometry(f"{self.gui_window_width}x{self.gui_window_height}")

        # configure grid layout (2x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create settings sidebar frame with widgets
        self.gui_settings_side_bar_frame = ctk.CTkFrame(self, corner_radius=0)
        self.gui_settings_side_bar_frame.grid(row=0, column=0, rowspan=3, sticky="ns")


        # create countdown frame with
        self.gui_countdown_frame = ctk.CTkFrame(self,height=20,corner_radius=0)
        self.gui_countdown_frame.grid(row=0, column=1, sticky="nswe",padx=5, pady=(0,5),)
        self.gui_countdown_frame.grid_rowconfigure(0, weight=1)
        self.gui_countdown_frame.grid_columnconfigure(0, weight=1)

        self.gui_countdown_value_label = ctk.CTkLabel(self.gui_countdown_frame, text=self.record_countdown, font=ctk.CTkFont(size=72, weight="bold"))
        self.gui_countdown_value_label.grid(row = 0, column = 0, sticky="sn")

        # create graph 1 frame with
        self.gui_wave_form_graph_frame = ctk.CTkFrame(self, corner_radius=0)
        self.gui_wave_form_graph_frame.grid(row=1, column=1, sticky="nswe",padx=5, pady=(0,0))
        self.gui_wave_form_graph_frame.grid_rowconfigure(0, weight=1)
        self.gui_wave_form_graph_frame.grid_columnconfigure(0, weight=1)

        # create graph 2 frame with
        self.gui_spectrogram_graph_frame = ctk.CTkFrame(self, corner_radius=0)
        self.gui_spectrogram_graph_frame.grid(row=2, column=1, sticky="nswe",padx=5, pady=(5,0))
        self.gui_spectrogram_graph_frame.grid_rowconfigure(0, weight=1)
        self.gui_spectrogram_graph_frame.grid_columnconfigure(0, weight=1)




        self.gui_header_0_name = "Settings"
        self.gui_header_1_name = "Speaker"
        self.gui_header_2_name = "Record"      

        # 0 row
        self.gui_header_0_label = ctk.CTkLabel(self.gui_settings_side_bar_frame, text=self.gui_header_0_name, font=ctk.CTkFont(size=24, weight="bold"))
        self.gui_header_0_label.grid(row=0, column=0, columnspan=5, padx=10, pady=20)

        # 0 row
        
        self.gui_input_device_label = ctk.CTkLabel(self.gui_settings_side_bar_frame, text="Input device", font=ctk.CTkFont(size=12, weight="bold"))
        self.gui_input_device_label.grid(row=1, column=0, columnspan=4, padx=(10,5), pady=5, sticky="nsw")

        self.gui_input_device_refresh_button = ctk.CTkButton(self.gui_settings_side_bar_frame, text="↺", width=50, command=self.update_input_devices)
        self.gui_input_device_refresh_button.grid(row=1, column=4, padx=(5,10), pady=5 ,sticky="nse")

        # 5 row
        
        self.gui_input_device_0_label = ctk.CTkLabel(self.gui_settings_side_bar_frame,text="1.", font=ctk.CTkFont(size=12, weight="bold"))
        self.gui_input_device_0_label.grid(row=2, column=0, padx=(10,5), pady=5, sticky="w")
        self.gui_input_device_0_combobox = ctk.CTkComboBox(self.gui_settings_side_bar_frame, values=self.input_device_list, command=self.input_device_0_combobox_callback)
        self.gui_input_device_0_combobox.grid(row=2, column=1, columnspan=4, padx=(5,10), pady=5, sticky="nsew")
       
       # 6 row
        self.gui_header_1_label = ctk.CTkLabel(self.gui_settings_side_bar_frame, text=self.gui_header_1_name, font=ctk.CTkFont(size=24, weight="bold"))
        self.gui_header_1_label.grid(row=6, column=0, columnspan=5, padx=10, pady=20)
        # 7 row
        self.gui_speaker_sex_segbutton = ctk.CTkSegmentedButton(self.gui_settings_side_bar_frame, values=self.speaker_sex_type_list, command= self.input_sex_type_segmented_button_callback)
        self.gui_speaker_sex_segbutton.grid(row=7, column=0, columnspan=5, padx=10, pady=5 , sticky="nsew")
        # 8 row
        self.gui_speaker_number_label = ctk.CTkLabel(self.gui_settings_side_bar_frame,text="Number", font=ctk.CTkFont(size=12, weight="bold"))
        self.gui_speaker_number_label.grid(row=8, column=0,columnspan=2, padx=(10,5), pady=5, sticky="w" )

        self.gui_speaker_prev_button = ctk.CTkButton(self.gui_settings_side_bar_frame, text="<", width=50, command=self.input_prev_speaker_button_callback)
        self.gui_speaker_prev_button.grid(row=8, column=2, padx=(10,5), pady=5, sticky="w" )

        self.gui_speaker_number_value_label = ctk.CTkLabel(self.gui_settings_side_bar_frame,text="0000", font=ctk.CTkFont(size=12))
        self.gui_speaker_number_value_label.grid(row=8, column=3, padx=(5,10), pady=5, sticky="ew")

        self.gui_speaker_next_button = ctk.CTkButton(self.gui_settings_side_bar_frame, text=">", width=50, command=self.input_next_speaker_button_callback)
        self.gui_speaker_next_button.grid(row=8, column=4, padx=(5,10), pady=5 ,sticky="e")
        # 9 row
        self.gui_command_attempt_label = ctk.CTkLabel(self.gui_settings_side_bar_frame,text="Attempt", font=ctk.CTkFont(size=12, weight="bold"))
        self.gui_command_attempt_label.grid(row=9, column=0,columnspan=2, padx=(10,5), pady=5, sticky="w" )

        self.gui_command_attempt_prev_button = ctk.CTkButton(self.gui_settings_side_bar_frame, text="<", width=50, command=self.input_prev_command_attempt_button_callback)
        self.gui_command_attempt_prev_button.grid(row=9, column=2, padx=(10,5), pady=5, sticky="w" )

        self.gui_command_attempt_value_label = ctk.CTkLabel(self.gui_settings_side_bar_frame,text="0000", font=ctk.CTkFont(size=12))
        self.gui_command_attempt_value_label.grid(row=9, column=3, padx=(5,10), pady=5, sticky="ew")

        self.gui_command_attempt_next_button = ctk.CTkButton(self.gui_settings_side_bar_frame, text=">", width=50, command=self.input_next_command_attempt_button_callback)
        self.gui_command_attempt_next_button.grid(row=9, column=4, padx=(5,10), pady=5 ,sticky="e")
        # 10 row
        self.gui_command_label = ctk.CTkLabel(self.gui_settings_side_bar_frame,text="Command", font=ctk.CTkFont(size=12, weight="bold"))
        self.gui_command_label.grid(row=10, column=0,columnspan=2, padx=(10,5), pady=5, sticky="w" )

        self.gui_command_combobox = ctk.CTkComboBox(self.gui_settings_side_bar_frame, values=self.command_list, command=self.input_command_combobox_callback)
        self.gui_command_combobox.grid(row=10, column=2,columnspan=3, padx=(5,10), pady=5 , sticky="nsew")
        # 11 row
        self.gui_header_2_label = ctk.CTkLabel(self.gui_settings_side_bar_frame,text=self.gui_header_2_name, font=ctk.CTkFont(size=24, weight="bold"))
        self.gui_header_2_label.grid(row=11, column=0, columnspan=5, padx=10, pady=20, sticky="nsew")
        # 12 row
        self.gui_rec_type_segbutton = ctk.CTkSegmentedButton(self.gui_settings_side_bar_frame, values=self.record_type_list, command=self.input_rec_type_segmented_button_callback)
        self.gui_rec_type_segbutton.grid(row=12, column=0, columnspan=5, padx=10, pady=5 , sticky="nsew")
        # 13 row
        self.gui_rec_window_time_label = ctk.CTkLabel(self.gui_settings_side_bar_frame,text="Time [s]", font=ctk.CTkFont(size=12, weight="bold"))
        self.gui_rec_window_time_label.grid(row=13, column=0,columnspan=2, padx=(10,5), pady=5, sticky="nsw")

        self.gui_rec_window_time_entry = ctk.CTkEntry(self.gui_settings_side_bar_frame, placeholder_text="2")
        self.gui_rec_window_time_entry.grid(row=13, column=2,columnspan=3, padx=(5,10), pady=5, sticky="nsew")
        # 14 row
        self.gui_record_path_label = ctk.CTkLabel(self.gui_settings_side_bar_frame,text="Record path", font=ctk.CTkFont(size=12, weight="bold"))
        self.gui_record_path_label.grid(row=14, column=0, columnspan=5, padx=10, pady=2, sticky="nsew")
        # 15 row
        self.gui_record_path_value_label = ctk.CTkLabel(self.gui_settings_side_bar_frame,text="data/command/person_sex_attempt.wav", font=ctk.CTkFont(size=12))
        self.gui_record_path_value_label.grid(row=15, column=0, columnspan=5, padx=10, pady=2, sticky="nsew")
        # 16 row
        self.gui_record_time_label = ctk.CTkLabel(self.gui_settings_side_bar_frame,text="Time m : s : ms", font=ctk.CTkFont(size=12, weight="bold"))
        self.gui_record_time_label.grid(row=16, column=0, columnspan=5, padx=10, pady=2, sticky="nsew")
        # 17 row
        self.gui_record_time_value_label = ctk.CTkLabel(self.gui_settings_side_bar_frame,text="00 : 00 : 0000", font=ctk.CTkFont(size=12))
        self.gui_record_time_value_label.grid(row=17, column=0, columnspan=5, padx=10, pady=2, sticky="nsew")
        # 18 row
        self.gui_record_button = ctk.CTkButton(self.gui_settings_side_bar_frame, text="Record", command=self.input_record_button_callback)
        self.gui_record_button.grid(row=18, column=0, columnspan=5, padx=10, pady=2, sticky="nsew")
        # 19 row
        self.gui_save_button = ctk.CTkButton(self.gui_settings_side_bar_frame, text="Save",command=self.input_save_button_callback)
        self.gui_save_button.grid(row=19, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")

        # 20 row
        self.gui_play_button = ctk.CTkButton(self.gui_settings_side_bar_frame, text="Play",command=self.play_record)
        self.gui_play_button.grid(row=20, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")




        # Set default values
        # 1
        self.gui_input_device_0_combobox.set(self.input_device_list[self.input_device_0_index])
        # 2
        self.gui_speaker_sex_segbutton.set(self.speaker_sex_type_list[self.speaker_sex_type_index])
        # 3
        self.gui_speaker_number_value_label.configure(text=f"{self.speaker_number:04d}")
        # 4
        self.gui_command_combobox.set(self.command_list[self.command_index])
        # 5
        self.gui_rec_type_segbutton.set(self.record_type_list[self.record_type_index])
        # 6
        self.gui_rec_window_time_entry.insert(0, str(self.record_type_time))
        # 7
        self.gui_record_path_value_label.configure(text=self.record_file_path)
        # 8
        self.gui_record_time_value_label.configure(text=self.record_time)


    def get_input_devices(self):
        audio = pyaudio.PyAudio()
        info = audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')

        input_devices_list = []

        for i in range(0, numdevices):
            if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                input_devices_list.append(audio.get_device_info_by_host_api_device_index(0, i).get('name'))

        audio.terminate()

        input_devices_list.append("None")

        return input_devices_list

    def update_input_devices(self):
        self.input_device_list = self.get_input_devices()
        self.gui_input_device_0_combobox.configure(values=self.input_device_list)

    # return filename based on actual variables
    def get_file_name(self):
        return f"{self.speaker_sex_type_list[self.speaker_sex_type_index][0]}_{self.speaker_number:04d}_{self.command_index}_{self.command_attempt}_{self.record_type_list[self.record_type_index][0]}.wav"

    # return file path based on actual variables
    def get_file_path(self):
        record_file_path = os.path.join(
            self.record_main_directory.lower(),
            self.command_list[self.command_index].lower(),
            self.record_file_name.lower()
        )

        record_file_path = record_file_path.replace(" ","_")

        return unidecode(record_file_path)

    # Update window
    def gui_update_labels(self):
        self.update_speaker_number()
        self.update_command_attempt_number()
        self.update_file_name()
        self.update_file_path()

    #
    def gui_update_record_time_label(self):
        frames = len(b"".join(self.rec_data_0_frames))
        self.gui_record_time_value_label.configure(text=f"{frames/(pyaudio.get_sample_size(self.rec_param_format)*self.rec_param_frame_rate):.4f}")

    def update_file_name(self):
        self.record_file_name = self.get_file_name()

    def update_file_path(self):
        self.record_file_path = self.get_file_path()
        self.gui_record_path_value_label.configure(text=self.record_file_path)

    #
    def update_speaker_number(self):
        self.gui_speaker_number_value_label.configure(text=f"{self.speaker_number:04d}")
    
    #
    def update_command_attempt_number(self):
        self.gui_command_attempt_value_label.configure(text=f"{self.command_attempt:04d}")


    # Przestawia index urządzenia 0 do nagrywania
    def input_device_0_combobox_callback(self, choice):
        self.input_device_0_index = self.input_device_list.index(choice)
        self.input_device_0_selected = True if self.input_device_0_index != len(self.input_device_list)-1 else False

    # Przestawia flagę płci próbki
    def input_sex_type_segmented_button_callback(self, choice):
        self.speaker_sex_type_index = self.speaker_sex_type_list.index(choice)
        self.gui_update_labels()

    # Zmniejsza numer mówcy o 1
    def input_prev_speaker_button_callback(self):
        if self.speaker_number > 0:
            self.speaker_number -= 1
        self.gui_update_labels()

    # Zwiększa numer mówcy o 1
    def input_next_speaker_button_callback(self):
        self.speaker_number += 1
        self.gui_update_labels()

    # Przestawia index komendy
    def input_command_combobox_callback(self, choice):
        self.command_index = self.command_list.index(choice)
        self.command_attempt = 0
        self.gui_update_labels()


    #
    def input_prev_command_attempt_button_callback(self):
        if self.command_attempt > 0:
            self.command_attempt -= 1
        self.gui_update_labels()

    #
    def input_next_command_attempt_button_callback(self):
        self.command_attempt += 1
        self.gui_update_labels()

    # Przestawia tryb nagrywania próbki 
    def input_rec_type_segmented_button_callback(self, choice):
        self.record_type_index = self.record_type_list.index(choice)
        self.gui_update_labels()

    def input_record_button_red(self):
        self.gui_record_button.configure(fg_color="#2B719E")
        self.gui_record_button.configure(hover_color="#144870")
        self.gui_record_button.configure(text="Record")
    
    def input_record_button_default(self):
        self.gui_record_button.configure(fg_color="#FF0040")
        self.gui_record_button.configure(hover_color="#8b0000")
        self.gui_record_button.configure(text="Stop")

    def countdown(self):
        self.record_countdown = 3
        self.record_countdown_end = False
        self.gui_countdown_value_label.configure(text=f"{self.record_countdown}")

        while(self.record_countdown):
            time.sleep(1)
            self.record_countdown -= 1
            self.gui_countdown_value_label.configure(text=f"{self.record_countdown}")

            if  self.record_countdown == 1:
                if self.record_type_index == 0:
                    threading.Thread(target=self.record_free).start()
                else:
                    threading.Thread(target=self.record_window).start()

        self.gui_countdown_value_label.configure(text="START")
        self.record_countdown_end = True




    # Rozpoczyna sekwencję nagrywania
    def input_record_button_callback(self):

        self.record_type_time = int(self.gui_rec_window_time_entry.get())

        if  self.input_device_0_selected == True :

            if self.rec_param_recording_flag == True:
                self.rec_param_recording_flag = False
                self.input_record_button_red()
            else:
                self.rec_param_recording_flag = True
                self.input_record_button_default()

                threading.Thread(target=self.countdown).start()


    #
    def record_free(self):  
        
        audio = pyaudio.PyAudio()

        stream = audio.open(
            format=self.rec_param_format,
            channels=self.rec_param_channels,
            rate=self.rec_param_frame_rate,
            input=True,
            frames_per_buffer=self.rec_param_frames_per_buffer,
            input_device_index=self.input_device_0_index
            )

        self.rec_data_0_frames = []


        while self.rec_param_recording_flag:
            data = stream.read(self.rec_param_frames_per_buffer)
            self.rec_data_0_frames.append(data)

            self.gui_update_record_time_label()

        stream.stop_stream()
        stream.close()
        audio.terminate()

        self.show_plt()


    def show_plt(self):
        frames = b"".join(self.rec_data_0_frames)
        frames_len = int(len(frames)/pyaudio.get_sample_size(self.rec_param_format))
        self.plot_wave(frames_len, frames)

    #
    def record_window(self):

        audio = pyaudio.PyAudio()

        stream = audio.open(
            format=self.rec_param_format,
            channels=self.rec_param_channels,
            rate=self.rec_param_frame_rate,
            input=True,
            frames_per_buffer=self.rec_param_frames_per_buffer,
            input_device_index=self.input_device_0_index
            )

        seconds :float = self.record_type_time / 1000
        self.rec_data_0_frames = []

        for i in range(0,int(self.rec_param_frame_rate/self.rec_param_frames_per_buffer*seconds)):
            data = stream.read(self.rec_param_frames_per_buffer)
            self.rec_data_0_frames.append(data)

            self.gui_update_record_time_label()

        stream.stop_stream()
        stream.close()
        audio.terminate()  
        self.input_record_button_callback()
        self.show_plt()


    def play_record(self):

        if len(self.rec_data_0_frames) > 0:
            p = pyaudio.PyAudio()

            # open stream based on the wave object which has been input.
            stream = p.open(format = self.rec_param_format,
                            channels = self.rec_param_channels,
                            rate = self.rec_param_frame_rate,
                            output = True)

            for i in range(0,len(self.rec_data_0_frames)):
                stream.write(b"".join(self.rec_data_0_frames[i*self.rec_param_frames_per_buffer:(i+1)*self.rec_param_frames_per_buffer]))
                
            # cleanup stuff.
            stream.close()    
            p.terminate()

    # Zapisuje nagranie
    def input_save_button_callback(self):

        if  len(self.rec_data_0_frames) > 0:

            record_full_path = os.path.join(os.getcwd(),self.record_file_path)
            head, tail = os.path.split(record_full_path)

            if os.path.exists(head) == False:
                os.makedirs(head)

            #ZAPIS DO PLIKU
            audio_file = wave.open(self.record_file_path, "wb")
            audio_file.setnchannels(self.rec_param_channels)
            audio_file.setsampwidth(pyaudio.get_sample_size(self.rec_param_format))
            audio_file.setframerate(self.rec_param_frame_rate)
            audio_file.writeframes(b"".join(self.rec_data_0_frames))
            audio_file.close()

            self.command_attempt += 1
            self.gui_update_labels()


    def plot_wave(self, frames_len, frames :bytes):

        wave_freq = self.rec_param_frame_rate
        wave_samples = frames_len
        wave_frames = frames
        wave_time = wave_samples / wave_freq
        
        signal_array = np.frombuffer(wave_frames, dtype=np.int32)
        times = np.linspace(0, wave_time, num=wave_samples)

        matplotlib.pyplot.close()

        f = plt.figure()
        ax = f.add_subplot(111)
        ax.plot(times, signal_array, linewidth=0.1)
        ax.set_title("Audio waveform")
        ax.set_ylabel("Signal wave amplitude")
        ax.set_xlabel("Time [s]")
        ax.set_xlim(0,wave_time)

        #f.set_facecolor('#2B2B2B')
        #ax.set_facecolor('#2B2B2B')
        #    
        #ax.tick_params(colors='w')
        #        
        #ax.xaxis.label.set_color('white')
        #ax.yaxis.label.set_color('white')
        #
        #ax.spines['left'].set_color('white')
        #ax.spines['right'].set_color('white')
        #ax.spines['top'].set_color('white')
        #ax.spines['bottom'].set_color('white')
       
        canvas = FigureCanvasTkAgg(f, master=self.gui_wave_form_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0,column=0,sticky="nswe")

        _fs = 44100
        _nfft = 256
        _noverlap = 128
        f2 = plt.figure()
        ax2 = f2.add_subplot(111)
        ax2.set_title("Spectrogram")
        ax2.set_ylabel("Frequency [Hz]")
        ax2.set_xlabel("Time [s]")


        Pxx, freqs, bins, im = ax2.specgram(signal_array,NFFT=_nfft,Fs=_fs,noverlap=_noverlap)

        canvas2 = FigureCanvasTkAgg(f2, master=self.gui_spectrogram_graph_frame)
        canvas2.draw()
        canvas2.get_tk_widget().grid(row=0,column=0,sticky="nswe")   


    def plot_spectrum(self):
        return 0


if __name__ == "__main__":
    app = App()
    app.mainloop()
