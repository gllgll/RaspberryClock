import os
import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget
from Ui_MainWindow import Ui_Dialog
import requests
import json
import pygame
import datetime  # 系统时间
import time  # 引入定时器
from PyQt5.QtCore import QTimer  # 引入定时器和线程
from Voice_To_Text import Talk
from Time_Sign_Module import Get_Time_Sign
from turing_robot import TuringRobot
from configobj import ConfigObj
from Text_To_Voice import text2voice
from threading import Thread
from SenoMessage import *
from VoiceNotes1 import *
from VoiceNotes2 import *
from VoiceNotes3 import *

pygame.mixer.init()  # 初始化pygame


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        # 初始化一些数据，这样直接运行后数据就会显示
        Thread(target=self.Clock_timer).run()
        Thread(target=self.QueryWeather).run()
        Thread(target=self.Weather_timer).run()
        # Thread(target=self.Tem_Hum).run()
        Thread(target=self.BoxMessage).run()
        Thread(target=self.showThings).run()
        Thread(target=self.Center).run()
        Thread(target=self.showData).run()
        Thread(target=self.showTemHumi).run()
        # self.QueryWeather()  # 请求一次天气信息

        # 对控件进行信号和槽的绑定
        self.ui.toDoBut.clicked.connect(lambda: Thread(target=self.showThings).run())
        self.ui.deleteLog.clicked.connect(lambda: Thread(target=self.deleteThings).run())
        self.ui.Voice.clicked.connect(lambda: Thread(target=self.Luyin).run())

        self.ui.Tuling.clicked.connect(lambda: Thread(target=self.Tuling).run())

        # self.ui.pushButton.clicked.connect(self.QueryWeather)
        self.ui.pushButton.clicked.connect(lambda: Thread(target=self.QueryWeather).run())
        self.ui.HomeBtn.clicked.connect(self.TabToHome)
        self.ui.WeatherBtn.clicked.connect(self.TabToWeather)
        self.ui.AboutBtn.clicked.connect(self.TabToAbout)
        self.ui.RefreshButton.clicked.connect(lambda: Thread(target=self.QueryWeather).run())

        self.ui.checkBox1.stateChanged.connect(self.Check1)
        self.ui.checkBox2.stateChanged.connect(self.Check2)
        self.ui.checkBox3.stateChanged.connect(self.Check3)
        self.ui.calendarWidget.clicked.connect(lambda: Thread(target=self.showData).run())
        # 温湿度和语音提醒
        self.ui.temHumiBut.clicked.connect(lambda: Thread(target=self.showTemHumi).run())
        self.ui.voiceNotes1.clicked.connect(lambda: Thread(target=self.voiceNote1).run())
        self.ui.voiceNotes2.clicked.connect(lambda: Thread(target=self.voiceNote2).run())
        self.ui.voiceNotes3.clicked.connect(lambda: Thread(target=self.voiceNote3).run())

    # 日历界面将点击的日期及时间显示在下面
    def showData(self):
        date = self.ui.calendarWidget.selectedDate()
        self.ui.showdata.setText(date.toString("yyyy-MM-dd dddd"))

    # 通过录音记录事件，然后在闹钟响起的时候将该语句原封不动的播放出来
    def voiceNote1(self):
        getVoice1()

    def voiceNote2(self):
        getVoice2()

    def voiceNote3(self):
        getVoice3()

    # 将整个界面剧中显示
    def Center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 设置下拉框
    def BoxMessage(self):
        a, b = [], []  # 用于存放下拉框里面的数据
        for i in range(0, 60):
            if i <= 23:
                # a.append(str(i))
                aa = str(i).rjust(2, '0')
                a.append(aa)
            else:
                # b.append(str(i))
                bb = str(i).rjust(2, '0')
                b.append(bb)
        for i in a:
            self.ui.HourBox1.addItem(i)
            self.ui.HourBox2.addItem(i)
            self.ui.HourBox3.addItem(i)
        for j in a + b:
            self.ui.MinuteBox1.addItem(j)
            self.ui.MinuteBox2.addItem(j)
            self.ui.MinuteBox3.addItem(j)
        # 通过点击设置获取下拉框里显示的数据

    def ring(self):
        file = './audio/qq.mp3'
        track = pygame.mixer.music.load(file)
        pygame.mixer.music.play(loops=3, start=0.0)

    def playring(self, file):
        # file = './audio/voiceNote1.wav'
        isFile = os.path.exists(file)
        if isFile == True:
            track = pygame.mixer.music.load(file)
            pygame.mixer.music.play(loops=1, start=0.0)
        else:
            print('没有记录事件')

    def showTemHumi(self):
        # QApplication.processEvents()  # 实时刷新界面
        temper, humidity = senoMessage()  # 获取温湿度
        self.ui.temHumiLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.temHumiLabel.setText('温度：{}℃'.format(temper) + '\n' + '湿度：{}'.format(humidity))
        # QApplication.processEvents()  # 实时刷新界面
        # time.sleep(1)
        

    # def Ring1(self):
    #     hour1 = self.ui.HourBox1.currentText()  # 获取下拉列表里的时间数据 时  <class 'str'>
    #     minutes1 = self.ui.MinuteBox1.currentText()  # 分
    #
    #     self.timer1_ring = QTimer()
    #     self.timer1_ring.timeout.connect(lambda: self.timer_ring_conn(hour1, minutes1, self.timer1_ring))
    #     self.timer1_ring.start(1000)
    # 设置闹钟界面的第一个函数
    def Check1(self):
        # self.ischeck1 == self.ui.checkBox1.isChecked()
        check_statue1 = self.ui.checkBox1.checkState()
        hour1 = self.ui.HourBox1.currentText()  # 获取下拉列表里的时间数据 时  <class 'str'>
        minutes1 = self.ui.MinuteBox1.currentText()  # 分
        self.timer1_ring = QTimer()
        if check_statue1 == 0:
            self.ui.checkBox1.setText('关')
        if check_statue1 == 2:
            self.ui.checkBox1.setText("开")
            self.timer1_ring.timeout.connect(lambda: self.timer_ring_conn1(hour1, minutes1, self.timer1_ring))
            self.timer1_ring.start(1000)

    def Check2(self):
        check_statue2 = self.ui.checkBox2.checkState()
        hour1 = self.ui.HourBox2.currentText()  # 获取下拉列表里的时间数据 时  <class 'str'>
        minutes1 = self.ui.MinuteBox2.currentText()  # 分
        self.timer2_ring = QTimer()
        if check_statue2 == 0:
            self.ui.checkBox2.setText("关")
        if check_statue2 == 2:
            self.ui.checkBox2.setText("开")
            self.timer2_ring.timeout.connect(lambda: self.timer_ring_conn2(hour1, minutes1, self.timer2_ring))
            self.timer2_ring.start(1000)

    def Check3(self):
        check_satatue3 = self.ui.checkBox3.checkState()
        hour1 = self.ui.HourBox3.currentText()  # 获取下拉列表里的时间数据 时  <class 'str'>
        minutes1 = self.ui.MinuteBox3.currentText()  # 分
        self.timer3_ring = QTimer()
        if check_satatue3 == 0:
            self.ui.checkBox3.setText("关")
        if check_satatue3 == 2:
            self.ui.checkBox3.setText("开")
            self.timer3_ring.timeout.connect(lambda: self.timer_ring_conn3(hour1, minutes1, self.timer3_ring))
            self.timer3_ring.start(1000)

    def timer_ring_conn1(self, ring_hour1, ring_minute1, timer_ring1):
        file = './audio/voiceNote1.wav'
        isFile = os.path.exists(file)
        now = time.strftime('%H:%M', time.localtime())
        now_hour, now_minute = now.split(':')
        # print(now[:2]+now[-2:]+'\r', end='')
        if now_hour == ring_hour1 and now_minute == ring_minute1:
            self.ring()
            time.sleep(5)
            self.playring(file)
            timer_ring1.stop()

    def timer_ring_conn2(self, ring_hour2, ring_minute2, timer_ring2):
        file = './audio/voiceNote2.wav'
        isFile = os.path.exists(file)
        now = time.strftime('%H:%M', time.localtime())
        now_hour, now_minute = now.split(':')
        # print(now[:2]+now[-2:]+'\r', end='')
        if now_hour == ring_hour2 and now_minute == ring_minute2:
            self.ring()
            time.sleep(5)
            self.playring(file)
            timer_ring2.stop()

    def timer_ring_conn3(self, ring_hour3, ring_minute3, timer_ring3):
        file = './audio/voiceNote3.wav'
        isFile = os.path.exists(file)
        now = time.strftime('%H:%M', time.localtime())
        now_hour, now_minute = now.split(':')
        # print(now[:2]+now[-2:]+'\r', end='')
        if now_hour == ring_hour3 and now_minute == ring_minute3:
            self.ring()
            time.sleep(5)
            self.playring(file)
            timer_ring3.stop()

    def timer_ring_conn(self, ring_hour, ring_minute, timer_ring):
        now = time.strftime('%H:%M', time.localtime())
        now_hour, now_minute = now.split(':')
        # print(now[:2]+now[-2:]+'\r', end='')
        if now_hour == ring_hour and now_minute == ring_minute:
            self.ring()
            timer_ring.stop()

    # 语音设置闹钟函数
    def Luyin(self):
        info = Talk(per=4, speed=3, pit=0, vol=10).run()  # 语音识别后的得到的文字
        self.ui.Things.setText(info)
        get_time_from_voice = Get_Time_Sign(info)
        try:
            with open('./things.txt', 'a', encoding='utf-8') as f:
                f.write(info + '\n')
            get_time_from_voice = get_time_from_voice.strftime('%H:%M')
            hour, minute = get_time_from_voice.split(':')
            self.audioTimer = QTimer()
            self.audioTimer.timeout.connect(lambda: self.timer_ring_conn(hour, minute, self.audioTimer))
            self.audioTimer.start(1000)
        except Exception as ex:
            print('无法识别的语音数据：', info)
            file = './audio/exception.mp3'
            track = pygame.mixer.music.load(file)
            pygame.mixer.music.play()

    # 调用图灵机器人进行对话
    def Tuling(self):
        try:
            Config = ConfigObj('./Config.ini', encoding='utf-8')
            tuling_key = Config['Tuling']['API']['tuling_api_key']
            # 获取机器人对象
            robot = TuringRobot(tuling_key)
            ask_text = Talk(per=4, speed=3, pit=0, vol=10).run()
            tuling_anwser = robot.getTalk(ask_text)["results"][0]["values"]["text"]
            text2voice(tuling_anwser)
            # time.sleep(1)
            file = './audio/语音.mp3'
            track = pygame.mixer.music.load(file)
            pygame.mixer.music.play()
        except Exception as e:
            # print('异常处理')
            file = './audio/exception.mp3'
            track = pygame.mixer.music.load(file)
            pygame.mixer.music.play()

        # print(tuling_anwser)
        # print('Turing的回答：%s' % obj_tr.getTalk(ask_text)["results"][0]["values"]["text"])
        # 将合成的语音读取并播报出来

    def deleteThings(self):
        self.ui.Things.setWordWrap(True)
        self.ui.Things.setAlignment(QtCore.Qt.AlignTop)
        self.ui.Things.setStyleSheet("color:red;")
        with open('./things.txt', 'w', encoding='utf-8') as f:
            f.write('')
        self.ui.Things.setText('暂无待做事情')

    def showThings(self):
        self.ui.Things.setWordWrap(True)
        self.ui.Things.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        # self.ui.Things.setAlignment(QtCore.Qt.AlignLeft)
        self.ui.Things.setStyleSheet("color:red;")
        things = []
        with open('./things.txt', 'r', encoding='utf-8') as f:
            for line in f.readlines():
                curLine = line.strip().split('\n')
                things.append(curLine)
        try:
            if len(things) >= 1:
                self.ui.Things.setText(things[-1][0])
            else:
                self.ui.Things.setText('暂无待做事情')
            # if len(things) >= 3:
            #     self.ui.Things.setText(things[-3][0] + '\n' + things[-2][0] + '\n' + things[-1][0])
            # elif len(things) == 2:
            #     self.ui.Things.setText(things[-2][0] + '\n' + things[-1][0])
            # elif len(things) == 1:
            #     self.ui.Things.setText(things[-1][0])
            # else:
            #     self.ui.Things.setText('暂无待做事情')
        except IndexError:
            self.ui.Things.setText('异常处理')

    def Tem_Hum(self):
        self.timer0 = QTimer()
        self.timer0.setInterval(10000) # 设置定时器10s触发一次
        self.timer0.start()
        self.timer0.timeout.connect(self.showTemHumi)

    # 触发时间与天气信息更新的两个定时器
    def Clock_timer(self):
        self.timer1 = QTimer()
        self.timer1.setInterval(1000)  # 设置定时器 1S触发一次
        self.timer1.start()  # 启动定时器
        self.timer1.timeout.connect(self.RefreshTimeLabels)  # 当定时器走完一个周期，执行一次RefreshTimeLabels

    def Weather_timer(self):
        self.timer2 = QTimer()
        self.timer2.setInterval(10800000)  # 设置定时器 3 小时触发一次
        self.timer2.start()  # 启动定时器
        self.timer2.timeout.connect(self.QueryWeather)  # 当定时器走完一个周期，执行一次天气查询

    # 请求时间信息
    def RefreshTimeLabels(self):
        now = datetime.datetime.now()  # 获取系统时间
        self.ui.TimeLabel.setText("<font color=%s>%s</font>" % ('#ffffff', now.strftime("%H:%M")))  # TimeLabel用于放置时间
        self.ui.DateLabel.setText(
            "<font color=%s>%s</font>" % ('#ffffff', now.strftime("%Y-%m-%d %A")))  # TimeLabel用于放置时间
        self.ui.SecondLabel.setText("<font color=%s>%s</font>" % ('#ffffff', now.strftime("%S")))  # TimeLabel用于放置秒

    # 请求天气信息
    def QueryWeather(self):
        print('* queryWeather  ')
        # 通过 API 请求城市天气信息
        rep = requests.get(
            'https://devapi.qweather.com/v7/weather/now?location=101240201&key=68059aba07ab4db78a93508b920f2839')
        # 注意：这里使用了“和风天气”的付费API接口，用于获取全球范围的所在地天气详情信息。
        # 可以在和风天气开发者中心里新建key，然后把key的值填入到上面一行代码的“&key=”的后面。
        # 调用基本天气接口：1元/1000次；调用天气预报接口：1元/1000次。
        # 本版本每天只调用8次接口，几块钱就能够满足一年的需求。

        rep.encoding = 'utf-8'  # 网页编码信息
        WeatherData1 = json.dumps(rep.json())  # 打印json网页信息
        PyData = json.loads(WeatherData1)
        # print(PyData)

        # 读取实时天气的JSON文本
        Now_Location = '九江'
        Now_Temp = '%s' % PyData['now']['temp'] + ''  # temp
        print('* ForecastWeather  ')
        # 通过 API 请求城市天气信息
        rep2 = requests.get(
            'https://devapi.qweather.com/v7/weather/3d?location=101240201&key=68059aba07ab4db78a93508b920f2839')
        rep2.encoding = 'utf-8'  # 网页编码信息
        WeatherData2 = json.dumps(rep2.json())  # 打印json网页信息
        PyData2 = json.loads(WeatherData2)

        # 如果白天和夜间天气情况不同，则显示“X 转Y”，否则只显示白天天气
        for day in range(0, 3):
            if PyData2['daily'][day]['textDay'] == PyData2['daily'][day]['textNight']:
                castNight = ''
            else:
                castNight = '转' + PyData2['daily'][day]['textNight']

        # 读取天气预报的JSON文本
        # Update_Date = '%s' % PyData['now']['obsTime'].split('T')[0]  # 天气信息更新时间  2020-11-24T08:36+08:00
        Update_Date = '更新时间：' + '%s' % PyData2['updateTime'].split('T')[1].split('+')[
            0]  # 天气信息更新时间  2020-11-24T08:36+08:00
        Today_Status = '%s' % PyData2['daily'][0]['textDay'] + castNight  # 今天整天的天气情况
        Today_Temp = '%s' % PyData2['daily'][0]['tempMin'] + ' ~ %s℃' % \
                     PyData2['daily'][0]['tempMax']  # 今天的温度范围
        Today_Hum = '%s%%' % PyData2['daily'][0]['humidity']  # 今天空气湿度
        Today_RainProb = '%s' % PyData2['daily'][0]['precip']  # 今天降雨概率
        Today_SunsetTime = '%s' % PyData2['daily'][0]['sunset']  # 今天日落时间
        Tomorrow_Date = '%s' % PyData2['daily'][1]['fxDate']  # 明天的天气预报日期
        Tomorrow_Temp = '%s' % PyData2['daily'][1]['tempMin'] + ' ~ %s℃' % \
                        PyData2['daily'][1]['tempMax']  # 明天的温度范围
        Tomorrow_Status = '%s' % PyData2['daily'][1]['textDay'] + castNight  # 明天整天的天气情况

        # 写入今日天气信息到Weather页面中
        self.ui.WF_Location.setText("<font color=%s>%s</font><br>" % ('#ffffff', Now_Location))
        self.ui.WF_Date.setText("<font color=%s>%s</font><br>" % ('#ffffff', Update_Date))
        self.ui.WF_Status.setText("<font color=%s>%s</font><br>" % ('#ffffff', Today_Status))
        self.ui.WF_Temp.setText(
            "<font color=%s>%s</font><font color=#ffffff><font size=5px>℃</font></font>" % ('#ffffff', Now_Temp))

        self.ui.WF_Title.setText("<font color=#ffffff>温度</font>")
        self.ui.WF_Title_2.setText("<font color=#ffffff>湿度</font>")
        self.ui.WF_Title_3.setText("<font color=#ffffff>降水量</font>")
        self.ui.WF_Title_4.setText("<font color=#ffffff>日落时间</font>")
        self.ui.ForecastToday.setText("<font color=%s>%s<br>%s</br><br>%s</br><br>%s</br></font>" % (
            '#ffffff', Today_Temp, Today_Hum, Today_RainProb, Today_SunsetTime))  # 将请求的信息放入ForecastToday中，设置字体为 [白色]

        # 写入明日天气信息到Weather页面中
        self.ui.WF_Nx_Title.setText("<font color=#ffffff>明天</font>")
        self.ui.WF_Nx_Time.setText("<font color=%s>%s</font>" % ('#ffffff', Tomorrow_Date[5:]))  # 去除年份，只显示日期
        self.ui.ForecastNx_Status.setText("<font color=%s>%s</font>" % ('#ffffff', Tomorrow_Status))
        self.ui.ForecastNx_Temp.setText("<font color=%s>%s</font>" % ('#ffffff', Tomorrow_Temp))

    def TabToHome(self):
        self.ui.MainTab.setCurrentIndex(0)

    def TabToWeather(self):
        self.ui.MainTab.setCurrentIndex(1)

    def TabToAbout(self):
        self.ui.MainTab.setCurrentIndex(2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    icon = QtGui.QIcon('./title.png')
    win.setWindowTitle('智能语音闹钟by物联网工程gll')
    win.setWindowIcon(icon)
    win.show()
    win.showFullScreen()
    sys.exit(app.exec_())
