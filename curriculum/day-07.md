# Day 7: MQTT协议与数据上传 | MQTT Protocol & Data Upload

> **今日目标 (Today's Goals):**
> - 理解MQTT发布/订阅模型
> - 实现ESP32 MQTT客户端
> - 上传传感器数据到MQTT Broker
> - 处理网络断开和重连
>
> **产出 (Deliverable):** 能通过MQTT上传数据的ESP32系统

---

## 🕒 时间安排 | Schedule

| 时间 | 活动类型 | 内容 |
|------|---------|------|
| 9:00-10:30 | 讲座 | MQTT协议原理与架构 |
| 10:45-12:00 | 实践 | MQTT库安装与配置 |
| 13:30-15:00 | 实践 | 数据上传实现 |
| 15:15-16:30 | 练习 | 错误处理与重连机制 |
| 16:30-17:00 | 总结 | 作业布置与Q&A |

---

## 📖 上午: MQTT协议原理 | Morning: MQTT Protocol

### 为什么要学MQTT? | Why Learn MQTT?

**MQTT vs HTTP:**

| 特性 | MQTT | HTTP |
|------|------|------|
| **设计目标** | 物联网设备通信 | 网页浏览 |
| **数据模式** | 发布/订阅 | 请求/响应 |
| **开销** | 极小(2字节头部) | 较大(数百字节) |
| **实时性** | 毫秒级 | 秒级 |
| **网络要求** | 低带宽/不稳定 | 高带宽/稳定 |
| **适用场景** | IoT传感器 | Web服务 |

**真实应用场景:**
- Facebook messenger(推送消息)
- 亚马逊Alexa(语音指令)
- 特斯拉车辆状态更新
- 智能家居设备通信

> **Why MQTT is IoT Standard:** Lightweight, real-time, works on unstable networks

---

### 任务7.1: MQTT核心概念 (40分钟)

**发布/订阅模型:**

```
发布者(Publisher)        Broker(代理)        订阅者(Subscriber)
    ESP32    →   home/airbutler/sensors  →    Grafana
    (数据)      (消息总线/主题)             (显示)
```

**关键术语:**

| 术语 | 说明 | 示例 |
|------|------|------|
| **Broker** | 消息代理服务器 | mosquitto, HiveMQ |
| **Client** | MQTT客户端(发布/订阅) | ESP32, 手机App |
| **Topic** | 消息主题(分层结构) | home/airbutler/sensors |
| **Publish** | 发布消息到主题 | ESP32上传数据 |
| **Subscribe** | 订阅主题 | 服务器接收数据 |
| **QoS** | 服务质量(0/1/2) | 消息送达保证 |

**Topic设计原则:**
```python
# 好的Topic设计
home/airbutler/sensors/temp     ← 温度
home/airbutler/sensors/humidity ← 湿度
home/airbutler/sensors/pm25     ← PM2.5

# 或使用单主题+JSON
home/airbutler/sensors          ← 所有数据(JSON格式)

# 避免过深的层次
home/airbutler/device01/sensor/bme680/reading/value
# ↑ 太复杂，不推荐
```

**QoS级别:**

| 级别 | 名称 | 说明 | 使用场景 |
|------|------|------|---------|
| **QoS 0** | 最多一次 | 发送后不管 | 频繁更新的传感器数据 |
| **QoS 1** | 至少一次 | 确认收到 | 重要报警信息 |
| **QoS 2** | 恰好一次 | 确保唯一 | 金融交易(本项目不用) |

**为什么QoS 0最适合传感器?**  
因为传感器数据更新频繁(如每秒一次),丢失一条数据影响很小。

> **Why QoS 0 for sensors?**  
> Frequent updates (1/sec), losing one reading has minimal impact

---

### 任务7.2: MQTT消息格式 (20分钟)

**JSON格式设计:**

```python
# 简洁的传感器消息
{
  "t": 1678901234,      # 时间戳
  "T": 25.5,            # 温度
  "H": 60.0,            # 湿度
  "P": 1013.25,         # 气压
  "PM25": 45            # PM2.5
}

# 完整的消息
{
  "timestamp": 1678901234,
  "device_id": "AIR_001",
  "readings": {
    "temperature": 25.5,
    "humidity": 60.0,
    "pressure": 1013.25,
    "pm25": 45,
    "pm10": 80
  },
  "status": "online",
  "battery": 85
}
```

**消息大小对比:**
- 简洁格式: ~50字节
- 完整格式: ~150字节
- HTTP请求: ~500字节

**为什么消息大小重要?**  
小的消息 = 更少的带宽消耗 = 更低的功耗 = 更稳定的连接。

---

## 💻 下午: MQTT实践 | Afternoon: MQTT Practice

### 任务7.3: 安装MQTT库 (20分钟)

**步骤:**

1. **安装umqtt库**
   ```python
   # 在Thonny中: 工具 → 管理包
   # 搜索并安装: "umqtt.simple"
   ```

2. **测试连接**
   ```python
   from umqtt.simple import MQTTClient
   import time

   # MQTT配置
   MQTT_BROKER = "broker.emqx.io"  # 公共测试Broker
   MQTT_PORT = 1883
   CLIENT_ID = "airbutler_" + str(time.ticks_ms())

   # 创建客户端
   client = MQTTClient(CLIENT_ID, MQTT_BROKER, MQTT_PORT)

   # 连接
   print(f"连接到 {MQTT_BROKER}...")
   client.connect()
   print("连接成功!")

   # 发布测试消息
   topic = b"home/airbutler/test"
   message = b"Hello MQTT from ESP32!"
   client.publish(topic, message)
   print(f"已发送消息到 {topic.decode()}")

   # 断开连接
   client.disconnect()
   ```

**预期结果:**
- 成功连接到Broker
- 消息发送成功
- 无连接错误

---

### 任务7.4: MQTT客户端封装 (60分钟)

**创建MQTT管理器:**

```python
from umqtt.simple import MQTTClient
import time
import ujson
import uos

class MQTTManager:
    """MQTT管理器 - 处理发布/订阅"""
    
    def __init__(self, broker, client_id, port=1883, user=None, passw=None):
        self.broker = broker
        self.client_id = client_id
        self.port = port
        self.user = user
        self.passw = passw
        
        # 连接状态
        self.connected = False
        self.last_connect = 0
        self.reconnect_interval = 10  # 10秒重连间隔
        
        # 消息回调
        self.message_callback = None
        
        # 创建客户端
        self._create_client()
    
    def _create_client(self):
        """创建MQTT客户端"""
        if self.user and self.passw:
            self.client = MQTTClient(
                self.client_id,
                self.broker,
                self.port,
                self.user,
                self.passw
            )
        else:
            self.client = MQTTClient(
                self.client_id,
                self.broker,
                self.port
            )
        
        # 设置回调
        self.client.set_callback(self._on_message)
        
        # 设置Last Will
        will_topic = f"home/airbutler/{self.client_id}/status"
        self.client.set_last_will(will_topic, b"offline", retain=True)
    
    def _on_message(self, topic, message):
        """消息接收回调"""
        if self.message_callback:
            self.message_callback(topic, message)
    
    def connect(self, timeout=10):
        """连接MQTT Broker"""
        print(f"连接MQTT: {self.broker}")
        
        try:
            self.client.connect()
            self.connected = True
            self.last_connect = time.time()
            
            # 发布上线消息
            status_topic = f"home/airbutler/{self.client_id}/status"
            self.client.publish(status_topic, b"online", retain=True)
            
            print("MQTT连接成功!")
            return True
        
        except Exception as e:
            print(f"MQTT连接失败: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.connected:
            # 发布离线消息
            status_topic = f"home/airbutler/{self.client_id}/status"
            self.client.publish(status_topic, b"offline", retain=True)
            
            self.client.disconnect()
            self.connected = False
            print("MQTT已断开")
    
    def check_connection(self):
        """检查连接，自动重连"""
        if not self.connected:
            now = time.time()
            if now - self.last_connect > self.reconnect_interval:
                self.connect()
        return self.connected
    
    def publish_sensor_data(self, reading):
        """发布传感器数据"""
        if not self.connected:
            return False
        
        try:
            # 构建消息
            payload = {
                "t": int(reading.timestamp),
                "T": reading.temperature,
                "H": reading.humidity,
                "P": reading.pressure,
                "PM25": reading.pm25,
                "PM10": reading.pm10
            }
            
            # 转JSON
            message = ujson.dumps(payload)
            
            # 发布(QoS 0)
            topic = b"home/airbutler/sensors"
            self.client.publish(topic, message, qos=0)
            
            return True
        
        except Exception as e:
            print(f"发布失败: {e}")
            self.connected = False
            return False
    
    def subscribe_commands(self, callback):
        """订阅命令主题"""
        try:
            topic = b"home/airbutler/commands"
            self.client.subscribe(topic)
            self.message_callback = callback
            print(f"已订阅: {topic.decode()}")
        except Exception as e:
            print(f"订阅失败: {e}")
    
    def check_messages(self):
        """检查是否有新消息"""
        try:
            self.client.check_msg()
        except:
            self.connected = False

# 使用示例
mqtt = MQTTManager("broker.emqx.io", "airbutler_001")
mqtt.connect()

# 发布数据
reading = SensorReading()
reading.temperature = 25.5
reading.pm25 = 45
mqtt.publish_sensor_data(reading)
```

---

## 🧪 练习: 完整上传系统 | Practice: Complete Upload System

### 任务7.5: 整合WiFi和MQTT (30分钟)

```python
class IoTMonitor:
    """IoT监测站 - 集成WiFi和MQTT"""
    
    def __init__(self, wifi_ssid, wifi_pass, mqtt_broker):
        # WiFi管理器
        self.wifi = WiFiManager(wifi_ssid, wifi_pass)
        
        # MQTT管理器
        client_id = f"airbutler_{uos.urandom(4).hex()}"
        self.mqtt = MQTTManager(mqtt_broker, client_id)
        
        # 传感器管理器
        self.sensors = SensorManager()
        
        # OLED显示
        self._init_display()
        
        # 状态
        self.last_upload = 0
        self.upload_interval = 60  # 60秒上传一次
    
    def _init_display(self):
        """初始化OLED"""
        i2c = I2C(0, scl=Pin(22), sda=Pin(21))
        self.oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    
    def update_display(self, reading):
        """更新显示"""
        self.oled.fill(0)
        self.oled.text("IoT Monitor", 30, 0)
        
        if reading.temperature:
            self.oled.text(f"T:{reading.temperature:5.1f}C", 0, 12)
        if reading.pm25:
            self.oled.text(f"PM:{reading.pm25:3d}", 64, 12)
        
        # 连接状态
        wifi_status = "W:ON" if self.wifi.is_connected() else "W:OFF"
        mqtt_status = "M:ON" if self.mqtt.connected else "M:OFF"
        self.oled.text(f"{wifi_status} {mqtt_status}", 0, 56)
        
        self.oled.show()
    
    def run(self):
        """主循环"""
        print("IoT监测站启动...")
        
        # 连接WiFi
        if not self.wifi.connect():
            print("WiFi连接失败!")
            return
        
        # 连接MQTT
        if not self.mqtt.connect():
            print("MQTT连接失败!")
            return
        
        while True:
            try:
                # 检查网络连接
                self.wifi.check_connection()
                self.mqtt.check_connection()
                
                # 读取传感器
                reading = self.sensors.read_all()
                
                if reading.valid:
                    # 更新显示
                    self.update_display(reading)
                    
                    # 定时上传
                    now = time.time()
                    if now - self.last_upload > self.upload_interval:
                        if self.mqtt.publish_sensor_data(reading):
                            print("数据已上传")
                            self.last_upload = now
                        else:
                            print("上传失败")
                
                time.sleep(1)
            
            except Exception as e:
                print(f"错误: {e}")
                time.sleep(5)

# 使用
app = IoTMonitor(
    wifi_ssid="Your_WiFi",
    wifi_pass="Your_Password",
    mqtt_broker="broker.emqx.io"
)
app.run()
```

---

## 📝 今日作业 | Today's Assignment

### 基础作业 (必做)

1. **MQTT连接测试**  
   - 测试不同Broker的连接速度
   - 测量消息往返时间(Ping)
   - 对比QoS 0和QoS 1的差异

2. **数据上传验证**  
   - 使用MQTT客户端工具(如MQTTX)订阅数据
   - 验证JSON格式正确性
   - 记录丢包率

3. **回答问题**  
   - MQTT和HTTP的主要区别?
   - 为什么需要Last Will?
   - 何时使用QoS 1而不是QoS 0?

### 进阶作业 (选做)

1. 实现: 命令接收功能(如远程重启)
2. 研究: MQTT over TLS(加密连接)
3. 思考: 如何降低消息发送频率以省电?

---

## 📚 参考资源 | References

- [MQTT协议规范](https://mqtt.org/mqtt-specification/)
- [umqtt库文档](https://github.com/micropython/micropython-lib/tree/master/umqtt.simple)
- [公共MQTT Broker列表](https://github.com/mqtt/mqtt.github.io/wiki/public_brokers)

---

## 🔮 明日预告 | Tomorrow's Preview

**Day 8: 服务器端搭建(一)**

- 安装Mosquitto MQTT Broker
- 搭建本地MQTT服务器
- 实现数据接收和存储
- Python MQTT订阅程序

**前置准备:**
- 确认电脑有Python 3.8+环境
- 准备好管理员权限(安装软件)

---

*最后更新: 2026-05-05 | Last updated: 2026-05-05*
