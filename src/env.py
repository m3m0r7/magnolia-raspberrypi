import argparse
import sys
import time
import logging
import os
from socket import *
from struct import *
from sense_hat import SenseHat

parser = argparse.ArgumentParser()
parser.add_argument("ip")
parser.add_argument("port")
args = parser.parse_args()
if not args.ip:
    print("Must set --ip\n")
    sys.exit()
if not args.port:
    print("Must set --port\n")
    sys.exit()

while True:
    print("Starting env.\n")
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
                cputemp = cputemp.replace('\'C\n', '')
                cputemp = float(cputemp)

                server.sendall(
                    pack("f", temp) +
                    pack("f", humidity) +
                    pack("f", pressure) +
                    pack("f", cputemp)
                )
                time.sleep(5)
        except Exception as e:
            logging.warning(
                'Disconnect client %s: %s',
                address,
                str(e)
            )
    except Exception as e:
        print("Connection refuse.\n")
    finally:
        print("Continue to start. Please wait 10 sec.\n")
        time.sleep(10)
