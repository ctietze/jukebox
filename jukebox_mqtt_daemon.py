#!/usr/bin/python3
import logging
import paho.mqtt.client as mqtt
import sys
import yaml

from jukebox import Jukebox
from jukebox import load_yaml_config

if sys.version_info >= (3, 8):
    from systemd.journal import JournalHandler
    journald_handler = JournalHandler()
else:
    from systemd.journal import JournaldLogHandler
    journald_handler = JournaldLogHandler()

log = logging.getLogger(__name__)
log.addHandler(journald_handler)
log.setLevel(logging.DEBUG)

FILE_CONFIG_MQTT = 'configuration/mqtt.yaml'

mqtt_config = load_yaml_config(FILE_CONFIG_MQTT)
host = mqtt_config.get("host")
port = mqtt_config.get("port", 1883)
topic = mqtt_config.get("topic")
    
def on_message(client, userdata, message):
    log.info('On message: %s.', message)
    card = str(message.payload.decode("utf-8"))

    jukebox = Jukebox()
    jukebox.handle_card(card)

def on_connect(client, userdata, flags, rc):
    log.info('Connected to MQTT Broker: %s.', host)
    client.subscribe(topic)

if __name__ == "__main__":
    if not host or not topic:
        log.error("Missing MQTT broker configuration. Got: %s.", mqtt_config)
        print("Please configure your MQTT broker properly.")
    else:
        mqttClient = mqtt.Client()
        mqttClient.on_connect = on_connect
        mqttClient.on_message = on_message
        mqttClient.connect(host, port)
        mqttClient.loop_forever()