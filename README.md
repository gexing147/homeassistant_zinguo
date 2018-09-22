# homeassistant_zinguo
配置文件参考如下:
```
 zinguo:
   username: 'username'
   password: 'passwd'

 switch:
   - platform: zinguo
     warmingSwitch1: 制暖1
     warmingSwitch2: 制暖2
     windSwitch: 吹风
     lightSwitch: 照明
     ventilationSwitch: 排气

 sensor:
   - platform: zinguo
     temperature: 洗手间温度
```
