#!/usr/bin/python3

# Student name and No.: Ritvik Singh
# Development platform: MacOS Montery 12.1 (Intel Chip)
# Python version: Python 3.8.5
from tkinter import *
from tkinter import ttk
from tkinter import font
import sys
import socket
import json
import os
import threading
import time

#
# Global variables
#
MLEN=1000      #assume all commands are shorter than 1000 bytes
USERID = None
NICKNAME = None
SERVER = None
SERVER_PORT = None
CLIENT_SOCKET = None
CONNECTED = False
HANDSHAKE = False
CLIENT_LIST = {}

##########################################
######### CLIENT IMPLEMENTATION ##########
##########################################


######### SYNCHRONOUS LOGGERS ############
# For printing success and failure       #
# messages to the terminal as well as    #
# console pane,                          #
#                                        #
# 1. connection_success()                #
# 2. connection_error()                  #
# 3. connection warning()                #
##########################################
def connection_success(conn, where, msg=""):
    if msg == "":
        return f"[CLIENT SUCCESS]({where}) : TCP Connection to {conn.getpeername()[0]}:{conn.getpeername()[1]} has been established."
    else:
        return f"[CLIENT SUCCESS] ({where}) : {msg}"
def connection_error(error, where):
    return f"[CLIENT ERROR]({where}) : {error}"

def connection_warning(conn, where, msg = ""):
    if msg == "":
        return f"[CLIENT WARNING]({where}) : TCP Connection to {conn.getpeername()[0]}:{conn.getpeername()[1]} already exists"
    else:
        return f"[CLIENT WARNING]({where}) : {msg}"

########## CONNECTION FUNCTIONS ########
# Establishing of TCP connection       #
# and logical connections ie sending   #
# JOIN command.                        #
#                                      #
# 1. start_client()                    #
# 2. establish_connection()            #
# 3. non_blocking_recv()               #
# 4. handle_message()                  # 
# 5. send_message()                    #
#                                      #
# NOTE: non_blockin_recv() will        #
# experinece timeout by defintion      #
########################################

def handle_message(data):
    global CONNECTED, CLIENT_SOCKET, USERID, NICKNAME, SERVER, SERVER_PORT, MLEN, CLIENT_LIST, HANDSHAKE
    CMD = data["CMD"]
    if CMD == "ACK":
        if data["TYPE"] == "OKAY": 
            HANDSHAKE = True
            print(connection_success(CLIENT_SOCKET, "handle_message()", "SUCCESS - HANDSHAKING COMPLETE - ACK RECEIVED"))
            console_print(connection_success(CLIENT_SOCKET, "handle_message()", "SUCCESS - HANDSHAKING COMPLETE - ACK RECEIVED"))
        else:
            print(connection_error("NACK received during duplicate hanshaking", "handle_message()"))
            console_print(connection_error("NACK received during duplicate hanshaking", "handle_message()"))
    elif CMD == "LIST":
        peer_list = data['DATA']
        peers = []
        for peer in peer_list:
            peers.append(peer['UN'] + " (" + peer["UID"] + ")")
            peer_string = ", ".join(peers)
            CLIENT_LIST[peer["UN"]] = peer["UID"]
        list_print(peer_string)
        print(connection_success(CLIENT_SOCKET, "handle_message()", f"LIST {json.dumps(data)} : PEER LIST UPDATED"))
        console_print(connection_success(CLIENT_SOCKET,"handle_message()", f"LIST {json.dumps(data)} : PEER LIST UPDATED"))
    elif CMD == "MSG":
        print("CLIENT_HERE")
        TYPE = data["TYPE"]
        uid = data["FROM"]
        message = data["MSG"]
        display_name = ""
        for nickname in CLIENT_LIST:
            if CLIENT_LIST[nickname] == uid:
                display_name = nickname
                break
        
        message_display_string = f"[{display_name}] {message}"
        if TYPE == "PRIVATE":
            chat_print(message_display_string, 'redmsg')
        elif TYPE == "GROUP":
            chat_print(message_display_string, 'greenmsg')
        else:
            chat_print(message_display_string, 'bluemsg')

        console_print("Received MSG " + json.dumps(data))
        

