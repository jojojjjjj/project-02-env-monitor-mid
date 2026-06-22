# 故障排查指南 | Hardware Troubleshooting Guide

> 项目 02 · 温湿度网络时钟 · 常见**硬件**问题诊断与修复
> Project 02 · Hardware issue diagnosis — symptom → cause → fix
>
> 症状→原因→对策 三段式。逐项排除，不要一次怀疑多个部件。复刻模型：先确认硬件通，再查配置/固件。

---

## 诊断总流程 | Diagnostic Flow

```
上电
 ↓
串口有 printf 输出? ── 否 → [1] CH340/串口驱动 + 烧录
 ↓ 是
SHT31 读到温湿度? ── 否 → [2] SHT31 I2C
 ↓ 是
OLED 显示字符? ── 否 → [3] OLED 软件 I2C
 ↓ 是
蜂鸣器能响? ── 否 → [4] 蜂鸣器 PWM
 ↓ 是
ESP-01S 回 AT OK? ── 否 → [5] ESP8266 AT 无响应
 ↓ 是
WiFi 联网成功? ── 否 → [6] WiFi 联网
 ↓ 是
NTP 时间正确? ── 否 → [7] SNTP 授时
 ↓ 是
✅ 全功能正常
```

---

## [1] CH340 / 串口驱动不识别 | Serial Driver Not Recognized

**症状**：插 USB 后电脑「设备管理器→端口(COM 和 LPT)」无新 COM 口，或 COM 口带黄色感叹号；串口助手打不开端口；烧录工具找不到设备。

**原因**：
- 没装 CH340/CP2102 驱动（开发板板载 USB 转串口芯片的驱动）。
- 用了**充电线**而非数据线（线内部只有 2 芯电源，无数据线）。
- USB 口/扩展坞供电不足。

