# Day 5: 数据整合与本地记录 | Data Integration & Local Logging

> **今日目标 (Today's Goals):**
> - 设计统一的传感器数据结构
> - 实现本地文件系统存储
> - 计算统计数据(最大/最小/平均)
> - 生成基础数据报告
>
> **产出 (Deliverable):** 能记录并分析环境数据的完整系统

---

## 🕒 时间安排 | Schedule

| 时间 | 活动类型 | 内容 |
|------|---------|------|
| 9:00-10:30 | 讲座 | 数据结构设计与文件系统 |
| 10:45-12:00 | 实践 | 传感器数据整合 |
| 13:30-15:00 | 实践 | 本地数据记录 |
| 15:15-16:30 | 练习 | 统计分析与报告 |
| 16:30-17:00 | 总结 | 作业布置与Q&A |

---

## 📖 上午: 数据结构设计 | Morning: Data Structure Design

### 为什么要统一数据结构? | Why Unified Data Structure?

**真实场景问题:**
```python
# 不同传感器的数据格式不一致
bme_data = {"temp": 25.5, "hum": 60}
pm_data = {"PM2.5": 45, "PM10": 80}
oled_data = "T:25C H:60%"

# 导致的问题:
# 1. 难以合并处理
# 2. 容易出错(键名不一致)
# 3. 难以扩展新传感器
```

**解决方案: 统一数据模型**
```python
# 统一格式
sensor_reading = {
    "timestamp": 1678901234,
    "temperature": 25.5,
    "humidity": 60.0,
    "pressure": 1013.25,
    "pm25": 45,
    "pm10": 80,
    "valid": True
}
```

> **Real-world Scenario Problem:** Different sensors have different data formats, causing integration issues.  
> **Solution:** Unified data model for consistent processing

---

### 任务5.1: 数据结构设计 (30分钟)

**统一数据模型:**

```python
class SensorReading:
    """传感器读数统一格式"""
    
    def __init__(self, timestamp=None):
        self.timestamp = timestamp if timestamp else time.time()
        self.temperature = None
        self.humidity = None
        self.pressure = None
        self.gas = None
        self.pm25 = None
        self.pm10 = None
        self.valid = False
        self.error = None
    
    def to_dict(self):
        """转换为字典"""
        return {
            "timestamp": self.timestamp,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "pm25": self.pm25,
            "pm10": self.pm10,
            "valid": self.valid
        }
    
    def to_json(self):
        """转换为JSON字符串"""
        import ujson
        return ujson.dumps(self.to_dict())
    
    def is_valid(self):
        """检查数据是否有效"""
        # 至少有一个有效读数
        return any([
            self.temperature is not None,
            self.humidity is not None,
            self.pm25 is not None
        ])

# 使用示例
reading = SensorReading()
reading.temperature = 25.5
reading.pm25 = 45
reading.valid = True

print(reading.to_json())
# {"timestamp":1678901234,"temperature":25.5,"pm25":45,"valid":true}
```

**数据验证:**
```python
def validate_reading(reading):
    """验证传感器读数合理性"""
    errors = []
    
    # 温度范围检查
    if reading.temperature:
        if not (-40 <= reading.temperature <= 80):
            errors.append("温度超出范围")
    
    # 湿度范围检查
    if reading.humidity:
        if not (0 <= reading.humidity <= 100):
            errors.append("湿度超出范围")
    
    # PM2.5范围检查
    if reading.pm25:
        if not (0 <= reading.pm25 <= 500):
            errors.append("PM2.5超出范围")
    
    return len(errors) == 0, errors
```

---

### 任务5.2: 传感器整合类 (60分钟)

**创建传感器管理器:**

```python
from machine import Pin, I2C, UART
import bme680
import time

class SensorManager:
    """传感器管理器 - 整合所有传感器"""
    
    def __init__(self):
        # 初始化I2C
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21))
        
        # 初始化BME680
        try:
            self.bme = bme680.BME680_I2C(i2c=self.i2c)
            self.bme_valid = True
        except:
            self.bme_valid = False
            print("BME680初始化失败")
        
        # 初始化UART(PMS5003)
        self.uart = UART(2, baudrate=9600, rx=16, tx=17)
        self.pm_buffer = bytearray(32)
    
    def read_bme(self):
        """读取BME680数据"""
        if not self.bme_valid:
            return None, None, None
        
        try:
            self.bme.get_sensor_data()
            temp = self.bme.data.temperature
            hum = self.bme.data.humidity
            pres = self.bme.data.pressure
            gas = self.bme.data.gas_resistance
            return temp, hum, pres
        except:
            return None, None, None
    
    def read_pm(self):
        """读取PMS5003数据"""
        if self.uart.any() >= 32:
            self.uart.readinto(self.pm_buffer, 32)
            
            # 验证帧头
            if self.pm_buffer[0] == 0x42 and self.pm_buffer[1] == 0x4D:
                # 计算校验和
                checksum = sum(self.pm_buffer[0:30]) & 0xFFFF
                received = (self.pm_buffer[30] << 8) | self.pm_buffer[31]
                
                if checksum == received:
                    pm25 = (self.pm_buffer[6] << 8) | self.pm_buffer[7]
                    pm10 = (self.pm_buffer[8] << 8) | self.pm_buffer[9]
                    return pm25, pm10
        
        return None, None
    
    def read_all(self):
        """读取所有传感器"""
        reading = SensorReading()
        
        # 读取BME680
        temp, hum, pres = self.read_bme()
        if temp is not None:
            reading.temperature = temp
            reading.humidity = hum
            reading.pressure = pres
        
        # 读取PMS5003
        pm25, pm10 = self.read_pm()
        if pm25 is not None:
            reading.pm25 = pm25
            reading.pm10 = pm10
        
        # 验证数据
        reading.valid = reading.is_valid()
        
        return reading

# 使用示例
manager = SensorManager()
reading = manager.read_all()
print(reading.to_json())
```

---

## 💻 下午: 本地数据记录 | Afternoon: Local Data Logging

### 任务5.3: ESP32文件系统 (30分钟)

**为什么要记录到文件?**
- 网络断开时数据不丢失
- 可以分析历史趋势
- 调试时有完整日志

**文件系统基础:**
```python
import uos
import time

# 检查文件系统
print("文件系统:", uos.uname())  # 查看存储信息
print("文件列表:", uos.listdir())  # 列出文件

# 创建目录
try:
    uos.mkdir("/data")
except:
    pass  # 目录已存在

# 写入文件
with open("/data/test.txt", "w") as f:
    f.write("Hello ESP32!\n")
    f.write(f"Time: {time.time()}\n")

# 读取文件
with open("/data/test.txt", "r") as f:
    content = f.read()
    print(content)

# 追加数据
with open("/data/test.txt", "a") as f:
    f.write("New line\n")
```

**⚠️ 重要提示:**
- ESP32文件系统容量有限(通常几MB)
- 频繁写入会缩短Flash寿命
- 需要定期清理旧文件

---

### 任务5.4: 数据记录器实现 (60分钟)

**创建数据记录器:**

```python
import uos
import ujson
import time

class DataLogger:
    """数据记录器 - 管理本地文件存储"""
    
    def __init__(self, base_dir="/data"):
        self.base_dir = base_dir
        self.current_file = None
        self.buffer = []
        self.buffer_size = 10  # 每10条写入一次
        
        # 创建目录
        try:
            uos.mkdir(base_dir)
        except:
            pass
        
        # 生成今日文件名
        self._open_today_file()
    
    def _get_today_filename(self):
        """生成今日文件名"""
        timestamp = time.time()
        date_str = time.gmtime(timestamp)
        filename = f"sensor_{date_str[0]}{date_str[1]:02d}{date_str[2]:02d}.log"
        return f"{self.base_dir}/{filename}"
    
    def _open_today_file(self):
        """打开今日文件"""
        filename = self._get_today_filename()
        self.current_file = filename
        
        # 检查文件是否存在
        try:
            with open(filename, "r") as f:
                pass  # 文件存在
        except:
            # 创建新文件，写入头
            with open(filename, "w") as f:
                f.write("# Air Butler Sensor Data Log\n")
                f.write(f"# Started: {time.time()}\n\n")
    
    def log(self, reading):
        """记录一条数据"""
        # 添加到缓冲区
        self.buffer.append(reading.to_json())
        
        # 缓冲区满时写入
        if len(self.buffer) >= self.buffer_size:
            self._flush()
    
    def _flush(self):
        """将缓冲区写入文件"""
        if not self.buffer:
            return
        
        try:
            with open(self.current_file, "a") as f:
                for entry in self.buffer:
                    f.write(entry + "\n")
            
            print(f"已写入 {len(self.buffer)} 条记录")
            self.buffer.clear()
        
        except Exception as e:
            print(f"写入失败: {e}")
    
    def get_stats(self):
        """获取文件统计信息"""
        try:
            with open(self.current_file, "r") as f:
                lines = f.readlines()
            
            # 过滤掉注释行
            data_lines = [l for l in lines if not l.startswith("#")]
            
            return {
                "file": self.current_file,
                "total_lines": len(lines),
                "data_records": len(data_lines)
            }
        except:
            return {"error": "无法读取文件"}
    
    def close(self):
        """关闭记录器"""
        self._flush()

# 使用示例
logger = DataLogger()

# 模拟数据记录
for i in range(15):
    reading = SensorReading()
    reading.temperature = 25.0 + i * 0.1
    reading.pm25 = 40 + i
    reading.valid = True
    
    logger.log(reading)
    time.sleep(0.1)

logger.close()

# 查看统计
stats = logger.get_stats()
print(stats)
```

---

## 📊 练习: 数据分析 | Practice: Data Analysis

### 任务5.5: 统计分析 (30分钟)

**实现统计分析器:**

```python
class StatisticsAnalyzer:
    """统计分析器"""
    
    def __init__(self, max_records=100):
        self.records = []
        self.max_records = max_records
    
    def add_record(self, reading):
        """添加记录"""
        self.records.append(reading)
        
        # 限制记录数
        if len(self.records) > self.max_records:
            self.records.pop(0)
    
    def calculate_stats(self, field):
        """计算指定字段的统计信息"""
        values = []
        
        for record in self.records:
            value = getattr(record, field, None)
            if value is not None:
                values.append(value)
        
        if not values:
            return None
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1]
        }
    
    def generate_report(self):
        """生成统计报告"""
        report = {
            "timestamp": time.time(),
            "temperature": self.calculate_stats("temperature"),
            "humidity": self.calculate_stats("humidity"),
            "pm25": self.calculate_stats("pm25")
        }
        
        return report

# 使用示例
analyzer = StatisticsAnalyzer()

# 添加测试数据
for i in range(20):
    reading = SensorReading()
    reading.temperature = 25.0 + (i % 5)
    reading.humidity = 60.0 + (i % 3)
    reading.pm25 = 40 + i
    analyzer.add_record(reading)

# 生成报告
report = analyzer.generate_report()

# 打印报告
print("\n=== 统计报告 ===")
for field, stats in report.items():
    if isinstance(stats, dict) and stats:
        print(f"\n{field.upper()}:")
        print(f"  最小值: {stats['min']:.1f}")
        print(f"  最大值: {stats['max']:.1f}")
        print(f"  平均值: {stats['avg']:.1f}")
        print(f"  最新值: {stats['latest']:.1f}")
        print(f"  样本数: {stats['count']}")
```

---

## 📝 今日作业 | Today's Assignment

### 基础作业 (必做)

1. **完整记录系统**  
   整合SensorManager和DataLogger，实现:
   - 每5分钟记录一次数据
   - 自动创建每日文件
   - 显示记录统计

2. **数据分析**  
   使用StatisticsAnalyzer分析1小时数据，找出:
   - 温度变化趋势
   - PM2.5峰值时刻
   - 异常数据点

3. **回答问题**  
   - 为什么需要缓冲区?
   - 如何处理文件写入失败?
   - 统计数据有什么实际用途?

### 进阶作业 (选做)

1. 实现: 数据压缩存储(减少文件大小)
2. 研究: ESP32 Flash寿命与写入次数的关系
3. 思考: 如何设计更高效的数据格式?

---

## 📚 参考资源 | References

- [MicroPython文件系统文档](https://docs.micropython.org/en/latest/library/uos.html)
- [uJSON库文档](https://docs.micropython.org/en/latest/library/ujson.html)
- [数据结构设计模式](https://refactoring.guru/design-patterns/catalog)

---

## 🔮 明日预告 | Tomorrow's Preview

**Day 6: WiFi连接与网络基础**

- 学习WiFi连接原理
- 实现ESP32联网功能
- 测试网络通信
- 准备MQTT基础

**前置准备:**
- 确认ESP32的WiFi天线连接
- 准备好可连接的WiFi网络信息

---

*最后更新: 2026-05-05 | Last updated: 2026-05-05*
