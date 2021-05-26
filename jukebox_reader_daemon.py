#!/usr/bin/python3
import asyncio
import logging
import paho.mqtt.publish as publish
import sys

from evdev import ecodes, InputDevice, list_devices
from jukebox import load_yaml_config
from time import sleep
from yaml import safe_load

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

FILE_CONFIG_READER = 'configuration/reader.yaml'
reader_config = load_yaml_config(FILE_CONFIG_READER)
device_name = reader_config.get("name")
device_id_range = reader_config.get("id_range")

devices = [InputDevice(path) for path in list_devices()]
for device in devices:
    if device_name == device.name:
        reader = InputDevice(device.path)
        log.info("Reader '%s' found on path '%s'", device, device.path)
    else:
        log.error("Reader '%s' not found", device_name)

async def read_card(device):
    card_id = ''
    key = ''
    async for event in device.async_read_loop():
        if event.type == 1 and event.value == 1:
            if 'KEY_ENTER' == ecodes.KEY[event.code]: 
                log.info('Publish card: %s', card_id)
                publish.single(topic, int(card_id), hostname=host, port=port)
                card_id = ''
                sleep( 5 )
            else:
                card_id += device_id_range[event.code]

if __name__ == "__main__":
    if not host or not topic: 
        log.error("Missing MQTT broker configuration. Got: %s.", mqtt_config)
        print("Please configure your MQTT broker properly.")
    elif not device_name or not device_id_range:
        log.error("Missing RFID reader configuration. Got: %s.", reader_config)
        print("Please configure your RFID reader properly.")
    else:
        asyncio.ensure_future(read_card(reader))
        loop = asyncio.get_event_loop()
        loop.run_forever()
