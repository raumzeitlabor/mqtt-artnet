#!/usr/bin/env python3

import socket
import struct

class sendArtNet:
    """Sends DMX Values encoded as Artnet-Package through UDP-Socket."""

    PORT = 6454  # 0x1936

    def __init__(self):
        self.sock = None

    def __make_message(self, data, port):
        # ID "Art-Net" + null termination
        signature = struct.pack("!cccccccx", b"A", b"r", b"t", b"-", b"N", b"e", b"t")
        opcode = struct.pack("<H", 0x5000)  # low byte first
        protocol = struct.pack("!H", 14)  # high byte first
        head = signature + opcode + protocol
    
        sequence = struct.pack("!x")  # 0x00 to disable
        pyhsical = struct.pack("!x")  # for information only
    
        if port is None:
            #                          aaaabbbbcccccccd
            port = struct.pack("!H", 0b0000000000000000)
    
        length = struct.pack("!H", len(data))
    
        return head + sequence + pyhsical + port + length + data
    
    def __encode_channels(self, *args):
        channels = [0] * 512
        for index, value in args:
            channels[index-1] = value # index-1 so dmx channels start with 1
        fmt = "!" + "B" * len(channels)
        return struct.pack(fmt, *channels)
    
    def __send_package(self, ip, msg):
        return self.sock.sendto(msg, (ip, self.PORT))
    
    
    def send(self, ip, channels, port=None):
        """Builds an ArtNet Package and sends it out. Checks if UDP Socket is
        already present.

        Parameters:
        - IPv4 to send Packet to.
        - Channels as tuple ((CHANNEL, VALUE), (CHANNEL, VALUE)...)
        - ArtNet Target-Port:
            15 bit port address:
            - a universe 0-3 (16 universes in 1 subnet, 256 universes in 1 net)
            - b subnet 4-7 (16 subnets in 1 net)
            - c net 8-14 (128 nets)
            - d 0 15
            --> total of 16*16*128 = 32768 universes/port addresses
                eg. 0b0000000000000000
                      aaaabbbbcccccccd
        """

        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        chandata = self.__encode_channels(*channels)
        msg = self.__make_message(chandata, port)
        bytecount = self.__send_package(ip, msg)
    
        #print(f"{bytecount} bytes sent to {ip}")
        #for x, y in channels:
        #    print(f"channel {x}: {y}")


if __name__ == "__main__":
    # Call: scriptname.py [IP] [CHANNEL] [VALUE]
    import sys
    artnet = sendArtNet()
    artnet.send(
        sys.argv[1], 
        ((int(sys.argv[2]), int(sys.argv[3])),)
    )

