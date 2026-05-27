# Day 3: UART通信与PM2.5传感器 | UART Communication & PM2.5 Sensor

> **今日目标 (Today's Goals):**
> - 理解UART串行通信协议
> - 学会解析传感器数据帧
> - 成功读取PM2.5和PM10数据
> - 计算空气质量指数(AQI)
>
> **产出 (Deliverable):** 能读取并显示PM2.5数据的完整程序

---

## 🕒 时间安排 | Schedule

| 时间 | 活动类型 | 内容 |
|------|---------|------|
| 9:00-10:30 | 讲座 | UART协议原理与数据帧结构 |
| 10:45-12:00 | 实践 | PMS5003传感器连接 |
| 13:30-15:00 | 实践 | UART数据读取与解析 |
| 15:15-16:30 | 练习 | AQI计算与健康建议 |
| 16:30-17:00 | 总结 | 作业布置与Q&A |

---

## 📖 上午: UART协议原理 | Morning: UART Protocol

### 为什么要学UART? | Why Learn UART?

**真实应用场景:**
- GPS模块接收卫星数据(NMEA协议)
- 蓝牙模块与MCU通信
- 激光雷达传输点云数据
- 工业PLC与传感器网络

**UART vs I2C:**

| 特性 | UART | I2C |
|------|------|-----|
| 线缆数量 | 2根(TX/RX) | 2根(SDA/SCL) |
| 速度 | 较高(可达Mbps) | 较低(通常400kHz) |
| 设备数量 | 点对点 | 多主多从 |
| 复杂度 | 简单 | 较复杂 |
| 典型应用 | GPS、蓝牙 | 传感器网络 |

> **Real-world Applications:**
> - GPS modules receiving satellite data (NMEA protocol)
> - Bluetooth modules communicating with MCUs
> - Lidar transmitting point cloud data
> - Industrial PLCs and sensor networks
>
> **UART vs I2C:** UART is faster and simpler, I2C supports multiple devices

---

### 任务3.1: UART协议基础 (40分钟)

**UART通信原理:**

```
发送端(TX) ─────────────→ 接收端(RX)
   ESP32                   PMS5003
   (RX ←── TX)             (TX ─→ RX)
```

**关键参数:**

| 参数 | 说明 | 本项目值 |
|------|------|---------|
| **波特率** | 数据传输速度 | 9600 bps |
| **数据位** | 每帧数据位数 | 8位 |
| **停止位** | 帧结束标志 | 1位 |
| **校验位** | 错误检测 | 无 |

**数据帧格式:**
```
[起始位][D0][D1][D2][D3][D4][D5][D6][D7][停止位]
  0      1   0   1   1   0   0   1   0    1
```

**为什么需要TX/RX交叉连接?**  
因为一方的发送(TX)要连接到另一方的接收(RX)。

> **Why cross-connect TX/RX?**  
> Because one side's transmit (TX) must connect to the other side's receive (RX).

---

### 任务3.2: PMS5003数据帧解析 (30分钟)

**PMS5003协议特点:**

| 特性 | 说明 |
|------|------|
| **波特率** | 9600 bps |
| **数据格式** | 二进制，32字节/帧 |
| **更新频率** | 约1秒/次 |
| **输出内容** | PM1.0, PM2.5, PM10 |

**数据帧结构:**
```
字节  0-1: 起始字节 (0x42, 0x4D)
字节  2-3: 帧长度 (0x00, 0x1C = 28字节)
字节  4-5: PM1.0 标准浓度 (μg/m³)
字节  6-7: PM2.5 标准浓度 (μg/m³)
字节  8-9: PM10 标准浓度 (μg/m³)
字节10-11: PM1.0 大气浓度
字节12-13: PM2.5 大气浓度
字节14-15: PM10 大气浓度
...
字节30-31: 校验和
```

**校验和计算:**
```python
checksum = sum(字节0到字节29) & 0xFFFF
if checksum == (字节30 << 8) | 字节31:
    数据有效
```

**为什么需要校验和?**  
防止传输错误导致数据异常(如PM2.5=9999)。

> **Why need checksum?**  
> To prevent data anomalies from transmission errors (e.g., PM2.5=9999).

---

## 💻 下午: PMS5003传感器实践 | Afternoon: PMS5003 Practice

### 任务3.3: PMS5003硬件连接 (30分钟)

**PMS5003引脚说明:**

| 引脚 | 功能 | 连接到ESP32 |
|------|------|-------------|
| VCC | 电源(5V) | VIN (5V) |
| GND | 地 | GND |
| TX | 发送 | GPIO16 (RX2) |
| RX | 接收 | 不连接(只读) |
| SET | 设置 | 不连接或接3.3V |

**⚠️ 重要提示:**
- PMS5003需要5V供电!
- TX/RX必须交叉连接
- ESP32的RX2是GPIO16

**接线图:**
```
PMS5003         ESP32
────────────────────────
VCC (红)   →    VIN (5V)
GND (黑)   →    GND
TX  (绿)   →    GPIO16 (RX2)
RX  (黄)   →    (不连接)
SET        →    (不连接)
```

**接线步骤:**

1. **断开ESP32电源** (防止短路)
2. **连接电源线** (VCC和GND)
3. **连接信号线** (TX到GPIO16)
4. **检查连接** (用万用表测试)
5. **上电测试** (观察PMS5003风扇是否转动)

**预期结果:**
- PMS5003风扇开始转动
- 无冒烟或发热现象
- 连接牢固无松动

**常见问题:**
- Q: 风扇不转?  
  A: 检查5V供电，确认VCC接到VIN
- Q: 发热严重?  
  A: 立即断电，检查是否有短路

---

### 任务3.4: UART数据读取 (60分钟)

**步骤:**

1. **编写UART读取程序**
   ```python
   from machine import UART, Pin
   import time

   # 初始化UART (波特率9600, RX=GPIO16)
   uart = UART(2, baudrate=9600, rx=16, tx=17, timeout=1000)

   # 数据缓冲区
   buffer = bytearray(32)

   print("PMS5003 PM2.5传感器读取")
   print("=" * 40)

   while True:
       # 等待数据
       if uart.any():
           # 读取数据
           uart.readinto(buffer, 32)
           
           # 检查起始字节
           if buffer[0] == 0x42 and buffer[1] == 0x4D:
               # 计算校验和
               checksum = sum(buffer[0:30]) & 0xFFFF
               received_checksum = (buffer[30] << 8) | buffer[31]
               
               if checksum == received_checksum:
                   # 解析数据
                   pm25_standard = (buffer[6] << 8) | buffer[7]
                   pm10_standard = (buffer[8] << 8) | buffer[9]
                   pm25_atmospheric = (buffer[12] << 8) | buffer[13]
                   
                   # 打印结果
                   print(f"PM2.5: {pm25_standard} μg/m³")
                   print(f"PM10:  {pm10_standard} μg/m³")
                   print(f"PM2.5(大气): {pm25_atmospheric} μg/m³")
                   print("-" * 40)
               else:
                   print("校验和错误!")
           else:
               print("帧头错误!")
       
       time.sleep(1)
   ```

2. **优化读取逻辑**
   ```python
   def read_pm_sensor(uart, timeout_ms=5000):
       """读取PM传感器数据，带超时"""
       start_time = time.ticks_ms()
       buffer = bytearray(32)
       
       while time.ticks_diff(time.ticks_ms(), start_time) < timeout_ms:
           if uart.any() >= 32:
               uart.readinto(buffer, 32)
               
               # 验证帧
               if buffer[0] == 0x42 and buffer[1] == 0x4D:
                   checksum = sum(buffer[0:30]) & 0xFFFF
                   received = (buffer[30] << 8) | buffer[31]
                   
                   if checksum == received:
                       return {
                           "pm25": (buffer[6] << 8) | buffer[7],
                           "pm10": (buffer[8] << 8) | buffer[9],
                           "valid": True
                       }
       
       return {"valid": False}
   ```

**预期结果:**
- 每秒显示一次PM2.5和PM10数据
- PM2.5通常在10-100μg/m³范围
- 无校验和错误

**常见问题:**
- Q: 读不到数据?  
  A: 检查TX是否连接到RX2(GPIO16)
- Q: 频繁出现校验和错误?  
  A: 可能是波特率不匹配或接触不良

---

## 🧪 练习: AQI计算 | Practice: AQI Calculation

### 任务3.5: 空气质量指数计算 (30分钟)

**为什么要计算AQI?**  
PM2.5的原始数值(μg/m³)不直观，AQI将数据转换为0-500的健康指数。

> **Why calculate AQI?**  
> Raw PM2.5 values (μg/m³) are not intuitive. AQI converts data to a 0-500 health index.

**AQI计算公式:**
```python
def calculate_aqi_pm25(pm25):
    """根据PM2.5计算AQI"""
    
    # AQI分段
    if pm25 <= 35:
        # 优
        aqi = (50 / 35) * pm25
        level = "优"
        color = "绿色"
    elif pm25 <= 75:
        # 良
        aqi = 50 + (50 / 40) * (pm25 - 35)
        level = "良"
        color = "黄色"
    elif pm25 <= 115:
        # 轻度污染
        aqi = 100 + (50 / 40) * (pm25 - 75)
        level = "轻度污染"
        color = "橙色"
    elif pm25 <= 150:
        # 中度污染
        aqi = 150 + (50 / 35) * (pm25 - 115)
        level = "中度污染"
        color = "红色"
    elif pm25 <= 250:
        # 重度污染
        aqi = 200 + (100 / 100) * (pm25 - 150)
        level = "重度污染"
        color = "紫色"
    else:
        # 严重污染
        aqi = 300 + (100 / 150) * (pm25 - 250)
        level = "严重污染"
        color = "褐红色"
    
    return int(aqi), level, color

# 使用示例
pm25_value = 45
aqi, level, color = calculate_aqi_pm25(pm25_value)
print(f"PM2.5: {pm25_value} μg/m³")
print(f"AQI: {aqi} ({level})")
print(f"等级颜色: {color}")
```

**健康建议系统:**
```python
def get_health_advice(aqi_level):
    """根据AQI等级给出健康建议"""
    
    advice = {
        "优": "空气很好，适合户外活动",
        "良": "空气质量可接受，正常活动",
        "轻度污染": "敏感人群减少户外活动",
        "中度污染": "减少户外活动，佩戴口罩",
        "重度污染": "避免户外活动，关闭门窗",
        "严重污染": "所有人避免户外活动"
    }
    
    return advice.get(aqi_level, "未知等级")

# 使用
advice = get_health_advice(level)
print(f"健康建议: {advice}")
```

---

### 任务3.6: 综合监测程序 (30分钟)

**整合BME680和PMS5003:**

```python
from machine import Pin, I2C, UART
import bme680
import time

# 初始化I2C和传感器
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
bme = bme680.BME680_I2C(i2c=i2c)

# 初始化UART
uart = UART(2, baudrate=9600, rx=16, tx=17)

# AQI计算函数(从上面复制)
def calculate_aqi_pm25(pm25):
    # ... (代码同上)
    pass

# 主循环
print("环境监测站启动...")
print("=" * 50)

while True:
    try:
        # 读取BME680
        bme.get_sensor_data()
        temp = bme.data.temperature
        hum = bme.data.humidity
        pres = bme.data.pressure
        
        # 读取PMS5003
        pm_data = read_pm_sensor(uart)
        if pm_data["valid"]:
            pm25 = pm_data["pm25"]
            pm10 = pm_data["pm10"]
            
            # 计算AQI
            aqi, level, color = calculate_aqi_pm25(pm25)
            
            # 显示完整数据
            print(f"\n时间: {time.ticks_ms()}")
            print(f"温度: {temp:.1f}°C | 湿度: {hum:.1f}%")
            print(f"气压: {pres:.1f} hPa")
            print(f"PM2.5: {pm25} μg/m³ | PM10: {pm10} μg/m³")
            print(f"AQI: {aqi} ({level}) - {color}")
            print("=" * 50)
    
    except Exception as e:
        print(f"错误: {e}")
    
    time.sleep(5)
```

---

## 📝 今日作业 | Today's Assignment

### 基础作业 (必做)

1. **完成AQI计算器**  
   实现完整的AQI计算函数，并测试边界值

2. **对比实验**  
   记录一整天的PM2.5数据:
   - 早晨(8:00)
   - 中午(12:00)
   - 傍晚(18:00)
   - 深夜(22:00)
   分析变化规律

3. **回答问题**  
   - UART和I2C的主要区别是什么?
   - 为什么PMS5003需要5V供电?
   - PM2.5和PM10有什么区别?

### 进阶作业 (选做)

1. 研究: AQI的国际标准差异(中国vs美国)
2. 实现: 数据异常检测(如PM2.5突然飙升)
3. 思考: 如何延长传感器的使用寿命?

---

## 📚 参考资源 | References

- [PMS5003数据手册](https://www.alibaba.com/product-detail/PMS5003-PMS5003-PM2-5-laser_1600101936536.html)
- [AQI计算标准](http://www.mee.gov.cn/)
- [MicroPython UART文档](https://docs.micropython.org/en/latest/esp32/quickref.html#uart-serial-bus)

---

## 🔮 明日预告 | Tomorrow's Preview

**Day 4: OLED显示屏与数据可视化**

- 学习SSD1306 OLED驱动
- 在屏幕上显示文字和图形
- 创建实时监测界面
- 设计美观的数据布局

**前置准备:**
- 了解屏幕分辨率概念
- 思考: 如何在有限空间显示更多信息?

---

*最后更新: 2026-05-05 | Last updated: 2026-05-05*
