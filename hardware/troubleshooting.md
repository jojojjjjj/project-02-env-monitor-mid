# 故障排查指南 | Troubleshooting Guide

> 常见问题与解决方案 | Common Issues and Solutions

---

## 🔍 问题诊断流程 | Diagnostic Flow

```
系统不工作
    ↓
检查电源 ─→ 无电源 → 检查USB线/更换电源
    ↓ 有电源
检查ESP32启动 ─→ 无启动 → 检查接线/重烧固件
    ↓ 启动正常
检查传感器 ─→ 无数据 → 检查I2C/UART接线
    ↓ 有数据
检查WiFi ─→ 不连接 → 检查密码/重启路由器
    ↓ 连接正常
检查MQTT ─→ 不连接 → 检查Broker地址
    ↓ 连接正常
检查显示 ─→ 不显示 → 检查OLED接线
```

---

## ⚡ 电源问题 | Power Issues

### ESP32无法启动

**症状:**
- OLED无显示
- 串口无输出
- 指示灯不亮

**可能原因:**
1. USB线损坏
2. 供电不足
3. ESP32损坏

**解决方案:**
```bash
# 1. 更换USB线
# 2. 测试USB口电压(应为5V)
# 3. 按住BOOT键上电(进入下载模式)
# 4. 检查ESP32引脚是否有短路
```

### 设备频繁重启

**症状:**
- 运行一段时间后重启
- 串口输出"Watchdog reset"

**可能原因:**
1. 功率不足
2. 代码死循环
3. 电源质量差

**解决方案:**
```python
# 1. 添加看门狗喂狗
import machine
wdt = machine.WDT(timeout=10000)
wdt.feed()

# 2. 检查是否有死循环
# 3. 使用质量好的USB供电
```

---

## 🌡️ 传感器问题 | Sensor Issues

### I2C扫描不到设备

**症状:**
```python
# 运行i2c.scan()返回空列表[]
```

**可能原因:**
1. 接线错误
2. 上拉电阻缺失
3. 地址错误
4. 传感器损坏

**解决方案:**
```python
# 1. 检查接线
# SDA -> GPIO21
# SCL -> GPIO22
# VCC -> 3.3V
# GND -> GND

# 2. 测试上拉电阻
# 大多数传感器模块已集成,如果没有需要添加4.7kΩ电阻

# 3. 尝试不同地址
for addr in [0x76, 0x77]:
    try:
        sensor = bme680.BME680_I2C(i2c=i2c, address=addr)
        print(f"Found at 0x{addr:02X}")
    except:
        pass
```

### BME680读数异常

**症状:**
- 温度显示0或None
- 湿度显示异常值
- 气压值不变化

**可能原因:**
1. 传感器未校准
2. 读取频率过高
3. 环境变化剧烈

**解决方案:**
```python
# 1. 传感器预热
import time
sensor = bme680.BME680_I2C(i2c=i2c)
for i in range(10):  # 预热10次
    sensor.get_sensor_data()
    time.sleep(1)

# 2. 设置采样间隔
time.sleep(2)  # 至少2秒间隔

# 3. 校准
# 与标准温度计对比,记录偏移量
temp_offset = standard_temp - sensor_temp
corrected_temp = sensor_temp + temp_offset
```

### PMS5003无数据

**症状:**
- UART读不到数据
- PM值始终为0

**可能原因:**
1. 接线错误
2. 波特率不匹配
3. 5V供电不足
4. 风扇不转

**解决方案:**
```python
# 1. 检查接线
# PMS5003 TX -> ESP32 GPIO16 (RX2)
# VCC -> VIN (5V,不是3V3!)

# 2. 确认波特率9600
uart = UART(2, baudrate=9600, rx=16, tx=17)

# 3. 检查风扇
# 上电后风扇应该转动,如果不转检查供电

# 4. 测试串口
while True:
    if uart.any():
        data = uart.read()
        print(data)  # 应该看到二进制数据
```

---

## 📺 显示问题 | Display Issues

### OLED无显示

