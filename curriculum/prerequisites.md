# 前置知识清单 | Prerequisites Checklist

> 在开始本项目之前，请确认以下前置条件已满足。
> Before starting, please confirm the following prerequisites are met.

本项目采用**复刻模式**，源码由课程提供，因此对编程基础的要求很低——**能读懂基础 C 语法即可**，无需任何 STM32 经验。真正需要你准备好的是**工具链**和**硬件套件**。

> **English summary**: This project uses a replication model — firmware is provided, so you only need basic C reading skills and a prepared toolchain + hardware kit. No prior STM32 experience required.

---

## 学习成果 | Learning Outcomes

完成本前置准备后，你应当能够：

- **识别 (Identify)** 本项目所需的全部软件工具链组件（CubeIDE / 串口驱动 / 串口终端 / esptool）及其各自用途
- **解释 (Explain)** 为什么 ESP8266 只支持 2.4GHz、为什么 CubeIDE 不支持中文路径
- **实现 (Implement)** 在自己的电脑上把工具链装好并验证通过（出现 COM 口、能新建工程）
- **分析 (Analyze)** 自己的环境是否满足项目要求，找出缺哪一块、该装什么

## 为什么学这个 | Why This Matters

> 类比：**装厨房比炒第一道菜更费劲，但没厨房就没法开火。** 工具链就是你的厨房——CubeIDE 是灶台，串口驱动是燃气接口，串口终端是看火候的窗口。Day 1 之前把厨房装好，课堂上才能直接「炒菜」（接线、烧录、调试），而不是全班卡在「老师我板子不识别」上。历年暑期课统计，**60% 的卡壳发生在工具链安装环节**，把它前置到课前是性价比最高的事。

---

## ✅ 前置清单 | Prerequisite Checklist

| 项 Item | 要求 Requirement | 说明 Notes |
|---|---|---|
| C 语法阅读能力 | 能看懂变量、函数、`while(1)`、`if`、`#define` | **不用会写**，能读懂即可，方便调试时改配置 |
| STM32 经验 | **无需** | 本课程从零教 CubeIDE 工具链 |
| 电脑 | 一台带 USB 口的 Windows / Mac / Linux | Windows 最省心（驱动齐全）|
| 硬件套件 | 见 [hardware/BOM.md](../hardware/BOM.md) | 总成本 < ¥500 |
| 工具链软件 | 见下方「工具链」 | 全部免费 |
| WiFi | 一台可联网的 2.4GHz WiFi 路由器 + 账号密码 | ESP8266 仅支持 2.4GHz，不支持 5GHz |

> 为什么 ESP8266 只支持 2.4GHz？因为它是一款早期 WiFi 芯片，硬件上就不支持 5GHz 频段。家里路由器若开了「双频合一」，请确认 2.4GHz 频段可用，否则 ESP8266 连不上。

---

## 🛠 工具链 | Toolchain

以下软件全部免费。建议在 Day 1 之前全部装好，避免课堂上卡在安装环节。

### 1. STM32CubeIDE（主开发环境）

