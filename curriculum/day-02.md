# Day 2: 第一个程序 —— 点灯 + 串口 printf + 烧录流程 | First Program: Blink + UART printf + Flashing

> **学习目标 | Learning Objectives**
> - 把昨天的 `day01_blink` 工程烧进板子，看到 LED 闪烁 + 串口打印 `tick`
> - 理解 GPIO 输出：怎么把一个引脚变高/变低，为什么需要「推挽输出」
> - 理解 UART 异步通信：波特率、起始位、数据位、停止位是怎么回事，为什么 `printf` 能走串口
> - 掌握 ST-Link 烧录 + 串口助手看日志的完整调试闭环

> **产出 | Deliverable**: 板子 LED 闪烁，串口助手稳定收到 `Hello KE1!` 和每 0.5s 一次的 `tick`

---

## 一、前置检查 | Pre-flight Checklist

- [ ] Day 1 的 `day01_blink` 工程能编译通过（0 error）
- [ ] KE1 板插在电脑上，设备管理器有 COM 口
- [ ] 装好一个串口助手（MobaXterm / PuTTY / 友善串口助手 任选）
- [ ] KE1 板有板载 ST-Link（大部分 KE1 板有；若没有，准备一个外部 ST-Link V2 小板，淘宝 ¥10）

---

## 二、GPIO 输出原理 —— 怎么点亮一个 LED | GPIO Output: Lighting an LED

### 2.1 LED 电路的真相

板载 LED 的接法通常是：`3.3V → LED → 限流电阻 → GPIO 引脚`（或反过来 `GPIO → 电阻 → LED → GND`）。

- 当 GPIO 输出**低电平 (0)**：电流流过 LED → 亮（共阳接法）
- 当 GPIO 输出**高电平 (3.3V)**：两端电压差为 0 → 灭

KE1 板的 LED 具体是共阳还是共阴，看你板子原理图。**点不亮先试着 `TogglePin` 几次**——程序对，LED 接法反了，最多就是「该亮的时候灭、该灭的时候亮」，不会烧。

> **WHY a current-limit resistor?** LED 是电流驱动器件，没有电阻的话电流会瞬间变大烧毁 LED 和 GPIO。板载 LED 已经焊了限流电阻，你自己外接 LED 一定要串一个 220Ω~1kΩ。

### 2.2 GPIO 是什么？

GPIO = General Purpose Input/Output，通用输入输出。每个 GPIO 引脚可以配置成：
- **输出模式**：你控制它是高 (3.3V) 还是低 (0V) —— 今天用这个点亮 LED
- **输入模式**：你读它是高还是低 —— Day 8 按键用
- **复用功能 (AF)**：引脚交给硬件外设（USART/I2C/SPI）—— 今天 USART1 就是 AF

### 2.3 推挽输出 vs 开漏输出（讲 WHY）

配置 GPIO 输出时 CubeMX 给两个选项：`Push-Pull`（推挽）和 `Open-Drain`（开漏）。

| 模式 | 高电平 | 低电平 | 用途 |
|------|--------|--------|------|
| **推挽 Push-Pull** | 主动输出 3.3V | 主动输出 0V | 驱动 LED、普通输出——**默认选这个** |
| **开漏 Open-Drain** | 高阻态（不输出） | 主动输出 0V | I2C 总线、电平转换 |

> **WHY Push-Pull for LED?** 推挽既能拉高也能拉低，驱动能力强。开漏只能拉低，拉高要靠外部上拉电阻——LED 不需要这个复杂度。**记住：普通 GPIO 输出选推挽。** Day 3 的 I2C 才会用到开漏。

### 2.4 HAL 库怎么操作 GPIO

```c
// 写高
HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
// 写低
HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);
// 翻转（取反）
HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
// 读输入（Day 8 按键用）
GPIO_PinState s = HAL_GPIO_ReadPin(BTN_GPIO_Port, BTN_Pin);
```

- `LED_GPIO_Port` 和 `LED_Pin` 是 CubeMX 根据你在 Day 1 给 PA5 起的 Label `LED` 自动生成的宏，在 `main.h` 里。
- **HAL** = Hardware Abstraction Layer，硬件抽象层。它把「写寄存器」封装成函数，这样换芯片也能用。

> **WHY HAL not bare registers?** 零基础直接读写寄存器要查 1000 页的参考手册。HAL 用函数名就能猜出意思，学习曲线平缓得多。代价是代码体积大一点、速度慢一点——这个项目完全不在乎。

---

## 三、UART 异步通信原理 —— printf 怎么走串口 | UART: How printf Reaches the Serial Port

### 3.1 串口通信的「异步」是什么意思

两根线：**TX（发送）** 和 **RX（接收）**。发送方把数据一位一位往外甩，接收方一位一位往里收。

- **同步通信**（如 I2C、SPI）：有一根单独的**时钟线 (SCL/SCK)**，发送方拉一下时钟，接收方就读一下数据。两边节奏完全锁定。
- **异步通信**（UART）：**没有时钟线**。两边事先约定好「每秒发多少位」（这就是**波特率 baud rate**），各自用自己的时钟按这个节奏发/收。

