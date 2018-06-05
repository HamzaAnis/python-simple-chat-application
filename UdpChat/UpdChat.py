import logging
from logging.config import fileConfig
from os import path
import os
import sys
import socket

class Server(object):
    """docstring for Server."""

    def __init__(self, port):
        super(Server, self).__init__()
        self.port = port

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('', int(self.port)))
        logging.info("Server started")
        while True:
            message, address = self.server_socket.recvfrom(1024)
            logging.info(message)
            self.server_socket.sendto("Welcome, You are registered.".encode(),address)
   

class Client(object):
    """docstring for Client."""

    def __init__(self, nickname, server_ip, server_port, client_port):
        super(Client, self).__init__()
        self.nick_name=nickname
        self.server_ip=server_ip
        self.server_port=server_port
        self.client_port=client_port
    def start(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(1.0)
        self.addr = (self.server_ip, int(self.server_port))
        self.do_registration()
        
    def do_registration(self):
        reg=self.nick_name+" "+self.client_port+" "+self.server_ip+" "+self.server_port
        self.client_socket.sendto(reg, self.addr)
        logging.info("Client reg send")
        data, server = self.client_socket.recvfrom(1024)
        print(str(data))
        logging.info("Welcome message received")


class UdpChat(object):
    """docstring for UdpChat."""

    def __init__(self, mode, port, nick_name, server_ip, server_port,
                 client_port):
        super(UdpChat, self).__init__()
        logging.info(mode)
        logging.info(port)
        logging.info(nick_name)
        logging.info(server_ip)
        logging.info(server_port)
        logging.info(client_port)
        self.mode = mode
        if (mode == "-c"):
            logging.info("Client Called")
            self.instance=Client(nick_name,server_ip,server_port,client_port)
        elif (mode == "-s"):
            logging.info("Server Called")
            self.instance = Server(port)


if __name__ == "__main__":
    fileConfig('log.conf')
    logger = logging.getLogger()
    logging.info(len(sys.argv))
    # Calling server
    if (len(sys.argv) == 3):
        U = UdpChat(sys.argv[1], sys.argv[2], None, None, None, None)
    # Calling client
    elif (len(sys.argv) == 6):
        U = UdpChat(sys.argv[1], None, sys.argv[2], sys.argv[3], sys.argv[4],
                    sys.argv[5])
    else:
        logging.critical("Invalid format!")
        print("Exiting")
        sys.exit(0)
    U.instance.start()