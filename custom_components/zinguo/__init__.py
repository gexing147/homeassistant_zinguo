"""
Support for ZINGUO
"""

import asyncio
import threading
import time
import logging
import json
from custom_components.zinguo.pyzinguo import *
import requests

from homeassistant.const import (
              EVENT_HOMEASSISTANT_START, EVENT_HOMEASSISTANT_STOP)
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_NAME, CONF_MAC, CONF_TOKEN, CONF_USERNAME, CONF_PASSWORD, ATTR_NAME)
from custom_components.zinguo.const import *

try:
    # Valid since HomeAssistant 0.66+
    from homeassistant.util import async_ as hasync
except ImportError:
    # backwards compatibility, with workaround to avoid reserved word "async"
    # from homeassistant.util import async as hasync  # <- invalid syntax in Python 3.7
    import importlib
    hasync = importlib.import_module("homeassistant.util.async")


COMPONENT_TYPES = ('switch')

_LOGGER = logging.getLogger(__name__)




def setup(hass, config):
    """ Setup the ZINGUO platform """

    _LOGGER.debug('ZINGUO : Starting')

    hass.data[ZINGUO_UPDATE_MANAGER] = ZinguoUpdateManager(hass = hass, config = config)

    def start_zinguo_update_keep_alive(event):
        hass.data[ZINGUO_UPDATE_MANAGER].start_keep_alive()

    def stop_zinguo_update_keep_alive(event):
        hass.data[ZINGUO_UPDATE_MANAGER].stop_keep_alive()
    def toggle_zinguo_switch(call):
        hass.data[ZINGUO_UPDATE_MANAGER]._zinguoSwitch.toggle_zinguo_switch(call.data.get(ATTR_NAME))

    hass.bus.listen_once(EVENT_HOMEASSISTANT_START, start_zinguo_update_keep_alive)
    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, stop_zinguo_update_keep_alive)
    hass.services.register(
                     DOMAIN, SERVICE_TOGGLE_ZINGUO_SWITCH, toggle_zinguo_switch)

    return True


class ZinguoUpdateManager(threading.Thread):


    def __init__(self, hass, config):
        """Init Zinguo Update Manager."""
        threading.Thread.__init__(self)
        self._run = False
        self._lock = threading.Lock()
        _LOGGER.debug('ZINGUO : %s',config[DOMAIN][CONF_MAC])
        _LOGGER.debug('ZINGUO : %s',config[DOMAIN][CONF_TOKEN])
        self._zinguoSwitch = ZinguoSwitchB2(config[DOMAIN][CONF_USERNAME], config[DOMAIN][CONF_PASSWORD])
        self._hass = hass

    def run(self):
        while self._run:
            self.zinguo_update()
            _LOGGER.debug('ZINGUO : loop')
            time.sleep(1)

    def start_keep_alive(self):
        """Start keep alive mechanism."""
        with self._lock:
            self._run = True
            threading.Thread.start(self)

    def stop_keep_alive(self):
        """Stop keep alive mechanism."""
        with self._lock:
            self._run = False
            self.join()

    def zinguo_update(self):
        _LOGGER.debug('ZINGUO : update0')
        eventMsg = {}
        eventSensorMsg = {}

        _LOGGER.debug('ZINGUO : update')
        self._zinguoSwitch.get_status()
        self._zinguoSwitch.get_state_change()
        eventSensorMsg[CONF_TEMPERATURE] = self._zinguoSwitch.temperatureState
        self._hass.bus.fire(CONF_EVENT_ZINGUO_SENSOR,json.dumps(eventSensorMsg))
        if self._zinguoSwitch.warmingSwitch1StateChange or \
                self._zinguoSwitch.warmingSwitch2StateChange or \
                self._zinguoSwitch.windSwitchStateChange or \
                self._zinguoSwitch.lightSwitchStateChange or \
                self._zinguoSwitch.ventilationSwitchStateChange:
            _LOGGER.debug('ZINGUO : event fire')
            if True == self._zinguoSwitch.warmingSwitch1StateChange:
                eventMsg[CONF_WARMING_SWITCH_1] =  self._zinguoSwitch.warmingSwitch1StateNew
            if True == self._zinguoSwitch.warmingSwitch2StateChange:
                eventMsg[CONF_WARMING_SWITCH_2] = self._zinguoSwitch.warmingSwitch2StateNew
            if True == self._zinguoSwitch.windSwitchStateChange:
                eventMsg[CONF_WIND_SWITCH] = self._zinguoSwitch.windSwitchStateNew
            if True == self._zinguoSwitch.lightSwitchStateChange:
                eventMsg[CONF_LIGHT_SWITCH] = self._zinguoSwitch.lightSwitchStateNew
            eventMsg[CONF_VENTILATION_SWITCH] = self._zinguoSwitch.ventilationSwitchStateNew
            _LOGGER.debug('ZINGUO : event msg:%s', json.dumps(eventMsg))
            self._hass.bus.fire(CONF_EVENT_ZINGUO_STATE_CHANGE,json.dumps(eventMsg))
        else:
            _LOGGER.debug('ZINGUO : event not fire')
