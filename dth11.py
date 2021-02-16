import RPi.GPIO as GPIO
import time

CHANNEL = 26  # 设置端口号
count = 0  # 初始化计数器
data = []  # 初始化列表

GPIO.setmode(GPIO.BCM)  # 设置gpio引脚编号模式
time.sleep(1)
GPIO.setup(CHANNEL, GPIO.OUT)  # 设置为输出模式
GPIO.output(CHANNEL, GPIO.LOW)  # 输出低电平，即发送触发信号

time.sleep(0.02)  # 低电平维持0.02秒，此过程至少需要18ms才能确保DHT检测到MCU信号
GPIO.output(CHANNEL, GPIO.HIGH)  # 输出高电平，标志低电平结束，上拉电压20us~40us回应DHT
GPIO.setup(CHANNEL, GPIO.IN)  # 设置端口模式为输入
# 跳过初始状态的低电平
while GPIO.input(CHANNEL) == GPIO.LOW:
    continue
# 跳过初始状态的高电平
while GPIO.input(CHANNEL) == GPIO.HIGH:
    continue

# 仅仅寸放40个数据
while count < 40:
    k = 0
    # 跳出低电平
    while GPIO.input(CHANNEL) == GPIO.LOW:
        continue
    # 如果是高电平，则进入循环，高电平结束时停止
    """计数器自增，如果计数器大于100，则跳出循环，数据错误
    如果计数器小于8，则认为值为0，否则为1"""
    while GPIO.input(CHANNEL) == GPIO.HIGH:
        k += 1
        if k > 100: #始终高电平，代表DHT未正确响应
            break
    if k < 8:
        data.append(0) #高电平信号持续为26~28us，写0
    else:
        data.append(1) #高电平持续信号为70us左右，写1
    count += 1  # 数据位数器加一
print(data)
# 按位切割数据
humidity_bit = data[0:8] # 湿度位
humidity_point_bit = data[8:16] # 湿度检测位
temperature_bit = data[16:24] # 温度位
temperature_point_bit = data[24:32] # 温度检测位
check_bit = data[32:40] # 检测位

humidity = 0
humidity_point = 0
temperature = 0
temperature_point = 0
check = 0
# 计算各个数据结果和校验值
for i in range(8):
    humidity += humidity_bit[i] * 2 ** (7 - i) # 换算湿度
    humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
    temperature += temperature_bit[i] * 2 ** (7 - i) # 换算温度
    temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
    check += check_bit[i] * 2 ** (7-i)
# 计算校验值
tmp = humidity + humidity_point + temperature + temperature_point
if check == tmp:
    print('数据正确')
    # print('温度：' + str(temperature) + '，湿度：' + str(humidity))
    print ("温度 :", temperature, "*C, 湿度 :", humidity, "%")
else:
    print('数据错误')
    # print('温度：' + str(temperature) + '，湿度：' + str(humidity) + '校验值：' + str(check) + '，检查值：' + str(tmp))
    print ("温度 :", temperature, "*C, 湿度 :", humidity, "% c校验值 :", check, ", 检查值 :", tmp)

GPIO.cleanup()