> **WHY no clock line is OK?** 因为双方约定了同样的波特率（比如 115200 bit/s），接收方按这个频率采样就行。代价是：**两边波特率必须一致**，差一点就会采样错位、收到乱码。这是串口调试 90% 的问题来源。

### 3.2 一个数据帧长什么样

发送一个字节 `0x41`（字符 'A'，二进制 `0100 0001`）在 115200 8N1 模式下：

```
空闲 ___    START   D0 D1 D2 D3 D4 D5 D6 D7   STOP   空闲 ___
        \___↓_____↓__↓__↓__↓__↓__↓__↓__↓__↓_____↓__________/
          0    1   0  1  0  0  0  0  1  0    1
       起始位   ←──── 数据位 (LSB first) ────→  停止位
```

- **起始位**：1 个低电平，告诉接收方「来了」
- **数据位**：8 位（这就是 `8N1` 里的 `8`），低位先发
- **校验位**：`N` = None，不要校验
- **停止位**：1 个高电平（这就是 `1`）

**115200 8N1** = 波特率 115200，8 数据位，无校验，1 停止位。这是 STM32 默认串口配置，**串口助手必须和它完全一致**才能正确收。

### 3.3 为什么 `printf` 能走串口

C 标准库的 `printf` 最终会调用一个底层函数 `fputc`（或 GCC 下的 `__io_putchar`）来输出一个字符。默认这个函数指向屏幕，但在嵌入式上没有屏幕，所以我们要**重定向 (retarget)** 它——让它把字符通过 `HAL_UART_Transmit` 发到 USART1。

```c
// 这就是 Day 1 抄的那段「咒语」
PUTCHAR_PROTOTYPE
{
    HAL_UART_Transmit(&huart1, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
    return ch;
}
```

- `huart1` 是 USART1 的句柄（CubeMX 生成）
- `HAL_UART_Transmit(..., 1, HAL_MAX_DELAY)` = 发 1 个字节，死等发完
- `printf("tick\r\n")` 会逐字符调用这个函数 → 每个字符从 PA9 (USART1_TX) 发出 → USB 转串口 → 电脑串口助手显示

> **WHY `\r\n` not just `\n`?** 串口助手很多按「`\r` 回车 + `\n` 换行」才正确换行。只发 `\n` 在 PuTTY 里可能不换行。养成 `\r\n` 习惯。

---

## 四、烧录流程 —— 把代码塞进芯片 | Flashing: Pushing Code Into the Chip

### 4.1 三种烧录方式（KE1 板常用前两种）

| 方式 | 接口 | 速度 | 能调试断点 | 本课程用 |
|------|------|------|-----------|---------|
| **ST-Link** | SWD（SWDIO+SWCLK+GND） | 快 | ✅ 能 | ✅ 主力 |
| **USB 虚拟串口 + ISP** | USB | 中 | ❌ | 备用（如果板子带 USB DFU） |
| **串口 ISP（BOOT0=1）** | USART1 | 慢 | ❌ | 应急 |

### 4.2 ST-Link 烧录步骤

1. 确认 KE1 板的 ST-Link SWD 接线和电脑连通（板载 ST-Link 的话 USB 线就行）。
2. CubeIDE 里右键工程 → `Run As → STM32 MCU Debug`（或点工具栏小虫子图标）。
3. 第一次会弹出 Debug Configuration，确认 ST-LINK 被识别，点 Debug。
4. 程序烧进去后停在 `main()` 开头，按 **F8 (Resume)** 全速运行。
5. LED 开始闪，串口助手开始收 `tick`。

> ✅ **检查点 2.1**: 看到 LED 闪烁 + 串口收到 `Hello KE1!` 和 `tick` → 烧录闭环通了。

### 4.3 不调试、直接烧（更快）

调试时要停下来看断点，慢。平时改完代码想快速看效果：右键工程 → `Run As → STM32 MCU C/C++ Application`（不带 Debug），直接烧录运行。

---

## 五、串口助手看日志 —— 你的「眼睛」 | Serial Terminal: Your Eyes

嵌入式开发没有屏幕调试器，**串口 printf 是你看程序状态的唯一窗口**。今天必须熟练。

### 5.1 推荐工具

| 软件 | 平台 | 优点 |
|------|------|------|
| **MobaXterm** | Windows | 免费、多标签、SSH/串口一体 |
| **PuTTY** | 全平台 | 极简、老牌 |
| **友善串口助手** | Windows | 中文、能看 hex、能存日志 |
| **VS Code + Serial Monitor 插件** | 全平台 | 写代码看日志一个窗口 |

### 5.2 打开串口的正确姿势

1. 波特率：**115200**（必须和程序一致）
2. 数据位 8 / 停止位 1 / 校验 None / 流控 None（即 8N1）
3. 选对 COM 口（Day 1 记下的那个）
4. 点「打开串口」

