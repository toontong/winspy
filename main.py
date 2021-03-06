#coding:utf-8
#Author: ChuanTong.Huang@Gmail.com 
#Dete: 2016-06-06

import os
import time
import socket
import logging
import traceback
import SocketServer
from optparse import OptionParser

import LedPlayer
import spycmd as CMD
import version
__version__ = version.VERSION 
UDP_PORT = 9999; 
CHECK_TIMEOUT = 15 

def dispath_cmd(ledPlayWindows, cmd):
    if cmd.startswith(CMD.CMD_MODE_PREFIX):
        _, index = cmd.split(CMD.CMD_MODE_PREFIX)
        ledPlayWindows.click_mode(int(index))
    else:
        func = getattr(ledPlayWindows, "click_" + cmd)
        func()
    logging.debug("\tcmd-->", cmd ," success.")

class MyUDPHandler(SocketServer.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        logging.info("Recv from {%s} data{%s}:", self.client_address[0], data)
        cmd_list = [c for c in data.split(CMD.CMD_SPLIT) if c]
        
        for cmd in cmd_list:
            cmd = cmd.strip()
            if not cmd:continue #empty string

            if cmd not in CMD.ALL_CMD:
                socket.sendto("CMD[%s] not support.\n" % cmd,
                    self.client_address)
                continue
            try:
                mainWindow = LedPlayer.iter_windows()
                if not mainWindow:
                    socket.sendto("LedPlayer not running.\n",
                    self.client_address)
                    break
            
                dispath_cmd(mainWindow, cmd)
            except Exception,e:
                socket.sendto(str(e), self.client_address)
                continue
            socket.sendto('ok', self.client_address)

        logging.info('End handle of packet: %s', cmd_list)
def init_logging(name, level=logging.ERROR):
    def _addHandler(level, hdlr, logger):
        '''防止重复加handler'''
        for h in logger.handlers:
            if h.__class__ == hdlr.__class__:
                return
        logger.addHandler(hdlr)
        logger.setLevel(level)
    logger = logging.getLogger(name)
    console = logging.StreamHandler()

    console.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s -[%(lineno)4d] - %(message)s')
    console.setFormatter(formatter)
    _addHandler(level, console, logger)

def main():
    parser = OptionParser()  
    parser.add_option("-p", "--port", dest="port", help="listen PORT", metavar="int",default=UDP_PORT)  
    #parser.add_option("-t", "--tcp", action="store_true", help ="using TCP,default ws upd", default=False)
    parser.add_option("-l", "--host", action="store_true", help ="listen host IP,default[0.0.0.0]", default="0.0.0.0")
    (options, args) = parser.parse_args()  

    init_logging("", logging.INFO)
    logging.info("Version: %s", __version__)

    host, port = options.host, options.port
    try:
        mainWindow = LedPlayer.iter_windows()
        if not  mainWindow:
            print "LedPlayer not running. PLS run [LedPlayer].\n"
            return -1

        logging.info("Process will listen at UDP[%s:%s]" , host, port)
        server = SocketServer.UDPServer((host, port), MyUDPHandler)
        server.serve_forever()   
    except socket.error, e:
        if e.errno == 10048:
            print u'端口被占用。请使用另一端口，或把占用程序 kiil 掉。'.encode('gbk')
            return 4
        else:
            traceback.print_exc()
            return 1
    except KeyboardInterrupt:
        return 0
    except Exception, e:
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    rt = main()
    if rt == 0:
        print 'process exit success.'
    else:
        print "process exit in exception."
 

 