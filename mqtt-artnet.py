#!/usr/bin/env python3

import time
import random
import sys

from sendartnet import sendArtNet

import paho.mqtt.client as mqtt

# MQTT-Config
MQTT_TOPIC = "artnet" # The Topic on the MQTT Broker to subscribe to
MQTT_HOST = "infra.rzl"
MQTT_PORT = 1883

# ARTNET-Config
IP = "172.22.36.117" # Target-IP of ArtNetNode
SPEED = 0.01   # default Speed on how fast to ramp things up and down
LUM = 40       # default brightness

# starting addresses of connected lights
STROBES = [1]
PARS = [10, 20]

artnet = sendArtNet()

################################################################################
# Methods manipulating DMX-Channels

def initstate():
    """set initial state of dmx-array. Set all channels to zero and set default
    brightness."""
    STATE = list()
    for i in range(1, 513):
        STATE.append((i, 0))
    # set initial brightnes for PARS
    for addr in PARS:
        STATE[addr-1] = (addr, LUM)


def fadeup(addr, target=255, speed=SPEED):
    """fade up one address to the target value"""
    if STATE[addr-1][1] < target:
        STATE[addr-1] = (addr, STATE[addr-1][1]+1)
        artnet.send(IP, STATE)
        time.sleep(speed)
        fadeup(addr, target, speed)
    else:
        return 


def fadedown(addr, target=0, speed=SPEED):
    """fade down one address to the target-value"""
    if STATE[addr-1][1] > target:
        STATE[addr-1] = (addr, STATE[addr-1][1]-1)
        artnet.send(IP, STATE)
        time.sleep(speed)
        fadedown(addr, target, speed)
    else:
        return


def random_rgb():
    """radomly choose a channel and ramp it up or down"""
    chans = list() # list of channels to choose from
    for par in PARS:
        chans.append(par + 1) # red
        chans.append(par + 2) # green
        chans.append(par + 3) # blue

    chan = random.choice(chans)
    val = random.randrange(0, 255)

    if val > STATE[chan-1][1]:
        fadeup(chan, val)
    else:
        fadedown(chan, val)


def blackout():
    """blackout all channels instantly."""
    initstate()


def fadeout(speed=SPEED):
    """fade out all channels."""
    flag = False
    for par in PARS:
        for i in range(0, 2): # Check all three channels (rgb)
            if STATE[par + i - 1][1] > 0:
                STATE[par + i -1] = (par, STATE[par + i - 1][1]-1)
                flag = True

    if flag == True: # at least one value has been changed
        artnet.send(IP, STATE)
        time.sleep(speed)
        fadeout()
    else:
        return

###############################################################################
# mqtt-interface

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    if msg.payload == b'random':
        random_rgb()

    elif msg.payload == b'red':
        fadeout()
        for par in PARS:
            fadeup(par+1)
            time.sleep(0.1)

    elif msg.payload == b'green':
        fadeout()
        for par in PARS:
            fadeup(par+2)
            time.sleep(0.1)

    elif msg.payload == b'blue':
        fadeout()
        for par in PARS:
            fadeup(par+3)
            time.sleep(0.1)

    elif msg.payload == b'yellow':
        fadeout()
        for par in PARS:
            fadeup(par+1)
            time.sleep(0.1)
            fadeup(par+2)
            time.sleep(0.1)

    elif msg.payload == b'purple':
        fadeout()
        for par in PARS:
            fadeup(par+1)
            time.sleep(0.1)
            fadeup(par+3)
            time.sleep(0.1)

    elif msg.payload == b'blackout':
        blackout()

    elif msg.payload == b'fadeout':
        fadeout()

    else:
        print("Payload is not recognized.")


if __name__ == "__main__":
    initstate()

    mqttclient = mqtt.Client()
    mqttclient.on_connect = on_connect
    mqttclient.on_message = on_message
    mqttclient.connect(MQTT_HOST, MQTT_PORT, 60)
    mqttclient.loop_forever()

