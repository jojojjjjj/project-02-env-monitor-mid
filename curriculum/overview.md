# 课程总纲 | Curriculum Overview

> WiFi 温湿度网络时钟 · 复刻模式 · 10 天全日制课程
> WiFi Temp/Humidity Network Clock · Replication Model · 10-Day Full-Time Course

---

## 课程设计理念 | Course Design Philosophy

### 循序渐进 (Fine-grained Scaffolding)
面向零基础高中生，本课程采用**超细粒度**任务分解：
- 每个概念都解释**为什么**（why），而不只是**怎么做**（how）。
- 每一步都有预期结果与验证方法。
- 每天都有明确的可交付成果。

> Every concept explains *why*, not just *how*. Every step has a verifiable expected result. Every day ships a deliverable.

### 复刻模式 (Replication Model)
**源码由课程提供**，学员不写代码从零。重点放在**架构理解 + 接线 + 工具链 + 配置 + 调试**——这些才是嵌入式工程师真正的日常。详见下方「复刻模式说明」。

---

## 项目目标 | Project Goals

10 天结束时，你将拥有一台**能用的桌面 WiFi 温湿度网络时钟**：

1. 开机自动连 WiFi；
2. 通过 SNTP 网络授时，时间准确；
3. OLED 同屏显示**时间 + 温度 + 湿度**；
4. 断网后仍能本地走时，重新联网自动校准；
5. （可选）整点蜂鸣报时。

---

## 学习成果 | Learning Outcomes

完成项目后，你将能够：

| 类别 Category | 学到的能力 What you learn |
|---|---|
| **嵌入式架构 Embedded Architecture** | **识别**「主控 MCU + WiFi 协处理器 + 传感器 + 显示」四块的职责边界，**解释**它们如何分工协作 |
| **接线 Wiring** | **看懂**引脚表，**正确连接** I2C / UART 设备，**分析**上拉与共地的必要性 |
| **工具链 Toolchain** | **安装并使用** STM32CubeIDE 编译、烧录 STM32L433 固件 |
| **配置 Configuration** | **修改** `wifi_config.h` 里的 WiFi 账号密码、NTP 服务器、时区等参数 |
| **调试 Debugging** | **用串口看输出**、**用 AT 命令试通** ESP8266、**定位**「OLED 不亮 / 读不到传感器 / 连不上 WiFi」等故障 |
| **工程素养 Engineering** | **实践** Git 版本管理、周报、最终演示与复盘 |

> ⚠️ 本项目**不**要求你从零写 C 代码。你需要能**读懂**基础 C 语法（变量、函数、`while(1)` 循环、`if` 判断）即可，以便在调试时理解源码做了什么、在哪里改配置。

---

## 你将做出什么 | What You Will Build

一台桌面摆件大小的电子时钟：

```
┌─────────────────────────────┐
│   14:23:45                  │  ← 时间（SNTP 网络授时）
│                             │
│   温度 Temperature  24.6°C  │  ← SHT31
│   湿度 Humidity    56%RH    │  ← SHT31
└─────────────────────────────┘
        0.96" OLED (128×64)
```

整机由一块 STM32L433 主控板 + ESP-01S WiFi 模块 + SHT31 传感器 + OLED 屏组成，USB 供电。

---

## 复刻模式说明 | About the Replication Model

### 为什么是「复刻」而不是「从零开发」？

对一个零基础的高中生，10 天里「从零写出能联网对时的 STM32 固件」几乎不可能。但「**看懂别人写好的代码、把它跑起来、并在出问题时定位修复**」是完全可以做到的——这恰恰是工程师每天都在做的事。

> Writing network-time-sync STM32 firmware from scratch in 10 days is unrealistic for a zero-foundation student. But *reading existing code, getting it to run, and fixing it when it breaks* is absolutely achievable — and it's exactly what engineers do daily.

### 在这个项目里，你学到的「不是编程，而是工程」：

| 你以为嵌入式是 | 其实嵌入式工程师每天做的（你将做的）|
|---|---|
| 写一堆 C 代码 | 读代码、理解架构、改配置 |
| 算法竞赛 | 接线、烧录、看串口日志、定位故障 |
| 一个人闷头写 | 查数据手册、查 AT 命令手册、查别人踩过的坑 |

### 源码从哪来？

课程随包提供完整 STM32L433 固件源码（位于 `software/src/`），整理自 UP 主「乐在程上」KE1 开发板例程：
- **SHT31 驱动**（I2C）+ **SSD1306 OLED 驱动**（软件 I2C）来自 KE1 NBIoT 温湿度采集例程；
- **UART/AT 命令框架**来自 KE1_UART 例程（原为 NB-IoT，本课程适配为 ESP8266 WiFi AT）；
- **GPIO / PWM** 来自 KE1_GPIO / KE1_PWM 例程；
- **新增**：ESP8266 WiFi + SNTP 联网逻辑、OLED 时间显示函数、时钟管理。

你不需要写这些——你需要**理解它们如何拼在一起**，并在自己板子上让它们跑起来。

---

## 项目架构图 | System Architecture

