import logging
from logging.config import fileConfig
from os import path
import os
import sys
import socket
import threading
from termcolor import cprint
from time import sleep


class Server(object):
    """docstring for Server."""

    def __init__(self, port):
        super(Server, self).__init__()
        self.port = port
        self.client_table = []

    def handle_deref(self, username, address):
        logging.info("Deregging received for "+username+"|")
        for i in range(len(self.client_table)):
            logging.info(str(i)+" i")
            v = self.client_table[i]
            if(v[0] == username):
                v[4] = "OFFLINE"
                logging.info("User found and deleted it")
                self.client_table_broadcast()
                sleep(5.0)
                self.server_socket.sendto(
                    "You are Offline. Bye.".encode(), address)

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('', int(self.port)))
        logging.info("Server started")
        while True:
            message, address = self.server_socket.recvfrom(1024)
            request = message.decode("utf-8")
            logging.info(request)
            to_do = request.split(" ")
            logging.info("To do is ")
            logging.info(to_do[0])
            if to_do[0] == "dereg":
                self.handle_deref(to_do[1], address)
                continue
            self.server_socket.sendto("Welcome, You are registered.".encode(),
                                      address)
            # client information received from client
            client_data = message.decode("utf-8").split(" ")
            client_data.append("ONLINE")
            # appending to the client table
            self.client_table.append(client_data)
            logging.info("Client Port is " + client_data[1])
            logging.info(client_data)
            self.client_table_broadcast()

    def client_table_broadcast(self):
        for v in self.client_table:
            self.send_table_to_client(v[2], int(v[1]))

    def send_table_to_client(self, client_ip, client_port):
        """To send the client table on the client's port

        Arguments:
            client_ip {[str]} -- [Client Ip]
            client_port {[int]} -- [Client Port]
        """

        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        b_addr = (client_ip, client_port)
        logging.info("Sent to " + client_ip + "  " + str(client_port))
        logging.info(self.table_to_string().encode())
        broadcast_socket.sendto(self.table_to_string().encode(), b_addr)

    def table_to_string(self):
        send = ""
        for v in self.client_table:
            send = send + v[0] + " " + v[1] + " " + \
                v[2] + " " + v[3] + " " + v[4] + "\n"
        return send


class Client(object):
    """docstring for Client."""

    def __init__(self, nickname, server_ip, server_port, client_port):
        super(Client, self).__init__()
        self.nick_name = nickname
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_port = client_port
        self.client_table = []

    def start(self):
        self.broadcast_thread = threading.Thread(
            group=None,
            target=self.client_table_broadcast_service,
            name="Broadcast Service")
        # starting broadcast thread to recieve client table from server
        self.broadcast_thread.start()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(1.0)
        self.addr = (self.server_ip, int(self.server_port))
        # starting client initial registration
        self.do_registration()
        # to start the thread to receive the table
        self.input_thread = threading.Thread(
            group=None,
            target=self.client_actions,
            name="Broadcast Service")
        self.input_thread.start()

    def print_client_table(self):
        header = "{:^10} {:^20} {:^10} {:^10}".format(
            'NAME', 'IP', 'PORT', 'STATUS')
        cprint(header, "red")
        logging.info(len(self.client_table))
        for i in range(len(self.client_table)-1):
            v = self.client_table[i]
            line = "{:^10} {:^20} {:^10} {:^10}".format(v[0], v[1], v[2], v[4])
            cprint(str(line), "red")

    def client_actions(self):
        while(1):
            cprint(
                "Multiple options available\n>>>> send <name> <message>\n>>>> list\n>>>> dereg <nick-name>\n", "red")
            command = input()
            choice = command.split(" ")[0]
            logging.info("Choice is ")
            logging.info(choice)
            if(choice == "send"):
                logging.info("Sending to the client")
            elif(choice == "list"):
                logging.info("Listing table")
                self.print_client_table()
            elif choice == "dereg":
                self.perform_dereg(command)

    def perform_dereg(self,command):
        logging.info("Deregging inititate")
        dereg_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dereg_client_socket.settimeout(0.5)
        dereg_client_socket.sendto(command.encode(), self.addr)
        retry=0
        while(retry<5):
            try:
                data, server = dereg_client_socket.recvfrom(1024)
                cprint(data.decode("utf-8"), "green")
                return None
            except socket.timeout:
                logging.info(str(retry)+": ACK not received on registration")
                retry=retry+1
        cprint("[Server not responding]\n[Exiting]","red")
        os._exit(1)
    def client_table_broadcast_service(self):
        """This method starts another socket on which it receives the update client table
        """

        logging.info("Client table service started at " + self.client_port)
        self.broadcast_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
        self.broadcast_socket.bind(('', int(self.client_port)))
        while True:
            message, address = self.broadcast_socket.recvfrom(1024)
            print("[Client table received]\n")
            logging.info("Client table service received at " +
                         self.client_port)
            self.update_client_table(message.decode("utf-8"))

    def update_client_table(self, table):
        logging.info("Table string is")
        logging.info(table)
        # clearing the list
        self.client_table[:] = []
        client_line = table.split("\n")
        logging.info("Client line is")
        logging.info(client_line)
        logging.info("length of data is "+str(len(client_line)))
        for v in client_line:
            client_data = v.split(" ")
            logging.info("1 client length is "+str(len(client_data)))
            self.client_table.append(client_data)
            logging.info("Table Updated: \n")
            logging.info(self.client_table)

    def do_registration(self):
        reg = self.nick_name + " " + self.client_port + \
            " " + self.server_ip + " " + self.server_port
        self.client_socket.sendto(reg.encode(), self.addr)
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
