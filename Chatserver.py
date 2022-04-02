#!/usr/bin/python3


# Student name and No.: Ritvik Singh
# Development platform: MacOS Montery 12.1 (Intel Chip)
# Python version: Python 3.8.5
# Version: 1.0 


import socket
import sys
import select
import time

def main(argv):
    if len(argv) == 2:
        port = int(argv[1])
    else:
        port = 40452

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind(("", port))
    except socket.error as err:
        print("bind() error: ", err)
        sys.exit(1)

    server_socket.listen(5)

    RList = [server_socket]
    CList = []
	
    while True:
        try:
            Rready, Wready, Eready = select.select(RList, [], [], 10)
        except select.error as err:
            print("select() error:", err)
            sys.exit(1)
        except KeyboardInterrupt:
            print("select() encountered KeyboardInterrupt")
            sys.exit(1)

        if Rready:
            for r in Rready:
                if r == server_socket:
                    client_socket, client_address = server_socket.accept()
                    RList.append(client_socket)
                    CList.append(client_socket)
                else:
                    receive_message = r.recv(50)
                    if receive_message:
                        print("Received a message")
                        if len(CList) > 1:
                            print("Relay to others")
                            for c in CList:
                                if c != r:
                                    c.send(receive_message)
                    else:
                        print("A connection is broken")
                        RList.remove(r)
                        CList.remove(r)
        else:
            print("Idling")

if __name__ == '__main__':
	if len(sys.argv) > 2:
		print("Usage: chatserver [<Server_port>]")
		sys.exit(1)
	main(sys.argv)
