import logging
from logging.config import fileConfig
from os import path
import os
import sys
import socket
import threading
from termcolor import cprint
from time import sleep
import datetime


class Server(object):
    """docstring for Server."""

    def __init__(self, port):
        super(Server, self).__init__()
        self.port = port
        self.client_table = []

    def handle_dereg(self, username, address):
        logging.info("Deregging received for "+username+"|")
        for i in range(len(self.client_table)):
            v = self.client_table[i]
            if(v[0] == username):
                v[4] = "OFFLINE"
                logging.info("User found and unregisterded it")
                self.client_table_broadcast()
                # sleep(5.0)
                self.server_socket.sendto(
                    "You are Offline. Bye.".encode(), address)

    def handle_reg(self, username, address):
        logging.info("Regging received for "+username+"|")
        for i in range(len(self.client_table)):
            v = self.client_table[i]
            if(v[0] == username):
                v[4] = "ONLINE"
                logging.info("User found and registered it")
                self.client_table_broadcast()
                # sleep(5.0)
                delayed_messages=self.get_file_messages(username)
                self.server_socket.sendto(delayed_messages.encode(),address)
                logging.info("offline message sent back that are "+delayed_messages)
                # self.server_socket.sendto(
                #     "You are online. Welcome again.".encode(), address)

    def check_already_exist(self, username):
        for i in range(len(self.client_table)):
            v = self.client_table[i]
            if(v[0] == username):
                return True

        return False

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
                self.handle_dereg(to_do[1], address)
                continue
            elif to_do[0] == "reg":
                self.handle_reg(to_do[1], address)
                continue
            elif to_do[0] == "savem":
                logging.info("Offline message received " +
                             message.decode("utf-8"))
                if(self.check_offline_status(to_do[1])):
                    self.server_socket.sendto(
                        "Message received by the server and saved".encode(), address)
                    mesage_body_after_header=message.decode("utf-8")[len(to_do[1])+len("savem")+2:]
                    logging.info("Message body is "+mesage_body_after_header)

                    self.handle_offline_message(
                        to_do[1], mesage_body_after_header)
                else:
                    exist_message= "Client "+to_do[1]+" exists!!"
                    self.server_socket.sendto(
                       exist_message.encode(), address)
                    self.client_table_broadcast()
                continue

            # client information received from client
            client_data = message.decode("utf-8").split(" ")
            client_data.append("ONLINE")

            # Check if the user do not already exists
            if(not self.check_already_exist(client_data[0])):
                self.server_socket.sendto("Welcome, You are registered.".encode(),
                                          address)
                # appending to the client table
                self.client_table.append(client_data)
                logging.info("Client Port is " + client_data[1])
                logging.info(client_data)
                self.client_table_broadcast()
            else:
                self.server_socket.sendto("Sorry user is already registered.".encode(),
                                          address)

    def handle_offline_message(self, filename, message):
        logging.info("Apending started")
        with open(filename, "a") as myfile:
            myfile.write(str(datetime.datetime.now())+"  "+message+"\n")
        logging.info("File appended")

    def get_file_messages(self,username):
        if(os.path.exists(username)):
            logging.info(username+" exists")
            file=open(username,"r")
            lines=file.readlines()
            content=""
            for V in lines:
                content=content+V+"\n"
            os.remove(username)
            return content
        else:
            logging.info(username+" do not exists")
        

    def check_offline_status(self, username):
        logging.info("Checking status for "+username)
        for v in self.client_table:
            if(v[0] == username):
                if(v[4] == "OFFLINE"):
                    return True
        return False

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
        logging.info("Sending table")
        send = "table "
        for v in self.client_table:
            send = send + v[0] + " " + v[1] + " " + \
                v[2] + " " + v[3] + " " + v[4] + "\n"
        return send


