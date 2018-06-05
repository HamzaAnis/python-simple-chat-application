import logging
from logging.config import fileConfig
import Server
from os import path
import os
import sys


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
        elif (mode == "-s"):
            logging.info("Server Called")


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
