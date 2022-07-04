import socket as sk
import sys
sys.path.insert(1,'..')
from utility_module import *

sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)             #socket create
server_address = ('localhost', 10000)
check = True

#navigation process
while check:                                #takes in input the choice from the user
    choice = input("\nPress: 1 for having the list of files available to download from the server;"
                   "\n 2 to receive a file from the server;"
                   "\n 3 to upload a file to the server;"
                   "\n other keys to stop the program.\n")
    if choice == '1':
        op_one(sock, server_address)
    elif choice == '2':
        filename = input("Insert the name of the file to download: ")
        filepath = input("Press 0 to save in the client directory or write the path. Example: /Users/MarioRossi/Desktop ")
        if filepath == '0':
            filepath = filename
        else:
            filepath += "/" + filename

        op_two(sock, server_address, filename,filepath)
    elif choice == '3':
        filename = input("Insert the name of the file to upload: ")
        filepath = input("Press 0 if the file is in the client directory or write the path. Example: /Users/MarioRossi/Desktop ")
        if filepath == '0':
            filepath = filename
        else:
            filepath += "/" + filename

        op_three(sock, server_address, filename, filepath)
    else:
        check = False

print ('closing socket')
sock.close()
