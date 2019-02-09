"""
Zinguo platform for sensors
"""
import json
import time
import asyncio
from homeassistant.components.sensor import (ENTITY_ID_FORMAT, PLATFORM_SCHEMA)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import (dispatcher_connect, dispatcher_send)
from homeassistant.const import (DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS, CONF_NAME, CONF_MAC, CONF_TOKEN, CONF_USERNAME)
import homeassistant.helpers.config_validation as cv
from custom_components.zinguo.const import *
import voluptuous as vol
from homeassistant.util import  slugify
import logging

_LOGGER = logging.getLogger(__name__)

deviceType = [CONF_TEMPERATURE]

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the ZiGate sensors."""
    devices = []
    for devType in deviceType:
        devices.append(ZinguoSensor(hass, config.get(devType), devType))

    add_devices(devices)


class ZinguoSensor(Entity):
    def __init__(self, hass, name, devType):
        """Initialize the sensor."""
        self._hass = hass
        self.entity_id = ENTITY_ID_FORMAT.format(slugify(devType))
        self._name = name
        self._type = devType
        self._state = None
        self._attributes = {}
        hass.bus.listen(CONF_EVENT_ZINGUO_SENSOR, self._handle_event)


    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    @property
    def device_class(self):
        """Return the device class of this entity."""
        return DEVICE_CLASS_TEMPERATURE

    def _handle_event(self, event):
        """eventMsg = json.loads(event.data)"""
        eventMsg = event.data
        _LOGGER.debug('ZINGUO : handle event start')
        if self._type in eventMsg:
            self._state = eventMsg[self._type]
            _LOGGER.debug('ZINGUO : self._state %s', self._state)
            #self.schedule_update_ha_state()

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return TEMP_CELSIUS


