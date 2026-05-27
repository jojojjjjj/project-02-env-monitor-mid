# 前置知识清单 | Prerequisites Checklist

> 在开始本项目之前，请确认已掌握以下基础知识  
> Before starting this project, please ensure you have mastered the following basics

---

## ✅ 必需基础 | Essential Basics

### 1. 数学基础 | Mathematics Fundamentals

| 主题 | 要求 | 应用场景 |
|------|------|---------|
| 基础代数 | 理解变量、方程、函数 | 传感器数据处理 |
| 百分比与小数 | 计算与单位转换 | 空气质量指数(AQI)计算 |
| 图表阅读 | 理解坐标轴、曲线、柱状图 | 数据可视化分析 |
| 基础统计 | 平均值、最大值、最小值 | 环境数据趋势分析 |

**练习资源:**
- [Khan Academy: Algebra Basics](https://www.khanacademy.org/math/algebra-basics)
- [可汗学院中文版](https://zh.khanacademy.org/math/algebra-basics)

---

### 2. 电脑操作 | Computer Operations

| 技能 | 说明 | 验证方式 |
|------|------|---------|
| 文件管理 | 创建文件夹、复制粘贴文件 | 能独立整理项目文件夹 |
| 文本编辑 | 使用记事本/VS Code编辑文本 | 能保存并修改.py文件 |
| 终端命令 | 基本cd、ls、python命令 | 能运行Python脚本 |
| USB设备 | 能识别驱动安装问题 | ESP32连接后能识别串口 |

---

## 📚 建议预习 | Recommended Preparation

### 3. Python基础 | Python Fundamentals

**为什么要学Python?**  
MicroPython是Python 3的精简版，运行在ESP32等微控制器上。掌握Python基础可以让你快速理解IoT设备编程逻辑。

> **Why learn Python?**  
> MicroPython is a lean implementation of Python 3 that runs on microcontrollers like ESP32. Mastering Python basics enables you to quickly understand IoT device programming logic.

#### 必需概念:

**① 变量与数据类型 (Variables & Data Types)**
```python
# 数值类型
temperature = 25.5  # 浮点数 - 用于传感器读数
humidity = 60       # 整数 - 百分比

# 字符串
device_name = "AirButler_01"

# 布尔值
is_online = True
```

**② 列表与字典 (Lists & Dictionaries)**
```python
# 列表 - 存储多个传感器读数
sensor_values = [25.5, 60, 1013.25]

# 字典 - 结构化数据
sensor_data = {
    "temperature": 25.5,
    "humidity": 60,
    "pressure": 1013.25
}
```

**③ 函数定义 (Functions)**
```python
def read_sensor():
    """读取传感器数据"""
    return {"temp": 25.5, "hum": 60}

# 调用函数
data = read_sensor()
```

**④ 循环与条件 (Loops & Conditions)**
```python
# while循环 - 主程序循环
while True:
    data = read_sensor()
    print(data)
    
    # if条件 - 异常检测
    if data["temp"] > 30:
        print("警告: 温度过高!")
```

**练习资源:**
- [Python官方教程(中文)](https://docs.python.org/zh-cn/3/tutorial/)
- [MicroPython快速入门](https://docs.micropython.org/en/latest/quickref.html)

---

### 4. 电子学概念 | Electronics Concepts

**为什么需要电子学知识?**  
理解电压、电流、电阻可以帮你避免烧毁传感器，并解决接线问题。

> **Why need electronics knowledge?**  
> Understanding voltage, current, and resistance helps prevent damaging sensors and solve wiring issues.

#### 核心概念:

| 概念 | 定义 | 本项目应用 |
|------|------|-----------|
| **电压 (Voltage)** | 电势差，单位V (伏特) | ESP32工作在3.3V，接5V会烧毁 |
| **电流 (Current)** | 电荷流动，单位A (安培) | 传感器耗电量决定电源需求 |
| **电阻 (Resistance)** | 阻碍电流，单位Ω (欧姆) | I2C总线上拉电阻(4.7kΩ) |
| **GND** | 接地，电路参考点 | 所有设备必须共地 |
| **数字信号** | 0/1高低电平 | GPIO引脚输出 |
| **模拟信号** | 连续电压值 | ADC读取(本项目主要用数字传感器) |

#### 关键安全规则:

⚠️ **永远不要将5V设备连接到ESP32的3.3V引脚**  
⚠️ **接线前确认电源正负极**  
⚠️ **不要带电拔插传感器**

**学习资源:**
- [SparkFun: Electronics概念](https://learn.sparkfun.com/tutorials/voltage-current-resistance-and-ohms-law)
- [立创EDA: 电子学入门(中文)](https://www.lceda.cn/)

---

### 5. 网络基础 | Networking Fundamentals

**为什么IoT需要网络知识?**  
物联网的本质是"连接"，理解网络协议是数据传输的基础。

> **Why does IoT need networking knowledge?**  
> The essence of IoT is "connection", understanding network protocols is fundamental to data transmission.

#### 必需概念:

| 概念 | 说明 | 本项目应用 |
|------|------|-----------|
| **WiFi** | 无线局域网 | ESP32连接路由器 |
| **IP地址** | 设备网络标识 | MQTT broker地址(如192.168.1.100) |
| **端口** | 服务访问通道 | MQTT默认端口1883 |
| **客户端/服务器** | 网络角色 | ESP32是MQTT客户端 |
| **发布/订阅** | 消息传递模式 | MQTT核心机制 |

#### MQTT协议简介:

```
发布者(Publisher) → 主题(Topic) → 订阅者(Subscriber)
     ESP32           home/airbutler        Grafana
   (sensor data)      (message bus)      (dashboard)
```

**学习资源:**
- [MQTT Essentials](https://www.hivemq.com/mqtt-essentials/)
- [MQTT中文教程](https://mcxiaoke.gitbooks.io/mqtt-cn/content/)

---

### 6. 串口通信 | Serial Communication

**为什么重要?**  
ESP32通过串口与电脑通信，用于烧录程序和调试输出。

> **Why important?**  
> ESP32 communicates with the computer via serial port for programming and debugging output.

#### 基本概念:

| 术语 | 说明 |
|------|------|
| **波特率 (Baud Rate)** | 数据传输速度，本项目用115200 |
| **TX/RX** | 发送/接收引脚 |
| **COM口** | Windows下串口设备名称(COM3, COM4等) |
| **PuTTY/Thonny** | 串口终端软件 |

**调试示例:**
```
ESP32输出 → 串口 → USB → 电脑 → PuTTY显示
"Temperature: 25.5°C"
```

---

## 🎯 自我评估 | Self-Assessment

完成以下检查题，评估准备情况:

### Python基础测试

```python
# 1. 创建一个存储温度数据的列表
temperatures = [22.5, 23.0, 24.5]

# 2. 计算平均温度
avg_temp = sum(temperatures) / len(temperatures)
print(f"平均温度: {avg_temp}")

# 3. 创建函数判断温度是否过高
def is_too_hot(temp):
    return temp > 30

# 4. 循环检测
for temp in temperatures:
    if is_too_hot(temp):
        print("警告!")
```

### 电子学测试

- [ ] 我知道3.3V和5V的区别
- [ ] 我明白GND是什么
- [ ] 我能看懂简单的接线图

### 网络测试

- [ ] 我知道自家WiFi的名称和密码
- [ ] 我理解IP地址的作用
- [ ] 我知道什么是客户端和服务器

---

## 📖 预习时间建议 | Recommended Study Time

| 主题 | 预计时间 | 优先级 |
|------|---------|-------|
| Python基础 | 4-6小时 | ⭐⭐⭐ |
| 电子学概念 | 2-3小时 | ⭐⭐ |
| 网络基础 | 2-3小时 | ⭐⭐ |
| **总计** | **8-12小时** | |

**建议预习顺序:** Python → 电子学 → 网络

---

## ❓ 常见问题 | FAQ

**Q1: 我完全没编程经验，能参加吗?**  
A: 可以! 项目从零开始，前3天会有Python基础教学。

**Q2: 需要购买额外的学习材料吗?**  
A: 不需要，所有学习资源都在线免费提供。

**Q3: 预习不来得及怎么办?**  
A: 不用担心，课程设计包含"补课环节"，关键概念会在项目中反复讲解。

---

*最后更新: 2026-05-05 | Last updated: 2026-05-05*
