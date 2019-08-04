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
        address = (
            os.environ.get("ENV_RECEIVE_SERVER_HOST"),
            int(os.environ.get("ENV_RECEIVE_SERVER_PORT"))
        )
        sense = SenseHat()
        try:
            while True:
                server = socket(
                    AF_INET,
                    SOCK_STREAM
                )
                server.connect(address)
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
                # Auth Key
                if len(auth_key) > 0:
                    server.sendall(auth_key)

                # Send packet information
                # Environments count (1 byte)
                server.sendall(pack("B", 4))
                
                # Send packets
                # Packet: Kind Tag (1byte) + Real data (4byte)
                # 0x00 = Temperature
                # 0x10 = Humidity
                # 0x20 = Pressure
                # 0x30 = CPU Temperature

                sendPacket(server, 0x00, temp)
                sendPacket(server, 0x10, humidity)
                sendPacket(server, 0x20, pressure)
                sendPacket(server, 0x30, cputemp)

                server.close()
                logging.debug("Waiting")
                time.sleep(5)
        except Exception as e:
            logging.warning(
                'Disconnect client %s: %s',
                address,
                str(e)
            )
    except Exception as e:
        logging.warning("Connection refuse.")
    finally:
        logging.warning("Continue to start. Please wait 10 sec.")
        time.sleep(10)