- **版本**：1.6.1+（UP 主原片使用 1.6.1；新版亦可）
- **用途**：编译、烧录、调试 STM32L433 固件
- **下载**：[https://www.st.com/en/development-tools/stm32cubeide.html](https://www.st.com/en/development-tools/stm32cubeide.html)
- **为什么用它**：它是 ST 官方免费 IDE，集成了 CubeMX 图形化配置 + GCC 编译器 + 烧录器，本课程源码工程就是基于它建的。

> ⚠️ **CubeIDE 不支持中文路径**。解压源码后，务必把工程复制到**全英文路径**的文件夹再导入，否则会报错。（UP 主 `使用说明.txt` 也特别提醒了这一点。）

### 2. STM32CubeProgrammer（烧录工具，可选）

- **用途**：独立烧录工具，CubeIDE 自带烧录功能不够时备用
- **下载**：[https://www.st.com/en/development-tools/stm32cubeprogrammer.html](https://www.st.com/en/development-tools/stm32cubeprogrammer.html)

### 3. 串口驱动（USB 转 TTL）

STM32L433 开发板通常用 CH340 或 CP210x 芯片做 USB 转串口。插入电脑后若未自动识别，装对应驱动：

- **CH340 驱动**：[https://www.wch.cn/downloads/CH341SER_EXE.html](https://www.wch.cn/downloads/CH341SER_EXE.html)
- **CP210x 驱动**：[https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)

> **验证**：插上板子后，Windows「设备管理器 → 端口 (COM 和 LPT)」里应出现一个 `COMx`（如 COM3）。看到 COM 号就说明驱动装好了。

### 4. 串口终端软件

用于看 STM32 的 `printf` 调试输出、手动发 AT 命令给 ESP8266。任选其一：

- **MobaXterm** / **PuTTY**（Windows 经典）
- **Tera Term**
- **VS Code + Serial Monitor 插件**

### 5. ESP8266 AT 固件烧录工具（esptool，可选）

ESP-01S 一般出厂就带 AT 固件，通常不需要重刷。但若 AT 命令无响应，可能需要重刷：

- **esptool**（Python）：`pip install esptool`
- **ESP8266 Flash Download Tool**（Espressif 官方图形工具）：[https://www.espressif.com/en/support/download/other-tools](https://www.espressif.com/en/support/download/other-tools)
- **AT 固件**：[Espressif ESP8266 AT 固件](https://docs.espressif.com/projects/esp-at/)

### 6. Python（仅用于串口测试脚本，可选）

`software/tests/` 下有一个用 pyserial 写的串口集成测试。若想跑它：

```bash
pip install pyserial
```

---

## 🧰 硬件套件 | Hardware Kit

完整清单与购买参考见 [hardware/BOM.md](../hardware/BOM.md)。核心组件：

- STM32L433 开发板（KE1 板或通用 STM32L433 最小系统板）
- ESP-01S（ESP8266）WiFi 模块
- SHT31 温湿度传感器模块
- SSD1306 OLED 0.96" 128×64（I2C）
- 无源蜂鸣器（可选）
- 轻触按键 ×2（可选）
- 面包板 + 杜邦线（MVP 版）/ 自制 PCB（进阶版）
- USB 数据线

> 总成本 < ¥500/套。面包板 MVP 版通常 ¥150–250 即可搞定。

---

## 📦 软件安装步骤 | Software Installation Steps

按顺序安装，每步装完都验证一下：

### 任务 1: 装 CubeIDE (难度: ⭐)

1. 下载 ST 账号登录后下载安装包，按默认选项安装。
2. 验证：启动 CubeIDE，能新建工程即成功。

### 任务 2: 装串口驱动 (难度: ⭐)

1. 插上 STM32 板子，装 CH340 或 CP210x 驱动。
2. 验证：设备管理器出现 `COMx`。

### 任务 3: 装串口终端 (难度: ⭐)

1. 装 MobaXterm 或 PuTTY。
2. 验证：能打开串口（波特率 115200）连上板子。

### 任务 4: （可选）装 esptool + pyserial (难度: ⭐)

```bash
pip install esptool pyserial
```
- 验证：`esptool.py version` 能打印版本号。

### 任务 5: 解压课程源码到英文路径 (难度: ⭐⭐)

1. 把 `software/src/` 工程解压到如 `D:\projects\env-clock\`（**不要有中文**）。
2. 用 CubeIDE `File → Open Projects from File System` 导入。
3. 验证：工程树出现 `env_clock`，`Core/Inc/wifi_config.h` 等文件可见。

---

## 🧪 自我评估 | Self-Assessment

开始前，确认以下都打勾：

- [ ] 我有一台带 USB 口的电脑
- [ ] 我知道自家 WiFi 的名称和密码，且是 2.4GHz
- [ ] 我能看懂下面这段 C 代码大概在干什么（不用会写）：
  ```c
  while (1) {
      KE1_I2C_SHT31(&temp, &humi);        // 读温湿度
      OLED_ShowClock(y, mo, d, h, mi, s,  // 刷一屏：日期+时间
                     wday, temp, humi,    // +温湿度+同步状态
                     Clock_IsSynced());
      HAL_Delay(200);                      // 主循环节流
  }
  ```
- [ ] 我装好了 CubeIDE，能新建工程
- [ ] 我插上板子，设备管理器出现了 COM 号

全部打勾？去 [day-01.md](day-01.md) 开始吧。

---

## 理解验证问题 | Comprehension Check

> 以下是理解类问题（不是纯识记）。先自己想，再对参考答案。能答对 2/3 即说明前置准备到位。

**Q1: ESP8266 (ESP-01S) 为什么只支持 2.4GHz WiFi 而不支持 5GHz？如果你家路由器是「双频合一」的，该怎么办？**

> **参考答案**: ESP8266 是一款早期 WiFi 芯片，其射频硬件只设计了 2.4GHz 频段，物理上就不支持 5GHz。5GHz 频段需要不同的射频前端和天线设计，ESP8266 没有这部分电路。双频合一的路由器会在 2.4/5GHz 间自动引导设备，部分路由器会把 ESP8266 误引到 5GHz 导致连不上。对策：在路由器设置里**临时关闭 5GHz**、或**分开命名**两个 SSID（如 `MyWiFi` 和 `MyWiFi_5G`），让 ESP8266 连 2.4GHz 那个；或用手机开热点（手机热点默认 2.4GHz）。

**Q2: 为什么 STM32CubeIDE 不支持中文路径？这反映了嵌入式工具链的什么共性？**

> **参考答案**: CubeIDE 底层调用 GCC arm 交叉编译器 + make + Python 脚本，这些工具大多源自 Linux/Unix 传统，对路径中的非 ASCII 字符（中文、空格）处理不一致，容易在编译/链接时找不到文件而报错。这反映了嵌入式工具链的共性——**沿袭 Unix 传统、对路径编码敏感**。对策：工程一律放全英文、无空格路径（如 `D:\projects\env-clock\`）。这也是为什么 UP 主 `使用说明.txt` 特别提醒。

**Q3: 为什么「充电线」会导致烧录/串口失败？如何判断一根 USB 线是数据线？**

> **参考答案**: USB 线内部有 4 芯：2 根电源（VBUS/GND）+ 2 根数据（D+/D-）。廉价「充电线」为省成本只焊了电源 2 芯，没有数据线，所以能充电但电脑识别不到设备、无法烧录/串口通信。判断方法：**用这根线连手机能传文件 = 数据线**；或看线缆包装标 `USB 2.0 Data`。买线时明确选「数据线」而非「快充线」。

---

## 评分标准 | Rubric

| 维度 | 满分 | 评分细则 |
|------|------|---------|
| 完成度 | 4 | 5 项安装任务全部完成且验证通过（COM 口出现 + 能新建工程 + 源码导入成功） |
| 理解深度 (CC 回答) | 3 | 能答对 Q1-Q3 中至少 2 个，并说出理由而非只背结论 |
| 环境质量 | 2 | 路径全英文无空格；驱动无感叹号；串口能稳定打开 |
| 创意拓展 | 1 | 额外装了 VS Code + PlatformIO 等进阶环境，或写了安装笔记 |

---

> **今日产出 = 明日输入**: 装好的工具链（CubeIDE 能编译 + COM 口出现 + 源码导入 0 error） = Day 1 烧录第一个固件、点亮 OLED 的输入。工具链没装好，Day 1 寸步难行。

---

## ❓ 常见问题 | FAQ

**Q1: 完全没碰过单片机，能跟上吗？**
A: 可以。本项目就是为零基础设计，源码提供，你学的是工具链与调试，不是从零编程。

**Q2: 需要会 C 语言吗？**
A: 只需**读懂**基础 C 语法（变量、函数、循环、判断），不用会写。Day 1 会带大家过一遍源码结构。

**Q3: Mac / Linux 能用吗？**
A: 能，CubeIDE 是跨平台的。但串口驱动和烧录工具在 Windows 上最省心，建议用 Windows。

**Q4: 家里只有 5GHz WiFi 怎么办？**
A: ESP8266 只支持 2.4GHz。大多数路由器都支持双频，在设置里开启 2.4GHz 频段即可；或用手机开热点（手机热点默认 2.4GHz）。

---

*最后更新: 2026-06-22 | Last updated: 2026-06-22*
