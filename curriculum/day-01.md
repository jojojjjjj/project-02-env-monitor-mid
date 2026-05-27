# Day 1: 项目启动与ESP32入门 | Project Launch & ESP32 Basics

> **今日目标 (Today's Goals):**
> - 理解项目整体架构和应用场景
> - 认识所有硬件组件及其功能
> - 完成ESP32开发环境搭建
> - 编写第一个MicroPython程序(LED闪烁)
>
> **产出 (Deliverable):** 能运行LED闪烁程序的ESP32开发板

---

## 🕒 时间安排 | Schedule

| 时间 | 活动类型 | 内容 |
|------|---------|------|
| 9:00-10:30 | 讲座 | 项目介绍与IoT概念 |
| 10:45-12:00 | 实践 | 硬件认识与MicroPython烧录 |
| 13:30-15:00 | 实践 | GPIO控制与LED实验 |
| 15:15-16:30 | 练习 | 编程练习与调试 |
| 16:30-17:00 | 总结 | 作业布置与Q&A |

---

## 📖 上午: 项目介绍与硬件认识 | Morning: Project Intro & Hardware

### 为什么要学这个? | Why Learn This?

**真实应用场景:**
- 家庭空气质量监测 - 知道何时开窗通风
- 教室环境优化 - 保持学习环境舒适
- 过敏原追踪 - PM2.5预警帮助鼻炎患者
- 智能家居集成 - 自动控制空调/净化器

**工程价值:**
- IoT是未来10年最重要的技术趋势之一
- MQTT协议广泛应用于工业物联网
- ESP32是最流行的IoT开发平台(全球月销量>100万片)

> **Real-world Applications:**
> - Home air quality monitoring - Know when to open windows
> - Classroom environment optimization - Maintain comfortable learning environment
> - Allergen tracking - PM2.5 alerts help rhinitis patients
> - Smart home integration - Automatically control AC/purifiers
>
> **Engineering Value:**
> - IoT is one of the most important tech trends for the next 10 years
> - MQTT protocol is widely used in industrial IoT
> - ESP32 is the most popular IoT development platform (>1M units/month globally)

---

### 任务1.1: 项目架构理解 (30分钟)

**步骤:**

1. **阅读项目README** (10分钟)
   ```bash
   # 打开项目README
   cat README.md
   ```

2. **绘制系统架构图** (15分钟)
   - 画出数据流: 传感器 → ESP32 → MQTT → 服务器 → 仪表盘
   - 标注每个组件的作用
   - 可手绘或使用draw.io

3. **小组讨论** (5分钟)
   - 这个系统可以用在哪里?
   - 可以添加什么传感器?

**预期结果:**
- 能用自己的话解释项目工作原理
- 画出完整的系统架构图

**常见问题:**
- Q: 为什么需要MQTT?  
  A: 因为WiFi不稳定，MQTT能保证消息可靠到达
- Q: 为什么用ESP32而不是Arduino?  
  A: ESP32自带WiFi，成本低，性能强

---

### 任务1.2: 硬件组件认识 (60分钟)

**硬件清单检查:**

| 组件 | 数量 | 检查方法 |
|------|------|---------|
| ESP32开发板 | 1 | 找到USB接口、GPIO引脚 |
| BME680传感器 | 1 | 找到4个引脚(VCC,GND,SCL,SDA) |
| PMS5003传感器 | 1 | 找到风扇和线缆 |
| OLED显示屏 | 1 | 找到I2C接口 |
| 面包板+杜邦线 | 1套 | 测试杜邦线导通性 |
| USB线 | 1 | 确认Micro-USB接口 |

**认识ESP32开发板:**

```
┌──────────────────────────────────────┐
│         ESP32 DevBoard               │
│  ┌────┐    ┌────┐    ┌────┐         │
│  │USB │    │RST │    │EN  │         │
│  └────┘    └────┘    └────┘         │
│                                      │
│  [GPIO00][GPIO01][GPIO02]...        │
│  [  GND ][  VIN ][3V3 ]...          │
└──────────────────────────────────────┘
   ⚠️ 重要: VIN=5V输入, 3V3=3.3V输出
```

**引脚识别练习:**
1. 找到3.3V引脚(红色标记)
2. 找到GND引脚(黑色标记)
3. 找到GPIO2(板载LED连接)
4. 找到I2C引脚(GPIO21=SDA, GPIO22=SCL)

**预期结果:**
- 能准确说出每个组件的名称
- 知道ESP32的主要引脚功能

**常见问题:**
- Q: 为什么有些引脚有红色标签?  
  A: 这些是特殊功能引脚，使用时要小心
- Q: 可以直接用5V供电吗?  
  A: 可以接到VIN引脚，但IO引脚只能是3.3V

---

## 💻 下午: MicroPython环境搭建 | Afternoon: MicroPython Setup

### 为什么要用MicroPython? | Why MicroPython?

**对比Arduino C++:**
- ✅ 语法简单，像普通Python
- ✅ 交互式REPL，立即测试代码
- ✅ 无需编译，开发效率高
- ✅ 丰富的库支持

> **Compared to Arduino C++:**
> - ✅ Simple syntax, like regular Python
> - ✅ Interactive REPL, test code immediately
> - ✅ No compilation, high development efficiency
> - ✅ Rich library support

---

### 任务1.3: 安装Thonny IDE (20分钟)

**步骤:**

1. **下载Thonny**
   - 访问: https://thonny.org/
   - 下载Windows安装包
   - 运行安装程序(全部默认设置)

2. **安装ESP32驱动**
   - 访问: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
   - 下载CP210x驱动
   - 安装完成后重启电脑

3. **测试连接**
   ```bash
   # Windows: 在设备管理器中查找COM口
   # 设备管理器 → 端口(COM和LPT) → Silicon Labs CP210x
   ```

**预期结果:**
- Thonny能正常启动
- 设备管理器能看到COM口(如COM3)

**常见问题:**
- Q: 找不到COM口?  
  A: 检查USB线是否连接，尝试更换USB口
- Q: 驱动安装失败?  
  A: 可能需要禁用驱动强制签名(Windows 10)

---

### 任务1.4: 烧录MicroPython固件 (40分钟)

**步骤:**

1. **下载固件**
   - 访问: https://micropython.org/download/ESP32_GENERIC/
   - 下载最新版本(.bin文件)

2. **烧录固件**
   - 在Thonny中: 工具 → Options → 解释器
   - 选择"MicroPython (ESP32)"
   - 点击"Install or update MicroPython"
   - 选择端口和固件文件
   - 点击"安装"

3. **验证安装**
   ```python
   # 在Thonny Shell中输入
   print("Hello ESP32!")
   # 应该看到: Hello ESP32!
   ```

**预期结果:**
- ESP32能执行Python命令
- Shell显示MicroPython版本信息

**常见问题:**
- Q: 烧录失败?  
  A: 按住BOOT按钮再接USB，进入下载模式
- Q: 固件版本过旧?  
  A: 重新下载最新版本烧录

---

## 🔧 实践: GPIO控制LED | Practice: GPIO LED Control

### 任务1.5: LED闪烁实验 (60分钟)

**为什么学GPIO?**  
GPIO(通用输入输出)是微控制器的"手指"，能控制外部设备。

> **Why learn GPIO?**  
> GPIO (General Purpose Input/Output) is the microcontroller's "fingers", capable of controlling external devices.

**步骤:**

1. **连接LED电路**
   ```
   ESP32 GPIO2 → 220Ω电阻 → LED正极
   ESP32 GND   → LED负极
   ```
   注: ESP32板载LED已连接到GPIO2，可直接使用

2. **编写控制程序**
   ```python
   from machine import Pin
   import time

   # 设置GPIO2为输出
   led = Pin(2, Pin.OUT)

   # 循环闪烁
   while True:
       led.value(1)      # 点亮LED
       print("LED ON")
       time.sleep(1)     # 等待1秒
       
       led.value(0)      # 熄灭LED
       print("LED OFF")
       time.sleep(1)     # 等待1秒
   ```

3. **上传并运行**
   - 在Thonny中粘贴代码
   - 保存为`main.py`(ESP32会自动运行)
   - 点击"运行"按钮

4. **实验改进**
   ```python
   # 挑战: 让LED闪烁3次后停止
   for i in range(3):
       led.value(1)
       time.sleep(0.5)
       led.value(0)
       time.sleep(0.5)
   print("Blink complete!")
   ```

**预期结果:**
- LED有节奏地闪烁
- Shell中打印ON/OFF信息
- 能修改闪烁频率

**常见问题:**
- Q: LED不亮?  
  A: 检查引脚号，确认GPIO2
- Q: 如何停止程序?  
  A: 按Ctrl+C或点击停止按钮

---

## 📝 今日作业 | Today's Assignment

### 基础作业 (必做)

1. **提交硬件照片**  
   拍摄你的ESP32开发板，标注出:
   - USB接口
   - 3.3V引脚
   - GND引脚
   - GPIO2引脚

2. **完成代码练习**  
   修改LED闪烁程序，实现:
   - SOS摩斯密码(三短三长三短)
   - 闪烁频率可调

3. **回答问题**  
   - 什么是IoT?请举3个生活中的例子
   - ESP32与Arduino有什么区别?

### 进阶作业 (选做)

1. 研究: MicroPython是如何运行的?
2. 尝试: 控制多个LED(需要额外硬件)
3. 思考: 如何让LED闪烁更精确?(提示: time.ticks_ms())

---

## 📚 参考资源 | References

- [MicroPython GPIO文档](https://docs.micropython.org/en/latest/esp32/quickref.html#gpio-pins)
- [ESP32引脚参考](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/gpio.html)
- [Thonny官方教程](https://github.com/thonny/thonny/wiki)

---

## 🔮 明日预告 | Tomorrow's Preview

**Day 2: MicroPython基础与I2C传感器**

- 学习I2C通信协议
- 连接BME680温湿度传感器
- 读取并显示环境数据

**前置准备:**
- 复习Python列表和字典
- 阅读I2C通信原理(5分钟)

---

*最后更新: 2026-05-05 | Last updated: 2026-05-05*
