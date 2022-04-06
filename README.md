# Multi User Chat Application

This repository contains a TCP implementation of a Multi-User Chat Application using Socket Programming in Python. 
The link to the repository is [here](https://github.com/pattharock/MUCA.git)

The files contained herein are:
  * `ChatApp.py` which starts a client instance for each client
  * `Chatserver.py` which starts the centralised server instance. 
  * `config(1, 2, 3).txt` used for initialising client state [SEE BELOW]
  * `start-OSX.sh` - a quick start script which initialises 4 client instances along with one server instance.

## Documentation Info
* `Name` __Ritvik Singh__
* `University Number` __3035553044__
* `Development Platform` __MacOS Montery 12.1__
* `Python Version` __Python 3.8.5__


## Getting Started
To run on OSX, use the shell script `start-OSX.sh`

```
sh start-OSX.sh
```

Or if you prefer to start individually,
 
 
the __server__ can be started using `python3 Chatserver.py <optional_port_number>`. If no port number is given server will start at PORT 40452.

```
python3 Chatserver.py
```

The client needs to be initialised using the config files as an argument. The content of the config files will be JSON as below

`config.txt`

```
{
  "USERID": "henry@hku.hk",
  "NICKNAME": "Henry",
  "SERVER": 127.0.0.1,
  "SERVER_PORT": 40452
}
```

Get a __client__ instance running using `python3 ChatApp.py <config-file>` 

```
python3 ChatApp.py config1.txt 
```

## Communication Protocol

For this project, the communication protocol employed is a JSON based toy protocol and consists of the following commands, all of which have been implemented. 

#### `JOIN`
* Send from client to server. upon clicking the join button. 
* Fields (mandatory)
  * "CMD": "JOIN"
  * "UN" : "Nickname of user"
  * "UID": "UID of user"
* Establishes a TCP connection with the server and initiates the handshake process.
* NOTE: Handshake here does not refer to the TCP Handshake, but the sending of join, followed by receipt of ACK:OKAY.

```
{
  "CMD": "JOIN",
  "UN": "Tony",
  "UID": "Tony@hku.hk"
}
```

#### `ACK`
* Send from server to client in response to `JOIN` command.
* Fields (mandatory)
  * "CMD" : "ACK" 
  * "TYPE": "OKAY/FAIL"
* Server sends OKAY/FAIL after accepting/rejecting the `JOIN` request. 

```
{
  "CMD": "ACK", 
  "TYPE": "OKAY"
}
```
is used as a positive acknowlegement and accordingly `FAIL` is used for Negative Acknowlegement. 


#### `LIST`
* Send by server to client to inform about the currently connected peers to the server.
* Fields (Mandatory)
  * "CMD" : "LIST"
  * "DATA": \[peer_list\]

Example usage

```
{
  "CMD": "LIST", 
  "DATA": [{"UN": "Mary", "UID": "mary@hku.hk"}, {"UN": "Henry", "UID": "henry@hku.hk"}]
}
```

#### `SEND`
* Sent by client to server to indicate message to be sent to target peers (can be individual, group, or broadcast).
* Fields (Mandatory)
  * "CMD": "SEND"
  * "MSG" : "message to be sent"
  * "TO": 
    * [] for broadcast to all (broadcasr)
    * ["tony@hku.hk"] for sending to single peer (individual/private)
    * ["peter@hku.hk", "mary@hku.hk"] for sending to multiple peers [group]
  * "FROM": "userID of sender"

NOTE: 
  1. Send does not directly send message to target peers, rather delivers to server for appropriate handling.
  2. Users can not send any kind of message to themselves (handled case)
Example usage

```
{
  "CMD": "SEND",
  "MSG": "This is a message",
  "TO": ["tony@hku.hk"],'
  "FROM": "peter@hku.hk"
}
```

#### `MSG`
* Used to send the messages from server to destination peers
* Fields (Mandatory)
  * "CMD": "MSG"
  * "TYPE": "ALL/GROUP/PRIVATE"
  * "MSG": "the message contents"
  * "FROM" : "the user ID of the sender"

Example usage

```
{
  "CMD": "MSG",
  "TYPE": "PRIVATE", 
  "MSG": "this is a private message",
  "FROM": "tony@hku.hk"
}
```

## Implementation Methodoloy

### Client
The client makes use of multi-threading. The worker thread created is used for accepting the asynchronous `recv()` calls and the main thread is used for `send()` as well as the _Tkinter GUI_.

### Server
The server makes use of single threaded process with `select()` for __IO__.


## Features Implemented

### Client
  * \[JOIN BUTTON\]
    * Can successfully join the Chatserver and detect a failure in joining
    * Allow user to rejoin the Chatserver if the connection to Chatserver is broken
    * Report to the user when the Chatserver is not reachable/available after 2 seconds
  * \[SEND BUTTON\]
    * Check the `TO:` and  `message` fields.
    * Handle Private, Group, and Broadcast Messages.
    *  Displaying messages
  * \[LEAVE BUTTON\]  
    * Closes the current TCP connection
    * Allows the user to rejoin the Chatroom.
  *  Display peer list
    * Can display the updated peer list upon receiving the LIST command
    * Display received chat messages
    * Can display those received messages with the correct display setting

### Server
  * Connection and peer management
    * Accept any TCP client requests
    * Able to detect broken connections
    * Accept/reject peer join request and send updated peer list after accepting the peer
    * Able to remove a specific peer when its TCP connection is broken and send updated peer list to all
  * Handle chat messages
    * Handle private, group, & broadcast messages
    * Correctly send the messages to target peer(s)  


## Note
1. If on starting up, you find that server port is already in use, you may try to wait for upto 1 minute before starting up again or aternatively use another port, although that may require changing the SERVER_PORT in the config files.

2. While specifying the recepients of the message, the delimiter between nicknames is ", " and not "," so nicknames will take the form `name1, name2, name3` and not `name1,name2,name3`

## Sample Outputs

Below find the sample outputs on running the application on the software and python verison as mentioned in _documentation info_

![Screenshot 1](./info/sc1.png?raw=true "Screenshot 1")

![Screenshot 2](./info/sc2.png?raw=true "Screenshot 2")
