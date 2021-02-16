# -*- coding = utf-8 -*-
""""
本模块是语音识别，将语音转换成文字
"""
from aip import AipSpeech
import pyaudio
import wave
import numpy as np
import pygame
from configobj import ConfigObj
from pydub import AudioSegment


class Talk():
    def __init__(self, per=1, speed=5, pit=5, vol=5):
        self.speed = speed  # 语速
        self.per = per  # 发音人选择
        self.pit = pit  # 语调
        self.vol = vol  # 音量
        self.man_wav = 'audio/man.wav'
        self.client = None  #
        self.listen = True
        self.stop = not True
        self.test = True

    """初始化pygame模块"""

    def pygame_init(self):
        pygame.mixer.init()

    """以二进制格式打开文件"""

    def get_file_content(self, filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    """播放WAV"""

    def play_wav(self, file):
        """参数：wav文件绝对路径"""
        """阻塞，直到播放完成"""
        CHUNK = 1024  # 定义数据流块
        wf = wave.open(file, 'rb')
        p = pyaudio.PyAudio()
        # 打开数据
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        data = wf.readframes(CHUNK)  # 返回最多n个音频帧
        while data:
            stream.write(data)
            data = wf.readframes(CHUNK)
        stream.stop_stream()
        stream.close()
        p.terminate()

    """MP3文件转WAV文件"""

    def mp3_to_wav(self, mp3, wav):
        """参数：MP3文件绝对路径，WAV文件绝对路径"""
        """输出：WAV文件"""
        sound = AudioSegment.from_mp3(mp3)  # 加载mp3文件
        sound.export(wav, format="wav")  # 转换格式

    """有声音就录音"""

    def recodeing(self, t):
        """参数：录音阈值，正常1500"""
        """
        阻塞，直到录音完成
        声音的处理在计算机里面是按chunk来存储，播放，录制的
        比如每一帧是代表声波的信号（单声道、双声道、混合声道等等）每一
        次进行量化之后的数据，那么chunk就是每次可以处理多少帧这样的数据
        """
        CHUNK = 4096  # 每次读取的音频流长度，数据流块
        FORMAT = pyaudio.paInt16  # 语音文件的格式
        CHANNELS = 1  # 声道数，百度语音识别要求单声道
        RATE = 8000  # 采样率， 8000 或者 16000， 推荐 16000 采用率
        wait = True  # 录音等待
        LEVEL = 1000
        p = pyaudio.PyAudio()
        # 打开数据流
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []
        while wait:
            data = stream.read(CHUNK)  # 读取数据  data就是数字音频数据，包含了音调、音色、振幅等信息
            audio_data = np.frombuffer(data, dtype=np.short)
            temp = np.max(audio_data)
            if temp > t:
                wait = not True
        large_count = np.sum(audio_data > LEVEL)
        while large_count > 10:
            frames.append(data)
            data = stream.read(CHUNK)
            audio_data = np.frombuffer(data, dtype=np.short)
            large_count = np.sum(audio_data > LEVEL)
        # 停止数据流
        stream.stop_stream()
        stream.close()
        # 关闭 PyAudio
        p.terminate()
        wf = wave.open(self.man_wav, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print('录音完毕...')

    def login(self):
        # # 根据登录信息创建百度云语音接口，以实现语音识别和语音合成
        Config = ConfigObj('./Config.ini', encoding='utf-8')
        APP_ID = Config['Baidu']['API']['client_AppID']
        API_KEY = Config['Baidu']['API']['client_id']
        SECRET_KEY = Config['Baidu']['API']['client_secret']
        self.client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    def listening(self):
        while self.listen:
            self.recodeing(1500)
            print("开始上传音频数据...")
            result_text = self.client.asr(self.get_file_content(self.man_wav), 'wav', 8000, {'dev_pid': '1537', })
            print('语音识别结果：')
            print(result_text)
            # print(result_text["result"][0][:-1])  #获取说的话
            if 'result' in result_text.keys():
                info = result_text["result"][0][:-1]
                if self.test:
                    print('唤醒音识别结果：' + info)
                    return info
                    # TODO:得到语音识别结果
            else:
                if self.test:
                    print('识别失败')

    def run(self):
        self.pygame_init()
        try:
            self.login()
            print("登录成功...")
        except:
            print("登录失败...")
        while True:
            message = self.listening()  # 得到所说的话
            print("录音完毕...")
            return message


if __name__ == '__main__':
    a = Talk(per=4, speed=3, pit=0, vol=10).run()
    print(a + 'b')
