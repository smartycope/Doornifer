from gpiozero import DigitalInputDevice, MotionSensor
from signal import pause
from time import sleep
from os import listdir, system
from os.path import join
from random import choice
from time import time as now
# from playsound import playsound
# from pydub import AudioSegment
# from pydub.playback import play
# from Tkinter import * b
# import tkSnack
import socket
import socketserver
import json
import re

ENABLE_SERVER = True
USE_MOTION_SENSOR = True
USE_DOOR_TOGGLE = False

CLIP_DIR = "/home/chadrick/clips"
HOST, PORT = "192.168.200.200", 9999
MINIMUM_AUDIO_CLIP_SIZE = 100
WAIT_DELAY_SEC = 30
PIN = 17

clips = listdir(CLIP_DIR)
doorOpen = False
lastOpened = now()


def playClip(clip):
    system(f'aplay {clip}')
    # play(AudioSegment.from_wav(clip))
    # snd.read('sound.wav')
    # snd.play(blocking=0)
    # playsound(clip)


def doorOpened():
    global clips, doorOpen
    print('playClip called')
    doorOpen = not doorOpen

    if (doorOpen or not USE_DOOR_TOGGLE) and now() - lastOpened > WAIT_DELAY_SEC:
        lastOpened = now()
        clip = choice(clips)
        # print(f'Playing {clip}')
        playClip(join(CLIP_DIR, clip))


if USE_MOTION_SENSOR:
    sensor = MotionSensor(PIN)
    sensor.when_motion = doorOpened
else:
    sensor = DigitalInputDevice(PIN, False)
    sensor.when_activated = doorOpened


class Server(socketserver.BaseRequestHandler):
    # Handler to manage incoming requests
    def handle(self):
        global doorOpen
        # self.request - TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        # self.data - is the incoming message
        print(f"{self.client_address[0]} sent:")
        print(self.data)

        command = self.data.decode().lower()

        # Return our current status in the form of json
        if command == 'update':
            self.request.sendall(json.dumps({
                'doorOpen': doorOpen,
                'clips': clips
            }).encode())
        elif command == 'toggle door':
            doorOpen = not doorOpen
        elif command == 'door closed':
            doorOpen = False
        elif command == 'door open':
            doorOpen = True
        # Told to play one of the clips
        elif command in clips:
            playClip(join(CLIP_DIR, command))
        elif len(command) > MINIMUM_AUDIO_CLIP_SIZE + 10 and command.startswith('clip'):
            name = re.match('clip (.+wav) ', self.data)
            if name is None:
                print("invalid sound data:")
                print(self.data)
            else:
                name = name.groups()[0]


if ENABLE_SERVER:
    # Init the TCP server object, bind it to the localhost on 9999 port
    tcp_server = socketserver.TCPServer((HOST, PORT), Server)
    print(f"Socket Server Started on : {HOST}, port: {PORT}")

if ENABLE_SERVER:
    tcp_server.serve_forever()
else:
    # pause()
    while True:
        sleep(.01)
