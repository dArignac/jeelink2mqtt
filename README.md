# Jeelink2MQTT

Reads from a [Jeelink](https://www.digitalsmarties.net/products/jeelink) (currently only the 868 MHz variant is tested) to resolve LaCrosse sensor values (e.g. [Technoline TX 29 DTH-IT](https://www.amazon.com/dp/B00392XX5U)). The values are then published to MQTT, mainly in a format to use it with [Home Assistant](https://www.home-assistant.io/).

## Requirements

Requires [uv](https://docs.astral.sh/uv/) to be installed.

## Config file

The config file defines the sensors that shall be published to MQTT.

```
; config.ini
[Kitchen]
id=14
[Living Room]
id=36
```

## Run

Run with `uv run jeelink2mqtt.py -c config.ini`.
