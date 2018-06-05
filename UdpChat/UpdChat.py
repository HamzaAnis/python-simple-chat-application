import logging
from logging.config import fileConfig
import Server
from os import path
import os

class UdpChat(object):
    """docstring for UdpChat."""
    def __init__(self, mode,port,nick_name,server_pi,server_port,client_port):
        super(UdpChat, self).__init__()
        self.mode=mode
        if(mode=="-c"):
            logging.info("Client Called")
        elif (mode=="-s"):
            logging.info("Server Called") 
if __name__ == "__main__":
    fileConfig('log.conf')
    logger = logging.getLogger()
    U=UdpChat("-c",None,None,None,None,None)