# Day 8: 服务器端搭建(一) | Server Setup Part 1

> **今日目标 (Today's Goals):**
> - 安装和配置Mosquitto MQTT Broker
> - 实现Python MQTT订阅程序
> - 实现数据接收和初步处理
> - 验证端到端数据流
>
> **产出 (Deliverable):** 能接收ESP32数据的本地MQTT服务器

---

## 🕒 时间安排 | Schedule

| 时间 | 活动类型 | 内容 |
|------|---------|------|
| 9:00-10:30 | 讲座 | MQTT Broker架构与安装 |
| 10:45-12:00 | 实践 | Mosquitto安装配置 |
| 13:30-15:00 | 实践 | Python订阅程序 |
| 15:15-16:30 | 练习 | 数据处理与验证 |
| 16:30-17:00 | 总结 | 作业布置与Q&A |

---

## 📖 上午: MQTT Broker | Morning: MQTT Broker

### 为什么需要本地Broker? | Why Need Local Broker?

**公共Broker的问题:**
- ❌ 不稳定(随时可能关闭)
- ❌ 延迟高(服务器在海外)
- ❌ 安全性差(任何人都能订阅)
- ❌ 无数据持久化

**本地Broker优势:**
- ✅ 完全控制
- ✅ 低延迟(局域网内)
- ✅ 可配置认证
- ✅ 可集成持久化

> **Local Broker Advantages:** Full control, low latency, configurable auth, persistence integration

---

### 任务8.1: Mosquitto安装 (40分钟)

**Windows安装:**

1. **下载安装包**
   ```bash
   # 访问官网下载
   https://mosquitto.org/download/
   # 选择Windows installer
   ```

2. **运行安装**
   - 双击安装包
   - 默认安装路径: `C:\Program Files\mosquitto`
   - 勾选"Service"选项(开机自启动)

3. **验证安装**
   ```bash
   # 打开PowerShell
   mosquitto --version
   # 应显示版本信息，如: mosquitto version 2.0.14
   ```

4. **启动服务**
   ```bash
   # Windows服务管理
   # 按 Win+R → services.msc → 找到"Mosquitto Broker"
   # 右键 → 启动
   ```

**配置文件修改:**

```bash
# 编辑配置文件
# 路径: C:\Program Files\mosquitto\mosquitto.conf

# 添加以下内容
# 允许匿名连接(测试用)
allow_anonymous true

# 监听端口
listener 1883

# 日志设置
log_dest file C:\Program Files\mosquitto\mosquitto.log
log_type all

# 持久化(可选)
persistence true
persistence_location C:\Program Files\mosquitto\data\
autosave_interval 1800
```

**重启服务:**
```bash
# PowerShell (管理员)
Restart-Service mosquitto
```

---

### 任务8.2: MQTT测试工具 (20分钟)

**安装MQTTX(跨平台MQTT客户端):**

1. **下载安装**
   - 官网: https://mqttx.app/
   - 支持Windows/Mac/Linux

2. **创建连接**
   - Host: localhost
   - Port: 1883
   - Client ID: test_client

3. **订阅测试**
   - 主题: home/airbutler/#
   - 点击"Subscribe"

4. **发布测试**
   - 主题: home/airbutler/test
   - 消息: {"test": "hello"}
   - 点击"Publish"

**预期结果:**
- 订阅端收到发布的消息
- 无连接错误

---

## 💻 下午: Python订阅程序 | Afternoon: Python Subscriber

### 任务8.3: 安装Python依赖 (15分钟)

```bash
# 创建虚拟环境(推荐)
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install paho-mqtt
pip install ujson
pip install python-dotenv
```

**requirements.txt:**
```
paho-mqtt==1.6.1
ujson==5.7.0
python-dotenv==1.0.0
influxdb-client==1.38.0
```

---

### 任务8.4: MQTT订阅程序 (60分钟)

**创建订阅器:**

```python
# subscriber.py
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
from collections import deque

class MQTTRSubscriber:
    """MQTT订阅器 - 接收传感器数据"""
    
    def __init__(self, broker="localhost", port=1883):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(client_id="server_subscriber")
        
        # 数据存储
        self.data_buffer = deque(maxlen=1000)
        self.device_status = {}
        
        # 回调设置
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
    
    def _on_connect(self, client, userdata, flags, rc):
        """连接回调"""
        if rc == 0:
            print("连接MQTT Broker成功!")
            
            # 订阅主题
            topics = [
                ("home/airbutler/sensors", 0),
                ("home/airbutler/+/status", 0)
            ]
            
            for topic, qos in topics:
                client.subscribe(topic, qos)
                print(f"已订阅: {topic}")
        else:
            print(f"连接失败，代码: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """消息接收回调"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            # 解析JSON
            data = json.loads(payload)
            
            # 添加时间戳
            data['received_at'] = datetime.now().isoformat()
            
            # 处理不同类型消息
            if 'sensors' in topic:
                self._handle_sensor_data(data)
            elif 'status' in topic:
                self._handle_status_message(topic, data)
        
        except json.JSONDecodeError:
            print(f"JSON解析错误: {payload}")
        except Exception as e:
            print(f"消息处理错误: {e}")
    
    def _handle_sensor_data(self, data):
        """处理传感器数据"""
        # 提取设备ID
        device_id = data.get('device_id', 'unknown')
        
        # 添加到缓冲区
        self.data_buffer.append({
            'device_id': device_id,
            'timestamp': data.get('t', time.time()),
            'temperature': data.get('T'),
            'humidity': data.get('H'),
            'pressure': data.get('P'),
            'pm25': data.get('PM25'),
            'pm10': data.get('PM10')
        })
        
        # 打印最新数据
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 收到传感器数据:")
        print(f"  设备: {device_id}")
        if data.get('T') is not None:
            print(f"  温度: {data['T']:.1f}°C")
        if data.get('H') is not None:
            print(f"  湿度: {data['H']:.1f}%")
        if data.get('PM25') is not None:
            print(f"  PM2.5: {data['PM25']} μg/m³")
        
        # TODO: 存储到InfluxDB
        # self._store_to_influxdb(data)
    
    def _handle_status_message(self, topic, data):
        """处理状态消息"""
        # 从主题提取设备ID
        device_id = topic.split('/')[2]
        status = data
        
        self.device_status[device_id] = {
            'status': status,
            'last_seen': datetime.now().isoformat()
        }
        
        print(f"\n设备 {device_id} 状态: {status}")
    
    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        if rc != 0:
            print("意外断开连接，尝试重连...")
    
    def start(self):
        """启动订阅器"""
        print(f"连接到 {self.broker}:{self.port}...")
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()
    
    def get_latest_data(self, count=10):
        """获取最新N条数据"""
        return list(self.data_buffer)[-count:]
    
    def get_device_status(self, device_id):
        """获取设备状态"""
        return self.device_status.get(device_id)

# 主程序
if __name__ == "__main__":
    subscriber = MQTTRSubscriber("localhost", 1883)
    
    try:
        subscriber.start()
    except KeyboardInterrupt:
        print("\n程序退出")
        subscriber.client.disconnect()
```

**运行测试:**

```bash
# 终端1: 启动订阅器
python subscriber.py

# 终端2: 使用ESP32发布数据
# 或使用MQTTX手动发布测试数据
```

---

### 任务8.5: 数据持久化 (30分钟)

**添加CSV日志:**

```python
# 在MQTTSubscriber类中添加方法

import csv
import os

def _init_csv_logger(self):
    """初始化CSV日志"""
    self.csv_file = f"data_{datetime.now().strftime('%Y%m%d')}.csv"
    
    # 写入表头
    if not os.path.exists(self.csv_file):
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'device_id',
                'temperature', 'humidity',
                'pressure', 'pm25', 'pm10'
            ])

def _log_to_csv(self, data):
    """记录数据到CSV"""
    try:
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                data.get('device_id', ''),
                data.get('T', ''),
                data.get('H', ''),
                data.get('P', ''),
                data.get('PM25', ''),
                data.get('PM10', '')
            ])
    except Exception as e:
        print(f"CSV写入错误: {e}")

# 在_handle_sensor_data中调用
def _handle_sensor_data(self, data):
    # ... 原有代码 ...
    self._log_to_csv(data)
```

---

## 🧪 练习: 端到端测试 | Practice: End-to-End Test

### 任务8.6: 完整数据流验证 (30分钟)

**测试步骤:**

1. **启动MQTT Broker**
   ```bash
   # 确认Mosquitto服务运行中
   sc query mosquitto
   ```

2. **启动订阅器**
   ```bash
   python subscriber.py
   ```

3. **启动ESP32上传**
   ```python
   # ESP32上运行Day 7的程序
   ```

4. **验证数据流**
   - ESP32 → WiFi → MQTT Broker → 订阅器
   - 检查CSV文件是否生成
   - 验证数据完整性

**常见问题排查:**

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 订阅器收不到数据 | 防火墙/Topic不匹配 | 检查防火墙，确认Topic |
| ESP32连接失败 | Broker地址错误 | 检查IP地址 |
| 数据格式错误 | JSON解析失败 | 检查消息格式 |

---

## 📝 今日作业 | Today's Assignment

### 基础作业 (必做)

1. **部署本地MQTT服务器**  
   - 成功安装Mosquitto
   - 配置允许局域网访问
   - 测试ESP32远程连接

2. **完整数据流测试**  
   - ESP32 → MQTT → 订阅器
   - 记录延迟时间
   - 验证数据完整性

3. **回答问题**  
   - 什么是MQTT Broker?
   - 订阅器和发布者的区别?
   - 为什么要通配符订阅(#+)?

### 进阶作业 (选做)

1. 实现: MQTT用户认证(用户名/密码)
2. 研究: MQTT Bridge(桥接)模式
3. 思考: 如何处理消息积压?

---

## 📚 参考资源 | References

- [Mosquitto官方文档](https://mosquitto.org/documentation/)
- [Paho-MQTT Python库](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)
- [MQTTX下载](https://mqttx.app/)

---

## 🔮 明日预告 | Tomorrow's Preview

**Day 9: 服务器端搭建(二) - 时序数据库与可视化**

- 安装InfluxDB时序数据库
- 实现数据持久化存储
- 配置Grafana数据可视化
- 创建实时监测仪表盘

**前置准备:**
- 确认有足够磁盘空间(>1GB)
- 准备Grafana管理员密码

---

*最后更新: 2026-05-05 | Last updated: 2026-05-05*
