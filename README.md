# Simple Chat Application

A python application using UDP sockets and consist of one server and clients.

## Dependencies
termcolor 
``` 
$ pip install termcolor
```

Python 3
```
$ python --version
Python 3.6.5
```
### Feautures
  - Realtime chat 
  
  - Offline Chat

  - Registering to Server

  - Deregistering to Server

  - Listing the client's table
  
  - Notification's for the message received
  
  - Handling the chat when server is down
  
  - Handling chat when the client is down

## How to start
The project consist of two parts. Server and Client.

First go the directory containg the python main file `UdpChat.py` and logging configuration file `log.conf`
```
$ cd UdpChat
```
#### Server
To start the server it has folowing format for the arguments passed to it.
Start the server before than the clients
```
$ python UdpChat.py -s {port}
```
e.g I want to start the server on 1444 then

```
$ python UdpChat.py -s 1444
```
#### Client
To start the client it has following format for the arguments passed to it.

```
$ python UdpChat.py -c {nick_name} {Server_IP} {Server_port} {Client_port}
```

e.g I want to start a client with a name test. The server IP will be `127.0.01` as it is running localhost in this case. The server_port will be the same on which the server is started. The client_port will be different for each client

##### Client 1 
```
$ python UdpChat.py -c X 127.0.0.1 1444 2000
```

##### Client 2
```
$ python UdpChat.py -c Y 127.0.0.1 1444 2001
```
##### Client 3 
```
$ python UdpChat.py -c Z 127.0.0.1 1444 2002
```
and so on.
