# 接线指南 | Wiring Guide

> ESP32与所有传感器的完整接线说明 | Complete Wiring Instructions for ESP32 and All Sensors

---

## 接线总览 | Wiring Overview

```
                    ESP32 DevBoard
    ┌────────────────────────────────────┐
    │  [USB]                            │
    │                                    │
    │  GPIO22 ──────────┬───────────────┤── I2C SCL (BME680, OLED)
    │  GPIO21 ─────┬────┼───────────────┤── I2C SDA (BME680, OLED)
    │  GPIO16  ───┼────┼────┬──────────┤── UART2 RX (PMS5003 TX)
    │            │  │ │    │          │
    │  3V3  ─────┼──┼-┼────┼──────────┤── 3.3V输出
    │  VIN  ─────┼──┼-┼────┼────┬─────┤── 5V输出(或输入)
    │  GND  ─────┼──┼-┼────┼────┼─────┤── 地
    └────────────┼──┼-┼────┼────┼─────┘
                 │  │ │    │    │
                 │  │ │    │    └── PMS5003 GND
                 │  │ │    └─────── PMS5003 VCC (5V)
                 │  │ └──────────── PMS5003 TX
                 │  └─────────────── BME680 VCC
                 └────────────────── BME680 GND
                                      
    同时连接:
    BME680 SCL ──── ESP32 GPIO22
    BME680 SDA ──── ESP32 GPIO21
    BME680 GND ──── ESP32 GND
    
    OLED SCL  ───── ESP32 GPIO22
    OLED SDA  ───── ESP32 GPIO21
    OLED GND  ───── ESP32 GND
```

---

## 详细接线表 | Detailed Wiring Table

### 1. ESP32 引脚定义

| 引脚 | 功能 | 连接设备 |
|------|------|---------|
| 3V3 | 3.3V输出 | BME680 VIN, OLED VCC |
| VIN | 5V输出/输入 | PMS5003 VCC |
| GND | 地 | 所有设备GND |
| GPIO21 | I2C SDA | BME680 SDA, OLED SDA |
| GPIO22 | I2C SCL | BME680 SCL, OLED SCL |
| GPIO16 | UART2 RX | PMS5003 TX |

### 2. BME680 接线

| BME680引脚 | 连接到 | 说明 |
|-----------|--------|------|
| VIN | ESP32 3V3 | 3.3V电源 |
| GND | ESP32 GND | 地 |
| SCL | ESP32 GPIO22 | I2C时钟 |
| SDA | ESP32 GPIO21 | I2C数据 |

### 3. PMS5003 接线

| PMS5003引脚 | 连接到 | 说明 |
|-----------|--------|------|
| VCC (红) | ESP32 VIN | 5V电源 |
| GND (黑) | ESP32 GND | 地 |
| TX (绿) | ESP32 GPIO16 | 数据发送 |
| RX (黄) | 不连接 | 不使用 |
| SET | 不连接或3.3V | 设置引脚 |

### 4. OLED 接线

| OLED引脚 | 连接到 | 说明 |
|---------|--------|------|
| VCC | ESP32 3V3 | 3.3V电源 |
| GND | ESP32 GND | 地 |
| SCL | ESP32 GPIO22 | I2C时钟 |
| SDA | ESP32 GPIO21 | I2C数据 |

---

## 接线步骤 | Wiring Steps

### 步骤1: 电源连接 (最重要!)

```
⚠️ 警告: 先断开ESP32的USB线!

1. 连接所有GND
   ESP32 GND → BME680 GND
   ESP32 GND → OLED GND
   ESP32 GND → PMS5003 GND

2. 连接3.3V设备
   ESP32 3V3 → BME680 VIN
   ESP32 3V3 → OLED VCC

3. 连接5V设备
   ESP32 VIN → PMS5003 VCC

4. 用万用表确认:
   - 3V3到GND: 3.3V
   - VIN到GND: 5V (当USB供电时)
```

### 步骤2: I2C总线连接

```
ESP32 GPIO22 (SCL) ─┬── BME680 SCL
                    └── OLED SCL

ESP32 GPIO21 (SDA) ─┬── BME680 SDA
                    └── OLED SDA
```

### 步骤3: UART连接

```
ESP32 GPIO16 (RX2) ←── PMS5003 TX
注意: TX接RX,单向连接
```

---

## 注意事项 | Important Notes

### ⚠️ 安全警告

1. **电压匹配**
   - ESP32 IO引脚只能承受3.3V
   - 连接5V设备会损坏ESP32
   - PMS5003需要5V供电,但信号是3.3V兼容

2. **电源顺序**
   - 先断电再接线
   - 确认无误再上电
   - 发热立即断电检查

3. **I2C总线**
   - 同一I2C总线设备地址不能重复
   - BME680: 0x76或0x77
   - OLED: 0x3C或0x3D
   - 无冲突可共用总线

### 🔍 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 设备不工作 | 电源接反 | 检查VCC/GND |
| ESP32发热 | 有短路 | 断电检查连线 |
| I2C扫描不到 | 接线松动 | 重新连接 |
| PM读数异常 | 波特率不对 | 设置为9600 |

---

## 接线图参考 | Reference Diagrams

### 简化接线图

```
        ESP32
    ┌─────────┐
    │   3V3   ├─────────┬──────→ BME680 VIN
    │         │         │
    │   GND   ├─────────┼──────→ BME680 GND
    │         │         │
    │  GPIO22 ├─────────┼──────→ BME680 SCL
    │         │         │
    │  GPIO21 ├─────────┴──────→ BME680 SDA
    │         │
    │   VIN   ├────────────────→ PMS5003 VCC
    │         │
    │   GND   ├────────────────→ PMS5003 GND
    │         │
    │  GPIO16 ├────────────────→ PMS5003 TX
    │         │
    │   3V3   ├─────────┬──────→ OLED VCC
    │         │         │
    │   GND   ├─────────┼──────→ OLED GND
    │         │         │
    │  GPIO22 ├─────────┼──────→ OLED SCL
    │         │         │
    │  GPIO21 ├─────────┴──────→ OLED SDA
    └─────────┘
```

---

## 工具清单 | Required Tools

- 万用表 (必需)
- 杜邦线套装 (必需)
- 面包板 (推荐)
- 小螺丝刀 (可选)
- 热胶枪 (可选)

---

*最后更新: 2026-05-05 | Last updated: 2026-05-05*