def non_blocking_recv():
    global CONNECTED, CLIENT_SOCKET, USERID, NICKNAME, SERVER, SERVER_PORT, MLEN
    print(connection_success(CLIENT_SOCKET, "non_blocking_recv()", "Slave Thread Started")) 
    console_print(connection_success(CLIENT_SOCKET, "non_blocking_recv()", "Slave Thread Started"))
    while CONNECTED:
        try:
            raw_message = CLIENT_SOCKET.recv(MLEN)
        except socket.error as err: 
            print(". . . .")
        else:
            if raw_message:
                rm = raw_message.decode("ascii").split("}{")
                print("No of messagees: ", len(rm))
                messages = []
                if len(rm) > 1:
                    for i  in range(len(rm)):
                        if i == 0:
                            messages.append(rm[i] + "}")
                        elif i == len(rm) - 1:
                            messages.append("{" + rm[i])
                        else:
                            messages.append("{" + rm[i] + "}")
                    for message in messages:
                        handle_message(json.loads(message))
                else:
                    [message] = rm
                    handle_message(json.loads(message))
            else:                      
                print(connection_error("Connection to server is broken", "non_blocking_recv()"))
                console_print(connection_error("Connection to server is broken", "non_blocking_recv()"))
                CONNECTED = False
                
            
def start_client():
    global CONNECTED, CLIENT_SOCKET, USERID, NICKNAME, SERVER, SERVER_PORT, HANDSHAKE
    if not CLIENT_SOCKET:
        CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if not CONNECTED:
        try:
            CLIENT_SOCKET.settimeout(2)
            CLIENT_SOCKET.connect((SERVER, SERVER_PORT))
        except socket.error as err:  
            print(connection_error(err, "start_client()"))
            console_print(connection_error(err, "start_client()")) 
    if not CONNECTED:
        CONNECTED = True
        establish_connection()
        reader_thread = threading.Thread(target=non_blocking_recv)
        reader_thread.start()
        print(connection_success(CLIENT_SOCKET, "start_client()"))
        console_print(connection_success(CLIENT_SOCKET, "start_client()"))
    else:
        establish_connection()
        print(connection_warning(CLIENT_SOCKET, "start_client()"))
        console_print(connection_warning(CLIENT_SOCKET, "start_client"))

def establish_connection():
    global CONNECTED, HANDSHAKE, CLIENT_SOCKET, USERID, NICKNAME, SERVER, SERVER_PORT
    if CONNECTED:
        message = {
            "CMD": "JOIN",
            "UN": NICKNAME,
            "UID": USERID,
        }
        string = json.dumps(message)
        try:  
            CLIENT_SOCKET.send(string.encode("ascii"))
        except socket.error as err: 
            print(connection_error(err, "establsh_connection()"))
            console_print(connection_error(err, "establsh_connection()"))       
    else:
        print(connection_error("Connection is broken", "establish_connection()"))
        console_print(connection_error("Connection is broken", "establish_connection"))

def send_message():
    global CONNECTED, HANDSHAKE, CLIENT_SOCKET, USERID, NICKNAME, SERVER, SERVER_PORT, CLIENT_LIST
    if CONNECTED and HANDSHAKE:
        message_string = get_sendmsg()
        to_string = get_tolist()
        to_field = []
        print(message_string)
        print(to_string)
        if message_string.strip() and to_string.strip():
            message_recepient_names = to_string.split(", ")
            if len(message_recepient_names) == 1 and message_recepient_names[0] == "ALL":
                if len(CLIENT_LIST) == 1:
                    print(connection_error("Can not send message to self. Try again", "send_message()"))
                    console_print(connection_error("Can not send message to self. Try again", "send_message()"))
                    return
                else:
                    to_field = []
            else:
                for name in message_recepient_names:
                    if name == NICKNAME:
                        print(connection_error("Can not send message to self. Try again", "send_message()"))
                        console_print(connection_error("Can not send message to self, Try again", "send_message()"))
                        return 
                    elif name not in CLIENT_LIST:
                        print(connection_error(f"'{name}' is not a valid recepient. Try again", "send_message()"))
                        console_print(connection_error(f"'{name}' is not a valid recepient. Try again", "send_message()"))
                        return
                    else:
                        to_field.append(CLIENT_LIST[name])
            raw_message = {
                "CMD": "SEND",
                "MSG": message_string,
                "TO": to_field,
                "FROM": USERID,
            }
            try:
                CLIENT_SOCKET.send(json.dumps(raw_message).encode("ascii"))
            except socket.error as err:
                print(connection_error(err, "send_message()"))
                console_print(connection_error(err, "send_message()"))
            else:
                chat_print(f"[To: {to_string}] {message_string}")
                print(connection_success(CLIENT_SOCKET, "send_message()", f"SENT MESSAGE : {json.dumps(raw_message)}" ))
                console_print(connection_success(CLIENT_SOCKET, "send_message()", f"SENT MESSAGE : {json.dumps(raw_message)}" ))
        else:
            print(connection_error("Please fill in TO: and MESSAGE", "send_message()"))
            console_print(connection_error("Please fill in TO: and MESSAGE", "send_message()"))
    else:
        print(connection_error("Establish Connection to Server before sending message", "send_message()"))
        console_print(connection_error("Establish Connection to Server before sending message", "send_message()"))

