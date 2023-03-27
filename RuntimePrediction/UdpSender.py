import socket
import xml.etree.ElementTree as ET
import os
import sys

class UdpSender:
    def __init__(self, settings):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, settings.udp_size) # 64 KB

        self.ip = settings.ip_address
        self.port = settings.port
        self.topic = settings.udp_topic

        self.host = os.environ['COMPUTERNAME']
        self.program = sys.argv[0].split(".")[0]
        self.pid = os.getpid()

        self.sender = f"{self.host}:{self.program}:{self.pid}"
        
        self.id = 0
        self.msg = ""

    def serialize(self, data):

        root = ET.Element('event')
        root.set('topic',str(self.topic))
        root.set('sender',str(self.sender))
        root.set('id',str(self.id))

        for i, value in enumerate(data):
            child = ET.SubElement(root, "command")
            child.set("id", f"C{i+1}")
            child.set("probability", f"{value:04f}")

        xml_data = ET.tostring(root)
        
        return xml_data

    def close(self):
        self.socket.close()

    def send(self, data):
        
        self.msg = self.serialize(data=data)

        try:
            self.socket.sendto(self.msg, (self.ip, self.port))
            self.id += 1
        except:
            print("Nieudane wysłanie")
