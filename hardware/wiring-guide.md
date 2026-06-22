# 接线指南 | Wiring Guide

> 项目 02 · 温湿度网络时钟 · STM32L433 与全部外设的引脚级接线
> Project 02 · Pin-level wiring between STM32L433 and all peripherals
>
> 所有引脚分配严格对齐 UP主 乐在程上 KE1 例程源码（I2C2 硬件接 SHT31、PB8/PB9 软件 I2C 接 OLED、TIM2_CH2 PWM 接蜂鸣器、USART3 接 ESP8266）。烧录课程提供的固件即可直接工作，无需改引脚。

---

## 引脚总览速查 | Pin Map at a Glance

| 外设 Peripheral | 接口 | STM32L433 引脚 | 方向 | 说明 |
|---|---|---|---|---|
| **SHT31** 温湿度 | I2C2（硬件） | PB13 = SCL | 双向 | 地址 0x44 |
| | | PB14 = SDA | 双向 | 已需上拉（模块自带） |
| **SSD1306 OLED** | 软件 I2C | PB8 = SCL | 输出 | 地址 0x3C |
| | | PB9 = SDA | 输出 | GPIO 模拟时序 |
| **ESP-01S** WiFi | USART3 | PB10 = TX → ESP RX | 输出 | 115200 baud, AT 命令 |
| | | PB11 = RX ← ESP TX | 输入 | 115200 baud |
| **无源蜂鸣器** | TIM2_CH2 PWM | PA1 | 输出 | 整点报时/闹铃 |
| **按键 KEY1** | GPIO + EXTI | PC13 | 输入 | 上拉，下降沿中断 |
| **按键 KEY2** | GPIO + EXTI | PA15 | 输入 | 上拉，下降沿中断 |
| **LED**（板载/外接） | GPIO 输出 | PB5 / PB6 / PB7 | 输出 | 状态指示（可选） |
| **调试串口** printf | USART1 | PA9 = TX → USB-TTL RX | 输出 | 115200，调试用 |
| | | PA10 = RX ← USB-TTL TX | 输入 | （若板载 USB 转串口则免接） |
| **电源** | — | 3V3 / GND | — | 全系统 3.3V |

> **引脚来源核对**（KE1 源码，可自行复核）：
> - SHT31 在 I2C2：`KE1_IoT.ioc` 中 `PB13→I2C2_SCL`、`PB14→I2C2_SDA`，`i2c.c` 的 `HAL_I2C_MspInit` 确认。
> - OLED 软件 I2C：`oled.h` 中 `OLED_SCLK_Clr/Set` 操作 `GPIO_PIN_8`、`OLED_SDIN_Clr/Set` 操作 `GPIO_PIN_9`。
> - 蜂鸣器：`KE1_PWM/tim.c` 中 TIM2_CH2 映射到 `PA1`，`Beep_Switch()` 启停。
> - 按键：`KE1_GPIO/gpio.c` 中 PC13（KEY1）与 PA15（KEY2）配 `GPIO_MODE_IT_RISING`。
> - 串口：`KE1_IoT.ioc` 中 USART1=PA9/PA10（调试）、USART3=PB10/PB11（原 NB-IoT @9600，本项目改 115200 接 ESP8266）。

---

## 接线总图 | Wiring Diagram (ASCII)

```
                          STM32L433 最小系统板
                ┌──────────────────────────────────────┐
                │  [USB] ── 5V/3.3V 供电 + 下载/调试      │
                │                                        │
   3V3 ────────┬─┤                          ├─┬───────── 3V3 总线
   GND ───────┬┴─┤                          ├─┴┬──────── GND 总线
              │  │                          │  │
              │  │  PB13 (I2C2_SCL) ────────┤  │──→ SHT31 SCL
              │  │  PB14 (I2C2_SDA) ──┬─────┤  │──→ SHT31 SDA
              │  │                    │     │  │
              │  │  PB8  (OLED_SCL) ──┼─────┤  │──→ OLED SCL
              │  │  PB9  (OLED_SDA) ──┼─────┤  │──→ OLED SDA
              │  │                    │     │  │
              │  │  PB10 (USART3_TX)──┤     │  │──→ ESP-01S RX
              │  │  PB11 (USART3_RX)──┤     │  │←── ESP-01S TX
              │  │                    │     │  │
              │  │  PA1  (TIM2_CH2) ──┤     │  │──→ 蜂鸣器 IN
              │  │  PC13 (KEY1) ──────┤     │  │──→ 按键1 → GND
              │  │  PA15 (KEY2) ──────┤     │  │──→ 按键2 → GND
              │  │                    │     │  │
              │  │  PA9  (USART1_TX)──┤     │  │──→ USB-TTL RX (调试)
              │  │  PA10 (USART1_RX)──┤     │  │←── USB-TTL TX (调试)
              └──┴────────────────────┴─────┴──┘

  电源总线分发：
   3V3 ──┬── SHT31 VCC
         ├── OLED VCC
         ├── ESP-01S VCC / CH_PD（EN）   ← ESP-01S 必须接 3.3V，禁 5V！
         └── 蜂鸣器 VCC（若模块有）
   GND ──┬── SHT31 GND
         ├── OLED GND
         ├── ESP-01S GND
         ├── 蜂鸣器 GND
         └── 两按键另一脚
```