#
# Functions to handle user input
#

def do_Join():
  start_client()

def do_Send():
  send_message()

def do_Leave():
  #The following statement is just for demo purpose
  #Remove it when you implement the function
  #list_print("Press do_Leave()")
  global CONNECTED, CLIENT_SOCKET, USERID, NICKNAME, SERVER, SERVER_PORT, MLEN, CLIENT_LIST, HANDSHAKE
  if CONNECTED and HANDSHAKE:
      CLIENT_SOCKET.close()
      CLIENT_SOCKET = None
      CONNECTED = False
      HANDSHAKE = False
      CLIENT_LIST = {}
      print(connection_success(None, "do_Leave()", "Client has terminatad this TCP connection. To rejoin, click Join again. "))
      console_print(connection_success(None, "do_Leave()", "Client has terminated this TCP connection. To rejoin, click Join agian."))
      list_print("")
#################################################################################
#Do not make changes to the following code. They are for the UI                 #
#################################################################################

#for displaying all log or error messages to the console frame
def console_print(msg):
  console['state'] = 'normal'
  console.insert(1.0, "\n"+msg)
  console['state'] = 'disabled'

#for displaying all chat messages to the chatwin message frame
#message from this user - justify: left, color: black
#message from other user - justify: right, color: red ('redmsg')
#message from group - justify: right, color: green ('greenmsg')
#message from broadcast - justify: right, color: blue ('bluemsg')
def chat_print(msg, opt=""):
  chatWin['state'] = 'normal'
  chatWin.insert(1.0, "\n"+msg, opt)
  chatWin['state'] = 'disabled'

#for displaying the list of users to the ListDisplay frame
def list_print(msg):
  ListDisplay['state'] = 'normal'
  #delete the content before printing
  ListDisplay.delete(1.0, END)
  ListDisplay.insert(1.0, msg)
  ListDisplay['state'] = 'disabled'

#for getting the list of recipents from the 'To' input field
def get_tolist():
  msg = toentry.get()
  toentry.delete(0, END)
  return msg

#for getting the outgoing message from the "Send" input field
def get_sendmsg():
  msg = SendMsg.get(1.0, END)
  SendMsg.delete(1.0, END)
  return msg

#for initializing the App
def init():
  global USERID, NICKNAME, SERVER, SERVER_PORT, CONNECTED

  #check if provided input argument
  if (len(sys.argv) > 2):
    print("USAGE: ChatApp [config file]")
    sys.exit(0)
  elif (len(sys.argv) == 2):
    config_file = sys.argv[1]
  else:
    config_file = "config.txt"

  #check if file is present
  if os.path.isfile(config_file):
    #open text file in read mode
    text_file = open(config_file, "r")
    #read whole file to a string
    data  = text_file.read()
    #close file
    text_file.close()
    #convert JSON string to Dictionary object
    config = json.loads(data)
    USERID = config["USERID"].strip()
    NICKNAME = config["NICKNAME"].strip()
    SERVER = config["SERVER"].strip()
    SERVER_PORT = config["SERVER_PORT"]
  else:
    print("Config file not exist\n")
    sys.exit(0)


if __name__ == "__main__":
  init()

#
# Set up of Basic UI
#
win = Tk()
win.title("ChatApp")

#Special font settings
boldfont = font.Font(weight="bold")

