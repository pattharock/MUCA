#!/usr/bin/python3


# Student name and No.: Ritvik Singh
# Development platform: MacOS Montery 12.1 (Intel Chip)
# Python version: Python 3.8.5
# Version: 1.0 


import socket
import sys
import select
import time
import json

SERVER_PORT = None
CONNECTED = False
SERVER_SOCKET = None
MLEN = 1000
CLIENT_DICT = {}

def connection_success(conn, where, msg=""):
    if msg == "":
        return f"[SERVER SUCCESS]({where}) : TCP Connection to {conn.getpeername()[0]}:{conn.getpeername()[1]} has been established."
    else:
        return f"[SERVER SUCCESS] ({where}) : {msg}"
def connection_error(error, where):
    return f"[SERVER ERROR]({where}) : {error}"

def connection_warning(conn, where, msg=""):
    if msg == "":
        return f"[SERVER WARNING]({where}) : TCP Connection to {conn.getpeername()[0]}:{conn.getpeername()[1]} already exists"
    else:
        return f"[SERVER WARNING]({where}) : {msg}"

########### CONNECTION FUNCTIONS ###########
# Starting and initialising the server.    #
#                                          #
# NOTE: The server is set to non blocking  # 
# mode.                                    # 
############################################
def handle_message(message_dict, SENDER_SOCKET):
    global SERVER_SOCKET, CONNECTED, SERVER_PORT, MLEN, CLIENT_DICT
    CMD = message_dict['CMD']
    if CMD == "JOIN":
        clients_connected_uids = []
        for PORT in CLIENT_DICT:
            if "UID" in CLIENT_DICT[PORT]:
                clients_connected_uids.append(CLIENT_DICT[PORT]["UID"])
        if message_dict['UID'] not in clients_connected_uids:
            to_send = {
                "CMD":"ACK",
                "TYPE":"OKAY"
            }
            CLIENT_DICT[SENDER_SOCKET]["UN"] = message_dict["UN"]
            CLIENT_DICT[SENDER_SOCKET]["UID"] = message_dict["UID"]
            SENDER_SOCKET.send(json.dumps(to_send).encode("ascii"))
        else:
            to_send = {
                "CMD": "ACK",
                "TYPE": "FAIL"
            }
            SENDER_SOCKET.send(json.dumps(to_send).encode("ascii"))
            
def start_server(argv):
    global SERVER_SOCKET, CONNECTED, SERVER_PORT, MLEN, CLIENT_DICT
    SERVER_PORT = int(argv[1]) if len(argv) == 2 else 40452
    if not SERVER_SOCKET:
        SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #SERVER_SOCKET.setblocking(0)
        try:
            SERVER_SOCKET.bind(("", SERVER_PORT))
        except socket.error as err:
            print(connection_error(err, "socket.bind()"))
        else:
            SERVER_SOCKET.listen()
            CONNECTED = True
        
        READ_LIST = [SERVER_SOCKET]
        WRITE_LIST = []
        CLIENT_LIST = []

        while CONNECTED:
            try:
                READ_READY, WRITE_READY, EXCEPTION_READY = select.select(READ_LIST, [], [], 10)
            except select.error as error:
                print(connection_error(error, "select()"))
            except KeyboardInterrupt:
                print(connection_error("[SERVER SHUTDOWN]", "KeyboardInterrupt"))
                sys.exit(1)
            else:
                if READ_READY:
                    for SOCKET in READ_READY:
                        if SOCKET == SERVER_SOCKET:
                            CLIENT_SOCKET, CLIENT_ADDRESS = SOCKET.accept()
                            READ_LIST.append(CLIENT_SOCKET)
                            CLIENT_LIST.append(CLIENT_SOCKET)
                            CLIENT_DICT[CLIENT_SOCKET] = {}
                            print(CLIENT_DICT)
                        else:
                            receive_message = SOCKET.recv(MLEN)
                            json_string_message = receive_message.decode("ascii")
                            if receive_message:
                                print(connection_success(SOCKET, "start_server()", f"Received message : {json_string_message}" ))
                                message = json.loads(json_string_message)
                                handle_message(message, SOCKET)
                                
                            else:
                                print(connection_error(f"connection to {CLIENT_SOCKET.getpeername()[0]}:{CLIENT_SOCKET.getpeername()[1]} is broken.", "select()"))
                                READ_LIST.remove(SOCKET)
                                CLIENT_LIST.remove(SOCKET)
                                break
                else:
                    print(connection_warning(None, "main_loop", "Server Idle"))

if __name__ == '__main__':
	if len(sys.argv) > 2:
		print("Usage: chatserver [<Server_port>]")
		sys.exit(1)
	start_server(sys.argv)
