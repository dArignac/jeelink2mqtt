import asyncio
import logging

import serial_asyncio

from lacrosse import LaCrosse
from sensors import Sensor


class Serial:
    log = logging.getLogger("jeelink2mqtt")

    def __init__(self, jeelink_address, mqtt, sensors, sensors_whitelist):
        self.jeelink_address = jeelink_address
        self.mqtt = mqtt
        self.sensors = sensors
        self.sensors_whitelist = sensors_whitelist

    async def main(self):
        while True:
            try:
                self.reader, self.writer = await serial_asyncio.open_serial_connection(
                    url=self.jeelink_address, baudrate=57600
                )
            except (IOError, OSError) as e:
                self.log.error("Can not open USB device! %s", e)
                await asyncio.sleep(5)
                continue

            # wait till jeelink has settled to ensure init sequence will be received
            await asyncio.sleep(2)
            self.log.info("Start receiving...")
            try:
                await self.receive()
            except (IOError, OSError, ConnectionError) as e:
                self.log.error("Serial connection lost: %s", e)
            finally:
                if hasattr(self, "writer") and self.writer:
                    try:
                        self.writer.close()
                    except Exception:
                        pass
            await asyncio.sleep(5)

    async def receive(self):
        while True:
            try:
                msg = await self.reader.readline()
                if not msg:
                    self.log.warning("Serial connection closed (EOF received)")
                    break

                decoded = LaCrosse.decodeMessage(msg)
                if decoded is not None:
                    sensor_id = decoded["id"]
                    # add/update sensor to sensors list
                    if sensor_id not in self.sensors:
                        is_whitelisted = sensor_id in self.sensors_whitelist
                        self.sensors[sensor_id] = Sensor(
                            self.mqtt,
                            sensor_id,
                            is_whitelisted,
                            self.sensors_whitelist[sensor_id]
                            if is_whitelisted
                            else None,
                        )
                    self.sensors[sensor_id].update(decoded)
            except (ValueError, asyncio.LimitOverrunError) as e:
                if hasattr(self.reader, "_buffer"):
                    self.reader._buffer.clear()
                self.log.warning(
                    "Oversized data received without newline from Jeelink: %s", e
                )
                await asyncio.sleep(0.5)
            except Exception as e:
                self.log.error("Unable to read from Jeelink: %s", e)
                await asyncio.sleep(1)
