# Prerequisites
MPD is installed and Spotify Premium account is configured.

# Installation
## Requirements
Python >= 3.7

The necessary python packages are summarized inside the requirements file.
```
sudo pip3 install -r requirements.txt
```

# Settings
Copy the example yaml files, remove the example suffix and change it to your needs.

- Configure RFID Reader within ```configuration/reader.yaml```
- Configure MQTT Broker within ```configuration/mqtt.yaml```
- Configure MPD, memcache and control cards within ```configuration/mqtt.yaml```
- Configure RFID cards. Add RFID card id <> Spotify mapping to ```configuration/cards.yaml```

# Development / Debugging
## MQTT queue
```
# Subscribe to MQTT topic and display messages
$ mosquitto_sub -v -t rfid_card

# Publish message to topic to simulate a scanned RFID card
$ mosquitto_pub -t rfid_card -m [CARD_ID]
```

## Show logs
```
$ journalctl --follow -u jukebox-mqtt.service -u jukebox-reader.service
```