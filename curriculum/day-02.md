# Day 2: MicroPython基础与I2C通信 | MicroPython Basics & I2C Communication

> **今日目标 (Today's Goals):**
> - 掌握MicroPython基本语法和数据结构
> - 理解I2C通信协议原理
> - 学会使用BME680传感器库
> - 成功读取温湿度、气压和气体数据
>
> **产出 (Deliverable):** 能实时读取并显示环境数据的ESP32程序

---

## 🕒 时间安排 | Schedule

| 时间 | 活动类型 | 内容 |
|------|---------|------|
| 9:00-10:30 | 讲座 | MicroPython语法复习与I2C协议 |
| 10:45-12:00 | 实践 | BME680传感器连接与驱动安装 |
| 13:30-15:00 | 实践 | 传感器数据读取与处理 |
| 15:15-16:30 | 练习 | 数据异常处理与校准 |
| 16:30-17:00 | 总结 | 作业布置与Q&A |

---

## 📖 上午: MicroPython与I2C协议 | Morning: MicroPython & I2C Protocol

### 为什么要学I2C? | Why Learn I2C?

**真实应用场景:**
- 智能手表读取多个传感器(心率、加速度、陀螺仪)
- 无人机获取姿态、GPS、气压数据
- 工业控制板读取多个温度传感器

**I2C的优势:**
- 只需2根线(SDA数据线 + SCL时钟线)
- 可挂载127个设备
- 广泛支持(几乎所有传感器都有I2C接口)

> **Real-world Applications:**
> - Smartwatches reading multiple sensors (heart rate, accelerometer, gyroscope)
> - Drones getting attitude, GPS, barometric data
> - Industrial control boards reading multiple temperature sensors
>
> **I2C Advantages:**
> - Only 2 wires needed (SDA data + SCL clock)
> - Up to 127 devices on one bus
> - Wide support (almost all sensors have I2C interface)

---

### 任务2.1: MicroPython语法速成 (40分钟)

**核心概念回顾:**

#### 1. 变量与数据类型
```python
# 数值型 - 用于传感器读数
temperature = 25.5      # float
humidity = 60           # int
pressure = 101325       # int

# 字符串 - 用于设备标识
device_id = "AIR_001"
status = "online"

# 布尔型 - 用于状态判断
is_heating = True
is_cooling = False
```

#### 2. 列表与字典
```python
# 列表 - 存储时间序列数据
readings = [25.1, 25.3, 25.2, 25.4]
print(readings[0])      # 第一个元素
print(len(readings))    # 长度
print(sum(readings))    # 求和

# 字典 - 结构化传感器数据
sensor_data = {
    "temp": 25.5,
    "hum": 60,
    "pres": 1013.25
}
print(sensor_data["temp"])  # 访问值
```

#### 3. 函数定义
```python
def celsius_to_fahrenheit(c):
    """摄氏度转华氏度"""
    return c * 9/5 + 32

def format_sensor_data(temp, hum, pres):
    """格式化传感器数据"""
    return f"T:{temp}C H:{hum}% P:{pres}hPa"

# 使用函数
f_temp = celsius_to_fahrenheit(25)
print(f_temp)  # 77.0
```

#### 4. 错误处理
```python
try:
    # 可能出错的代码
    value = sensor.read()
except Exception as e:
    # 出错时的处理
    print(f"Error: {e}")
    value = None
```

**练习题:**
```python
# 1. 创建一个存储温度的列表
temps = [22.0, 23.5, 24.0]

# 2. 计算平均温度
avg_temp = sum(temps) / len(temps)
print(f"平均温度: {avg_temp}")

# 3. 创建函数检查温度是否过高
def is_high_temp(temp, threshold=30):
    return temp > threshold

# 4. 测试函数
print(is_high_temp(32))  # True
print(is_high_temp(25))  # False
```

---

### 任务2.2: I2C协议原理 (30分钟)

**I2C基础:**

```
主设备(ESP32) ←───SDA(数据线)───→ 从设备1(BME680)
    │                              ↓
    └───SCL(时钟线)───→ 从设备2(OLED)
```

**关键概念:**

| 概念 | 说明 |
|------|------|
| **主设备** | 控制通信的设备(ESP32) |
| **从设备** | 响应主设备的设备(传感器) |
| **地址** | 每个从设备的唯一ID(如0x76) |
| **时钟** | 主设备提供时序信号 |
| **起始/停止** | 标记通信开始和结束 |

**通信过程:**
1. 主设备发送起始信号
2. 主设备发送从设备地址 + 读/写位
3. 从设备应答(ACK)
4. 数据传输
5. 主设备发送停止信号

**为什么不需要CS(片选)信号?**  
因为I2C有地址机制，每个设备只响应自己的地址。

> **Why no CS (chip select) signal?**  
> Because I2C has addressing, each device only responds to its own address.

---

## 💻 下午: BME680传感器实践 | Afternoon: BME680 Sensor Practice

### 任务2.3: BME680硬件连接 (30分钟)

**BME680引脚说明:**

| 引脚 | 功能 | 连接到ESP32 |
|------|------|-------------|
| VIN | 电源(3.3V) | 3V3 |
| GND | 地 | GND |
| SCL | 时钟线 | GPIO22 (I2C SCL) |
| SDA | 数据线 | GPIO21 (I2C SDA) |

**接线步骤:**

1. **准备面包板**
   - 将ESP32插入面包板
   - 确保USB接口朝外

2. **连接电源**
   ```
   ESP32 3V3 ────────── BME680 VIN
   ESP32 GND ────────── BME680 GND
   ```

3. **连接I2C信号**
   ```
   ESP32 GPIO22 ─────── BME680 SCL
   ESP32 GPIO21 ─────── BME680 SDA
   ```

4. **检查连接**
   - 用万用表测试连通性
   - 确认没有短路(3V3和GND不应导通)

**预期结果:**
- 所有引脚正确连接
- 无短路或接触不良

**常见问题:**
- Q: 接反了会怎样?  
  A: 可能烧毁传感器，务必确认VIN/GND
- Q: 为什么是GPIO21/22?  
  A: ESP32的默认I2C引脚

---

### 任务2.4: 扫描I2C设备 (20分钟)

**步骤:**

1. **编写I2C扫描程序**
   ```python
   from machine import Pin, I2C

   # 初始化I2C (ESP32默认引脚: SDA=21, SCL=22)
   i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

   # 扫描I2C总线上的设备
   devices = i2c.scan()

   if devices:
       print(f"找到 {len(devices)} 个I2C设备:")
       for device in devices:
           print(f"  地址: 0x{device:02X}")
   else:
       print("未找到I2C设备!")
       print("请检查:")
       print("  1. 接线是否正确")
       print("  2. 传感器是否供电")
       print("  3. I2C引脚是否正确")
   ```

2. **运行扫描**
   - 上传到ESP32
   - 查看Shell输出
   - 应该看到: `地址: 0x76` 或 `0x77`

**预期结果:**
- 找到BME680的I2C地址
- 理解I2C设备扫描原理

**常见问题:**
- Q: 找不到设备?  
  A: 检查接线，确认上拉电阻存在(通常集成在传感器模块)
- Q: 地址是0x76还是0x77?  
  A: 取决于传感器模块，两个都正常

---

### 任务2.5: BME680传感器读取 (60分钟)

**步骤:**

1. **安装BME680库**
   ```python
   # 在Thonny中: 工具 → 管理包
   # 搜索并安装: "bme680-micropython"
   ```

2. **编写读取程序**
   ```python
   from machine import Pin, I2C
   import bme680
   import time

   # 初始化I2C
   i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

   # 创建传感器对象
   sensor = bme680.BME680_I2C(i2c=i2c)

   # 设置传感器参数
   sensor.set_humidity_oversample(bme680.OS_2X)
   sensor.set_pressure_oversample(bme680.OS_4X)
   sensor.set_temperature_oversample(bme680.OS_8X)
   sensor.set_filter(bme680.FILTER_SIZE_3)

   # 主循环
   while True:
       try:
           # 读取传感器数据
           sensor.get_sensor_data()
           
           # 获取读数
           temp = sensor.data.temperature
           hum = sensor.data.humidity
           pres = sensor.data.pressure
           gas = sensor.data.gas_resistance
           
           # 打印结果
           print(f"温度: {temp:.1f}°C")
           print(f"湿度: {hum:.1f}%")
           print(f"气压: {pres:.1f} hPa")
           print(f"气体: {gas:.0f} Ω")
           print("-" * 30)
           
       except OSError as e:
           print(f"传感器读取错误: {e}")
       
       time.sleep(2)
   ```

3. **校准传感器**
   ```python
   # 海平面气压校准(根据当地海拔调整)
   SEA_LEVEL_PRESSURE = 1013.25  # hPa

   # 计算海拔(近似)
   def calculate_altitude(pressure, sea_level=SEA_LEVEL_PRESSURE):
       return 44330 * (1 - (pressure / sea_level) ** 0.1903)

   # 使用
   altitude = calculate_altitude(pres)
   print(f"海拔: {altitude:.1f}米")
   ```

**预期结果:**
- 每2秒显示一次环境数据
- 温度在20-30°C范围
- 湿度在30-70%范围
- 气压在980-1040 hPa范围

**常见问题:**
- Q: 读数异常?  
  A: 传感器需要预热，运行5分钟后稳定
- Q: 气体电阻总是0?  
  A: 需要等待传感器加热(约30秒)

---

## 🧪 练习: 数据异常处理 | Practice: Error Handling

### 任务2.6: 健壮的传感器读取 (30分钟)

**问题:** 传感器偶尔会读失败，如何让程序不崩溃?

**解决方案:**

```python
from machine import Pin, I2C
import bme680
import time

class BME680Sensor:
    def __init__(self, i2c):
        self.sensor = bme680.BME680_I2C(i2c=i2c)
        self.error_count = 0
        self.max_errors = 5
        
    def read(self):
        """读取传感器数据，带错误处理"""
        try:
            self.sensor.get_sensor_data()
            data = {
                "temp": self.sensor.data.temperature,
                "hum": self.sensor.data.humidity,
                "pres": self.sensor.data.pressure,
                "gas": self.sensor.data.gas_resistance,
                "valid": True
            }
            self.error_count = 0  # 重置错误计数
            return data
            
        except Exception as e:
            self.error_count += 1
            print(f"读取错误 #{self.error_count}: {e}")
            
            if self.error_count >= self.max_errors:
                print("传感器故障!请检查连接")
                return {"valid": False}
            
            return {"valid": False}

# 使用示例
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
bme = BME680Sensor(i2c)

while True:
    data = bme.read()
    if data["valid"]:
        print(f"温度: {data['temp']:.1f}°C")
    else:
        print("读数无效，重试...")
    
    time.sleep(2)
```

---

## 📝 今日作业 | Today's Assignment

### 基础作业 (必做)

1. **完成数据记录程序**  
   修改读取程序，记录最近10次温度读数并计算平均值

2. **回答问题**  
   - I2C协议需要几根线?分别是什么?
   - BME680的I2C地址是多少?
   - 什么是"从设备地址"?

3. **提交实验报告**  
   包含:
   - 接线照片
   - 串口输出截图
   - 遇到的问题及解决方法

### 进阶作业 (选做)

1. 研究: BME680的气体传感器如何工作?
2. 实现: 根据温湿度计算体感温度(热指数)
3. 思考: 如何减少传感器功耗?(提示: 间歇读取)

---

## 📚 参考资源 | References

- [BME680数据手册](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme680-ds001.pdf)
- [MicroPython I2C文档](https://docs.micropython.org/en/latest/esp32/quickref.html#i2c-bus)
- [I2C协议详解](https://www.i2c-bus.org/i2c-primer/)

---

## 🔮 明日预告 | Tomorrow's Preview

**Day 3: UART通信与PM2.5传感器**

- 学习UART串行通信协议
- 连接PMS5003 PM2.5传感器
- 解析传感器数据帧
- 计算空气质量指数(AQI)

**前置准备:**
- 复习Python字符串操作
- 了解十六进制数的基本概念

---

*最后更新: 2026-05-05 | Last updated: 2026-05-05*
