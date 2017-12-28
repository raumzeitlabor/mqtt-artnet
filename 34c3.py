#!/usr/bin/env python3

import time
from sendartnet import sendArtNet

ip = "192.168.1.131"
sleep = 0.05
s = sendArtNet()

while True:
    for i in range(0, 255, 1):
        s.send(ip, ((1, i), ))
        time.sleep(sleep)
    
    for i in range(0, 255, 1):
        s.send(ip, ((1, 255-i), ))
        time.sleep(sleep)
        