**症状:**
- 屏幕全黑或全白
- 无文字显示

**可能原因:**
1. I2C地址错误
2. 接线问题
3. 显示屏损坏

**解决方案:**
```python
# 1. 扫描I2C地址
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
devices = i2c.scan()
# 应该看到0x3C或0x3D

# 2. 尝试不同地址
for addr in [0x3C, 0x3D]:
    try:
        oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=addr)
        oled.fill(0)
        oled.text("TEST", 0, 0)
        oled.show()
        print(f"Working at 0x{addr:02X}")
    except:
        pass

# 3. 检查对比度
oled.contrast(255)  # 最大对比度
```

### OLED显示乱码

**症状:**
- 显示方块或乱码
- 文字重叠

**可能原因:**
1. 字库缺失
2. 刷新频率过高
3. 内存不足

**解决方案:**
```python
# 1. 使用内置字体
# 不要尝试加载自定义字体

# 2. 降低刷新率
time.sleep(1)  # 每秒刷新一次

# 3. 清空显示
oled.fill(0)  # 每次显示前清空
```

---

## 📶 网络问题 | Network Issues

### WiFi连接失败

**症状:**
- 无法连接到路由器
- IP获取失败

**可能原因:**
1. SSID或密码错误
2. 路由器问题
3. ESP32 WiFi损坏

**解决方案:**
```python
# 1. 检查WiFi凭据
# 注意大小写和特殊字符

# 2. 扫描可用网络
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
networks = wlan.scan()
for net in networks:
    print(f"SSID: {net[0]}, RSSI: {net[3]}")

# 3. 尝试不同频段
# 2.4G vs 5G,ESP32只支持2.4G

# 4. 重启ESP32
machine.reset()
```

### MQTT连接失败

**症状:**
- 无法连接到Broker
- 频繁断开

**可能原因:**
1. Broker地址错误
2. 端口被防火墙阻止
3. 网络不稳定

**解决方案:**
```python
# 1. 检查Broker地址
# 使用公共Broker测试
broker = "broker.emqx.io"  # 应该能连接

# 2. 检查端口
# 默认1883,SSL是8883

# 3. 添加错误处理
try:
    client.connect()
except Exception as e:
    print(f"连接失败: {e}")

# 4. 实现重连机制
while not connected:
    try:
        client.connect()
        connected = True
    except:
        time.sleep(5)
```

---

## 🔧 调试技巧 | Debugging Tips

### 串口调试

```python
# 使用串口输出调试信息
print("DEBUG: 程序启动")

# 打印变量值
print(f"温度: {temperature}")

# 打印错误堆栈
import sys
try:
    # 你的代码
except Exception as e:
    sys.print_exception(e)
```

### 分步测试

```python
# 测试单个功能
def test_i2c():
    i2c = I2C(0, scl=Pin(22), sda=Pin(21))
    devices = i2c.scan()
    print(f"I2C设备: {devices}")

def test_sensor():
    sensor = bme680.BME680_I2C(i2c=i2c)
    sensor.get_sensor_data()
    print(f"温度: {sensor.data.temperature}")

# 逐个测试
test_i2c()
test_sensor()
```

### 性能分析

```python
import time
import gc

# 测量执行时间
start = time.ticks_ms()
# 你的代码
end = time.ticks_ms()
print(f"执行时间: {time.ticks_diff(end, start)}ms")

# 检查内存
print(f"剩余内存: {gc.mem_free()} bytes")
```

---

## 📞 获取帮助 | Getting Help

### 信息收集

在寻求帮助前,请准备:

1. **硬件信息**
   - ESP32型号
   - 传感器型号
   - 接线照片

2. **软件信息**
   - MicroPython版本
   - 错误信息
   - 相关代码

3. **问题描述**
   - 预期行为
   - 实际行为
   - 复现步骤

### 资源链接

- [MicroPython论坛](https://forum.micropython.org/)
- [ESP32论坛](https://www.esp32.com/viewforum.php?f=20)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/micropython)

---

*最后更新: 2026-05-05*
