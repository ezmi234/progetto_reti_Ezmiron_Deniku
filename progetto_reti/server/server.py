import sys
sys.path.insert(1,'..')
from utility_module import *
import socket as sk
import time
import os

#function that returns files in server
def get_files_list():
    clean = ['.DS_Store','server.py']
    l = os.listdir()
    for ob in clean:
        if ob in l:
            l.remove(ob)
    return l

sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)                     #UDP socket creation
server_address = ('localhost', 10000)
print('\n\r starting up on %s port %s' % server_address)
sock.bind(server_address)

#server process always listening
while True:
    print('\n\r waiting to receive message...\n')
    data, address = sock.recvfrom(8192)                                     #receives a packet with the instruction in the header
    packet = json.loads(data.decode('utf8'))
    if packet['HEADER'][0] == 1:                                            #answers the LIST request
        content = json.dumps(get_files_list())
        try:
            send(content, address, sock)
        except Exception as info:
            set_header_content('END',1)
            sock.sendto(packet_create('END', str(info)), address)
            set_header_content('END', 0)
            print(info)
    elif packet['HEADER'][0] == 2:                                          #answers the GET request
        filename = packet["CONTENT"]
        try:
            send(read_file(filename), address, sock, 8192)
        except Exception as info:
            set_header_content('END',1)
            sock.sendto(packet_create('END', str(info)), address)
            set_header_content('END', 0)
            print(info)
    elif packet['HEADER'][0] == 3:                                          #answers the PUT request
        filename = packet['CONTENT']
        file, status = receive(sock)
        if status == 0:
            save_file(file, filename)
            content = "file correctly uploaded"
        else:
            print(file)
            content = "file wrongly uploaded: " + file
        set_header_content('END', 1)
        sock.sendto(packet_create('END', content), address)
        set_header_content('END', 0)
    else:
        print("undetected problem")

