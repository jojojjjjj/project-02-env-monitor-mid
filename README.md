# 环境感知监测站 "空气管家" | Environmental Monitor "Air Butler"

> 面向高中生的暑期IoT实践项目 | A Summer IoT Practicum Project for High School Students

---

## 项目概述 | Project Overview

本项目将带领学员构建一个**实时环境质量监测站**，能够监测温度、湿度、气压、空气质量（CO₂/TVOC）、PM2.5/PM10等关键环境指标，并通过MQTT协议上传数据，在Web仪表盘上实时可视化展示。

> This project guides students to build a **real-time environmental quality monitoring station** capable of monitoring temperature, humidity, pressure, air quality (CO₂/TVOC), PM2.5/PM10, and other key environmental indicators. Data is uploaded via MQTT protocol and visualized in real-time on a web dashboard.

---

## 核心学习目标 | Core Learning Objectives

| 类别 | 学习目标 |
|------|---------|
| **硬件** | ESP32微控制器、I2C/UART通信协议、多传感器整合 |
| **软件** | MicroPython编程、MQTT物联网协议、Python数据处理 |
| **系统** | IoT架构设计、数据采集-传输-存储-可视化全流程 |
| **工程** | 电路焊接、外壳设计、系统调试、文档撰写 |

---

## 技术架构 | Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    硬件层 (Hardware Layer)                    │
├─────────────────────────────────────────────────────────────┤
│  ESP32 DevBoard                                              │
│  ├── BME680 (I2C)  → 温度、湿度、气压、气体                   │
│  ├── PMS5003 (UART) → PM2.5、PM10                            │
│  ├── OLED (I2C)     → 本地显示                               │
│  └── WiFi Module    → 网络连接                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  通信层 (Communication Layer)                 │
├─────────────────────────────────────────────────────────────┤
│  MQTT Protocol (publish/subscribe)                           │
│  Topic: home/airbutler/sensors                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   服务层 (Server Layer)                       │
├─────────────────────────────────────────────────────────────┤
│  Mosquitto Broker  ←  MQTT消息代理                           │
│  InfluxDB         ←  时序数据库存储                           │
│  Grafana          ←  数据可视化仪表盘                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 硬件清单 | Bill of Materials

| 组件 | 型号 | 数量 | 价格 | 说明 |
|------|------|------|------|------|
| ESP32开发板 | ESP32-WROOM-32 | 1 | ¥35 | 主控制器 |
| 环境传感器 | BME680 | 1 | ¥45 | 温湿度/气压/气体 |
| PM传感器 | PMS5003 | 1 | ¥80 | PM2.5/PM10检测 |
| CO₂传感器 | SCD40 | 1 | ¥120 | 可选升级项 |
| OLED显示屏 | SSD1306 0.96" | 1 | ¥15 | 本地数据显示 |
| 面包板套装 | 标准400孔 | 1 | ¥20 | 原型搭建 |
| 杜邦线 | 公对母/母对母 | 1套 | ¥15 | 连接线材 |
| USB数据线 | Micro-USB | 1 | ¥5 | 程序烧录 |
| **总计** | | | **¥200-320** | 基础版/完整版 |

---

## 课程安排 | Curriculum Schedule

| 周期 | 天数 | 主题 | 产出 |
|------|------|------|------|
| **第一周** | Day 1-3 | 硬件基础与传感器入门 | 可读取环境数据 |
| | Day 4-6 | 显示与数据整合 | 本地监测原型 |
| **第二周** | Day 7-9 | 网络通信与服务器搭建 | 远程监控系统 |
| | Day 10-12 | 系统集成与项目展示 | 完整IoT产品 |

详细每日任务见 [curriculum/overview.md](curriculum/overview.md)

---

## 前置知识要求 | Prerequisites

**必需:**
- 高中数学基础（代数、函数）
- 基本电脑操作能力

**建议预习:**
- Python基础语法（变量、函数、列表）
- 电子学入门（电压、电流、电阻概念）

详见: [curriculum/prerequisites.md](curriculum/prerequisites.md)

---

## 快速开始 | Quick Start

### 1. 硬件准备
```bash
# 检查硬件清单
cd hardware
cat BOM.md  # 确认所有组件
```

### 2. 软件环境
```bash
# 安装PC端依赖
pip install -r software/requirements.txt
```

### 3. 第一天任务
```bash
# 开始Day 1: ESP32入门
cat curriculum/day-01.md
```

---

## 项目亮点 | Project Highlights

✅ **真实IoT系统** - 完整的数据采集→传输→存储→可视化链路  
✅ **工业级协议** - MQTT是物联网标准通信协议  
✅ **开源生态** - 基于ESP32、MicroPython、Grafana成熟项目  
✅ **可扩展性** - 易于添加新传感器或功能模块  
✅ **实用价值** - 可实际部署于教室/家中监测空气质量  

---

## 参考资源 | References

- [MicroPython官方文档](https://docs.micropython.org/)
- [ESP32数据手册](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32d_esp32-wroom-32u_datasheet_en.pdf)
- [MQTT协议规范](https://mqtt.org/mqtt-specification/)
- [BME680驱动库](https://github.com/robert-hh/BME680-Micropython)
- [InfluxDB文档](https://docs.influxdata.com/)
- [Grafana教程](https://grafana.com/tutorials/)

---

## 许可证 | License

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE)

---

*最后更新: 2026-05-05 | Last updated: 2026-05-05*
