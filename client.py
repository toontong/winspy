#coding:utf-8
#Author: ChuanTong.Huang@Gmail.com 
#Dete: 2016-06-06

from optparse import OptionParser

import random
import socket
import sys
import time
import spycmd as CMD
random.seed(time.time())

def main():  
    parser = OptionParser()  
    parser.add_option("-p", "--port", dest="port", help="listen PORT", metavar="int",default=9999)  
    parser.add_option("-c", "--cmd", dest="cmd",action="store_true", help ="sending cmd", default="play;")
    parser.add_option("-l", "--host", action="store_true", help ="listen host IP,default[127.0.0.1]", default="127.0.0.1")
    (options, args) = parser.parse_args()  
    
    print options
    host, port,cmd = options.host, options.port, options.cmd


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for i in range(10):
        cmd=""
        n = 3
        while n:
            r = random.randint(0, len(CMD.ALL_CMD)-1)
            cmd += CMD.ALL_CMD[r] + ';'
            n-=1
        
        # cmd ="play;stop;play_as_screenshots;mode_13;"
        sock.sendto(cmd, (host, port))
        # return
        print "Send to [%s:%s] CMD=[%s]" % (host, port, cmd)
        received = sock.recv(1024)
        print "Received: {}".format(received)
        time.sleep(2)
        # return

if __name__ == '__main__':
    main()