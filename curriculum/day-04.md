# Day 4: OLED显示屏驱动 | OLED Display Driver

> **今日目标 (Today's Goals):**
> - 理解OLED显示原理和SSD1306驱动
> - 学会在OLED上显示文字和图形
> - 创建实时环境监测界面
> - 优化数据布局和可读性
>
> **产出 (Deliverable):** 能显示环境数据的OLED界面

---

## 🕒 时间安排 | Schedule

| 时间 | 活动类型 | 内容 |
|------|---------|------|
| 9:00-10:30 | 讲座 | 显示屏原理与SSD1306驱动 |
| 10:45-12:00 | 实践 | OLED硬件连接与测试 |
| 13:30-15:00 | 实践 | 文字与图形显示 |
| 15:15-16:30 | 练习 | 界面设计与优化 |
| 16:30-17:00 | 总结 | 作业布置与Q&A |

---

## 📖 上午: OLED显示原理 | Morning: OLED Display Principles

### 为什么要学习OLED? | Why Learn OLED?

**真实应用场景:**
- 智能手表主屏幕
- 无人机遥控器显示
- 医疗监护仪界面
- 工业设备状态面板

**OLED优势:**
- 自发光(无需背光)
- 高对比度(纯黑显示)
- 低功耗(关键数据显示时)
- 快速响应(适合动画)

> **Real-world Applications:**
> - Smartwatch main display
> - Drone controller display
> - Medical monitor interface
> - Industrial equipment status panel
>
> **OLED Advantages:** Self-emitting, high contrast, low power, fast response

---

### 任务4.1: SSD1306驱动基础 (40分钟)

**硬件规格:**

| 参数 | 说明 |
|------|------|
| **分辨率** | 128×64像素 |
| **接口** | I2C (默认地址0x3C) |
| **颜色** | 单色(蓝/白/黄) |
| **视野角度** | >160° |
| **电压** | 3.3V-5V |

**显示缓冲原理:**
```
内存缓冲区 (1024字节) → SSD1306驱动 → OLED屏幕
每页8行，共8页:
┌────────────────┐
│ Page 0 (行0-7) │ ← 128字节
│ Page 1 (行8-15)│ ← 128字节
│ ...            │
│ Page 7 (行56-63)│ ← 128字节
└────────────────┘
```

**为什么需要页(Page)概念?**  
因为屏幕按页刷新，理解页结构可以优化布局。

> **Why need Page concept?**  
> Because the screen refreshes by pages, understanding page structure optimizes layout.

---

### 任务4.2: 文字显示原理 (20分钟)

**字符编码:**
```python
# ASCII编码
'A' = 65 (十进制) = 0x41 (十六进制)

# 字体点阵(5×7像素)
  ###
 #   #
 #####
 #   #
 #   #
```

**文字渲染流程:**
1. 将字符编码转换为字体索引
2. 从字体表读取点阵数据
3. 将点阵写入显示缓冲区
4. 刷新屏幕

---

## 💻 下午: OLED实践 | Afternoon: OLED Practice

### 任务4.3: OLED硬件连接 (20分钟)

**SSD1306引脚说明:**

| 引脚 | 功能 | 连接到ESP32 |
|------|------|-------------|
| VCC | 电源(3.3V-5V) | 3V3 |
| GND | 地 | GND |
| SCL | 时钟线 | GPIO22 |
| SDA | 数据线 | GPIO21 |

**⚠️ I2C总线共享:**
- BME680和OLED共享I2C总线
- 两者地址不同(0x76/0x77 vs 0x3C)
- 可以同时连接

**接线图:**
```
ESP32                    BME680          OLED
────────────────────────────────────────────
3V3  ────┬───────── VIN              VCC
        │
GND  ────┼───────── GND              GND
        │
GPIO22 ──┼───────── SCL              SCL
        │
GPIO21 ──┴───────── SDA              SDA
```

**预期结果:**
- OLED屏幕亮起(全白或全黑)
- I2C扫描显示两个设备

---

### 任务4.4: 基础显示程序 (40分钟)

**步骤:**

1. **安装OLED库**
   ```python
   # 在Thonny中安装库
   # 包名: "ssd1306-micropython"
   ```

2. **初始化OLED**
   ```python
   from machine import Pin, I2C
   import ssd1306

   # 初始化I2C
   i2c = I2C(0, scl=Pin(22), sda=Pin(21))

   # 初始化OLED (128×64)
   oled = ssd1306.SSD1306_I2C(128, 64, i2c)

   # 清空屏幕
   oled.fill(0)
   oled.show()
   ```

3. **显示文字**
   ```python
   # 设置文字样式
   oled.text('Hello!', 0, 0)      # 在(0,0)显示
   oled.text('OLED Test', 0, 10)  # 在(0,10)显示
   oled.show()                    # 刷新屏幕
   ```

4. **显示图形**
   ```python
   # 画矩形
   oled.rect(0, 20, 50, 30, 1)    # (x,y,w,h,颜色)
   
   # 画填充矩形
   oled.fill_rect(60, 20, 50, 30, 1)
   
   # 画线
   oled.line(0, 60, 127, 60, 1)   # 底部横线
   
   oled.show()
   ```

**预期结果:**
- 屏幕显示文字和图形
- 位置和大小正确

**常见问题:**
- Q: 屏幕全黑?  
  A: 检查I2C地址(可能是0x3D)
- Q: 文字显示不全?  
  A: 注意每行只能显示约20个字符

---

### 任务4.5: 创建监测界面 (60分钟)

**界面设计原则:**
- 信息层次清晰
- 数字字体较大
- 单位明确
- 更新不频繁(避免闪烁)

**完整监测程序:**

```python
from machine import Pin, I2C, UART
import bme680
import ssd1306
import time

# 初始化设备
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
bme = bme680.BME680_I2C(i2c=i2c)
uart = UART(2, baudrate=9600, rx=16, tx=17)

# 布局常量
HEADER_Y = 0
TEMP_Y = 12
HUM_Y = 24
PM_Y = 36
AQI_Y = 48
BOTTOM_Y = 58

def draw_header():
    """绘制标题栏"""
    oled.fill_rect(0, HEADER_Y, 128, 10, 1)
    oled.text("AIR BUTLER", 35, HEADER_Y + 1, 0)
    oled.show()

def draw_sensor_data(temp, hum, pm25, aqi, level):
    """绘制传感器数据"""
    oled.fill(0)  # 清屏
    
    # 标题
    draw_header()
    
    # 温度
    oled.text(f"T:{temp:5.1f}C", 0, TEMP_Y)
    
    # 湿度
    oled.text(f"H:{hum:5.1f}%", 64, TEMP_Y)
    
    # PM2.5
    oled.text(f"PM2.5:{pm25:3d}", 0, HUM_Y)
    
    # AQI
    aqi_text = f"AQI:{aqi:3d}"
    if len(level) <= 3:
        aqi_text += f" {level}"
    oled.text(aqi_text, 0, PM_Y)
    
    # 底部装饰
    oled.line(0, BOTTOM_Y, 127, BOTTOM_Y, 1)
    
    # 时间/状态
    status = "ONLINE" if pm25 > 0 else "OFFLINE"
    oled.text(status, 90, BOTTOM_Y + 2)
    
    oled.show()

def calculate_aqi(pm25):
    """简化的AQI计算"""
    if pm25 <= 35:
        return int((50 / 35) * pm25), "优"
    elif pm25 <= 75:
        return int(50 + (50 / 40) * (pm25 - 35)), "良"
    else:
        return int(100 + (50 / 40) * (pm25 - 75)), "差"

# 主程序
print("环境监测站启动...")
draw_header()

last_update = 0
UPDATE_INTERVAL = 2  # 2秒更新一次

while True:
    try:
        # 定时更新
        if time.ticks_diff(time.ticks_ms(), last_update) > UPDATE_INTERVAL * 1000:
            # 读取BME680
            bme.get_sensor_data()
            temp = bme.data.temperature
            hum = bme.data.humidity
            
            # 读取PMS5003
            # (简化版，实际应使用之前的read_pm_sensor)
            pm25 = 25  # 示例值
            
            # 计算AQI
            aqi, level = calculate_aqi(pm25)
            
            # 更新显示
            draw_sensor_data(temp, hum, pm25, aqi, level)
            
            last_update = time.ticks_ms()
    
    except Exception as e:
        oled.fill(0)
        oled.text(f"ERROR:{str(e)[:10]}", 0, 20)
        oled.show()
        print(f"错误: {e}")
    
    time.sleep(0.1)
```

---

## 🎨 练习: 界面优化 | Practice: Interface Optimization

### 任务4.6: 高级显示效果 (30分钟)

**1. 进度条显示:**
```python
def draw_progress_bar(x, y, width, height, percent):
    """绘制进度条"""
    # 背景
    oled.rect(x, y, width, height, 1)
    
    # 填充
    fill_width = int(width * percent / 100)
    oled.fill_rect(x + 1, y + 1, fill_width - 2, height - 2, 1)

# 使用: 湿度进度条
draw_progress_bar(0, 50, 100, 8, hum)
```

**2. 简单动画:**
```python
def draw_loading_bar():
    """加载动画"""
    for i in range(128):
        oled.fill(0)
        oled.text("Loading...", 40, 28)
        oled.fill_rect(0, 40, i, 4, 1)
        oled.show()
        time.sleep(0.02)

# 启动时显示
draw_loading_bar()
```

**3. 图标显示:**
```python
def draw_temperature_icon(x, y):
    """温度计图标(简化)"""
    oled.vline(x + 5, y, 10, 1)     # 竖线
    oled.fill_rect(x + 3, y + 10, 4, 2, 1)  # 底部
    oled.fill_rect(x + 4, y, 2, 3, 1)      # 顶部

# 使用
draw_temperature_icon(0, 12)
oled.text(f"{temp}C", 15, 12)
```

---

## 📝 今日作业 | Today's Assignment

### 基础作业 (必做)

1. **自定义界面**  
   设计一个与众不同的监测界面，包含:
   - 你的名字/学号
   - 4个传感器数据
   - 至少1个图形元素

2. **界面对比**  
   评价3种不同布局方案的优劣

3. **回答问题**  
   - 为什么OLED更新频率不能太高?
   - I2C总线如何区分多个设备?
   - 128×64分辨率是什么意思?

### 进阶作业 (选做)

1. 实现: 屏幕亮度调节(PWM控制)
2. 研究: SSD1306的其他显示模式(水平/垂直滚动)
3. 思考: 如何在有限空间显示更多信息?(提示: 页面切换)

---

## 📚 参考资源 | References

- [SSD1306数据手册](https://www.sparkfun.com/datasheets/LCD/Monochrome-OLED.pdf)
- [MicroPython OLED教程](https://docs.micropython.org/en/latest/esp32/quickref.html#oled-display)
- [ASCII艺术生成器](https://www.ascii-art-generator.org/)

---

## 🔮 明日预告 | Tomorrow's Preview

**Day 5: 数据整合与本地记录**

- 设计统一的数据结构
- 实现本地文件系统存储
- 计算统计数据(最大/最小/平均值)
- 生成数据质量报告

**前置准备:**
- 复习Python文件操作
- 思考: 如何处理传感器异常数据?

---

*最后更新: 2026-05-05 | Last updated: 2026-05-05*
