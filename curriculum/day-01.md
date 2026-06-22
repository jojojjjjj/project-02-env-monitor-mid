# Day 1: 项目导览 + 认识 STM32L433 (KE1 板) + 工具链安装 | Project Tour + Meet the STM32L433 (KE1 Board) + Toolchain

> **学习目标 | Learning Objectives**
> - 理解我们要复刻的「WiFi 温湿度网络时钟」到底是什么、由哪些模块组成
> - 认识主控芯片 STM32L433 和 UP主「乐在程上」的 KE1 教学板，理解为什么选它
> - 理解「复刻 (replication)」学习模式：代码已提供，你负责接线 + 烧录 + 配置 + 调试
> - 在自己电脑上装好 STM32CubeIDE，能新建一个能编译通过的工程
>
> **产出 | Deliverable**: 一台能被电脑识别出 COM 口的 KE1 板 + 一个能在 CubeIDE 里编译通过的空工程

---

## 一、前置检查 | Pre-flight Checklist

开始今天之前，确认你手上和电脑上都有这些：

| 项目 | 要求 | 怎么检查 |
|------|------|---------|
| 硬件套件 | STM32L433 KE1 板 (或兼容 STM32L433 最小系统板)、ESP-01S、SHT31、SSD1306 OLED、USB-TypeC/Micro-USB 线 | 对照 `hardware/BOM.md` 清点 |
| 电脑 | Windows 10/11（Mac/Linux 也可，但本课程截图以 Windows 为准） | — |
| USB 口 | 至少一个空闲 USB 口 | 板子插上后能亮灯 |
| 网络 | 能访问 ST 官网下载 CubeIDE | 浏览器打开 `st.com` 试试 |
| 心态 | 零基础没关系，但要肯读报错信息 | — |

> ⚠️ **重要提醒**: 今天不写任何代码。今天的核心是「把工具装好、把板子点亮」。磨刀不误砍柴工。

---

## 二、我们要复刻什么？| What Are We Replicating?

### 2.1 项目一句话介绍

