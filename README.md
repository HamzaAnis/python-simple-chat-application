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

  - Deregistering yourslef on Server
  
  - Deregistering anyone on the Server

  - Listing the client's table that is maintaines by server
  
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

## Working
There are multiple options for the client
```
Multiple options available
>>>> send <name> <message>
>>>> list
>>>> reg <nick-name>
>>>> dereg <nick-name>
>>>>>deregA <any one>
>>>>exit
```
  - list
  
  Displays the details for the client that are registered on the server and theie status

  - send <name_of_receiver>
  
  This sends the message to another user 
  
  - dereg <yourname>
  
  This makes only yourself dereg/offline on the server
  
  - deregA <any_one_else>
  
  This command helps you derestering anyone in the server
  
  - reg <yourname>
  
  This command make you online/reg on the server again after being online.

## Logging

The logging for the program is diabled by default. If you want to enable it then go to the `log.conf` file and change this handleer at Line 10 from

```
[logger_root]
level=WARNING
handlers=stream_handler, file 
```
to
```
[logger_root]
level=DEBUG
handlers=stream_handler, file 
```
By doing this you can see all the messages that are generated between the servers and clients.
