import logging


class LaCrosse:
    """
    Class for decoding the LaCrosse messages.
    Protocol: http://fredboboss.free.fr/articles/tx29.php
    """

    @staticmethod
    def decodeMessage(message):
        # log.debug(f"LaCrosse: Decoding message: {message}")
        values = message.split()
        log = logging.getLogger("jeelink2mqtt")

        if len(values) == 0:
            # if message != b"\n":
            log.debug(f"LaCrosse: Received empty message {message}")
            return

        if values[0].startswith(b"[LaCrosse"):
            log.debug(f"LaCrosse: Receiver is {str(values[0])}")
            return

        if values[0] != b"OK" or values[1] != b"9":
            log.debug(f"LaCrosse: Unknown message received {message}")
            return

        try:
            id = int(values[2])
            batteryNew = int(values[3]) >> 7
            # type = int(values[3]) & 0x7F
            temperature = int(values[4]) * 256 + int(values[5])
            temperature = (float(temperature) - 1000) / 10
            batteryWeak = int(values[6]) >> 7
            humidity = int(values[6]) & 0x7F
        except Exception as err:
            log.debug(f"LaCrosse: Illegal message received {message}, {err}")
            return

        # log.debug(
        #     f"LaCrosse: Sensor reporting: ID {id}, Temperature {temperature}, Humidity {humidity}, Battery new {batteryNew}, Battery weak {batteryWeak}"
        # )

        return {
            "id": id,
            "batteryNew": batteryNew,
            "batteryWeak": batteryWeak,
            "temperature": temperature,
            "humidity": humidity,
        }
