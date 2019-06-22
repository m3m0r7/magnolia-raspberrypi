import argparse
import sys
import time
import logging
import os
from socket import *
from struct import *
from sense_hat import SenseHat

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
    level=logging.DEBUG,
    format=formatter
)

# Connection Parameters
parser = argparse.ArgumentParser()
parser.add_argument("ip")
parser.add_argument("port")
args = parser.parse_args()

while True:
    logging.info("Starting env.")
    try:
        address = (
            args.ip,
            int(args.port)
        )
        server = socket(
            AF_INET,
            SOCK_STREAM
        )
        server.connect(address)
        sense = SenseHat()
        try:
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

                # Packet: Kind Tag (1byte) + Real data (4byte)
                # 0x00 = Temperature
                # 0x10 = Humidity
                # 0x20 = Pressure
                # 0x30 = CPU Temperature

                logging.debug("Send a data")

                sendPacket(server, 0x00, temp)
                sendPacket(server, 0x10, humidity)
                sendPacket(server, 0x20, pressure)
                sendPacket(server, 0x30, cputemp)

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
