import logging
from logging.config import fileConfig
from os import path
import os
import sys
import socket
import threading


class Server(object):
    """docstring for Server."""

    def __init__(self, port):
        super(Server, self).__init__()
        self.port = port
        self.client_table = []

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('', int(self.port)))
        logging.info("Server started")
        while True:
            message, address = self.server_socket.recvfrom(1024)
            logging.info(message)
            self.server_socket.sendto("Welcome, You are registered.".encode(),
                                      address)
            client_data = str(message).split(" ")
            logging.info("Client Port is " + client_data[1])
            logging.info(client_data)
            self.client_table_broadcast_service(client_data[2],int(client_data[1]))

    def client_table_broadcast_service(self, client_ip, client_port):
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        b_addr = (client_ip, client_port)
        logging.info("Sent to "+client_ip+"  "+str(client_port))
        broadcast_socket.sendto("Here is your client table".encode(), b_addr)


class Client(object):
    """docstring for Client."""

    def __init__(self, nickname, server_ip, server_port, client_port):
        super(Client, self).__init__()
        self.nick_name = nickname
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_port = client_port

    def start(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(1.0)
        self.addr = (self.server_ip, int(self.server_port))
        self.broadcast_thread = threading.Thread(
            group=None,
            target=self.client_table_broadcast_service,
            name="Broadcast Service")
        self.broadcast_thread.start()
        self.do_registration()
        # to start the thread to receive the table
       

    def client_table_broadcast_service(self):
        logging.info("Client table service started at "+self.client_port)
        self.broadcast_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
        self.broadcast_socket.bind(('', int(self.client_port)))
        while True:
            message, address = self.broadcast_socket.recvfrom(1024)
            print("[Client table received]\n" + message)
            logging.info("Client table service received at "+self.client_port)


    def do_registration(self):
        reg = self.nick_name + " " + self.client_port + " " + self.server_ip + " " + self.server_port
        self.client_socket.sendto(reg, self.addr)
        logging.info("Client reg send")
        data, server = self.client_socket.recvfrom(1024)
        print(str(data))
        logging.info("[Welcome message received]")


class UdpChat(object):
    """docstring for UdpChat."""

    def __init__(self, mode, port, nick_name, server_ip, server_port,
                 client_port):
        super(UdpChat, self).__init__()
        logging.info("Mode " + mode)
        logging.info("Sever port" + str(port))
        logging.info("Nick name " + str(nick_name))
        logging.info("Server IP: " + str(server_ip))
        logging.info("Sever Port: " + str(server_port))
        logging.info("Client Port:" + str(client_port))
        self.mode = mode
        if (mode == "-c"):
            logging.info("Client Called")
            self.instance = Client(nick_name, server_ip, server_port,
                                   client_port)
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