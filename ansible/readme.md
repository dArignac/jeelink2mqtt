# Ansible role for Jeelink2MQTT
This helps with installing and allows for running Jeelink2MQTT in a docker container (recomended).

You can install nativly or in a container. The later is required with newer versions of Ubuntu (e.g. 24.04) since it comes with Python 3.12 and does not allow to install pipenv via pip anymore.

In you hostfile you need to enable the role and set it up:

```
ENABLE_JEELINK2MQTT: true
JEELINK2MQTT_IN_DOCKER: true

JEELINK_SERNUM: "sernum"
JEELINK_PID: "6001"
JEELINK_VID: "0403"

JEELINK2MQTT_USER: "j2m"
JEELINK2MQTT_GROUP: "j2m"

JEELINK2MQTT_SENSORS:
  - Balkon: 24
  - Garage: 43

```

Notes to the above:
  - The user j2m must be created in another role or manually.
	It also must be a member of the group dialout.
  - Ensure the VID/PID and serila number fits to your lacross receiver.

## Details
The role creates a service module for systemd, so you can start/stop it with "sudo systemctl start jeelink2mqtt.service".

An udev rule is created, so the constant name "dev/jeelink" can be used.
