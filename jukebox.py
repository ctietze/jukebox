#!/usr/bin/python3
import logging
import os
import sys
import yaml

from mpd import MPDClient
from pymemcache.client import base

if sys.version_info >= (3, 8):
    from systemd.journal import JournalHandler
    journald_handler = JournalHandler()
else:
    from systemd.journal import JournaldLogHandler
    journald_handler = JournaldLogHandler()

log = logging.getLogger(__name__)
log.addHandler(journald_handler)
log.setLevel(logging.DEBUG)

def load_yaml_config(filename):
    with open(filename, 'r') as file:
        config = yaml.safe_load(file)
    return config

class Jukebox:

    FILE_CONFIG_CARDS = "configuration/cards.yaml"
    FILE_CONFIG_JUKEBOX = "configuration/jukebox.yaml"

    def __init__(self):
        self.config = load_yaml_config(self.FILE_CONFIG_JUKEBOX)
        self.cards = load_yaml_config(self.FILE_CONFIG_CARDS)

        memcache_host = self.config['memcache'].get('host', '127.0.0.1' )
        memcache_port = self.config['memcache'].get('port', 11211 )
        self.memc = base.Client((memcache_host, memcache_port))

        mpd_host = self.config['mpd'].get('host', 'localhost' )
        mpd_port = self.config['mpd'].get('port', 6600 )

        self.mpdc = MPDClient()
        self.mpdc.connect(mpd_host, mpd_port)

        self.card_volume_up = self.config['controlcards']['volume_up']
        self.card_volume_down = self.config['controlcards']['volume_up']
        self.card_pause = self.config['controlcards']['pause']
        self.card_clear = self.config['controlcards']['clear']
        self.card_shutdown = self.config['controlcards']['shutdown']

    def handle_card(self, card):
        log.debug("Handle card: '%s'.", card)

        last_card = self.find_last_card()
        
        if self.card_pause == card or last_card == card:
            self.play_pause()
        elif self.card_volume_up == card :
            self.volume(10)
        elif self.card_volume_down == card:
            self.volume(-10)
        elif self.card_clear == card:
            self.clear()
        elif self.card_shutdown == card:
            self.clear()
            self.shutdown()
        else:
            self.play(card)
        
        self.mpdc.disconnect()

    def play(self, card):
        log.debug("Play card: '%s'.", card)
        if card in self.cards:
            self.mpdc.clear()
            command = "mpc insert " + self.cards[card]
            os.system(command)
            self.mpdc.play()
            self.memc.set('last_card', card)
        else:
            log.error("Card '%s' not found.", card)

    def play_pause(self):
        log.debug("Play or pause.")
        
        if self.mpdc.status()["state"] == "stop":
            self.mpdc.play()
        else:
            self.mpdc.pause()

    def clear(self):
        log.debug("Stop and clear all.")
        self.mpdc.stop()
        self.mpdc.clear()
        self.mpdc.setvol(self.config['mpd']['startvolume'])
        self.memc.set('last_card', '')

    def volume(self, vol_change):
        log.debug("Change volume: '%s'.", vol_change)
        self.mpdc.volume(vol_change)

    def shutdown(self):
        log.debug("Shutdown now.")
        os.system("sudo shutdown now")
        
    def find_last_card(self):
        optional_last_card = self.memc.get('last_card')
        if optional_last_card is not None:
            last_card = optional_last_card.decode("utf-8")
        else:
            last_card = ""

        log.debug("Find last card: '%s'.", last_card)
        return last_card
