# Day 9: 服务器端搭建(二) - 数据存储与可视化 | Server Setup Part 2 - Storage & Visualization

> **今日目标 (Today's Goals):**
> - 安装InfluxDB时序数据库
> - 实现数据持久化存储
> - 配置Grafana可视化仪表盘
> - 创建实时监测面板
>
> **产出 (Deliverable):** 完整的数据存储与可视化系统

---

## 🕒 时间安排 | Schedule

| 时间 | 活动类型 | 内容 |
|------|---------|------|
| 9:00-10:30 | 讲座 | 时序数据库原理与Grafana介绍 |
| 10:45-12:00 | 实践 | InfluxDB安装配置 |
| 13:30-15:00 | 实践 | Grafana安装与数据源配置 |
| 15:15-16:30 | 练习 | 仪表盘设计与创建 |
| 16:30-17:00 | 总结 | 作业布置与Q&A |

---

## 📖 上午: 时序数据库 | Morning: Time Series Database

### 为什么需要时序数据库? | Why Need TSDB?

**传统数据库 vs 时序数据库:**

| 特性 | MySQL/PostgreSQL | InfluxDB |
|------|-----------------|----------|
| **优化目标** | 事务处理 | 时间序列查询 |
| **写入性能** | 每秒数千条 | 每秒百万条 |
| **压缩率** | 低 | 高(90%+) |
| **聚合查询** | 慢 | 极快 |
| **数据保留** | 永久 | 自动过期 |

**真实应用场景:**
- IoT传感器数据(本项目)
- 股票价格走势
- 服务器监控指标
- 天气历史数据

> **Time Series Data:** Data points indexed by time, optimized for time-based queries

---

### 任务9.1: InfluxDB安装 (40分钟)

**Windows安装:**

1. **下载InfluxDB 2.x**
   ```bash
   # 访问官网下载
   https://portal.influxdata.com/downloads/
   # 选择Windows 64-bit
   ```

2. **运行安装**
   - 双击安装包
   - 默认安装路径
   - 安装后自动启动服务

3. **初始化设置**
   ```bash
   # 访问Web UI
   http://localhost:8086
   
   # 首次访问会要求设置:
   - 用户名: admin
   - 密码: (自行设置)
   - 组织名: airbutler
   - Bucket名: sensors
   ```

4. **验证安装**
   ```bash
   # PowerShell
   influx version
   
   # 或访问API
   curl -I http://localhost:8086/health
   ```

**InfluxDB核心概念:**

| 概念 | 说明 | 示例 |
|------|------|------|
| **Bucket** | 数据存储桶 | sensors |
| **Measurement** | 测量名称 | temperature |
| **Field** | 字段(必须有值) | value=25.5 |
| **Tag** | 标签(索引) | device="air001" |
| **Timestamp** | 时间戳 | 1678901234 |

---

### 任务9.2: 数据写入实现 (30分钟)

**安装Python客户端:**

```bash
pip install influxdb-client
```

**创建InfluxDB写入器:**

```python
# influx_writer.py
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime

class InfluxDBWriter:
    """InfluxDB数据写入器"""
    
    def __init__(self, url="http://localhost:8086", token="", org="airbutler"):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = "sensors"
        
        # 创建客户端
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYCHRONOUS)
    
    def write_sensor_data(self, data):
        """写入传感器数据"""
        try:
            # 创建数据点
            point = Point("sensor_reading") \
                .tag("device_id", data.get('device_id', 'unknown')) \
                .time(datetime.datetime.fromtimestamp(data.get('t', 0)))
            
            # 添加字段(必须)
            if data.get('T') is not None:
                point = point.field("temperature", float(data['T']))
            if data.get('H') is not None:
                point = point.field("humidity", float(data['H']))
            if data.get('P') is not None:
                point = point.field("pressure", float(data['P']))
            if data.get('PM25') is not None:
                point = point.field("pm25", int(data['PM25']))
            if data.get('PM10') is not None:
                point = point.field("pm10", int(data['PM10']))
            
            # 写入数据库
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            return True
        
        except Exception as e:
            print(f"InfluxDB写入错误: {e}")
            return False
    
    def query_data(self, measurement="temperature", time_range="-1h"):
        """查询数据"""
        query_api = self.client.query_api()
        
        query = f'''
            from(bucket: "{self.bucket}")
              |> range(start: {time_range})
              |> filter(fn: (r) => r._measurement == "{measurement}")
              |> filter(fn: (r) => r.device_id == "air001")
        '''
        
        result = query_api.query(org=self.org, query=query)
        return result
    
    def close(self):
        """关闭连接"""
        self.client.close()

# 使用示例
# 在MQTT订阅器的_handle_sensor_data中添加:
# influx_writer.write_sensor_data(data)
```

---

## 💻 下午: Grafana可视化 | Afternoon: Grafana Visualization

### 任务9.3: Grafana安装 (30分钟)

**Windows安装:**

1. **下载Grafana**
   ```bash
   # 访问官网下载
   https://grafana.com/grafana/download
   # 选择Windows版本
   ```

2. **解压并运行**
   ```bash
   # 解压到 C:\Program Files\Grafana
   cd C:\Program Files\Grafana\bin
   
   # 启动服务
   .\grafana-server.exe
   ```

3. **访问Web UI**
   ```
   http://localhost:3000
   
   # 默认登录
   用户名: admin
   密码: admin
   # 首次登录会要求修改密码
   ```

---

### 任务9.4: 配置数据源 (30分钟)

**添加InfluxDB数据源:**

1. **导航**
   - 设置 → Data sources → Add data source
   - 选择"InfluxDB"

2. **配置**
   ```
   Name: InfluxDB_AirButler
   Query Language: Flux
   URL: http://localhost:8086
   Org: airbutler
   Token: (你的InfluxDB Token)
   ```

3. **测试连接**
   - 点击"Save & Test"
   - 应显示"Data source is working"

---

### 任务9.5: 创建仪表盘 (60分钟)

**创建监测面板:**

1. **新建仪表盘**
   - Create → Dashboard
   - "Add visualization"

2. **温度面板**
   ```
   标题: 温度趋势 (°C)
   可视化: Time series
   
   Query:
   from(bucket: "sensors")
     |> range(start: v.timeRange)
     |> filter(fn: (r) => r._measurement == "sensor_reading")
     |> filter(fn: (r) => r._field == "temperature")
     |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
   
   右侧配置:
   - Unit: Temperature → Celsius (°C)
   - Min: 0
   - Max: 40
   - Alert: >30°C 警告
   ```

3. **PM2.5面板**
   ```
   标题: PM2.5 浓度 (μg/m³)
   可视化: Time series
   
   Query:
   from(bucket: "sensors")
     |> range(start: v.timeRange)
     |> filter(fn: (r) => r._measurement == "sensor_reading")
     |> filter(fn: (r) => r._field == "pm25")
     |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
   
   右侧配置:
   - Unit: Short
   - 阈值:
     * 绿色: 0-35
     * 黄色: 35-75
     * 红色: >75
   ```

4. **湿度面板**
   ```
   标题: 湿度 (%)
   可视化: Gauge
   
   Query:
   from(bucket: "sensors")
     |> range(start: v5m)
     |> filter(fn: (r) => r._measurement == "sensor_reading")
     |> filter(fn: (r) => r._field == "humidity")
     |> last()
   
   右侧配置:
   - Min: 0
   - Max: 100
   - 阈值:
     * 舒适: 40-60%
   ```

5. **多值统计面板**
   ```
   标题: 实时数据统计
   可视化: Stat
   
   Query: 添加多个查询
   - 温度最新值
   - 湿度最新值
   - PM2.5最新值
   ```

6. **保存仪表盘**
   - 右上角"Save dashboard"
   - 名称: "Air Butler Monitor"

---

## 🧪 练习: 高级可视化 | Practice: Advanced Visualization

### 任务9.6: 创建高级面板 (30分钟)

**1. 空气质量评分面板:**

```
可视化: Stat
计算AQI:
from(bucket: "sensors")
  |> range(start: v.timeRange)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "pm25")
  |> map(fn: (r) => ({
      r with
      _value: if r._value <= 35 then 50
              else if r._value <= 75 then 100
              else if r._value <= 115 then 150
              else 200
    }))
  |> last()
```

**2. 数据表格面板:**

```
可视化: Table
显示最近10条记录
```

**3. 告警配置:**

```
Alert规则:
- PM2.5 > 75 → 发送邮件
- 温度 > 30 → 发送通知
```

---

## 📝 今日作业 | Today's Assignment

### 基础作业 (必做)

1. **完整可视化系统**  
   - InfluxDB正常写入数据
   - Grafana显示所有传感器
   - 仪表盘包含至少4个面板

2. **数据验证**  
   - 对比ESP32显示和Grafana显示
   - 验证数据一致性
   - 测试历史数据查询

3. **回答问题**  
   - 时序数据库适合什么场景?
   - Grafana的优势是什么?
   - 什么是聚合窗口(aggregateWindow)?

### 进阶作业 (选做)

1. 实现: 告警通知(邮件/Webhook)
2. 研究: Grafana变量与模板化
3. 思考: 如何优化长期存储性能?

---

## 📚 参考资源 | References

- [InfluxDB文档](https://docs.influxdata.com/)
- [Grafana文档](https://grafana.com/docs/)
- [Flux查询语言](https://docs.influxdata.com/flux/v0.x/)

---

## 🔮 明日预告 | Tomorrow's Preview

**Day 10: 硬件整合与外壳设计**

- 电路整理与焊接入门
- 3D打印/激光切割外壳
- 传感器校准
- 产品化组装

**前置准备:**
- 准备焊接工具(如有)
- 设计外壳草图

---

*最后更新: 2026-05-05 | Last updated: 2026-05-05*