```
                 ┌──────────────┐
   SHT31 (I2C) ──┤              ├── SSD1306 OLED (I2C, 0.96")
   Buzzer (PWM)──┤  STM32L433   ├── ESP-01S / ESP8266 (UART, AT 固件 → WiFi SNTP)
   Buttons (GPIO)┤   (KE1 板)   ├── USB (供电 + 调试串口)
                 └──────┬───────┘
                        │ UART (AT 命令)
                 ┌──────▼───────┐
                 │   ESP8266    │── WiFi ── NTP 服务器 (SNTP 网络授时)
                 └──────────────┘
```

### 四块各自干什么 | Who does what

| 模块 | 职责 | 接口 |
|---|---|---|
| **STM32L433** | 总指挥：读传感器、刷显示、管时间、发 AT 命令 | — |
| **SHT31** | 量温度、量湿度 | I2C（0x44）|
| **SSD1306 OLED** | 显示时间 + 温湿度 | 软件 I2C（PB8/PB9）|
| **ESP8266 (ESP-01S)** | 连 WiFi、向 NTP 服务器取时间、回传给主控 | UART（AT 命令）|

> 关键认知：STM32L433 **没有** WiFi。所有联网动作都交给 ESP8266——主控只能通过 UART「发命令、等回复」。理解了这一点，你就理解了为什么需要 AT 命令框架。

---

## 10 天课程总览 | 10-Day Course Overview

```
第一周: 嵌入式基础与传感器显示 | Week 1: Embedded Basics & Sensor Display
┌─────────┬─────────────────────────────────────────────────────┐
│ Day 1-3 │ STM32L433 入门 + 工具链 + 点灯/串口 + SHT31           │
│         │ → 能读温湿度、串口能看到数值                          │
├─────────┼─────────────────────────────────────────────────────┤
│ Day 4-5 │ OLED 显示温湿度 + ESP8266 AT 试通 + WiFi 联网         │
│         │ → OLED 显示温湿度；ESP8266 连上 WiFi（Week 1 不碰 SNTP）│
└─────────┴─────────────────────────────────────────────────────┘

第二周: 网络授时与整合 | Week 2: SNTP & Integration
┌─────────┬─────────────────────────────────────────────────────┐
│ Day 6-7 │ SNTP 网络授时 + OLED 时钟显示函数                     │
│         │ → SNTP 取到网络时间，OLED 显示时间                    │
├─────────┼─────────────────────────────────────────────────────┤
│ Day 8   │ 时钟整合（时间+温湿度同屏）+ 蜂鸣/按键/断网回退       │
│         │ → 一台能联网对时、能调时、断网照走的时钟              │
├─────────┼─────────────────────────────────────────────────────┤
│ Day 9-10│ 组装（焊接/外壳）+ 调试 + 最终演示 + 复盘             │
│         │ → 桌面摆件成品 + 最终演示                             │
└─────────┴─────────────────────────────────────────────────────┘
```

> **阶段边界 (Phase boundary)**：Week 1 = Day 1-5，Week 2 = Day 6-10。Week 1 的里程碑是「能读温湿度 + OLED 显示 + ESP8266 连上 WiFi」——**Week 1 不做 SNTP**（SNTP 留到 Day 6，Week 2 的第一件事）。这样切分让第一周专注本地感知与显示，第二周专注联网授时与整合，每周一个清晰的能力跃迁。

每日详细安排见 `day-01.md` … `day-10.md`。

---

## 每周里程碑 | Weekly Milestones

### 第一周里程碑 | Week 1 Milestone：本地感知 + 显示 + 联网（Day 1-5）
- [ ] 工具链装好，能编译烧录 STM32L433
- [ ] SHT31 能读出温湿度，串口可见
- [ ] OLED 能显示温湿度
- [ ] ESP8266 通过 AT 命令连上 WiFi（`WIFI GOT IP`）
- [ ] 提交 Week 1 Check-in Report

> Week 1 不做 SNTP 网络授时——先把「本地能感知、能显示、能联网」三件事做扎实，SNTP 留到 Day 6。

### 第二周里程碑 | Week 2 Milestone：网络授时与成品（Day 6-10）
- [ ] SNTP 取到网络时间，OLED 显示正确北京时间
- [ ] 时间 + 温湿度同屏显示（`OLED_ShowClock(...)`）
- [ ] 蜂鸣报时 / 按键调时 / 断网回退全部跑通
- [ ] 焊接 + 外壳组装完成，成品稳定运行
- [ ] 最终演示 + 复盘报告

---

## 学习支持资源 | Learning Support Resources

- **视频源**：[Bilibili BV1tb4y1U7Du](https://www.bilibili.com/video/BV1tb4y1U7Du/)（UP 主：乐在程上）
- **KE1 例程**：`resources/视频中的例程源码_v0.1.zip`
- **参考例程**：`resources/NBIoT温湿度采集_参考.zip`、`resources/STM32_I2C基础_参考.zip`
- **STM32CubeIDE**：[ST 官网下载](https://www.st.com/en/development-tools/stm32cubeide.html)
- **ESP8266 AT 指令集**：[Espressif 官方文档](https://docs.espressif.com/projects/esp-at/)

---

## 重要提醒 | Important Notes

1. **每日成果当天提交**——及时反馈是学习关键。
2. **遇问题先看串口、再查文档、最后问人**——培养定位能力。
3. **定期 Git 提交**——保护你的工作成果，也方便回退。
4. **改配置而非改代码**——本项目大部分「定制」是改 WiFi/NTP/时区配置，不是改逻辑代码。

---

*最后更新: 2026-06-22 | Last updated: 2026-06-22*
