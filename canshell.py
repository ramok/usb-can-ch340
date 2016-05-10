#!/usr/bin/python3
# -*- coding: utf-8 -*-

import usb_can_ch340 as can
import threading
import time
import sys
import select
import re

class candriver(threading.Thread):
    
    USBCAN = None
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.USBCAN = can.USBCAN (500000, "standard", "normal", timeout=0.005)
        self.USBCAN.flush()
        
    def run(self):
        self.starttime=time.time()
        while 1:
            
            inputready = select.select([sys.stdin, self.USBCAN.canport], [], [])[0]

            for s in inputready:
                if s == sys.stdin:
                    line = sys.stdin.readline()
                    if line == "\n":
                        continue

                    line = line.strip("\n")

                    try:
                        if "send " in line and "#" in line:
                            self.cansend(line.split("send ")[-1])
                        elif "#" in line:
                            self.cansend(line)
                        elif line == "s":
                            self.USBCAN.bus_status()
                            print ("Bus Status: {}".format(self.USBCAN.Buserrors))
                        elif not line:
                            return
                        else:
                            print ("wrong input line")
                    except:
                        print ("Error: ", sys.exc_info()[0])

                if s == self.USBCAN.canport:
                    self.USBCAN.rec()
                    while len(self.USBCAN.Message) > 0:
                        acttime = time.time()
                        message = self.USBCAN.Message.pop(0)
                        print( " (" + "{:.6f}".format(acttime) +
                            ") can0  RX - -  " + message["ID"][-3:] +
                            "   ["+ str(message["length"]) + "]  " +
                            ' '.join('{:02x}'.format(x) for x in message["data"]) )
            
            
    def cansend(self, adddata):
        addr = adddata.split( "#" ) [0]
        data = adddata.split( "#" ) [1]
        
        while len(addr) < 8:
            addr = "0" + addr
        
        data = re.sub('\.', '', data)
        
        self.USBCAN.send(addr, data)
        acttime = time.time()
                   
        data = re.findall('.{2}', data)
        
        print( " (" + "{:.6f}".format(acttime) +
        ") can0  TX - -  " + addr[-3:] +
        "   ["+ str(len(data)) + "]  " +
        " ".join(data))
        
    def close(self):
        self.USBCAN.close()
    
    def __del__(self):
        self.close()

if __name__ == "__main__":
    
    canthread=candriver()
    #canthread.cansend( "000#8100" )
    canthread.start()
    
    # USBCAN=can.USBCAN(500000,"Standard","normal")
    # try:
    #     #USBCAN.set_IDfilter(["00000584","00000604"])
    #     USBCAN.send("11111111","123456")
    #     #time.sleep(2)
    #     print(USBCAN.rec(10))
    #     print(USBCAN.Message)
    #     USBCAN.flush()
    #     print(USBCAN.Message)
    # finally:
    #     USBCAN.close()
