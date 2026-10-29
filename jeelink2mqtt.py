import argparse
import asyncio
import configparser
import logging
import sys
import time

import paho
import paho.mqtt
import paho.mqtt.client

from serials import Serial

# contains all fetched sensors via Jeelink
sensors = {}
# list of sensor that we want to publish to MQTT
sensors_whitelist = {}


log = logging.getLogger("jeelink2mqtt")


def mqtt_on_connect(client, userdata, connect_flags, reason_code, properties):
    if reason_code == 0:
        log.info("MQTT: Connected successfully to the MQTT broker")
    else:
        log.error(f"MQTT: Failed to connect with code {reason_code}")


def mqtt_on_disconnect(client, userdata, flags, reason_code, properties):
    log.info("MQTT: Disconnected from the MQTT broker")


def mqtt_on_log(client, userdata, level, buf):
    log.debug(f"MQTT: Message {buf}")


def main():
    # cli arguments
    parser = argparse.ArgumentParser(
        prog="Jeelink2MQTT",
        description="Connects to LaCrosse sensors via Jeelink and publishes received information to MQTT",
    )
    parser.add_argument(
        "-j",
        "--jeelink",
        help="Serial port address of the connected JeeLink, default: /dev/ttyUSB0",
        metavar="serial_address",
        default="/dev/ttyUSB0",
        dest="jeelink_address",
    )
    parser.add_argument(
        "-c",
        "--config-file",
        help="Path to the config ini file, default: config.ini",
        metavar="config_file",
        default="config.ini",
        dest="config_file",
    )
    parser.add_argument(
        "--mqtt",
        help="Hostname of MQTT, default: localhost",
        metavar="host",
        default="localhost",
        dest="mqtt_host",
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="Print out debug messages",
        action="store_true",
        default=False,
        dest="debug",
    )
    args = parser.parse_args()

    # config file
    config = configparser.ConfigParser()
    config.read(args.config_file)

    for sensor_name in config.sections():
        sensors_whitelist[int(config[sensor_name]["id"])] = sensor_name

    # logging
    log.setLevel("DEBUG" if args.debug else "INFO")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)7s: %(message)s"))
    log.addHandler(sh)

    # mqtt
    mqtt = paho.mqtt.client.Client(
        paho.mqtt.enums.CallbackAPIVersion.VERSION2, client_id="jeelink2mqtt"
    )
    mqtt.on_connect = mqtt_on_connect
    # mqtt.on_log = mqtt_on_log
    mqtt.on_disconnect = mqtt_on_disconnect

    mqtt.connect(args.mqtt_host, 1883, 60)
    mqtt.loop_start()

    while not mqtt.is_connected():
        log.debug("MQTT: Waiting for connection")
        time.sleep(1)

    # event loop
    try:
        s = Serial(args.jeelink_address, mqtt, sensors, sensors_whitelist)
        asyncio.run(s.main())
    except KeyboardInterrupt:
        mqtt.loop_stop()
        mqtt.disconnect()
        time.sleep(2)
        print("Terminated")


if __name__ == "__main__":
    main()
