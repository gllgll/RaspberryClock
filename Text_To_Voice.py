# -*- coding = utf-8 -*-

"""
本模块为语音合成，用于将文字转换为语音
"""

import os
from configobj import ConfigObj
from aip import AipSpeech
import pygame

pygame.mixer.init()

def text2voice(text):
    try:
        os.mkdir('audio')
    except FileExistsError:
        pass

    Config = ConfigObj('./Config.ini', encoding='utf-8')

    # my_mac = uuid.UUID(int=uuid.getnode()).hex[-12:]  # 获取本机MAC
    # print(my_mac)

    # 获取百度API参数
    APP_ID = Config['Baidu']['API']['client_AppID']
    API_KEY = Config['Baidu']['API']['client_id']
    SECRET_KEY = Config['Baidu']['API']['client_secret']
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    # f = open('文字.txt', 'r', encoding='utf-8')
    # sentenses = f.read().replace('\n', '')
    # f.close()

    result = client.synthesis(text, 'zh', 1,
                              {'vol': 5,  # 音量，取值0-15，默认为5中音量
                               'per': 4,  # 发音人选择, 0为女声，1为男声，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女
                               'spd': 5,  # 语速，取值0-9，默认为5中语速
                               'pit': 5  # 音调，取值0-9，默认为5中语调
                               }
                              )

    # 识别正确返回语音二进制 错误则返回dict
    if not isinstance(result, dict):
        with open('./audio/语音.mp3', 'wb') as f:
            f.write(result)
    f.close()


if __name__ == '__main__':
    text2voice('抱歉，您说的话中没有时间标志')
    file = './audio/语音.mp3'
    # pygame.mixer.init()
    track = pygame.mixer.music.load(file)
    pygame.mixer.music.play()
