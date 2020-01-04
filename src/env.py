import argparse
import sys
import time
import logging
import os
from socket import *
from struct import *
from sense_hat import SenseHat
from dotenv import load_dotenv
import os
from os.path import join, dirname
import requests

def sendPacket(server, kindTag, value):
    # Kind Tag
    server.sendall(pack("B", kindTag))

    # Data
    splitValue = str(round(value, 2)).split(".")

    if len(splitValue) == 1:
        splitValue.append("0")

    server.sendall(
        pack("ll", int(splitValue[0]), int(splitValue[1]))
    )

# Set logging format
formatter = '[%(levelname)s][%(asctime)s] %(message)s'
logging.basicConfig(
    level=logging.WARNING,
    format=formatter
)

# Connection Parameters
load_dotenv(join(dirname(__file__), '../.env'))

while True:
    logging.info("Starting env.")
    try:
        sense = SenseHat()
        while True:
            logging.debug("Processing")

            # Get environment from Sensor Hat

            logging.debug("Getting sensor hat environments")
            humidity = sense.get_humidity()
            pressure = sense.get_pressure()
            temp = sense.get_temperature_from_pressure()

            # Get CPU temperature
            logging.debug("Getting measure temp")
            process = os.popen('/opt/vc/bin/vcgencmd measure_temp')
            cputemp = process.read()
            cputemp = cputemp.replace('temp=', '')
            cputemp = cputemp.replace('\'C', '')
            cputemp = float(cputemp)

            logging.debug("Send a data")

            auth_key = bytes(os.environ.get("AUTH_KEY", "").encode("utf-8"))

            requests.put(
                "http://" + os.getenv("API_SERVER_HOST") + ":" + os.getenv("API_SERVER_PORT") + "/api/v1/env",
                {
                    "temperature": temp,
                    "humidity": humidity,
                    "cpu_temperature": cputemp,
                    "pressure": pressure,
                }
            )

            logging.debug("Waiting")
            time.sleep(30)
    except Exception as e:
        logging.warning("Connection refuse.")
    finally:
        logging.warning("Continue to start. Please wait 10 sec.")
        time.sleep(10)
