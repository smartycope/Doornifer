# This Python file uses the following encoding: utf-8
import os
import sys
import json
from os.path import dirname, join

from PyQt5.QtWidgets import QApplication, QWidget
# from PyQt5.QtCore import QFile
from PyQt5 import uic

import socket


class Main(QWidget):
    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi(join(dirname(__file__), "form.ui"), self)

        self.setLayout(self.mainLayout)

        self.client = None

        # self.portBox.textEdited.connect(self.reconnect)
        self.portBox.returnPressed.connect(self.reconnect)
        # self.addressBox.textEdited.connect(self.reconnect)
        self.addressBox.returnPressed.connect(self.reconnect)

        self.updateButton.pressed.connect(self.request)
        self.closeDoorButton.pressed.connect(
            lambda: self.request('door closed'))
        self.openDoorButton.pressed.connect(lambda: self.request('door open'))
        self.toggleDoorButton.pressed.connect(
            lambda: self.request('toggle door'))
        self.playClipButton.pressed.connect(lambda: self.request('play clip'))

    def reconnect(self):
        if self.client is not None:
            self.client.close()
        print(
            f'Establishing connection to {self.addressBox.text()}:{int(self.portBox.text())}')
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.addressBox.text(), int(self.portBox.text())))

    def request(self, command='update'):
        if self.client is None:
            self.reconnect()

        if command == 'play clip':
            self.client.sendall(clipsBox.currentText().encode())
        else:
            self.client.sendall(command.encode())
        # Read data from the TCP server and close the connection
        received = self.client.recv(1024)

        print("Bytes Sent:     {}".format(command))
        print("Bytes Received: {}".format(received.decode()))

        if command == 'update':
            try:
                data = json.loads(received.decode())
            except json.decoder.JSONDecodeError:
                print("Invalid json returned from server:")
                print(received.decode())
                return

            if data['doorOpen']:
                self.doorLabel.setText('Open')
            else:
                self.doorLabel.setText('Closed')

            # Fill the combo box of clips
            self.clipsBox.clear()
            self.clipsBox.addItems(data['clips'])


if __name__ == "__main__":
    app = QApplication([])
    widget = Main()
    widget.show()
    try:
        sys.exit(app.exec_())
    finally:
        widget.client.close()
