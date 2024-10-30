import logging

from paho.mqtt.client import Client

from homeassistant import HomeAssistantSensor


class Sensor(HomeAssistantSensor):
    log = logging.getLogger("jeelink2mqtt")

    def __init__(self, mqtt: Client, id: str, is_whitelisted: bool, name="invalid"):
        self.mqtt = mqtt
        self.id = id
        self.is_whitelisted = is_whitelisted
        self.name = name
        self.batteryNew = None
        self.batteryWeak = None
        self.temperature = None
        self.humidity = None
        self.logged_new = False

        super(Sensor, self).__init__(mqtt, id, name)

        if self.is_whitelisted:
            self.publish_hass_discovery()

    def update(self, values):
        self._update("batteryNew", values["batteryNew"])
        self._update("batteryWeak", values["batteryWeak"])
        self._update("temperature", values["temperature"])
        self._update("humidity", values["humidity"])
        if self.batteryNew and not self.is_whitelisted and not self.logged_new:
            self.log.info(f"New device found {self.id}: {self.temperature}, {self.humidity}")
            self.logged_new = True # do not SPAM the logs

        # log new devices that usually have a new battery set
        if self.batteryNew and not self.is_whitelisted and not self.logged_new:
            self.log.info(f"New device found {self}")
            self.logged_new = True

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value

    def _update(self, prop, value):
        # update the value if it changes
        if getattr(self, prop) != value:
            self.log.debug(
                f"Sensor {self.id}\t{prop}\tfrom\t{self.__getattribute__(prop)}\tto\t{value:<4}"
            )
            setattr(self, prop, value)

            # publish to mqtt
            if self.is_whitelisted:
                self.publish_hass_change()

    def __repr__(self) -> str:
        return f"Sensor(id={self.id}, temperature={self.temperature}, humidity={self.humidity}, batteryWeak={self.batteryWeak}, batteryNew={self.batteryNew})"
