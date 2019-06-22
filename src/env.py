import argparse
import sys
import time
import logging
import os
from socket import *
from struct import *
from sense_hat import SenseHat

# Set logging format
formatter = '[%(levelname)s][%(asctime)s] %(message)s'
logging.basicConfig(
    level=logging.INFO,
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
                # Get environment from Sensor Hat
                humidity = sense.get_humidity()
                pressure = sense.get_pressure()
                temp = sense.get_temperature_from_pressure()

                # Get CPU temperature
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
                server.sendall(
                    pack("Bf", 0x00, temp) +
                    pack("Bf", 0x10, humidity) +
                    pack("Bf", 0x20, pressure) +
                    pack("Bf", 0x30, cputemp)
                )
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
