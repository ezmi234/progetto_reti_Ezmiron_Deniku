import sys
import time
import json
import base64
import hashlib

#dictinary key = header_type, value = (number of the header_type, content of the header)
packet_header = {'LIST': (1,0),
                 'GET': (2,0),
                 'PUT': (3,0),
                 'SEND': (4,0),
                 'END': (5,0)}

#set the header content, taking as arguments the key of the header and the content of it
def set_header_content(key, content):
    packet_header[key] = (packet_header[key][0],content)

#create a packet used for splitting in multiple packets the message
#takes as arguments the header_type and the content(message splitted in chunks)
#it returns the packet encoded
def packet_create(header, content = 0):
    packet = {"HEADER" : packet_header[header],
               "CONTENT" : content}
    return json.dumps(packet).encode()

#function used to read a file
#it returns the file decoded in utf-8
def read_file(filename):
    with open(filename, 'rb') as f:
        file = f.read()
        file = base64.b64encode(file).decode()
        f.close()
    return file

#function used to save the file
#it takes as arguments the file and its name
def save_file(file, filename):
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(file.encode()))
        f.close()

#function that generates a process to send the entire message
def send(message, address, socket, buffer = 8192):
    hasher = hashlib.md5()
    hasher.update(message.encode())
    while len(message) > 0:
        p = packet_create('SEND',(message[:(buffer-40)]))               #sending chunks of the message inside packets
        socket.sendto(p, address)
        message = message[buffer-40:]
    socket.sendto(packet_create("END", hasher.hexdigest()), address)    #sending the last packet, header_type 'END'
    print("message sent")

#funciton used to receive the message
def receive(socket):
    message = "";
    while True:                                        #receiving packets with header_type 'SEND'
        data, address = socket.recvfrom(8192)          #until he does receive last packet with header_type 'END'
        packet = json.loads(data.decode('utf8'))
        if packet['HEADER'][0] == 5:
            if packet['HEADER'][1] == 1:
                return packet['CONTENT'], 1            #returns a error if there problems detected by the sender
            break                                      #that can be for example: the file required does not exist
        message += packet["CONTENT"]

    hasher = hashlib.md5()
    hasher.update(message.encode())
    print()
    if hasher.hexdigest() != packet['CONTENT']:
        print("file wrongly received")                 #returns a error if the checksum fails
        return "checksum failed", 1
    print("file correctly received")
    return message, 0                                  #returns the message if everything goes right

'''-----Client Navigation Functions-----'''

#function used to manage the command LIST
def op_one(socket, address):
    try:
        socket.sendto(packet_create('LIST'), address)       #sends to the server the packet with header_type list
    except Exception as info:
        print(info)

    print('waiting to receive from')
    message, status = receive(socket)                       #receives the message from the server
    if status == 0:
        for ob in json.loads(message):                      #prints the file list
            print(" {} -" .format(ob), end = "")
    else:
        print(message)
    print()

#function used to manage the command GET
def op_two(socket, address, filename, filepath=""):
    try:
        socket.sendto(packet_create('GET',filename), address)   #sends to the server the packet with header_type Get, content the filename
    except Exception as info:
        print(info)

    print('\nwaiting to receive files..\n')
    message, status = receive(socket)                           #receives the message from the server
    if status == 0:
        save_file(message, filepath)                            #saves the file
    else:
        print(message)                                          #prints the error message

#function used to manage the command GET
def op_three(socket, address, filename, filepath=""):
    try:
        socket.sendto(packet_create('PUT',filename), address)           #sends to the server the packet with header_type PUT, content the filename
        print('\nuploading files..\n')
        try:
            send(read_file(filepath), address, socket)                  #sends the file
        except Exception as info:
            set_header_content('END', 1)
            socket.sendto(packet_create('END', str(info)),address)      #sends an error message in case of errors
            set_header_content('END', 0)
            print(info)
    except Exception as info:
        print(info)

    message, status = receive(socket)
    print(message)

