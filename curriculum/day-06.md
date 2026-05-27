# Day 6: WiFi连接与网络基础 | WiFi Connection & Networking Basics

> **今日目标 (Today's Goals):**
> - 理解WiFi连接原理和网络基础
> - 实现ESP32自动连接WiFi
> - 学习网络调试和错误处理
> - 完成第一周项目检查点
>
> **产出 (Deliverable):** 能稳定连接WiFi的ESP32系统

---

## 🕒 时间安排 | Schedule

| 时间 | 活动类型 | 内容 |
|------|---------|------|
| 9:00-10:30 | 讲座 | WiFi原理与网络基础 |
| 10:45-12:00 | 实践 | WiFi连接实现 |
| 13:30-15:00 | 实践 | 网络测试与调试 |
| 15:15-16:30 | 练习 | 第一周项目整合 |
| 16:30-17:00 | 总结 | Week 1检查与Q&A |

---

## 📖 上午: WiFi与网络基础 | Morning: WiFi & Networking

### 为什么要学网络连接? | Why Learn Networking?

**IoT的核心价值在于连接:**
```
无连接设备          IoT设备
温度传感器    →    云端分析    →    智能控制
(只能本地读)        (远程访问)      (自动化)
```

**真实应用场景:**
- 远程监控家中空气质量
- 多设备数据汇聚分析
- 云端AI处理传感器数据
- 自动化控制(如空气差自动开净化器)

> **IoT's Core Value is Connection:**  
> Networking transforms local sensors into cloud-connected smart devices

---

### 任务6.1: 网络基础概念 (30分钟)

**核心概念:**

| 概念 | 说明 | 示例 |
|------|------|------|
| **SSID** | WiFi网络名称 | "Home_WiFi_5G" |
| **密码** | WiFi安全密钥 | "password123" |
| **IP地址** | 设备在网络中的标识 | 192.168.1.100 |
| **子网掩码** | 网络范围标识 | 255.255.255.0 |
| **网关** | 连接到外网的出口 | 192.168.1.1 |
| **DNS** | 域名解析服务器 | 8.8.8.8 |
| **MAC地址** | 设备硬件唯一ID | AA:BB:CC:DD:EE:FF |

**IP地址分类:**
```
局域网IP (私有):
- 192.168.x.x (最常见)
- 10.x.x.x
- 172.16-31.x.x

公网IP (全球唯一):
- 由ISP分配
- 用于互联网访问

本机回环:
- 127.0.0.1 (指自己)
```

**为什么需要DHCP?**  
自动分配IP地址，避免手动配置冲突。

> **Why need DHCP?**  
> Automatically assigns IP addresses to avoid manual configuration conflicts

---

### 任务6.2: WiFi连接流程 (30分钟)

**ESP32 WiFi架构:**
```
ESP32 WiFi子系统
├── Station Mode (STA)    ← 连接到路由器(本项目用)
├── AP Mode               ← 作为热点
└── AP+STA Mode           ← 同时连接和创建热点
```

**连接流程:**
```
1. 设置WiFi为Station模式
   ↓
2. 配置网络信息(SSID/密码)
   ↓
3. 开始连接
   ↓
4. 等待连接成功
   ↓
5. 获取IP地址
   ↓
6. 连接完成
```

**状态码:**
```python
# WiFi连接状态
STAT_IDLE = 1000      # 空闲
STAT_CONNECTING = 1001 # 连接中
STAT_GOT_IP = 1010    # 获得IP(成功)
STAT_NO_AP_FOUND = 201 # 找不到AP
STAT_WRONG_PASS = 202  # 密码错误
STAT_CONNECT_FAIL = 203 # 连接失败
```

---

## 💻 下午: WiFi实践 | Afternoon: WiFi Practice

### 任务6.3: WiFi连接实现 (60分钟)

**步骤:**

1. **扫描可用网络**
   ```python
   import network
   import time

   # 创建WLAN对象(Station模式)
   wlan = network.WLAN(network.STA_IF)
   wlan.active(True)

   # 扫描网络
   print("扫描WiFi网络...")
   networks = wlan.scan()

   print(f"找到 {len(networks)} 个网络:")
   for net in networks:
       ssid = net[0].decode('utf-8')
       rssi = net[3]  # 信号强度
       print(f"  {ssid} - 信号: {rssi} dBm")
   ```

2. **连接WiFi**
   ```python
   def connect_wifi(ssid, password, timeout=10):
       """连接WiFi"""
       wlan = network.WLAN(network.STA_IF)
       wlan.active(True)
       
       # 断开旧连接
       wlan.disconnect()
       
       # 连接新网络
       print(f"连接到 {ssid}...")
       wlan.connect(ssid, password)
       
       # 等待连接
       start_time = time.time()
       while not wlan.isconnected():
           if time.time() - start_time > timeout:
               print("连接超时!")
               return False
           time.sleep(0.5)
           print(".", end="")
       
       print("\n连接成功!")
       
       # 打印网络信息
       print(f"IP地址: {wlan.ifconfig()[0]}")
       print(f"子网掩码: {wlan.ifconfig()[1]}")
       print(f"网关: {wlan.ifconfig()[2]}")
       print(f"DNS: {wlan.ifconfig()[3]}")
       
       return True

   # 使用
   connect_wifi("Your_WiFi_Name", "Your_Password")
   ```

3. **自动重连机制**
   ```python
   class WiFiManager:
       """WiFi管理器 - 处理连接和重连"""
       
       def __init__(self, ssid, password):
           self.ssid = ssid
           self.password = password
           self.wlan = network.WLAN(network.STA_IF)
           self.wlan.active(True)
           self.connected = False
           self.last_check = 0
           self.check_interval = 30  # 30秒检查一次
       
       def connect(self, timeout=10):
           """连接WiFi"""
           print(f"连接到 {self.ssid}...")
           self.wlan.connect(self.ssid, self.password)
           
           start_time = time.time()
           while not self.wlan.isconnected():
               if time.time() - start_time > timeout:
                   print("连接失败!")
                   self.connected = False
                   return False
               time.sleep(0.5)
           
           print("连接成功!")
           print(f"IP: {self.wlan.ifconfig()[0]}")
           self.connected = True
           return True
       
       def check_connection(self):
           """检查连接状态，自动重连"""
           now = time.time()
           
           # 定时检查
           if now - self.last_check > self.check_interval:
               self.last_check = now
               
               if not self.wlan.isconnected():
                   print("连接断开，尝试重连...")
                   self.connected = False
                   self.connect()
       
       def is_connected(self):
           """是否已连接"""
           return self.wlan.isconnected()
       
       def get_ip(self):
           """获取IP地址"""
           if self.wlan.isconnected():
               return self.wlan.ifconfig()[0]
           return None

   # 使用
   wifi = WiFiManager("Your_WiFi", "password")
   wifi.connect()
   ```

---

### 任务6.4: 网络测试 (30分钟)

**1. Ping测试(如果可用):**
```python
def ping_test(host="8.8.8.8", count=4):
    """简单的Ping测试"""
    print(f"Ping {host}...")
    
    success = 0
    for i in range(count):
        # MicroPython没有原生ping，使用socket连接测试
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((host, 80))  # 尝试连接HTTP端口
            sock.close()
            success += 1
            print(f"  包 {i+1}: 成功")
        except:
            print(f"  包 {i+1}: 超时")
    
    print(f"成功率: {success}/{count}")
```

**2. HTTP请求测试:**
```python
def http_get(url):
    """简单的HTTP GET请求"""
    import socket
    
    try:
        # 解析URL
        if "://" in url:
            url = url.split("://")[1]
        
        host, path = url.split("/", 1) if "/" in url else (url, "")
        path = "/" + path
        
        # 创建socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        # 连接服务器
        print(f"连接 {host}...")
        sock.connect((host, 80))
        
        # 发送HTTP请求
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"
        sock.send(request.encode())
        
        # 接收响应
        response = sock.recv(1024)
        sock.close()
        
        print(response.decode())
        return True
    
    except Exception as e:
        print(f"请求失败: {e}")
        return False

# 测试
http_get("example.com/")
```

**3. NTP时间同步:**
```python
def get_ntp_time():
    """获取NTP网络时间"""
    import socket
    import struct
    
    NTP_HOST = "ntp.aliyun.com"  # 阿里云NTP服务器
    NTP_PORT = 123
    
    try:
        # 创建UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        
        # NTP请求包(48字节)
        NTP_PACKET = b'\x1b' + 47 * b'\0'
        
        # 发送请求
        sock.sendto(NTP_PACKET, (NTP_HOST, NTP_PORT))
        
        # 接收响应
        data, _ = sock.recvfrom(48)
        sock.close()
        
        # 解析时间(从第40字节开始)
        timestamp = struct.unpack("!I", data[40:44])[0]
        
        # NTP时间戳转换(Unix时间戳)
        ntp_time = timestamp - 2208988800
        
        # 设置RTC
        import machine
        rtc = machine.RTC()
        rtc.datetime(time.gmtime(ntp_time))
        
        print(f"时间已同步: {time.gmtime(ntp_time)}")
        return ntp_time
    
    except Exception as e:
        print(f"NTP同步失败: {e}")
        return None

# 使用
get_ntp_time()
```

---

## 📝 第一周检查 | Week 1 Checkpoint

### 任务6.5: 项目整合 (60分钟)

**整合第一周所有功能:**

```python
# main.py - 完整的环境监测站(本地版)
from machine import Pin, I2C
import bme680
import ssd1306
import time
import ujson

# 导入之前的类
# (实际项目中这些应该在单独文件中)
from sensor_manager import SensorManager
from data_logger import DataLogger
from wifi_manager import WiFiManager

class AirButler:
    """空气管家 - 主控制类"""
    
    def __init__(self, wifi_ssid, wifi_pass):
        print("=" * 50)
        print("  空气管家 Environmental Monitor")
        print("  版本: 1.0 (本地版)")
        print("=" * 50)
        
        # 初始化WiFi
        self.wifi = WiFiManager(wifi_ssid, wifi_pass)
        
        # 初始化传感器
        print("\n初始化传感器...")
        self.sensor_manager = SensorManager()
        
        # 初始化OLED
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21))
        self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c)
        
        # 初始化数据记录器
        self.logger = DataLogger()
        
        # 统计分析
        self.temp_readings = []
        self.pm_readings = []
        
        # 显示启动画面
        self._show_splash()
    
    def _show_splash(self):
        """显示启动画面"""
        self.oled.fill(0)
        self.oled.text("AIR BUTLER", 30, 10)
        self.oled.text("Starting...", 30, 30)
        self.oled.show()
        time.sleep(2)
    
    def update_display(self, reading):
        """更新OLED显示"""
        self.oled.fill(0)
        
        # 标题
        self.oled.text("AIR BUTLER", 30, 0)
        
        # 传感器数据
        if reading.temperature:
            self.oled.text(f"T:{reading.temperature:5.1f}C", 0, 12)
        
        if reading.humidity:
            self.oled.text(f"H:{reading.humidity:5.1f}%", 64, 12)
        
        if reading.pm25:
            self.oled.text(f"PM2.5:{reading.pm25:3d}", 0, 24)
        
        # WiFi状态
        if self.wifi.is_connected():
            self.oled.text("WiFi:ON ", 0, 56)
        else:
            self.oled.text("WiFi:OFF", 0, 56)
        
        # 记录数
        self.oled.text(f"LOG:{len(self.temp_readings)}", 70, 56)
        
        self.oled.show()
    
    def run(self):
        """主循环"""
        print("\n主程序启动...")
        
        last_log_time = 0
        log_interval = 300  # 5分钟记录一次
        
        while True:
            try:
                # 检查WiFi
                self.wifi.check_connection()
                
                # 读取传感器
                reading = self.sensor_manager.read_all()
                
                if reading.valid:
                    # 更新显示
                    self.update_display(reading)
                    
                    # 记录数据
                    now = time.time()
                    if now - last_log_time > log_interval:
                        self.logger.log(reading)
                        
                        # 更新统计
                        if reading.temperature:
                            self.temp_readings.append(reading.temperature)
                        if reading.pm25:
                            self.pm_readings.append(reading.pm25)
                        
                        # 限制统计数组大小
                        if len(self.temp_readings) > 100:
                            self.temp_readings.pop(0)
                        if len(self.pm_readings) > 100:
                            self.pm_readings.pop(0)
                        
                        last_log_time = now
                        print(f"已记录数据 ({len(self.temp_readings)}条)")
                
                time.sleep(1)
            
            except Exception as e:
                print(f"错误: {e}")
                time.sleep(5)

# 主程序
if __name__ == "__main__":
    # 配置WiFi
    WIFI_SSID = "Your_WiFi_Name"
    WIFI_PASS = "Your_Password"
    
    # 创建并运行
    app = AirButler(WIFI_SSID, WIFI_PASS)
    app.run()
```

---

## 📝 今日作业 | Today's Assignment

### 基础作业 (必做)

1. **WiFi连接测试**  
   - 测试在不同位置的连接质量
   - 记录信号强度和连接成功率
   - 分析影响连接的因素

2. **完整系统演示**  
   拍摄视频展示:
   - 系统启动过程
   - 传感器数据读取
   - OLED显示更新
   - WiFi连接状态

3. **Week 1检查报告**  
   提交包含:
   - 已完成功能清单
   - 遇到的问题和解决方案
   - 系统当前状态
   - Week 2目标

### 进阶作业 (选做)

1. 实现: WiFi信号强度指示器(在OLED上显示)
2. 研究: 如何加密传输WiFi密码?
3. 思考: 如何在多个WiFi之间自动切换?

---

## 📚 参考资源 | References

- [ESP32 WiFi编程指南](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/network/esp_wifi.html)
- [MicroPython网络文档](https://docs.micropython.org/en/latest/esp32/quickref.html#networking)
- [TCP/IP协议详解](https://www.tcpipguide.com/)

---

## 🔮 明日预告 | Tomorrow's Preview

**Day 7: MQTT协议与数据上传**

- 学习MQTT发布/订阅模型
- 实现ESP32 MQTT客户端
- 上传传感器数据到云端
- 实现远程监控基础

**前置准备:**
- 确保WiFi连接稳定
- 了解什么是"消息代理"

---

## 🎯 第一周总结 | Week 1 Summary

### 已完成技能:
- [x] ESP32开发环境搭建
- [x] MicroPython基础编程
- [x] I2C/UART通信协议
- [x] 多传感器整合
- [x] OLED显示驱动
- [x] 本地数据记录
- [x] WiFi网络连接

### 下周目标:
- [ ] MQTT物联网协议
- [ ] 服务器端搭建
- [ ] 数据可视化仪表盘
- [ ] 完整IoT系统

---

*最后更新: 2026-05-05 | Last updated: 2026-05-05*