---

## 逐器件接线表 | Per-Device Wiring Tables

### 1. SHT31 温湿度传感器（I2C2 硬件，0x44）

| SHT31 模块 | 连接到 STM32L433 | 说明 |
|---|---|---|
| VCC | 3V3 | 3.3V 供电 |
| GND | GND | 公共地 |
| SCL | PB13 | I2C2 时钟（硬件 AF4） |
| SDA | PB14 | I2C2 数据（硬件 AF4） |
| ADDR（若有） | GND 或悬空 | 选 0x44 地址 |

- **为什么用 I2C2 硬件而非软件模拟**：SHT31 读取时序紧凑，硬件 I2C 更稳；且 KE1 例程即用 I2C2，复刻固件直接可用。
- **上拉电阻**：模块通常自带 4.7kΩ 上拉到 VCC，无需外加。若 I2C 扫描不到设备，补焊一对 4.7kΩ 上拉（SCL/SDA 各一个到 3V3）。

### 2. SSD1306 OLED 显示（软件 I2C，0x3C）

| OLED 4 针 | 连接到 STM32L433 | 说明 |
|---|---|---|
| VCC | 3V3 | 3.3V 供电 |
| GND | GND | 公共地 |
| SCL | PB8 | 软件 I2C 时钟（GPIO 输出） |
| SDA | PB9 | 软件 I2C 数据（GPIO 输出） |

- **为什么 OLED 用软件 I2C 而 SHT31 用硬件 I2C**：KE1 例程的历史选择——OLED 驱动 `oled.c` 用 GPIO 模拟时序（`OLED_SCLK_Clr/Set` 等），SHT31 用硬件 I2C2。两者**不共用同一条 I2C 总线**（引脚不同：OLED 在 PB8/PB9，SHT31 在 PB13/PB14），因此地址即便不同也不会冲突。这是 KE1 的设计，复刻时照搬即可。
- **地址确认**：大多数 SSD1306 模块默认 0x3C；少数丝印/批次为 0x3D（背焊电阻不同）。若 `OLED_Init()` 后屏幕全黑，先试改地址（见 `troubleshooting.md`）。

### 3. ESP-01S WiFi 模块（USART3，115200 baud，AT 固件）

| ESP-01S 引脚 | 连接到 STM32L433 | 说明 |
|---|---|---|
| VCC | 3V3 | **必须 3.3V，接 5V 会烧模块** |
| GND | GND | 公共地 |
| TX | PB11 (USART3_RX) | ESP 发 → MCU 收 |
| RX | PB10 (USART3_TX) | MCU 发 → ESP 收 |
| CH_PD (EN) | 3V3 | 使能脚，必须拉高（串联 10kΩ 或直连 3V3） |
| RST | 悬空 或接 3V3 | 复位脚，不用可拉高 |
| GPIO0 | 悬空（运行模式） | 接 GND 才进烧录模式（本项目不烧 ESP） |
| GPIO2 | 悬空 | 不用 |

- **交叉接线铁律**：MCU 的 TX 接 ESP 的 RX，MCU 的 RX 接 ESP 的 TX。记不住就默念「**T 接 R，R 接 T**」。
- **波特率**：ESP-01S 出厂 AT 固件默认 **115200**，USART3 配 115200。若用老版 ESP-01（默认 9600），先单独用 USB-TTL 串口发 `AT+UART_DEF=115200,8,1,0,0` 改波特率（见 `troubleshooting.md`）。
- **供电稳定性**：ESP-01S 发射 WiFi 时瞬态电流可达 300mA，3.3V 必须稳。若频繁重启/连不上网，多半是供电不足——在 VCC 与 GND 间并一个 100μF 电解 + 0.1μF 陶瓷电容。

### 4. 无源蜂鸣器（TIM2_CH2 PWM）

| 蜂鸣器模块 | 连接到 STM32L433 | 说明 |
|---|---|---|
| +（信号/IN） | PA1 | TIM2_CH2 PWM 输出 |
| -（GND） | GND | 公共地 |
| VCC（若有 3 脚版） | 3V3 | 3.3V 供电 |

