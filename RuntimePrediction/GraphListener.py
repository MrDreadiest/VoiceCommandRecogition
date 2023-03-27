import json
import socket
import xml.etree.ElementTree as ET

SETTINGS_FILE_UDP = 'settings.json'
IP_ADDRESS = None
PORT = None
DATA_GLOB = []
COMMANDS = []

def print_asci_bar_chart():
    max_value = max(count for _, count in DATA_GLOB)
    increment = max_value / 25

    longest_label_length = max(len(label) for label, _ in DATA_GLOB)

    print(f"\033[{len(DATA_GLOB)*2 + 1}A\033[J")

    for label, count in DATA_GLOB:

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

# Load the UDP settings from the JSON file
with open(SETTINGS_FILE_UDP, 'r', encoding='utf-8') as f:
    try:
        settings = json.load(f)  # 👈️ parse the JSON with load()
        
        IP_ADDRESS = settings['ip_address']
        PORT = settings['port']
        COMMANDS = settings['commands']

        print(f"UDP SETTINGS: {IP_ADDRESS}:{PORT}")
    except BaseException as e:
        print('The file contains invalid JSON')

if __name__ == "__main__":

    # # Create a UDP socket and bind it to the specified IP address and port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP_ADDRESS, PORT))

    # Receive data sent to the port
    while True:
        try:
            try:
                data, addr = server_socket.recvfrom(1024)
                root = ET.fromstring( data)

                DATA_GLOB.clear()

                for i, command_elem in enumerate(root.findall('command')):
                    probability = float(command_elem.attrib['probability'])
                    DATA_GLOB.append((COMMANDS[i], probability))

                print_asci_bar_chart()
            except:
                pass
        except KeyboardInterrupt:
            server_socket.close()
            exit()  