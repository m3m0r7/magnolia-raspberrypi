import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
from socket import *
from struct import *
import argparse
import sys
import time
from dotenv import load_dotenv
import os
from os.path import join, dirname

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:

    # Set logging format
    formatter = '[%(levelname)s][%(asctime)s] %(message)s'
    logging.basicConfig(
        level=logging.WARNING,
        format=formatter
    )

    load_dotenv(join(dirname(__file__), '../.env'))

    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')

    while True:
        logging.info("Starting camera.")
        try:
            address = (
                os.environ.get("CAMERA_RECEIVE_SERVER_HOST"),
                int(os.environ.get("CAMERA_RECEIVE_SERVER_PORT"))
            )
            server = socket(
                AF_INET,
                SOCK_STREAM
            )
            server.connect(address)
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    server.sendall(
                        os.environ.get("AUTH_KEY") + pack("L", len(frame)) + frame
                    )
            except Exception as e:
                logging.warning(
                    'Disconnect client %s: %s',
                    address,
                    str(e)
                )
        finally:
            camera.stop_recording()
            logging.warning("Continue to start. Please wait 10 sec.")
            time.sleep(10)
