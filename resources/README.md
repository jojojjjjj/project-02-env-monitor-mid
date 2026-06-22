# 参考资源说明 | Resources README

> 本目录存放 UP 主「乐在程上」公开共享的 KE1 开发板例程源码与参考例程。
> These are the KE1 example sources and reference episodes shared by Bilibili creator 乐在程上.

本项目的源码基础来自 B 站 UP 主 **乐在程上** 的「STM32 超简单的开发方法」系列（视频 [BV1tb4y1U7Du](https://www.bilibili.com/video/BV1tb4y1U7Du/)）。本目录保留了与本项目直接相关的核心例程，移除了系列其余各期（与温湿度网络时钟无关，属噪音）。

---

## 文件清单 | File List

### 1. `视频中的例程源码_v0.1.zip`（核心 · CORE）

视频中所用的 KE1 开发板基础例程源码。解压后包含四个 STM32L433 工程（HAL 库 + CubeIDE）：

| 子工程 | 内容 | 本项目用途 |
|---|---|---|
| **KE1_GPIO** | GPIO 输入输出（点灯、按键）| Day 2 点灯 / 按键调时基础 |
| **KE1_PWM** | 定时器 PWM（无源蜂鸣器）| Day 8 整点报时 |
| **KE1_ADC** | ADC 模拟量采集 | 参考学习（本项目主用数字传感器）|
| **KE1_UART** | UART 串口 + AT 命令框架（原为 NB-IoT）| **本项目 ESP8266 WiFi AT 框架的直接来源** |

> ⚠️ 这是本项目软件源码的主要依据，请重点参考 `KE1_UART` 的 AT 命令收发框架。

### 2. `使用说明.txt`

UP 主附带的开发工具版本与版权声明，要点：

- **开发工具版本**：STM32CubeIDE **1.6.1** · ESP SDK V3.4 · Android Studio 4.1.3
- **版权**：「本共享例程源码**无版权，可随意使用**」；所引用 SDK 源码版权归其所有者。
- **注意事项**：STM32CubeIDE **不支持中文路径**，解压后须将工程复制到无中文的路径再导入。

### 3. `NBIoT温湿度采集_参考.zip`（参考 · REFERENCE）

UP 主「STM32 超简单的开发方法」系列中的 NBIoT 温湿度采集一期。本工程提供了本项目直接复用的两个关键驱动：

- **SHT31 驱动**（`Core/Src/i2c.c`）：`KE1_I2C_SHT31_Init()`、`KE1_I2C_SHT31(float *pfTemp, float *pfHumi)`
- **SSD1306 OLED 驱动**（`Core/Src/oled.c` + `oledfont.h`）：`OLED_Init`、`OLED_Clear`、`OLED_ShowString`、`OLED_ShowNum`、`OLED_ShowT_H(float T, float H)`、`OLED_ShowCHinese`、`OLED_DrawBMP` 等（软件 I2C，PB8=SCL / PB9=SDA）

> 原工程用 NB-IoT 上传数据；本项目把通信部分换成 ESP8266 WiFi + SNTP 授时，传感器与显示驱动原样复用。

### 4. `STM32_I2C基础_参考.zip`（参考 · REFERENCE）

STM32 I2C 通信基础参考例程，供想深入理解 I2C 协议时序（起始/停止/应答）的同学参考。本项目主用软件 I2C，此包作为原理补充。

---

## 关于「其余各期」| About the rest of the series

UP 主「乐在程上」的「STM32 超简单的开发方法」系列还有其它各期（ADC 应用、NB-IoT 进阶、Android 端等）。这些内容与「WiFi 温湿度网络时钟」项目目标无关，已作为噪音移除，不在本课程包范围内。如果你对系列其它内容感兴趣，可直接去 UP 主 B 站主页观看。

> Other episodes in the series (ADC apps, NB-IoT advanced, Android client, etc.) are out of scope for this clock project and have been removed as noise. Visit the creator's Bilibili channel if interested.

---

## 版权与致谢 | License & Acknowledgements

- 例程源码：按 UP 主 `使用说明.txt` 声明，「无版权，可随意使用」；引用的 SDK 源码版权归其所有者。
- 本课程包文档：MIT 许可证。
- 特别致谢：UP 主 **乐在程上** 提供的开源教学资源。

---

*最后更新: 2026-06-22 | Last updated: 2026-06-22*