### 5.3 给 printf 加时间戳（实用技巧）

```c
/* USER CODE BEGIN 0 */
#include <stdio.h>
#include <stdarg.h>
extern UART_HandleTypeDef huart1;

void log(const char *fmt, ...) {
    char buf[128];
    va_list ap;
    va_start(ap, fmt);
    int len = vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);
    HAL_UART_Transmit(&huart1, (uint8_t*)buf, len, HAL_MAX_DELAY);
}
/* USER CODE END 0 */
```

调用 `log("[%lu] tick\r\n", HAL_GetTick())` —— `HAL_GetTick()` 返回开机以来毫秒数，方便看时间间隔。

---

## 六、常见错误 | Common Errors

| 现象 | 原因 | 解决 |
|------|------|------|
| 烧录报错 `No ST-LINK detected` | ST-Link 驱动没装 / USB 线不行 | 重装 CubeIDE 勾 ST-LINK 驱动；换数据线 |
| 烧录报错 `Target not connected` | SWD 接线松 / 芯片被锁 | 检查 SWDIO/SWCLK/GND；按住板子 RESET 再烧 |
| 烧录成功但 LED 不闪 | 引脚标签 `LED` 和实际板载 LED 引脚对不上 | 查你板子原理图，改 CubeMX 引脚，重新 Generate |
| LED 闪但串口收到乱码 | 波特率不匹配 | 串口助手改 115200；或检查 USART1 Baud Rate 配置 |
| 串口什么都收不到 | 没重定向 `__io_putchar` / USART1 没初始化 / COM 口选错 | 回 Day 1 §5.4 检查；确认 `MX_USART1_UART_Init()` 被调用 |
| `printf` 不换行 | 只发了 `\n` | 改成 `\r\n` |
| 烧录后程序不跑 | BOOT0 拉高了 | 检查板子 BOOT0 跳线 = 0（正常运行模式） |

---

## 七、调试技巧 | Debugging Tips

1. **最小化问题**: LED 不亮？先写 `HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);` 写死低电平，看 LED 常亮不常亮——分离「引脚配错」和「Toggle 逻辑错」。
2. **串口是示波器**: 怀疑某段代码跑没跑，在那段前后 `printf("A\r\n"); ... printf("B\r\n");`，看串口有没有 AB。
3. **`HAL_GetTick()` 测时间**: 在两段代码前后读 tick，差值就是耗时毫秒数。比肉眼看准。
4. **断点调试**: CubeIDE Debug 模式下双击代码行号设断点，运行到那里会停，鼠标悬停变量看值。**这是排查逻辑 bug 的核武器**。
5. **复位看启动**: 串口助手开着，按板子 RESET 键，应该能看到 `Hello KE1!` 重新打印——确认程序每次上电都从头跑。

---

## 八、今日检查点 | Day 2 Checkpoints

- [ ] `day01_blink` 烧进板子，LED 闪烁
- [ ] 串口助手 115200 8N1 打开，收到 `Hello KE1! Day 1 alive.` 和持续 `tick`
- [ ] 能解释「为什么串口两边波特率必须一致」
- [ ] 能解释「为什么 `printf` 要重定向 `__io_putchar`」
- [ ] 会用 CubeIDE 断点调试（设一个断点，跑到那里停下，看变量）
- [ ] 截图：串口助手收到 `tick` 的画面 + 板子 LED 亮着的照片，存进 week-1-checkin.md

---

## 九、今日作业 | Homework

1. **改闪烁频率**: 把 `HAL_Delay(500)` 改成 `100`，观察串口 `tick` 间隔变化（应该 ~100ms）。再改回 500。
2. **SOS 摩斯码**: 用 GPIO 写一个 SOS（三短三长三短，短=200ms，长=600ms，字母间隔 200ms），串口同步打印 `.` 和 `-`。
3. **串口回显**: 用 `HAL_UART_Receive` 阻塞收 1 个字符，收到后立刻 `printf` 回显出来。在串口助手键盘输入，看回显。（这会用到中断，做不出就记下问题，Day 5 会系统讲。）
4. **回答**:
   - 推挽输出和开漏输出的区别？LED 该用哪个？
   - 115200 8N1 各代表什么？
   - 为什么 `printf` 默认在 STM32 上不输出？怎么解决？
5. **Git 提交**:
   ```bash
   git add curriculum/day-02.md
   git commit -m "day02: blink + uart printf + flashing flow"
   ```

---

## 十、明日预告 | Tomorrow

**Day 3: SHT31 温湿度传感器 —— I2C 原理 + 接线 + 烧录驱动读数值**
- 系统讲 I2C 协议（SCL/SDA、地址、ACK、开漏+上拉）
- 接 SHT31 到 PB13/PB14，烧 UP主提供的驱动
- 串口打印真实温度湿度数值，用手捂热看数值变化

**前置准备**: 把今天的板子收好；找一卷杜邦线（母对母 4 根）准备明天接 SHT31。

---

*最后更新: 2026-06 | Last updated: 2026-06*