**对策**：
1. 看开发板上 USB 口旁的小芯片丝印：`CH340` → 装 [CH340 驱动](https://www.wch.cn/downloads/CH341SER_EXE.html)；`CP2102` → 装 [CP210x 驱动](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)；`STM32F103` 充当 USB 转串口 → 装 STM32 虚拟串口驱动。
2. 换一根**数据线**（能传文件的线）。判断：用这根线连手机能传文件 = 数据线。
3. 直插电脑主板 USB 口，避开 USB Hub/扩展坞。
4. 装完驱动重启电脑，设备管理器应出现 `USB-SERIAL CH340 (COMx)`，无感叹号。

---

## [2] 烧录失败 | Flash/Program Failure

**症状**：STM32CubeProgrammer / ST-Link Utility 报 `No ST-Link detected` / `Cannot connect to target`；或烧录到一半报错。

**原因**：
- ST-Link 驱动未装或 ST-Link 固件过旧。
- SWD 接线（SWCLK/SWDIO/GND/3V3）松动或接反。
- 之前烧了错代码把 SWD 引脚复用掉了（「锁死」）。
- 目标板供电不足。

**对策**：
1. 装 ST-Link 驱动（STM32CubeIDE 安装时自带；或单独下 `STM32 ST-LINK Utility`）。
2. 检查 SWD 四线：SWCLK→SWCLK、SWDIO→SWDIO、GND→GND、3V3→3V3，别接反。
3. 若是板载 ST-Link 复合板，确认板载 ST-Link 的 USB 也插好（部分板子要插两根 USB）。
4. **锁死恢复**：CubeProgrammer 里勾 `Connect Under Reset`，按住开发板 RESET 键不放 → 点 Connect → 松 RESET，可强行连上被错配置的芯片。
5. 换 USB 口/线，确认目标板 3V3 稳。

---

## [3] SHT31 读取失败 | SHT31 Read Failure

**症状**：串口打印 `SHT31 read fail` 或温湿度恒为 0 / -45°C / 0xFF；I2C 扫描不到 0x44。

**原因**：
- I2C 接线错（SCL/SDA 接反、漏接）。
- 模块无上拉电阻（裸 SHT31 芯片需外接 4.7kΩ 上拉；模块通常自带）。
- 地址错（SHT31 有 0x44 / 0x45 两个地址，由 ADDR 引脚决定）。
- 用了 5V 供电（SHT31 可 2.15–5.5V，但若与 3.3V MCU 共线，电平不匹配会读乱）。

**对策**：
1. 核对引脚：SCL→**PB13**、SDA→**PB14**、VCC→3V3、GND→GND。SCL/SDA 接反是最常见错误。
2. 在 PB13、PB14 各并一个 4.7kΩ 上拉到 3V3（模块无上拉时必须加）。
3. 确认 ADDR 引脚接 GND（地址 0x44）；若接 VCC 则地址 0x45，固件里改地址宏。
4. 全部用 3.3V，不要 5V。
5. 跑 I2C 扫描例程：`HAL_I2C_IsDeviceReady(&hi2c2, 0x44<<1, 3, 100)` 返回 HAL_OK 即通。

---

## [4] OLED 不显示 | OLED No Display

**症状**：屏幕全黑 / 全亮 / 花屏 / 无字符。

**原因**：
- I2C 地址错（0x3C vs 0x3D）。
- 接线错（PB8/PB9 接反，或 VCC/GND 接反）。
- 软件 I2C 时序引脚没初始化成 GPIO 输出。
- OLED 模块是 SPI 版（7 针）而非 I2C 版（4 针）。

**对策**：
1. 核对引脚：SCL→**PB8**、SDA→**PB9**、VCC→3V3、GND→GND。注意 OLED 在 PB8/PB9，**不是** PB13/PB14（那是 SHT31）。
2. 改地址试：`oled.c` 里把 `0x3C` 改成 `0x3D`（部分模块背焊电阻不同）。最稳妥：用万用表量模块上 `D/C` 或 `SA0` 焊盘是否接地。
3. 确认是 **I2C 4 针版**（VCC/GND/SCL/SDA）。7 针是 SPI 版，固件不兼容，换 I2C 版。
4. `OLED_Init()` 后先 `OLED_Clear()` 再 `OLED_ShowString(0,0,"test",16)`，应显示 test。
5. 屏幕全亮（全白）：多半初始化序列没跑完，检查 `OLED_Init()` 是否执行到末尾（可在每步加 printf）。

---

## [5] ESP8266 AT 无响应 | ESP8266 AT No Response

**症状**：STM32 发 `AT` 后串口收不到 `OK`；或收到乱码。

**原因**：
- **波特率不匹配**（最常见）：ESP-01S 出厂默认 115200，但老版 ESP-01 是 9600；或之前被人改过。
- **交叉接线没接对**：TX 接了 TX（应 T 接 R）。
- CH_PD(EN) 没拉高（模块不工作）。
- 供电不足（ESP 发射 WiFi 时瞬态电流大，3.3V 跌落导致重启）。
- AT 固件被刷坏（有人用错了烧录工具把固件擦了）。
- 用了 5V 供电（ESP-01S 只能 3.3V，接 5V 会烧）。

**对策**：
1. **波特率排查**：先用 115200 测；若乱码，改 9600 测。确定真实波特率后，固件 USART3 改成对应值。若想统一用 115200 但模块是 9600：用 USB-TTL 串口模块直连 ESP-01S（VCC/CH_PD→3V3，GND→GND，TX→USB-TTL RX，RX→USB-TTL TX），发 `AT+UART_DEF=115200,8,1,0,0` 改波特率（改完断电重启）。
2. **接线核对**：MCU 的 **PB10(TX)→ESP RX**，**PB11(RX)←ESP TX**。默念「T 接 R，R 接 T」。
3. **CH_PD 必须接 3V3**（直连或串 10kΩ）。不接模块不启动。
4. **供电加固**：VCC 与 GND 间并 **100μF 电解 + 0.1μF 陶瓷**电容；必要时单独用一路 3.3V 电源给 ESP 供电，不与 MCU 共线。
5. **测固件**：USB-TTL 直连，发 `AT` 应回 `OK`；发 `AT+GMR` 看固件版本。若无响应，可能固件坏，用 `ESP8266 Flash Download Tool` 重刷 AT 固件（固件bin 在乐鑫官网或淘宝店家处取）。
6. **永远 3.3V**，ESP-01S 接 5V 即烧。

---

## [6] WiFi 联网失败 | WiFi Connection Failure

**症状**：`AT+CWDHCP` / `AT+CWJAP` 返回 `FAIL` 或一直 `WIFI DISCONNECT`。

**原因**：
- SSID/密码错（大小写、空格、特殊字符）。
- 路由器是 5GHz only（ESP8266 只支持 2.4GHz）。
- 路由器开了 MAC 过滤 / 隐藏 SSID。
- 信号弱（ESP-01S 天线小，距离远/隔墙连不上）。

**对策**：
1. 仔细核对 SSID/密码，注意大小写与首尾空格。手机热点先测（关 5GHz，仅开 2.4GHz）。
2. 路由器开 2.4GHz；若双频合一，先关 5GHz 测。
3. 关闭 MAC 过滤、开放 SSID 广播。
4. ESP-01S 靠近路由器测试；必要时加焊一段导线到天线焊盘增强信号。
5. 发 `AT+CWLAP` 看能否扫描到目标 AP，能扫到说明射频 OK。

---

## [7] SNTP 授时不准 / 不更新 | SNTP Time Sync Issue

**症状**：WiFi 连上了，但时间不对、停留在初始值、或不刷新。

**原因**：
- NTP 服务器域名不通（`pool.ntp.org` 在国内时通时不通）。
- 时区没配（UTC vs 北京时间 UTC+8）。
- SNTP 查询超时（防火墙挡 UDP 123）。

**对策**：
1. 换国内 NTP：`ntp.aliyun.com` / `cn.ntp.org.cn` / `time.windows.com`。
2. 固件里设时区 `AT+CIPSNTPCFG=1,8,"ntp.aliyun.com"`（1=启用，8=UTC+8 北京时间）。
3. 查 `AT+CIPSNTPTIME?` 应返回同步后的时间字符串。
4. 路由器别挡 UDP 123 出站。

---

## [8] 掉电 / 供电不足 | Power Drop / Instability

**症状**：插上 ESP-01S 后 STM32 反复重启；OLED 闪烁；串口输出中断；连 WiFi 瞬间死机。

**原因**：
- ESP-01S 发射时瞬态电流 200–300mA，把 3.3V 拉低，STM32 欠压复位。
- USB 口供电不足（劣质电源/长线/Hub）。
- 面包板接触电阻大。

**对策**：
1. ESP-01S VCC 并 **100μF 电解 + 0.1μF 陶瓷**电容（储能 + 滤高频）。
2. ESP-01S 单独用一路 3.3V 供电（如 AMS1117-3.3 从 USB 5V 单独稳压），与 STM32 的 3.3V 分开，只共 GND。
3. 换高质量 USB 口/线，避开 Hub。
4. 面包板版若供电不稳，直接上 PCB 版（走线电阻小）。

---

## [9] 按键无响应 | Button No Response

**症状**：按键没反应，或不按也触发中断。

**原因**：
- 按键没接 GND（另一脚悬空）。
- 引脚没配 `GPIO_PULLUP` + `GPIO_MODE_IT_RISING/FALLING`。
- 抖动导致一次按下触发多次中断。

**对策**：
1. 按键一脚→PC13（或 PA15），**另一脚必须接 GND**。
2. 固件配 `GPIO_PULLUP`、`GPIO_MODE_IT_FALLING`（按下拉低，下降沿触发）。
3. 中断回调里做 20ms 软件消抖：记录 `HAL_GetTick()`，两次间隔 < 20ms 则忽略。
4. PC13 常是板载 USER 键，可直接用板子上的。

---

## [10] 蜂鸣器不响 / 一直响 | Buzzer Issues

**症状**：不响、声音太小、或一直响不停。

**原因**：
- 用了**有源**蜂鸣器（给电就响，PWM 控不了）。
- PA1 没配成 TIM2_CH2 复用功能。
- PWM 占空比为 0（不响）或 100%（直流，也不响，无源蜂鸣器需交流）。

**对策**：
1. 确认是**无源**蜂鸣器（黑色塑壳，无驱动电路）。
2. PA1 配 `GPIO_AF1_TIM2`、`TIM_OCMODE_PWM1`，`HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2)`。
3. 占空比 50% 响声最大（KE1 例程 Pulse=180/Period=370≈49%）。
4. `Beep_Switch(1)` 开、`Beep_Switch(0)` 关。一直响说明 `Stop` 没调用。

---

## 调试心法 | Debugging Mindset

- **一次只改一处**：改完测，确认有效再改下一处。一次改多处，分不清哪个起作用。
- **从最简到最繁**：先单独测每个模块（SHT31 单独、OLED 单独、ESP 单独），全通再整合。
- **串口是最好的调试器**：在每个关键步骤 `printf` 状态码，比盯着不工作的屏幕强百倍。
- **怀疑电源**：80% 的「玄学问题」（重启、连不上、读错）根因是供电。
- **看 KE1 源码**：本项目固件改编自 UP主 KE1 例程，引脚/外设配置与源码一致。卡住时去 `verify/project02/inspect/` 对照源码看原始实现。

---

## 求助前准备 | Before Asking for Help

收集好以下信息，能让别人 5 分钟内定位问题：
1. **硬件**：开发板型号、各模块型号、接线照片。
2. **现象**：预期 vs 实际，串口打印的完整输出。
3. **已试过**：改过哪些引脚/波特率/电源，结果分别如何。
4. **固件版本**：用的是课程提供的哪个版本，有没有自己改过。

---

*最后更新：2026-06 | Last updated: 2026-06*
