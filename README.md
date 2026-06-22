# 温湿度网络时钟 EnvClock | WiFi Temp/Humidity Network Clock

> 面向高中生零基础暑期嵌入式实践项目 · 复刻模式 | A Summer Embedded Practicum for High School Students — Replication Model

---

## 项目简介 | Project Overview

本项目带你复刻一个**桌面 WiFi 温湿度网络时钟**：它通过 WiFi 自动对时（SNTP 网络授时），在 OLED 屏幕上同时显示**时间、温度、湿度**。开机联网后时间永远准确，断网时也能继续走时。整个项目以 B 站 UP 主「乐在程上」的同款自制温湿度时钟视频为蓝本，**源码由课程提供**，学员只需接线、烧录、配置、调试，无需从零写代码。

> This project walks you through replicating a **desktop WiFi temp/humidity network clock**: it syncs time automatically over WiFi (SNTP), and shows **time + temperature + humidity** on an OLED. Once online, the clock stays accurate; it keeps ticking even without WiFi. The project follows Bilibili creator 乐在程上's DIY temp/humidity clock video. **Firmware code is provided** — students wire, flash, configure, and debug; they do not write code from scratch.

---

## 硬件平台 | Hardware Platform

| 角色 Role | 型号 Model | 说明 Notes |
|---|---|---|
| 主控 MCU | **STM32L433**（KE1 板）| 视频原片所用芯片，低功耗 Cortex-M4 |
| WiFi 协处理器 | **ESP-01S (ESP8266)** | 出厂 AT 固件，通过 UART 收发 AT 命令联网与对时 |
| 温湿度传感器 | **SHT31** | I2C 接口，0x44；温度 ±0.2°C，湿度 ±2%RH |
| 显示屏 | **SSD1306 OLED 0.96"** | 128×64，I2C；KE1 源码用软件 I2C（PB8=SCL / PB9=SDA）|
| 蜂鸣器（可选）| 无源蜂鸣器 | TIM2 PWM，整点报时 / 闹钟 |
| 按键（可选）| 轻触按键 ×2 | GPIO，手动调时 / 模式切换 |
| 供电 | USB 5V → 板载 3.3V LDO | 桌面摆件常电供电 |

> STM32L433 本身没有 WiFi，所以用 ESP8266 做「WiFi 协处理器」——主控通过 UART 发 AT 命令，让 ESP8266 去连 WiFi、去 NTP 服务器取时间，再把结果回传给主控。这是嵌入式里非常典型的「分工」架构。
>
> STM32L433 has no WiFi of its own, so an ESP8266 acts as a "WiFi coprocessor": the MCU sends AT commands over UART, the ESP8266 connects to WiFi, queries an NTP server, and returns the time. This division of labor is a textbook embedded architecture.

---

## 功能特性 | Features

- 🕐 **WiFi 自动对时** — SNTP 网络授时，开机联网即自动校准，走时准确。
- 🌡️ **温湿度实时显示** — SHT31 高精度传感器，温度 ±0.2°C、湿度 ±2%RH。
- 🖥️ **OLED 多信息同屏** — 128×64 OLED 同时显示时间 + 温度 + 湿度。
- 🔔 **整点报时（可选）** — 无源蜂鸣器 PWM 整点提示。
- ⏱️ **断网回退** — 联网对时后断网仍能本地走时，重新联网自动校准。
- 🔧 **复刻友好** — 源码全部提供，零基础学员也能跑通。

---

## 技术栈 | Tech Stack

- **MCU 固件**：C 语言 · STM32 HAL 库 · STM32CubeIDE（原片使用 1.6.1）
- **通信协议**：I2C（SHT31 / OLED）、UART（ESP8266 AT 命令）
- **网络授时**：ESP8266 AT 固件 · SNTP / NTP
- **工具链**：STM32CubeIDE · STM32CubeProgrammer · 串口驱动（CH340 / CP210x）· esptool（ESP8266 固件烧录）

---

## 开源出处 | Open-source Basis

本项目复刻自 B 站 UP 主 **乐在程上** 的「STM32 超简单的开发方法」系列中的温湿度时钟自制视频，并使用其公开共享的 KE1 开发板例程源码作为软件基础。