- **为什么用无源**：无源蜂鸣器靠 PWM 频率决定音调，可编程旋律（整点报时 do-re-mi）。有源蜂鸣器给电就响、频率固定，无法调音。
- **PWM 参数**：KE1 例程 `tim.c` 设 Prescaler=32-1、Period=370-1，主频 32MHz → PWM 频率约 2.7kHz，适合蜂鸣器。`Beep_Switch(1)` 开、`Beep_Switch(0)` 关。

### 5. 按键（GPIO + 外部中断）

| 按键 | 一脚接 STM32L433 | 另一脚接 | 说明 |
|---|---|---|---|
| KEY1 | PC13 | GND | 上拉输入，按下产生下降沿 → EXTI15_10 |
| KEY2 | PA15 | GND | 上拉输入，按下产生下降沿 → EXTI15_10 |

- **为什么用 PC13/PA15**：KE1 例程即用这两个脚做按键，配 `GPIO_MODE_IT_RISING` + `GPIO_PULLUP`。PC13 也常是板载按键，可直接用板子上的 USER 键。
- **消抖**：硬件上 0.1μF 电容并到 GND 可消抖；软件上在中断回调里做 20ms 软件消抖更可靠（见 `software/src/gpio.c`）。

### 6. 调试串口（USART1，115200）

| USB-TTL 串口模块 | 连接到 STM32L433 | 说明 |
|---|---|---|
| RX | PA9 (USART1_TX) | MCU 发 → 电脑收 |
| TX | PA10 (USART1_RX) | 电脑发 → MCU 收（一般不用） |
| GND | GND | 公共地 |

- 若开发板**板载 USB 转串口**（CH340/CP2102），且该串口已桥接到 PA9/PA10，则只需插一根 USB 线即可，无需外接 USB-TTL。KE1 板即如此。确认方式：看开发板原理图，或插上 USB 后电脑设备管理器出现 COM 口、`printf` 能在串口助手显示即说明已桥接。

---

## 电源总则 | Power Rules

1. **全系统 3.3V**：STM32L433、SHT31、OLED、ESP-01S、蜂鸣器全部 3.3V 供电。USB 5V 经开发板板载 LDO 降到 3.3V。
2. **共地**：所有器件的 GND 必须连在一起，否则信号参考不一致，I2C/UART 全乱。
3. **先接线后上电**：接线时拔掉 USB；接好并用万用表测过 3V3↔GND 无短路再上电。
4. **ESP-01S 供电是头号坑**：瞬态电流大，单独供电/加滤波电容（见上文）。

---

## I2C 地址汇总 | I2C Address Summary

| 设备 | 地址（7-bit） | 接口 | 引脚 |
|---|---|---|---|
| SHT31 | **0x44** | 硬件 I2C2 | PB13/PB14 |
| SSD1306 OLED | **0x3C**（少数 0x3D） | 软件 I2C（GPIO） | PB8/PB9 |

> 两个设备不在同一总线（硬件 I2C2 vs 软件 GPIO I2C），故地址互不影响。

---

## UART 波特率汇总 | UART Baud Summary

| UART | 引脚 | 波特率 | 用途 |
|---|---|---|---|
| USART1 | PA9/PA10 | 115200 | 调试 printf → 电脑串口助手 |
| USART3 | PB10/PB11 | 115200 | STM32 ↔ ESP-01S AT 命令 |

---

## 接线步骤（推荐顺序）| Recommended Wiring Order

> 顺序原则：**先电源 → 再 MCU → 再传感器/显示 → 再 WiFi 模块**。每接一类就测一类，分而治之。

1. **电源轨**：在面包板两侧电源轨上标好 3V3 和 GND，从开发板 3V3/GND 引到电源轨。
2. **STM32 开发板**：插面包板中央，USB 口朝外。
3. **SHT31**：接 PB13/PB14/3V3/GND → 烧 SHT31 读取例程 → 串口看到温湿度数值 → 确认 I2C2 通。
4. **OLED**：接 PB8/PB9/3V3/GND → 烧 OLED 例程 → 屏幕显示字符 → 确认软件 I2C 通。
5. **蜂鸣器**：接 PA1/GND → 烧 PWM 例程 → 听到响 → 确认 TIM2 通。
6. **按键**：接 PC13/PA15 → GND → 烧 GPIO 例程 → 按键触发中断翻转 LED。
7. **ESP-01S（最后接）**：接 PB10/PB11/3V3/GND/CH_PD → 单独先测 AT 响应（见 `troubleshooting.md`）→ 再整合联网。

> 详见 `assembly-steps.md` 的分阶段组装流程。

---

*最后更新：2026-06 | Last updated: 2026-06*