class Client(object):
    """docstring for Client."""

    def __init__(self, nickname, server_ip, server_port, client_port):
        super(Client, self).__init__()
        self.nick_name = nickname.lower()
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_port = client_port
        self.client_table = []

    def start(self):
        self.broadcast_thread = threading.Thread(
            group=None,
            target=self.client_table_broadcast_message_service,
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
            line = "{:^10} {:^20} {:^10} {:^10}".format(v[0], v[2], v[1], v[4])
            cprint(str(line), "red")

    def client_actions(self):
        while(1):
            cprint(
                "Multiple options available\n>>>> send <name> <message>\n>>>> list\n>>>> dereg <nick-name> \n>>>>>deregA <any one>\n", "red")
            command = input()
            choice = command.split(" ")[0]
            logging.info("Choice is ")
            logging.info(choice)
            if(choice == "send"):
                logging.info("Sending to the client")
                self.handle_message_sending(command)
            elif(choice == "list"):
                logging.info("Listing table")
                self.print_client_table()
            elif choice == "dereg":
                self.perform_dereg(command)
            elif choice == "deregA":
                self.perform_deregon_all(command)
            elif choice == "reg":
                self.perform_reg(command)

    def perform_reg(self, command):
        logging.info("Regging inititate")
        reg_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        reg_client_socket.sendto(command.lower().encode(), self.addr)
        data, server = reg_client_socket.recvfrom(1024)
        cprint(data.decode("utf-8"), "green")
        logging.info("reg again")

    def handle_message_sending(self, command):
        logging.info("Sending message "+command[4:])
        send_name = command.split(" ")[1].lower()
        logging.info("Username is ")
        logging.info(send_name)
        message = "msage "+self.nick_name+": "+command[len(send_name)+6:]
        logging.info("Sending message |"+message+"|")
        for i in range(len(self.client_table)):
            v = self.client_table[i]
            if(v[0] == send_name):
                if(v[4] == "ONLINE"):
                    logging.info("User found and it's port: "+v[1])
                    addr = ("127.0.0.1", int(v[1]))
                    message_client_socket = socket.socket(
                        socket.AF_INET, socket.SOCK_DGRAM)
                    message_client_socket.settimeout(0.5)
                    message_client_socket.sendto(message.encode(), addr)
                    try:
                        ack, user = message_client_socket.recvfrom(1024)
                        cprint(ack.decode("utf-8"), "green")
                        logging.info("Message received")
                    except socket.timeout:
                        cprint("[No ACK from "+send_name +
                               ", message sent to server]", "green")
                        logging.info("Message not received")
                else:
                    logging.info("Offline message request to be sent!")
                    send = "savem "+send_name+" "+self.nick_name +": "+command[len(send_name)+6:]
                    self.save_message_request(send)

                    

    def save_message_request(self, message):
        logging.info("Deregging inititate")
        save_message_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        save_message_socket.settimeout(0.5)
        save_message_socket.sendto(message.encode(), self.addr)
        try:
            ack, server = save_message_socket.recvfrom(1024)
            cprint(ack.decode("utf-8"), "green")
        except socket.timeout:
            logging.info("ACK not received on saving offline message")

    def perform_deregon_all(self, command):
        username = command.lower().split(" ")[1]
        logging.info("User is ")
        logging.info(username)
        logging.info("Deregging inititate")
        dereg_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dereg_client_socket.settimeout(0.5)
        dereg_client_socket.sendto(command.lower().encode(), self.addr)
        retry = 0
        while(retry < 5):
            try:
                data, server = dereg_client_socket.recvfrom(1024)
                cprint(data.decode("utf-8"), "green")
                return None
            except socket.timeout:
                logging.info(str(retry)+": ACK not received on registration")
                retry = retry+1
            cprint("[Server not responding]\n[Exiting]", "red")
            os._exit(1)

    def perform_dereg(self, command):
        username = command.lower().split(" ")[1]
        logging.info("User is ")
        logging.info(username)
        if(username == self.nick_name):
            logging.info("Deregging inititate")
            dereg_client_socket = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
            dereg_client_socket.settimeout(0.5)
            dereg_client_socket.sendto(command.lower().encode(), self.addr)
            retry = 0
            while(retry < 5):
                try:
                    data, server = dereg_client_socket.recvfrom(1024)
                    cprint(data.decode("utf-8"), "green")
                    return None
                except socket.timeout:
                    logging.info(
                        str(retry)+": ACK not received on registration")
                    retry = retry+1
            cprint("[Server not responding]\n[Exiting]", "red")
            os._exit(1)
        else:
            cprint("You can not de-register someone else.\n", "red")

    def client_table_broadcast_message_service(self):
        """This method starts another socket on which it receives the update client table. Also it handles the messages
        """

        logging.info(
            "Client table service and message started at " + self.client_port)
        self.broadcast_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
        self.broadcast_socket.bind(('', int(self.client_port)))
        while True:
            message, address = self.broadcast_socket.recvfrom(1024)
            ack = "[Message received by "+self.nick_name+"]"
            self.broadcast_socket.sendto(ack.encode(), address)
            message_str = message.decode("utf-8")

            header = message_str[:6]
            logging.info("Header tag: "+header+"|")
            if(header == "table "):
                print("[Client table received]\n")
                logging.info(
                    "Client table service received at " + self.client_port)
                self.update_client_table(message_str[6:])
            elif(header == "msage "):
                # sender_name = message_str.split(" ")[1]
                # logging.info("Sender is ")
                # logging.info(sender_name)
                # message_rsv = message_str[6+len(sender_name):]
                logging.info(
                    "Message received after the header is "+message_str[6:])
                cprint(message_str[6:], "green")
            elif(header == "headr "):
                logging.info("Offline message received")
                detail = message_str[6:]
                logging.info(detail)

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
        data_str = data.decode("utf-8")
        if(data_str == "Sorry user is already registered."):
            cprint(data_str, "red")
            os._exit(1)
        logging.info("[First message received]")


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
