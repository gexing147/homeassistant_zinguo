"""
Zinguo platform for switches
"""
import json
import time
import asyncio
from homeassistant.components.switch import (SwitchDevice,ENTITY_ID_FORMAT, PLATFORM_SCHEMA)
from homeassistant.helpers.dispatcher import (dispatcher_connect, dispatcher_send)
from homeassistant.const import (CONF_NAME, CONF_MAC, CONF_TOKEN, CONF_USERNAME)
import homeassistant.helpers.config_validation as cv
from custom_components.zinguo.const import *
import voluptuous as vol
from homeassistant.util import  slugify
import logging


_LOGGER = logging.getLogger(__name__)

deviceType = [CONF_WARMING_SWITCH_1,
        CONF_WARMING_SWITCH_2,
        CONF_WIND_SWITCH,
        CONF_LIGHT_SWITCH,
        CONF_VENTILATION_SWITCH]

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the ZiGate switchs."""
    devices = []
    for devType in deviceType:
        devices.append(ZinguoSwitch(hass, config.get(devType), devType))

    add_devices(devices)


class ZinguoSwitch(SwitchDevice):
    def __init__(self, hass, name, devType):
        """Initialize the switch."""
        self._hass = hass
        self.entity_id = ENTITY_ID_FORMAT.format(slugify(devType))
        self._name = name
        self._type = devType
        self._state = False
        self._attributes = {}
        hass.bus.listen(CONF_EVENT_ZINGUO_STATE_CHANGE, self._handle_event)

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        if self.is_on is False:
            ret = self._hass.services.call(DOMAIN,SERVICE_TOGGLE_ZINGUO_SWITCH, {"name":self._type})
            if ret is True:
                self._state = True
                _LOGGER.debug('ZINGUO : turn on')
                self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        if self.is_on is True:
            ret = self._hass.services.call(DOMAIN,SERVICE_TOGGLE_ZINGUO_SWITCH, {"name":self._type})
            if ret is True:
                self._state = False
                _LOGGER.debug('ZINGUO : turn off')
                self.schedule_update_ha_state()
    def _handle_event(self, event):
        eventMsg = json.loads(event.data)
        _LOGGER.debug('ZINGUO : handle event start')
        if self._type in eventMsg:
            _LOGGER.debug('ZINGUO : handle event %s' ,eventMsg[self._type])
            _LOGGER.debug('ZINGUO : handle event %s', event)
            if CONF_ON == eventMsg[self._type]:
                self._state = True
                _LOGGER.debug('ZINGUO : ON_STATE')
                self.schedule_update_ha_state()
            elif  CONF_OFF == eventMsg[self._type]:
                self._state = False
                _LOGGER.debug('ZINGUO : OFF_STATE')
                self.schedule_update_ha_state()
            else:
                _LOGGER.debug('ZINGUO : handle event something goes wrong')


