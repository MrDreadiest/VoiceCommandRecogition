import audio_listener as al
import udp_sender as sender
import xml.etree.ElementTree as ET
import time


import AudioHelper as ah

if __name__ == "__main__":

    audio_recorder = al.AudioListenerThread(1)
    audio_recorder.start()
    
    sender = sender.UdpSenderThread(1)
    sender.start()


    try:
        while True:
            time.sleep(1)

            data = audio_recorder.get_data()

            path = ah.get_new_file_name("data","test.wav")

            ah.save_audio(path, data, 16000)

            root = ET.Element('prediction')
            root.set('values',path)

            xml_data = ET.tostring(root)
            
            sender.set_msg(xml_data)

    except KeyboardInterrupt:
        audio_recorder.stop()
        sender.stop()


