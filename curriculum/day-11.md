# Day 11: 系统优化与测试 | System Optimization & Testing

> **今日目标 (Today's Goals):**
> - 优化代码结构和性能
> - 完善异常处理机制
> - 进行稳定性测试
> - 准备演示材料
>
> **产出 (Deliverable):** 经过优化的稳定系统和演示准备材料

---

## 🕒 时间安排 | Schedule

| 时间 | 活动类型 | 内容 |
|------|---------|------|
| 9:00-10:30 | 讲座 | 代码优化原则与方法 |
| 10:45-12:00 | 实践 | 代码重构与优化 |
| 13:30-15:00 | 实践 | 异常处理与测试 |
| 15:15-16:30 | 练习 | 演示材料准备 |
| 16:30-17:00 | 总结 | 作业布置与Q&A |

---

## 📖 上午: 代码优化 | Morning: Code Optimization

### 为什么需要优化? | Why Need Optimization?

**优化目标:**

| 维度 | 目标 | 影响 |
|------|------|------|
| **性能** | 更快的响应 | 更好的用户体验 |
| **稳定性** | 更少的崩溃 | 更可靠的系统 |
| **可维护性** | 更清晰的代码 | 更容易修改 |
| **功耗** | 更低的能耗 | 更长的续航 |

> **Good Code:** Not just working, but working efficiently and maintainably

---

### 任务11.1: 代码重构 (40分钟)

**重构原则:**

1. **模块化**
```python
# 差: 所有代码在main.py
# 好: 分模块组织

project/
├── main.py           # 主程序入口
├── config.py         # 配置文件
├── sensors.py        # 传感器模块
├── mqtt_handler.py   # MQTT处理
├── wifi_manager.py   # WiFi管理
├── display.py        # 显示模块
└── utils.py          # 工具函数
```

2. **单一职责**
```python
# 差: 一个函数做多件事
def process(data):
    validate(data)
    transform(data)
    save(data)
    upload(data)

# 好: 每个函数做一件事
def validate_data(data):
    pass

def transform_data(data):
    pass

def save_data(data):
    pass

def upload_data(data):
    pass
```

3. **配置分离**
```python
# config.py
class Config:
    # WiFi
    WIFI_SSID = "Your_WiFi"
    WIFI_PASS = "Your_Password"
    
    # MQTT
    MQTT_BROKER = "broker.emqx.io"
    MQTT_PORT = 1883
    MQTT_TOPIC = "home/airbutler/sensors"
    
    # 传感器
    TEMP_MIN = -40
    TEMP_MAX = 80
    
    # 系统参数
    UPDATE_INTERVAL = 60  # 秒
    UPLOAD_INTERVAL = 300  # 秒

# 使用
from config import Config
ssid = Config.WIFI_SSID
```

---

### 任务11.2: 性能优化 (30分钟)

**优化技巧:**

**1. 减少内存分配**
```python
# 差: 每次循环创建新字符串
for i in range(1000):
    message = "Temperature: " + str(i)

# 好: 使用格式化
for i in range(1000):
    message = f"Temperature: {i}"
```

**2. 缓存计算结果**
```python
# 差: 重复计算
def get_aqi(pm25):
    if pm25 <= 35:
        return (50 / 35) * pm25
    # ... 每次都计算

# 好: 使用查找表
AQI_TABLE = [
    (35, 50, 0, 50),
    (75, 50, 50, 100),
    # ...
]

def get_aqi(pm25):
    for limit, bp_lo, aqi_lo, aqi_hi in AQI_TABLE:
        if pm25 <= limit:
            return aqi_lo + (aqi_hi - aqi_lo) * (pm25 - bp_lo) / (limit - bp_lo)
```

**3. 异步处理(高级)**
```python
import uasyncio

async def main():
    # 并发执行
    await asyncio.gather(
        read_sensors(),
        update_display(),
        upload_data()
    )
```

---

## 💻 下午: 异常处理与测试 | Afternoon: Error Handling & Testing

### 任务11.3: 完善异常处理 (40分钟)

**异常处理策略:**

```python
# 分层异常处理

class SensorError(Exception):
    """传感器异常"""
    pass

class NetworkError(Exception):
    """网络异常"""
    pass

class SystemError(Exception):
    """系统异常"""
    pass

def safe_read_sensor(sensor_func, max_retries=3):
    """安全的传感器读取"""
    for attempt in range(max_retries):
        try:
            data = sensor_func()
            if data and validate(data):
                return data
        except OSError as e:
            print(f"读取失败 #{attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
    
    raise SensorError(f"传感器读取失败(重试{max_retries}次)")

def safe_upload(data, upload_func, max_retries=3):
    """安全的数据上传"""
    for attempt in range(max_retries):
        try:
            if upload_func(data):
                return True
        except Exception as e:
            print(f"上传失败 #{attempt + 1}: {e}")
    
    raise NetworkError(f"数据上传失败(重试{max_retries}次)")

# 使用
try:
    temp_data = safe_read_sensor(read_temperature)
    safe_upload(temp_data, mqtt_publish)
except SensorError as e:
    print(f"传感器错误: {e}")
    # 记录错误，继续运行
except NetworkError as e:
    print(f"网络错误: {e}")
    # 缓存数据，稍后重试
```

---

### 任务11.4: 稳定性测试 (40分钟)

**测试用例:**

**1. 网络断开测试**
```python
# 测试场景:
# - 断开WiFi
# - MQTT Broker关闭
# - 网络延迟

# 预期行为:
# - 自动重连
# - 数据缓存
# - 不影响其他功能
```

**2. 传感器故障测试**
```python
# 测试场景:
# - 断开传感器连接
# - 提供异常数据
# - 快速变化数据

# 预期行为:
# - 检测异常
# - 使用默认值
# - 记录错误
```

**3. 长时间运行测试**
```python
# 测试场景:
# - 连续运行24小时
# - 监控内存使用
# - 记录错误率

# 预期行为:
# - 无内存泄漏
# - 错误率 < 1%
# - 自动恢复
```

**测试代码:**
```python
def run_stability_test(duration_hours=24):
    """稳定性测试"""
    print(f"开始{duration_hours}小时稳定性测试")
    
    start_time = time.time()
    error_count = 0
    success_count = 0
    
    while (time.time() - start_time) < duration_hours * 3600:
        try:
            # 执行完整循环
            reading = sensor_manager.read_all()
            if reading.valid:
                mqtt_manager.publish(reading)
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            error_count += 1
            print(f"错误: {e}")
        
        time.sleep(60)
    
    # 生成报告
    total = success_count + error_count
    error_rate = error_count / total if total > 0 else 0
    
    print("\n=== 稳定性测试报告 ===")
    print(f"运行时间: {duration_hours}小时")
    print(f"总次数: {total}")
    print(f"成功: {success_count}")
    print(f"失败: {error_count}")
    print(f"错误率: {error_rate:.2%}")
```

---

## 🎨 练习: 演示准备 | Practice: Demo Preparation

### 任务11.5: 演示材料准备 (60分钟)

**1. 系统功能清单**

```
✅ 已实现功能:
- 传感器数据采集
  - 温度 (BME680)
  - 湿度 (BME680)
  - 气压 (BME680)
  - PM2.5 (PMS5003)
  - PM10 (PMS5003)

- 本地显示
  - OLED实时数据显示
  - 状态指示灯

- 数据上传
  - WiFi自动连接
  - MQTT数据发布
  - 自动重连机制

- 数据存储
  - 本地CSV日志
  - InfluxDB时序数据库
  - 数据保留策略

- 数据可视化
  - Grafana实时仪表盘
  - 历史趋势图
  - AQI计算

- 系统管理
  - 远程配置
  - 状态监控
  - 错误日志
```

**2. 演示脚本**

```
开场 (1分钟):
- 介绍项目背景
- 说明项目目标
- 演示流程预告

硬件展示 (2分钟):
- 展示原型机
- 介绍各组件
- 说明设计亮点

功能演示 (4分钟):
1. 本地监测
   - OLED显示
   - 传感器读数
2. 数据上传
   - WiFi连接状态
   - MQTT消息
3. 远程监控
   - Grafana仪表盘
   - 历史数据查询

技术细节 (2分钟):
- 系统架构
- 关键技术点
- 遇到的挑战

总结 (1分钟):
- 项目成果
- 未来改进
- 感谢
```

**3. 视觉材料**

```
准备:
- 系统架构图
- 数据流图
- 演示视频(可选)
- 产品照片
- 代码截图
```

---

## 📝 今日作业 | Today's Assignment

### 基础作业 (必做)

1. **代码优化**  
   - 完成至少3处优化
   - 提交对比报告

2. **稳定性测试**  
   - 运行1小时稳定性测试
   - 记录测试结果

3. **演示准备**  
   - 完成演示脚本
   - 准备演示环境

### 进阶作业 (选做)

1. 实现: 自动化测试框架
2. 研究: 性能分析工具
3. 思考: 如何实现OTA升级?

---

## 📚 参考资源 | References

- [Python性能优化](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [异常处理最佳实践](https://docs.python.org/3/tutorial/errors.html)
- [测试驱动开发](https://www.python.org/dev/peps/pep-0366/)

---

## 🔮 明日预告 | Tomorrow's Preview

**Day 12: 项目展示与总结**

- 项目演示
- 同伴互评
- 经验分享
- 未来展望

**前置准备:**
- 准备10分钟演示
- 整理项目文档

---

*最后更新: 2026-05-05 | Last updated: 2026-05-05*