我们要复刻 UP主「乐在程上」的 Bilibili 视频 [`BV1tb4y1U7Du`](https://www.bilibili.com/video/BV1tb4y1U7Du/) —— 一台 **WiFi 温湿度网络时钟**：摆在桌上，OLED 屏幕显示时间、温度、湿度，时间通过 WiFi 自动校准（网络授时），不用手调。

> **One-sentence summary**: We're replicating UP主 乐在程上's Bilibili video — a **WiFi temp/humidity network clock**: a desktop ornament whose OLED shows time, temperature, and humidity, with the time auto-synced over WiFi (SNTP), no manual setting.

### 2.2 为什么叫「网络时钟」？

普通电子时钟靠芯片内部的晶振计时，走久了会慢几秒几分钟。**网络时钟**每隔一段时间通过 WiFi 向互联网上的 NTP 服务器「对一次表」，所以永远准。这是物联网 (IoT) 设备最典型的能力：**能联网、能拿云端的真实数据**。

> A normal clock drifts. A **network clock** periodically asks an NTP server on the internet for the correct time over WiFi, so it stays accurate. This is the most typical IoT capability: **it can go online and fetch real data from the cloud**.

### 2.3 系统架构图（先看懂这张图，后面 10 天都在填它）

```
                 ┌──────────────┐
   SHT31 (I2C) ──┤              ├── SSD1306 OLED (软件 I2C, 0.96")
   蜂鸣器(PWM) ──┤  STM32L433   ├── ESP-01S / ESP8266 (UART, AT 固件 → WiFi SNTP)
   按键 (GPIO) ──┤   (KE1 板)   ├── USB (供电 + 调试串口)
                 └──────┬───────┘
                        │ UART (AT 命令)
                 ┌──────▼───────┐
                 │   ESP8266    │── WiFi ── NTP 服务器 (网络授时)
                 └──────────────┘
```

**每个模块的职责（讲 WHY）**:

| 模块 | 干什么 | 为什么需要它 |
|------|--------|-------------|
| **STM32L433** | 主控 MCU，跑固件 | 它是「大脑」，但**没有 WiFi**——所以需要下面的 ESP8266 当「网卡」 |
| **ESP8266 (ESP-01S)** | WiFi 协处理器 | L433 没有 WiFi 硬件，用 ESP8266 通过串口 AT 命令帮它联网、对时 |
| **SHT31** | 测温湿度 | I2C 接口，±0.2°C / ±2%RH，比 DHT11 准一个数量级 |
| **SSD1306 OLED** | 显示 | 0.96" 128×64，I2C，显示时间/温湿度 |
| **蜂鸣器** | 整点报时 | 选做，用 PWM 驱动无源蜂鸣器 |
| **按键** | 手动调时 | 选做，断网时备用 |

> **关键认知**: STM32L433 和 ESP8266 是**两块独立的芯片**，通过串口(UART)用「AT 命令」这种文字协议通信。这不是一块带 WiFi 的芯片（比如 ESP32），而是「主控 + 网卡」的经典分工。理解这个分工，你就理解了一大半架构。

### 2.4 「复刻」学习模式说明

| 传统项目课 | 本项目的「复刻」模式 |
|-----------|---------------------|
| 老师讲原理，你从零写代码 | UP主的固件代码**已经提供**在 `software/src/` |
| 重点在「写」 | 重点在「读得懂 + 接得对 + 烧得进 + 调得好」 |
| 容易卡在语法 | 卡点在硬件接线、工具链、AT 命令时序——这些才是真实工程能力 |

> **Why replication?** 零基础学员从零写 STM32 固件会被 HAL 库、寄存器、链接脚本淹没。复刻模式下，**代码是脚手架**，你站在脚手架上学习「真实硬件工程」的流程：看原理图 → 接线 → 配 CubeMX → 编译烧录 → 看串口日志 → 排错。这才是你以后做任何嵌入式项目都要用的核心能力。

---

## 三、认识 STM32L433 和 KE1 板 | Meet the STM32L433 & KE1 Board

### 3.1 STM32L433 是什么？

STM32 是 ST（意法半导体）公司的 32 位 ARM Cortex-M 单片机系列。**L4** 子系列主打**低功耗 + 性能平衡**，L433 是其中一颗：

- 内核：ARM Cortex-M4，最高 80MHz（KE1 板跑 32MHz）
- Flash：256KB，RAM：64KB（对我们这个项目绰绰有余）
- 封装：LQFP48（KE1 板上的 CBT6 是 48 脚）
- 自带外设：I2C ×3、USART ×3、SPI ×2、ADC、定时器……**但没有 WiFi/蓝牙**

> **Why L433 and not the cheaper F103?** L4 系列更新、低功耗更好、Flash/RAM 更大，且 UP主 的 KE1 教学板用的就是它——我们复刻视频，自然跟着用同一颗芯片，引脚、时钟配置才能对得上。

### 3.2 KE1 板是什么？

KE1 是 UP主「乐在程上」为教学设计的 STM32L433 开发板，板载：
- STM32L433CBT6 主控
- USB-TypeC 接口（供电 + 虚拟串口 + 烧录，板载 ST-Link 或 USB 转串口芯片）
- 8MHz HSE 晶振
- 引出所有 GPIO，方便插 SHT31/OLED/ESP-01S
- 板载一个 LED（用于「点灯」实验，一般在 PB5 或 PA5，以你的板子丝印为准）

> ⚠️ **买不到 KE1 板怎么办？** 用任何 STM32L433 最小系统板都能复刻，只是引脚要按 `hardware/wiring-guide.md` 重新映射。课程以 KE1 板的引脚为准。

### 3.3 看看板子：识别关键位置

拿起你的 KE1 板，找到这些位置（对照板子丝印）：

```
        ┌──────── USB-TypeC ────────┐
        │                            │
   [LED]│  ┌──────────────────┐     │
        │  │   STM32L433CBT6  │     │
        │  │   (主控芯片)      │     │
        │  └──────────────────┘     │
        │   [8MHz 晶振]              │
        │                            │
        │  PA0 PA1 PA9 PA10 ...      │  ← 排针引出的 GPIO
        │  PB8 PB9 PB10 PB13 PB14   │  ← 今天记住这几个，后面天天用
        └────────────────────────────┘
```

**今天必须记住的引脚**（后面 9 天反复出现）：

| 引脚 | 功能 | 用在哪 |
|------|------|--------|
| **PA9 / PA10** | USART1 TX/RX | 调试串口 printf（USB 看日志） |
| **PB10 / PB11** | USART3 TX/RX | 连 ESP8266，发 AT 命令 |
| **PB13 / PB14** | I2C2 SCL/SDA | 硬件 I2C，连 SHT31 |
| **PB8 / PB9** | 软件 I2C | 连 SSD1306 OLED |
| **板载 LED** | GPIO 输出 | 今天点灯用 |

---

## 四、安装工具链：STM32CubeIDE | Install the Toolchain: STM32CubeIDE

### 4.1 为什么用 CubeIDE？

写 STM32 程序有几条路：Keil（收费、Windows）、裸 Makefile+GCC（配置烦）、**STM32CubeIDE（免费、跨平台、ST 官方、自带 CubeMX 图形化配引脚）**。我们用 CubeIDE——它把「配引脚时钟」和「写代码编译」合在一个软件里，对零基础最友好。

> **Why CubeIDE?** It's free, official, cross-platform, and bundles CubeMX (graphical pin/clock config) with a GCC compiler and debugger. For zero-foundation students, one tool does everything.

### 4.2 下载与安装（约 30-60 分钟，取决于网速）

1. **注册 ST 账号**（可选但推荐，下载更快）：访问 `https://www.st.com/en/development-tools/stm32cubeide.html`，点 "Get Software"，会要求登录/注册。
2. **下载** 对应你系统的安装包（Windows 选 `stm32cubeide_win.zip` 或 `.exe`）。版本 **1.6.1 或更高**都行。
3. **安装**：双击运行，全部默认下一步。注意安装最后会问要不要装 **ST-LINK 驱动**，**必须勾上**——这是烧录和调试的驱动。
4. **安装后重启电脑**（让驱动生效）。

### 4.3 验证安装：插上板子，看 COM 口

1. 用 USB 线把 KE1 板插上电脑。
2. Win+X → 设备管理器 → 展开 "端口 (COM 和 LPT)"。
3. 应该能看到一个新设备，名字类似 `STMicroelectronics Virtual COM Port (COM3)` 或 `USB Serial Device (COM3)`。**记住这个 COM 号**，后面天天用。

> ✅ **检查点 1.1**: 设备管理器能看到 COM 口 → 驱动装好了。看不到？见下方「常见错误」。

---

## 五、在 CubeIDE 里新建一个能编译的空工程 | Create a Compilable Empty Project

这一步是今天下午的重头戏。目标：让 CubeIDE 认识你的 STM32L433，配好最小系统（时钟 + 一个 LED + 调试串口），编译通过。

### 5.1 新建工程

1. 打开 CubeIDE，选一个 workspace 目录（路径**不要有中文和空格**，比如 `D:\ke1_ws`）。
2. `File → New → STM32 Project`。
3. 搜 `L433`，选 `STM32L433CBTx`（KE1 板就是这个），点 Next。
4. Project Name 填 `day01_blink`，Targeted Language 选 **C**，点 Finish。
5. 弹出 "Initialize all peripherals with their default Mode?" 选 Yes。打开 CubeMX 图形界面（芯片引脚图）。

### 5.2 配时钟（讲 WHY）

STM32 上电默认用内部 16MHz HSI，但精度差（±1%），跑串口/USB 会偏。KE1 板有 8MHz 外部晶振 (HSE)，我们用它 + PLL 倍频到 32MHz。

1. 左侧 `Pinout & Configuration → System Core → RCC`，把 **High Speed Clock (HSE)** 改成 `Crystal/Ceramic Resonator`。
2. 切到 `Clock Configuration` 标签页，把 `HSE` 设为输入，PLL Source 选 HSE，`PLLM=1, PLLN=8, PLLR=2`，SYSCLK 选 PLLCLK，最终 `HCLK = 32 MHz`。（KE1 固件就是这么配的，见参考源码 `SystemClock_Config()`。）

> **WHY 32MHz not 80MHz?** L433 最高能跑 80MHz，但 32MHz 已经够这个项目用，且功耗低、串口分频更整。UP主 固件用 32MHz，复刻要对齐。

### 5.3 配一个 GPIO 输出（板载 LED）和调试串口 USART1

1. 在引脚图上找到板载 LED 对应的引脚（查你的板子丝印，假设是 **PA5**），点它选 `GPIO_Output`。
2. 左侧 `System Core → GPIO`，给 PA5 起个用户标签 `LED`。
3. 左侧 `Connectivity → USART1`，Mode 选 `Asynchronous`（异步串口），参数页把 Baud Rate 设 `115200`。USART1 默认走 PA9/PA10，正好和 KE1 一致，不用改引脚。
4. `Project → Generate Code`（或 Ctrl+S）。

### 5.4 让 printf 走串口（讲 WHY）

CubeMX 生成的代码里 `printf` 默认**什么都不输出**——因为 C 标准库不知道你要往哪个串口发。我们要重定向 `__io_putchar`。在 `main.c` 的 `/* USER CODE BEGIN 0 */` 区里加：

```c
/* USER CODE BEGIN 0 */
#include <stdio.h>
#ifdef __GNUC__
#define PUTCHAR_PROTOTYPE int __io_putchar(int ch)
#else
#define PUTCHAR_PROTOTYPE int fputc(int ch, FILE *f)
#endif
PUTCHAR_PROTOTYPE
{
    HAL_UART_Transmit(&huart1, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
    return ch;
}
/* USER CODE END 0 */
```

> **WHY this matters**: 这段是 STM32 串口 printf 的「标准咒语」。KE1 参考源码 `usart.c` 里就是这么写的。看不懂没关系，照抄，Day 2 会讲每一行。关键：**必须放在 `USER CODE BEGIN/END` 之间**，否则下次 Generate Code 会被覆盖。

### 5.5 在 main 循环里点灯 + 打印

在 `main()` 的 `/* USER CODE BEGIN WHILE */` 后：

```c
/* USER CODE BEGIN WHILE */
printf("Hello KE1! Day 1 alive.\r\n");
while (1)
{
    HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
    printf("tick\r\n");
    HAL_Delay(500);
    /* USER CODE END WHILE */
}
```

### 5.6 编译

按 **Ctrl+B** 编译。Console 应该出现 `Build Finished. 0 errors, 0 warnings.`

> ✅ **检查点 1.2**: 编译 0 error → 工具链完全就绪。今天**不烧录**也行（烧录放 Day 2 专门讲），但如果你想现在就看到灯闪，可以按 Run 按钮，CubeIDE 会用板载 ST-Link 烧进去。

---

## 六、常见错误 | Common Errors

| 现象 | 原因 | 解决 |
|------|------|------|
| 设备管理器看不到 COM 口 | USB 线是「只能充电」的线 / ST-Link 驱动没装 | 换一根能传数据的 USB 线；重装 CubeIDE 时勾上 ST-LINK 驱动 |
| 设备管理器有黄色感叹号 | 驱动冲突 | 右键 → 卸载设备 → 拔插重装 |
| CubeIDE 新建工程找不到 L433 | 芯片库没下载 | 装新版 CubeIDE（1.10+ 自带全系列 MCU 包） |
| 编译报错 `cannot find -lstdc++` | 工具链没装全 | 重装 CubeIDE，别自定义跳过组件 |
| `printf` 编译过但串口没输出 | 没重定向 / USART1 没初始化 / 波特率不对 | 检查 5.4 的代码块；串口助手用 115200 打开对应 COM |
| 编译警告 `LED_Pin undeclared` | PA5 标签没起名 `LED` 或没 Generate Code | 回 CubeMX 给引脚起 Label，重新 Generate |

---

## 七、调试技巧 | Debugging Tips

1. **报错从上往下看第一个**：C 编译器第一个错误后面经常是一连串「被牵连」的错误，只修第一个再编译，往往少一大半。
2. **Console 别关**：CubeIDE 底部 Console 窗口显示编译/烧录的完整输出，报错都在这。
3. **串口助手推荐**: 用 **MobaXterm / PuTTY / 友善串口助手**，波特率 115200，8N1。先确认能收到板子的 `tick` 再继续。
4. **USER CODE 区是命根子**: 永远只在自己代码写在 `/* USER CODE BEGIN X */ ... END X */` 之间。写在别处，下次 Generate 会被删。

---

## 八、今日检查点 | Day 1 Checkpoints

- [ ] 能用自己的话讲清楚「STM32L433 + ESP8266」为什么是两块芯片、各自干嘛
- [ ] 设备管理器能看到 KE1 板的 COM 口
- [ ] CubeIDE 装好，新建了 `day01_blink` 工程
- [ ] 工程编译 0 error（点灯 + printf 代码已加，但今天不要求烧录看到效果，那是 Day 2）
- [ ] 截图：CubeIDE 编译通过的 Console 输出，存到 `assignments/week-1-checkin.md` 里 Day1 的位置

---

## 九、今日作业 | Homework

1. **读**: 浏览 Bilibili 视频 [`BV1tb4y1U7Du`](https://www.bilibili.com/video/BV1tb4y1U7Du/) 的前 5 分钟，对最终成品有直观印象。
2. **画**: 在纸上或用 [draw.io](https://app.diagrams.net/) 画一遍 §2.3 的系统架构图，标注每个模块的「职责」和「为什么需要它」。拍照存档。
3. **写**: 在 `assignments/week-1-checkin.md` 的 Day 1 小节填写：COM 口号、CubeIDE 版本、编译是否通过、遇到的 1 个坑及怎么解决的。
4. **Git 提交**（养成习惯）:
   ```bash
   cd project-02-env-monitor-mid
   git add curriculum/day-01.md assignments/week-1-checkin.md
   git commit -m "day01: toolchain ready, project compiles"
   ```

---

## 十、明日预告 | Tomorrow

**Day 2: 第一个程序 —— 点灯 + 串口 printf + 烧录流程**
- 把今天的代码烧进板子，看到 LED 闪烁 + 串口打印 `tick`
- 系统讲 GPIO 输出和 UART 异步通信的原理
- 学会 ST-Link 烧录 + 串口助手看日志的完整闭环

**前置准备**: 把今天的 `day01_blink` 工程编译通过；装好一个串口助手软件。

---

*最后更新: 2026-06 | Last updated: 2026-06*
