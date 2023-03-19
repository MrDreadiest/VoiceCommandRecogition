import json
import socket
import os

SETTINGS_FILE_UDP = 'udp_settings.json'
IP_ADDRESS = None
PORT = None

# Load the UDP settings from the JSON file
with open(SETTINGS_FILE_UDP, 'r', encoding='utf-8') as f:
    try:
        settings = json.load(f)  # 👈️ parse the JSON with load()
        
        IP_ADDRESS = settings['ip_address']
        PORT = settings['port']

        print(f"UDP SETTINGS: {IP_ADDRESS}:{PORT}")
    except BaseException as e:
        print('The file contains invalid JSON')


# # Create a UDP socket and bind it to the specified IP address and port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((IP_ADDRESS, PORT))

# Receive data sent to the port
while True:
    data, addr = server_socket.recvfrom(1024)
    print("Received data from {}: {}".format(addr, data.decode()))