#Frame for displaying connection parameters
topframe = ttk.Frame(win, borderwidth=1)
topframe.grid(column=0,row=0,sticky="w")
ttk.Label(topframe, text="NICKNAME", padding="5" ).grid(column=0, row=0)
ttk.Label(topframe, text=NICKNAME, foreground="green", padding="5", font=boldfont).grid(column=1,row=0)
ttk.Label(topframe, text="USERID", padding="5" ).grid(column=2, row=0)
ttk.Label(topframe, text=USERID, foreground="green", padding="5", font=boldfont).grid(column=3,row=0)
ttk.Label(topframe, text="SERVER", padding="5" ).grid(column=4, row=0)
ttk.Label(topframe, text=SERVER, foreground="green", padding="5", font=boldfont).grid(column=5,row=0)
ttk.Label(topframe, text="SERVER_PORT", padding="5" ).grid(column=6, row=0)
ttk.Label(topframe, text=SERVER_PORT, foreground="green", padding="5", font=boldfont).grid(column=7,row=0)


#Frame for displaying Chat messages
msgframe = ttk.Frame(win, relief=RAISED, borderwidth=1)
msgframe.grid(column=0,row=1,sticky="ew")
msgframe.grid_columnconfigure(0,weight=1)
topscroll = ttk.Scrollbar(msgframe)
topscroll.grid(column=1,row=0,sticky="ns")
chatWin = Text(msgframe, height='15', padx=10, pady=5, insertofftime=0, state='disabled')
chatWin.grid(column=0,row=0,sticky="ew")
chatWin.config(yscrollcommand=topscroll.set)
chatWin.tag_configure('redmsg', foreground='red', justify='right')
chatWin.tag_configure('greenmsg', foreground='green', justify='right')
chatWin.tag_configure('bluemsg', foreground='blue', justify='right')
topscroll.config(command=chatWin.yview)

#Frame for buttons and input
midframe = ttk.Frame(win, relief=RAISED, borderwidth=0)
midframe.grid(column=0,row=2,sticky="ew")
JButt = Button(midframe, width='8', relief=RAISED, text="JOIN", command=do_Join).grid(column=0,row=0,sticky="w",padx=3)
QButt = Button(midframe, width='8', relief=RAISED, text="LEAVE", command=do_Leave).grid(column=0,row=1,sticky="w",padx=3)
innerframe = ttk.Frame(midframe,relief=RAISED,borderwidth=0)
innerframe.grid(column=1,row=0,rowspan=2,sticky="ew")
midframe.grid_columnconfigure(1,weight=1)
innerscroll = ttk.Scrollbar(innerframe)
innerscroll.grid(column=1,row=0,sticky="ns")
#for displaying the list of users
ListDisplay = Text(innerframe, height="3", padx=5, pady=5, fg='blue',insertofftime=0, state='disabled')
ListDisplay.grid(column=0,row=0,sticky="ew")
innerframe.grid_columnconfigure(0,weight=1)
ListDisplay.config(yscrollcommand=innerscroll.set)
innerscroll.config(command=ListDisplay.yview)
#for user to enter the recipents' Nicknames
ttk.Label(midframe, text="TO: ", padding='1', font=boldfont).grid(column=0,row=2,padx=5,pady=3)
toentry = Entry(midframe, bg='#ffffe0', relief=SOLID)
toentry.grid(column=1,row=2,sticky="ew")
SButt = Button(midframe, width='8', relief=RAISED, text="SEND", command=do_Send).grid(column=0,row=3,sticky="nw",padx=3)
#for user to enter the outgoing message
SendMsg = Text(midframe, height='3', padx=5, pady=5, bg='#ffffe0', relief=SOLID)
SendMsg.grid(column=1,row=3,sticky="ew")

#Frame for displaying console log
consoleframe = ttk.Frame(win, relief=RAISED, borderwidth=1)
consoleframe.grid(column=0,row=4,sticky="ew")
consoleframe.grid_columnconfigure(0,weight=1)
botscroll = ttk.Scrollbar(consoleframe)
botscroll.grid(column=1,row=0,sticky="ns")
console = Text(consoleframe, height='10', padx=10, pady=5, insertofftime=0, state='disabled')
console.grid(column=0,row=0,sticky="ew")
console.config(yscrollcommand=botscroll.set)
botscroll.config(command=console.yview)

win.mainloop()
