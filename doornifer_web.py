from flask import Flask, render_template_string, request
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

CLIP_DIR = "/home/chadrick/clips"
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



def play_clip(clip):
    t = Thread(target=system, args=(f'aplay {clip}',))
    t.start()
    t.join()


def door_opened():
    global clips, doorOpen, lastOpened
    doorOpen = not doorOpen

    if ((doorOpen or not USE_DOOR_TOGGLE) and
        (now() - lastOpened > WAIT_DELAY_SEC) and
        (not ENABLE_TIME_RANGE or (localtime().tm_hour >= ACTIVE_TIME_RANGE[0] and localtime().tm_hour < ACTIVE_TIME_RANGE[1])) and
        enabled
        ):
        lastOpened = now()
        clip = choice(clips)
        play_clip(join(CLIP_DIR, clip))

    if not enabled:
        print('Not playing, muted')



def setVolume(percentage):
    system(f'amixer sset Headphone {percentage}% -M')


# Global variable to hold log messages
log = "System initialized."


def get_system_volume():
    # Example command to get system volume (this might need adjustment depending on the OS)
    result = subprocess.run(["amixer", "get", "Master"], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if "Playback" in line and "%" in line:
            return int(line.split("[")[1].split("%")[0])
    return 0

def set_system_volume(change):
    # Example command to change system volume (this might need adjustment depending on the OS)
    subprocess.run(["amixer", "set", "Master", f"{change}%+"], capture_output=False)
    global log
    log += f"\nSystem volume changed by {change}%"
    print(f"System volume changed by {change}%")

# HTML Template for the webpage
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Flask Button Page</title>
  </head>
  <body>
    <h1>Flask Button Webpage</h1>
    <div>
      <button onclick="window.location.href='/play_sound'">Call Function One</button>
      The door is currently {{ "open" if doorOpen else "closed" }}
      <button onclick="window.location.href='/set_door_closed'">Set door as closed</button>
      <button onclick="window.location.href='/set_door_open'">Set door as open</button>

    </div>
    <h2>Files in Directory</h2>
    <ul>
      {% for file in files %}
        <li><a href="/handle_file/{{ file }}">{{ file }}</a></li>
      {% endfor %}
    </ul>
    <h2>System Volume</h2>
    <div>
      <p>Current Volume: {{ volume }}%</p>
      <button onclick="window.location.href='/volume_up'">+</button>
      <button onclick="window.location.href='/volume_down'">-</button>
    </div>
    <h2>Log</h2>
    <pre>{{ log }}</pre>
  </body>
</html>
"""

@app.route('/')
def index():
    # List files in the specified directory
    files = os.listdir(CLIP_DIR) if os.path.exists(CLIP_DIR) else []
    volume = get_system_volume()
    return render_template_string(HTML_TEMPLATE, files=files, volume=volume, log=log)

@app.route('/play_sound')
def play_sound():
    global log
    log += "\nFunction One Called"
    print("Function One Called")
    return "Function One was called! <a href='/'>Go Back</a>"

@app.route('/set_door_open')
def set_door_open():
    global log
    log += "\nFunction Two Called"
    print("Function Two Called")
    return "Function Two was called! <a href='/'>Go Back</a>"

@app.route('/set_door_closed')
def set_door_closed():
    global log
    log += "\nFunction Two Called"
    print("Function Two Called")
    return "Function Two was called! <a href='/'>Go Back</a>"

@app.route('/handle_file/<path:filename>')
def handle_file(filename):
    file_path = os.path.join(CLIP_DIR, filename)
    global log
    log += f"\nFile clicked: {file_path}"
    print(f"File clicked: {file_path}")
    return f"File '{filename}' was clicked! <a href='/'>Go Back</a>"

@app.route('/volume_up')
def volume_up():
    set_system_volume(5)
    return "Volume increased by 5%! <a href='/'>Go Back</a>"

@app.route('/volume_down')
def volume_down():
    set_system_volume(-5)
    return "Volume decreased by 5%! <a href='/'>Go Back</a>"

if __name__ == "__main__":
    sensor = DigitalInputDevice(HALL_SENSOR_PIN, PULL_UP)
    sensor.when_activated = door_opened

    # First set the starting volume
    setVolume(volume)

    # Run the app on the local network, accessible to other devices on the same network
    app.run(host=HOST, port=PORT, debug=True)
