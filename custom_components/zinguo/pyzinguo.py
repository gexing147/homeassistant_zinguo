# _*_ coding: utf-8 _*_

import codecs
import logging
import requests
import hashlib
import json
import sys
from requests import Response
from custom_components.zinguo.const import *
from homeassistant.const import (CONF_NAME, CONF_MAC, CONF_TOKEN, CONF_USERNAME)

############################################################################################

############################################################################################
_LOGGER = logging.getLogger(__name__)


class ZinguoSwitchB2():

    def __init__(self, masterUser, password):
        self.password = password
        self.mac = None
        self.token = None
        self.masterUser = masterUser

        self.warmingSwitch1StateChange = False
        self.warmingSwitch2StateChange = False
        self.windSwitchStateChange = False
        self.lightSwitchStateChange = False
        self.ventilationSwitchStateChange = False

        self.warmingSwitch1StateOld = CONF_OFF
        self.warmingSwitch2StateOld = CONF_OFF
        self.windSwitchStateOld = CONF_OFF
        self.lightSwitchStateOld = CONF_OFF
        self.ventilationSwitchStateOld = CONF_OFF

        self.warmingSwitch1StateNew = CONF_OFF
        self.warmingSwitch2StateNew = CONF_OFF
        self.windSwitchStateNew = CONF_OFF
        self.lightSwitchStateNew = CONF_OFF
        self.ventilationSwitchStateNew = CONF_OFF

        self.temperatureState = '0'

        _LOGGER.debug('ZINGUO : b2 init')
        self.login()


    def login(self):
        url = 'http://114.55.66.106:8002/api/v1/customer/login'
        headers = {'User-Agent': 'okhttp/3.6.0',
                'Content-Type': 'aplication/json;charset=UTF-8',
                'x-access-token': 'null'
                }
        sha1 = hashlib.sha1()
        sha1.update(self.password.encode('utf-8'))
        hash_pass = sha1.hexdigest()
        data = {'account': self.masterUser, 'password': hash_pass}

        try:
            r= requests.post(url, json=data, headers=headers, timeout = 2)
        except requests.exceptions.ConnectionError:
            _LOGGER.debug('ZINGUO : ConnectionError')
            return False
        except:
            _LOGGER.debug('ZINGUO : except')
            return False

        json_data = json.loads(r.text)
        self.token = json_data['token']
        self.mac = json_data['deviceIds'][0]['mac']

        return True

    def get_status(self):
        _LOGGER.debug('ZINGUO : get status1')
        url="http://114.55.66.106:8002/api/v1/device/getDeviceByMac?mac=" + self.mac
        _LOGGER.debug('ZINGUO : get status2')
        headers = {'User-Agent': 'okhttp/3.6.0',
                'Content-Type': 'aplication/json;charset=UTF-8',
                'x-access-token': self.token
                }
        _LOGGER.debug('ZINGUO : get status3')

        try:
            r = requests.get(url,headers=headers, timeout = 2)
        except requests.exceptions.ConnectionError:
            _LOGGER.debug('ZINGUO : ConnectionError')
            return False
        except:
            _LOGGER.debug('ZINGUO : except')
            return False

        json_data = json.loads(r.text)

        _LOGGER.debug('ZINGUO : get status4')
        if json_data != None:
            self.warmingSwitch1StateOld = self.warmingSwitch1StateNew
            self.warmingSwitch2StateOld = self.warmingSwitch2StateNew
            self.windSwitchStateOld = self.windSwitchStateNew
            self.lightSwitchStateOld = self.lightSwitchStateNew
            self.ventilationSwitchStateOld = self.ventilationSwitchStateNew

            self.warmingSwitch1StateNew = json_data[CONF_WARMING_SWITCH_1] #暖风一档
            self.warmingSwitch2StateNew = json_data[CONF_WARMING_SWITCH_2] #暖风二档
            self.windSwitchStateNew = json_data[CONF_WIND_SWITCH] #吹风
            self.lightSwitchStateNew = json_data[CONF_LIGHT_SWITCH]  #照明
            self.ventilationSwitchStateNew = json_data[CONF_VENTILATION_SWITCH] #排气

            self.temperatureState = json_data[CONF_TEMPERATURE]#温度
            return True
        else:
            _LOGGER.debug('ZINGUO : json data is null')
            return False



    def get_state_change(self):
        if self.warmingSwitch1StateOld == self.warmingSwitch1StateNew:
            self.warmingSwitch1StateChange = False
        else:
            self.warmingSwitch1StateChange = True

        if self.warmingSwitch2StateOld == self.warmingSwitch2StateNew:
            self.warmingSwitch2StateChange = False
        else:
            self.warmingSwitch2StateChange = True

        if self.windSwitchStateOld == self.windSwitchStateNew:
            self.windSwitchStateChange = False
        else:
            self.windSwitchStateChange = True

        if self.lightSwitchStateOld == self.lightSwitchStateNew:
            self.lightSwitchStateChange = False
        else:
            self.lightSwitchStateChange = True

        if self.ventilationSwitchStateOld == self.ventilationSwitchStateNew:
            self.ventilationSwitchStateChange = False
        else:
            self.ventilationSwitchStateChange = True

    def toggle_zinguo_switch(self, switchName):
        url = "http://114.55.66.106:8002/api/v1/wifiyuba/yuBaControl"
        headers = {'User-Agent': 'okhttp/3.6.0' ,
                  'Content-Type':'aplication/json;charset=UTF-8',
                  'x-access-token':self.token
                  }
        data = {"mac":self.mac,
                switchName:1,
                "turnOffAll":0,
                "setParamter":False,
                "action":False,
                "masterUser":self.masterUser}

        try:
            r = requests.put(url, json=data, headers=headers, timeout = 2)
        except requests.exceptions.ConnectionError:
            _LOGGER.debug('ZINGUO : ConnectionError')
            return False
        except:
            _LOGGER.debug('ZINGUO : except')
            return False

        json_data = json.loads(r.text)
        result = json_data['result']
        if requests != "设置成功":
            return True
        else:
            return False

############################################################################################
