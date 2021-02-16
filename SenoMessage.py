#!/usr/bin/python
# encoding:utf-8
import time
import Adafruit_DHT


def senoMessage():
    # 11表示使用DH11， 26表示GPIO BCM模式下的引脚
    humidity, temperature = Adafruit_DHT.read_retry(11, 26)
    if humidity is not None and temperature is not None:
        # print('Temp={0:0.2f}度  Humidity={1:0.2f}%'.format(temperature, humidity))
        Temp = '{0:0.2f}'.format(temperature)
        Humidity = '{0:0.2f}%'.format(humidity)
        return Temp, Humidity
    else:
        # print('读取数据失败')
        return '读取数据失败', '读取数据失败'


tem, hum = senoMessage()
print('温度：{}'.format(tem))
print('湿度：{}'.format(hum))
# while(1):
#     if humidity is not None and temperature is not None:
#         print('Temp={0:0.2f}度  Humidity={1:0.2f}%'.format(temperature, humidity))
#         time.sleep(1)
#     else:
#         print('读写数据失败')
