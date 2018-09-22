# homeassistant_zinguo
峥果智能浴霸开关是一款使用8266为基础的wifi智能开关，可以使用官方提供的手机APP进行远程状态查询和开关操作。
本插件通过模仿手机APP的登陆、查询、操作行为实现通过HA同步状态信息和远程操作。
![image](https://github.com/gexing147/homeassistant_zinguo/edit/master/zinguo.png)

# 使用步骤
## 配置智能开关
根据产品说明书进行配置，直到通过手机APP可以远程控制开关，及为配置成功。

## 创建插件目录
```
cd 你的配置文件目录
mkdir custom_components
```
## 获取插件
```
cd custom_components
git clone https://github.com/gexing147/homeassistant_zinguo/
cp homeassistant_zinguo/custom_components/ -r ./
```

## 配置configuration.yaml
配置文件参考如下:
```
 zinguo:
   #手机APP的用户名称
   username: 'username'
   #手机APP的密码
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
