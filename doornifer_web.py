from flask import Flask, render_template_string, request, redirect
import os
from gpiozero import DigitalInputDevice, MotionSensor
from signal import pause
from time import sleep, localtime
import subprocess
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
from threading import Thread


VERBOSE = True
ENABLE_SERVER = False
USE_MOTION_SENSOR = False
USE_DOOR_TOGGLE = True
PULL_UP = True

CLIP_DIR = "/home/pi/clips"
HOST, PORT = '0.0.0.0', 8080
MINIMUM_AUDIO_CLIP_SIZE = 100
WAIT_DELAY_SEC = 1
SLEEP_TIME = 0.005
MOTION_SENSOR_PIN = 17
HALL_SENSOR_PIN = 21
ENABLE_TIME_RANGE = False
ACTIVE_TIME_RANGE = [7, 25]
MOTION_SENSOR_THRESHOLD = .5
VOLUME_INCREMENTS = 10

volume = 60
clips = listdir(CLIP_DIR)
doorOpen = False
lastOpened = now()
enabled = True

app = Flask(__name__)

with open('doornifer_web.html') as f:
    HTML_TEMPLATE = f.read()

_log = "System initialized"

def log(msg):
    global _log
    _log += '\n'
    _log += msg
    print(msg)


def play_clip(clip=None):
    if not clip:
        clip = join(CLIP_DIR, choice(clips))
    log(f'Playing clip {clip.split("/")[-1]}')
    # system(f'aplay {clip}')
    subprocess.run(['aplay', clip], capture_output=False)
    # t = Thread(target=system, args=(f'aplay {clip}',))
    # t.start()
    # t.join()

def door_opened():
    global doorOpen, lastOpened
    doorOpen = not doorOpen
    log(f"Sensor tripped! Door is now {'open' if doorOpen else 'closed'}")

    if ((doorOpen or not USE_DOOR_TOGGLE) and
        (now() - lastOpened > WAIT_DELAY_SEC) and
        (not ENABLE_TIME_RANGE or (localtime().tm_hour >= ACTIVE_TIME_RANGE[0] and localtime().tm_hour < ACTIVE_TIME_RANGE[1])) and
        enabled
        ):
        lastOpened = now()
        play_clip()

    if not enabled:
        print('Not playing, muted')

def get_system_volume():
    result = subprocess.run(["amixer", "get", "Master"], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if "Playback" in line and "%" in line:
            return int(line.split("[")[1].split("%")[0])
    return 0

def set_system_volume(change):
    subprocess.run(["amixer", "set", "Master", f"{change}%+"], capture_output=False)
    # system(f'amixer sset Headphone {percentage}% -M')
    log(f"System volume changed by {change}%")


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, files=clips, volume=get_system_volume(), log=log)

@app.route('/play_sound')
def play_sound():
    play_clip()
    return redirect('/')

@app.route('/set_door_open')
def set_door_open():
    global doorOpen
    doorOpen = True
    log('Door manually set to open')
    return redirect('/')

@app.route('/set_door_closed')
def set_door_closed():
    global doorOpen
    doorOpen = False
    log('Door manually set to closed')
    return redirect('/')

@app.route('/handle_file/<path:filename>')
def handle_file(filename):
    play_clip(join(CLIP_DIR, filename))
    return redirect('/')

@app.route('/volume_up')
def volume_up():
    set_system_volume(5)
    return redirect('/')

@app.route('/volume_down')
def volume_down():
    set_system_volume(-5)
    return redirect('/')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part! <a href='/'>Go Back</a>"
    file = request.files['file']
    if file.filename == '':
        return "No selected file! <a href='/'>Go Back</a>"
    if file:
        file.save(os.path.join(CLIP_DIR, 'uploaded_' + file.filename))
        log(f"File uploaded: {file.filename}")
        return f"File '{file.filename}' uploaded successfully! <a href='/'>Go Back</a>"

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return "No audio file part! <a href='/'>Go Back</a>"
    audio = request.files['audio']
    if audio.filename == '':
        return "No selected audio file! <a href='/'>Go Back</a>"
    if audio:
        audio.save(os.path.join(CLIP_DIR, 'recorded_' + audio.filename))
        log(f"\nAudio file uploaded: {audio.filename}")
        return f"Audio file '{audio.filename}' uploaded successfully! <a href='/'>Go Back</a>"


if __name__ == "__main__":
    sensor = DigitalInputDevice(HALL_SENSOR_PIN, PULL_UP)
    sensor.when_activated = door_opened

    # First set the starting volume
    set_system_volume(volume)

    # Run the app on the local network, accessible to other devices on the same network
    app.run(host=HOST, port=PORT, debug=True)