- **视频 UP 主**：乐在程上
- **视频**：[【自制温湿度时钟】桌面摆件 物联网 极客DIY](https://www.bilibili.com/video/BV1tb4y1U7Du/)
- **KE1 例程源码**：随 `resources/视频中的例程源码_v0.1.zip` 一并提供（含 GPIO / PWM / ADC / UART 基础例程）。按 UP 主 `使用说明.txt` 声明：**「本共享例程源码无版权，可随意使用」**，所引用的 SDK 源码版权归其所有者。

> 本课程包在原片基础上整理为教学版：保留了视频中的核心例程与 NBIoT 温湿度采集参考例程（SHT31 + OLED 驱动），移除了与本项目无关的系列其余各期内容，并补充了 WiFi 联网授时与时钟显示的教学说明。

---

## Bilibili 视频 | Bilibili Video

**📺 https://www.bilibili.com/video/BV1tb4y1U7Du/**

这是本项目的「真相之源」(source of truth)：硬件选型、接线思路、最终效果均以该视频为准。建议在动手前完整观看一遍。

> This video is the source of truth for the project. Watch it end-to-end before you start.

---

## 难度与时长 | Difficulty & Duration

| 项 Item | 值 Value |
|---|---|
| 难度 Difficulty | **2/5 基础 Basic** |
| 时长 Duration | **约 10 天 ~10 days**（全日制夏令营 full-time camp）|
| 模式 Model | **复刻 Replication**（源码提供，学员接线+烧录+配置+调试）|

---

## 复刻说明 | About the Replication Model

本项目采用**复刻模式**：课程的源码已经写好并随包提供，学员**不需要从零编程**。你要做的是真正属于「嵌入式工程师」的日常工作：

1. **看懂架构** — 理解 STM32L433 主控 + ESP8266 WiFi 协处理器 + SHT31 传感器 + OLED 显示这四块如何协作。
2. **接线** — 按接线表把各模块连到正确的引脚，I2C 上拉、共地、电平匹配都要正确。
3. **工具链** — 安装 STM32CubeIDE，学会编译、烧录。
4. **配置** — 填入你自己的 WiFi 账号密码、NTP 服务器、时区。
5. **调试** — 串口看输出、AT 命令试通、OLED 不亮怎么办……这些才是真本事。

> 为什么采用复刻模式？因为对一个零基础的高中生来说，10 天里「从零写出能联网对时的 STM32 固件」几乎不可能；但「看懂别人写好的代码、把它跑起来、并在出问题时定位修复」是完全可以做到的——这正是工程师每天都在做的事。你学到的是**嵌入式架构与工程方法**，而不是单纯的语法。

---

## 目录结构 | Directory Structure

```
project-02-env-monitor-mid/
├── README.md                  ← 你在这里 You are here
├── curriculum/                ← 课程：总纲、前置、每日课程、作业、评分
│   ├── overview.md            ← 项目目标 / 学习成果 / 架构图
│   ├── prerequisites.md       ← 前置清单 / 工具链 / 安装步骤
│   ├── day-01.md … day-10.md  ← 10 天每日课程
│   ├── assignments.md         ← 作业总览
│   └── grading-rubric.md      ← 评分量规
├── hardware/                  ← 硬件：BOM、接线、组装、排错
│   ├── BOM.md
│   ├── wiring-guide.md
│   ├── assembly-steps.md
│   └── troubleshooting.md
├── software/                  ← 固件源码（提供）+ 构建/烧录/配置说明
│   ├── src/                   ← STM32L433 固件（HAL/CubeIDE）
│   ├── config.template.yaml   ← WiFi/NTP/时区 配置模板
│   ├── README.md              ← 构建/烧录/配置说明
│   └── tests/                 ← 串口集成测试
├── assignments/               ← 周报与展示模板
│   ├── week-1-checkin.md
│   ├── week-2-checkin.md
│   ├── final-presentation.md
│   └── rubric.md
└── resources/                 ← UP 主例程源码与参考（含 README 说明）
```

---

## 快速开始 | Quick Start

1. 看一遍 [Bilibili 视频](https://www.bilibili.com/video/BV1tb4y1U7Du/)，了解最终效果。
2. 读 [curriculum/overview.md](curriculum/overview.md) 理解项目目标与架构。
3. 按 [curriculum/prerequisites.md](curriculum/prerequisites.md) 装好工具链。
4. 照 [hardware/BOM.md](hardware/BOM.md) 备齐套件，按 [hardware/wiring-guide.md](hardware/wiring-guide.md) 接线。
5. 从 [curriculum/day-01.md](curriculum/day-01.md) 开始 10 天课程。

---

## 许可证 | License

本项目课程包文档采用 MIT 许可证。所附 UP 主「乐在程上」KE1 例程源码按其 `使用说明.txt` 声明「无版权，可随意使用」；所引用的 SDK 源码版权归其所有者。

---

*最后更新: 2026-06-22 | Last updated: 2026-06-22*
