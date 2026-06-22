# Day 5: ESP8266 WiFi 模块 —— AT 固件 + 接线 + AT 命令试通 | ESP8266 WiFi: AT Firmware + Wiring + AT Commands

> **English summary**: Today we add WiFi to the clock. The ESP-01S module is a "WiFi coprocessor" that the STM32L433 talks to over UART using text-based AT commands. The big traps are power (ESP-01S needs its own 3.3V rail) and baud rate. By end of day the board is connected to your WiFi.

> **⏱ 预计耗时 | Estimated Time**: 约 5-6 小时 | ~5-6 hours（供电调试最耗时）

> **学习成果 | Learning Outcomes**
> - **识别** ESP-01S (ESP8266) 作为「WiFi 协处理器」的角色，**解释**为什么主控+WiFi 模组要用 AT 命令通信而不是在 STM32 上跑 WiFi 协议栈
> - **实现** ESP-01S 与 KE1 板 USART3 (PB10/PB11) 的接线，**分析**电平匹配和独立供电的必要性（瞬态电流 300-400mA）
> - **解释**串口中断接收 + 环形缓冲区的工作原理，对比 Day 2 阻塞接收的区别
> - **实现** `AT`/`AT+GMR`/`AT+CWMODE`/`AT+CWJAP` 命令序列，让 ESP8266 连上你的 WiFi 并收到 `WIFI GOT IP`

## 为什么学这个 | Why This Matters

STM32L433 是一颗很强的大脑，但它「不懂 WiFi」——它没有无线射频电路。ESP8266 是一颗「只懂 WiFi」的小芯片。把它们用串口连起来，就相当于**给一个不会说外语的聪明人雇了个翻译**：你（STM32）用中文（AT 命令）告诉翻译「帮我连上 WiFi」「帮我问一下现在几点」，翻译（ESP8266）用外语（WiFi 协议）去办，办完用中文回报结果。这种「主控 + 协处理器」分工是工业界最常见的联网方案——今天你亲手搭一遍。注意：今天 ESP-01S 的供电是本项目第一大坑，**吃不好电它就反复复位、AT 全无响应**，务必用独立 3.3V。

> **产出 | Deliverable**: 串口能看到 ESP8266 回复 `OK`，并能成功连上 WiFi（`WIFI CONNECTED` / `WIFI GOT IP`）

---

## 一、前置检查 | Pre-flight Checklist

- [ ] Day 4 的 OLED + SHT31 已跑通
- [ ] 手上有 ESP-01S 模块（8 针）+ 一个稳定的 3.3V 电源（ESP-01S 瞬态电流可达 300mA+，KE1 板载 LDO 可能不够）
- [ ] 知道自己 WiFi 的 SSID（名称）和密码（**用 2.4GHz WiFi，不是 5GHz**——ESP8266 只支持 2.4G）
- [ ] 杜邦线若干 + 可能需要一个 AMS1117-3.3 模块做独立供电

---

## 二、为什么是 ESP8266 + AT 命令 | Why ESP8266 + AT Commands

### 2.1 两块芯片的分工（再次强调）

回忆 Day 1 的架构：**STM32L433 是大脑（没 WiFi），ESP8266 是网卡**。它们之间通过**串口 (UART)** 用一种叫 **AT 命令**的文字协议沟通：

```
STM32L433                          ESP8266 (ESP-01S)
  PB10 TX ────────────────────► RX
  PB11 RX ◄──────────────────── TX
         (USART3, 115200, 文字)
  
  STM32 发: "AT\r\n"          →  ESP 回: "AT\r\r\nOK\r\n"
  STM32 发: "AT+CWJAP=\"ssid\",\"pwd\"\r\n" → ESP 回: "WIFI CONNECTED...OK"
```

**AT 命令**就是以 `AT` 开头、`\r\n` 结尾的文字指令，源自 90 年代调制解调器标准。ESP8266 出厂烧的「AT 固件」内置了一套 WiFi 相关的 AT 命令集，你发命令、它执行并回复。

> **WHY AT commands and not a library on STM32?** 两个选择：(1) STM32 自己跑 WiFi 协议栈——但 L433 没有足够 RAM/算力，且 ST 没给现成 lwIP+WiFi 栈给 L433。(2) 把 WiFi 交给专门的 ESP8266，STM32 只发高层文字命令——简单、可靠、分工清晰。UP主 选了 (2)，这是工业界「主控+WiFi 模组」的标准做法。

### 2.2 ESP-01S 是什么

ESP-01S 是 ESP8266 芯片的最小模块：8 针，自带 2MB Flash，板载天线，3.3V 供电，跑乐鑫官方 AT 固件。关键引脚：

| ESP-01S 引脚 | 功能 | 接哪 |
|-------------|------|------|
| VCC | 3.3V 供电 | **独立 3.3V 电源**（别用 KE1 板载 LDO，电流不够） |
| GND | 地 | 和 KE1 共地 |
| TX | 串口发送 | → KE1 PB11 (USART3_RX) |
| RX | 串口接收 | ← KE1 PB10 (USART3_TX) |
| EN (CH_PD) | 使能，必须拉高 | → 3.3V（通过 10kΩ 电阻） |
| RST | 复位，低有效 | 悬空或接 3.3V（可接一个按钮手动复位） |
| GPIO0 | 启动模式 | 正常运行：拉高或悬空；烧录固件：拉低 |
| GPIO2 | 启动模式 | 悬空（内部上拉） |

### 2.3 供电是最大的坑（讲 WHY）

ESP-01S 在 WiFi 发射瞬间峰值电流可达 **300-400mA**。KE1 板的 3.3V 通常来自 USB → LDO，LDO 额定可能只有 300-500mA，带不动 ESP-01S 瞬态 → **ESP-01S 反复复位、AT 无响应、连不上 WiFi**。

> **WHY a separate 3.3V?** 这是 ESP8266 项目第一大坑。解决办法：用一个独立的 AMS1117-3.3 模块（淘宝 ¥1），输入 5V USB，输出 3.3V 专供 ESP-01S，并在 VCC 旁边加一个 **100μF 电解 + 0.1μF 陶瓷**去耦电容。记住：「ESP-01S 必须吃得好」。

---

## 三、接线 —— ESP-01S 接到 USART3 | Wiring ESP-01S to USART3

### 3.1 接线表

| ESP-01S | KE1 板 | 备注 |
|---------|--------|------|
| VCC | 独立 3.3V (AMS1117 输出) | **不要接 KE1 的 3.3V 引脚**，电流不够 |
| GND | KE1 GND（共地！） | 独立电源的 GND 也要接一起 |
| TX | PB11 (USART3_RX) | TX→RX 交叉接 |
| RX | PB10 (USART3_TX) | RX←TX 交叉接 |
| EN/CH_PD | 独立 3.3V（串 10kΩ） | 必须拉高，否则模块不工作 |
| RST | 悬空 或 接按钮到 GND | 可选，方便手动复位 |
| GPIO0 | 悬空（正常运行） | 要烧 AT 固件时才拉低 |
| GPIO2 | 悬空 | — |

> ⚠️ **电平说明**: ESP-01S 的 IO 是 3.3V，KE1 的 STM32L433 也是 3.3V，**电平一致，不需要电平转换**。这比接 5V Arduino 简单。但绝对不能把 ESP-01S 的 VCC 接 5V，会烧。

### 3.2 CubeMX 配置 USART3 (难度: ⭐⭐)

1. `.ioc` 里 PB10 设为 `USART3_TX`，PB11 设为 `USART3_RX`。
2. `Connectivity → USART3`，Mode = `Asynchronous`，Baud Rate = **115200**（ESP-01S 默认 AT 固件波特率，部分老固件是 9600，如果收不到试改 9600）。8N1。
3. **开启 USART3 全局中断**：在 NVIC Settings 标签勾 `USART3 global interrupt → Enabled`。这是关键——我们用中断接收，不能阻塞主循环。
4. `Generate Code`。

> **WHY interrupt receive not blocking?** Day 2 的 `HAL_UART_Receive` 是阻塞的——它在等数据时 CPU 啥都干不了。ESP8266 的 AT 响应可能 50ms 来、可能 2 秒来，长度不定。阻塞接收会让 OLED 刷新卡死、SHT31 读数停滞。**中断接收**：数据来了硬件触发中断，在中断回调里存到环形缓冲区，主循环想看就看，不阻塞。KE1 源码 `usart.c` 的 `HAL_UART_RxCpltCallback` 就是这个思路。

### 3.3 波特率不匹配的坑

ESP-01S 出厂 AT 固件波特率有两个常见版本：
- **新版固件**：115200（大多数现在的 ESP-01S）
- **老版固件 / 某些刷过 Anker 固件的**：9600

如果发 `AT` 完全没反应，**把 USART3 波特率改 9600 再试**。还不行就接 USB-TTL 直接用电脑串口工具发 `AT+UART_DEF=115200,8,1,0,0` 改波特率（见 troubleshooting）。

---

## 四、串口中断接收 —— UP主的 AT 框架 | UART Interrupt Receive: The AT Framework

复刻模式：AT 收发框架 UP主 已经写好，在参考源码 `usart.c`。我们读懂它。

### 4.1 环形缓冲区（讲 WHY） (难度: ⭐⭐⭐)

ESP8266 一次回复可能是几十到几百字节，主循环不一定立刻来读。需要一个**缓冲区**存着。KE1 源码用一个 256 字节的环形缓冲区 (ring buffer)：

```c
uint8_t aucUsart3_Rev_Buf[256] = {0};
volatile uint8_t ucUsart3_In = 0, ucUsart3_Out = 0;  // 读写指针

// 中断回调：每收到 1 字节触发
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *UartHandle) {
    if (USART3 == UartHandle->Instance) {
        aucUsart3_Rev_Buf[ucUsart3_In++] = ucUart3Ch;  // 存到 In 位置，In 指针后移
        HAL_UART_Receive_IT(&huart3, &ucUart3Ch, 1);    // 重新开启下一次中断接收
    }
}
```

- `ucUart3Ch` 是单字节接收缓存
- `ucUsart3_In` 是「写指针」，中断来一字节写一字节、往后走
- `ucUsart3_Out` 是「读指针」，主循环从这里取
- `volatile` 关键字告诉编译器「这变量会被中断改，别优化掉」

> **WHY ring buffer?** 如果用普通数组+标志位，中断来快、主循环读慢，数据会丢。环形缓冲区让中断只管往里塞、主循环只管往外取，互不阻塞——这是嵌入式串口接收的标准模式。

### 4.2 发 AT + 收响应 (难度: ⭐⭐)

```c
// 发送 AT 命令
int UART_Put_AT_Cmd(char *pcAt) {
    HAL_UART_Transmit(&huart3, (uint8_t*)pcAt, strlen(pcAt), 2000);
    return strlen(pcAt);
}

// 接收响应（带超时）
int UART_Get_AT_Resp(uint8_t *pucBuff, uint16_t usSize, uint16_t usTimeout) {
    int len = 0;
    uint16_t timeout = usTimeout/100;
    do {
        if (ucUsart3_In != ucUsart3_Out) {       // 缓冲区有数据
            pucBuff[len++] = aucUsart3_Rev_Buf[ucUsart3_Out++];  // 取一字节
            if (usSize == len) break;
        } else {
            if (timeout) { HAL_Delay(100); timeout--; continue; }
        }
    } while (timeout);
    return len;
}
```

**关键点**：`UART_Get_AT_Resp` 是**阻塞但有超时**的——主循环调它时会等 `usTimeout` 毫秒取数据。这是「发一条命令→等回复→处理」的同步 AT 模式，简单够用。

### 4.3 启动中断接收

`main` 初始化区必须调一次：

```c
/* USER CODE BEGIN 2 */
UART_Enable_Receive_IT();   // 开启 USART3 中断接收
printf("ESP8266 AT test\r\n");
/* USER CODE END 2 */
```

---

## 五、试通 AT 命令 | Testing AT Commands

### 5.1 第一步：发 `AT` 看 `OK` (难度: ⭐)

`USER CODE BEGIN WHILE`：

```c
/* USER CODE BEGIN WHILE */
uint8_t resp[256] = {0};
while (1)
{
    UART_Put_AT_Cmd("AT\r\n");
    int n = UART_Get_AT_Resp(resp, sizeof(resp)-1, 1000);
    resp[n] = 0;
    printf("--- ESP resp ---\r\n%s\r\n", resp);
    OLED_ShowString(0, 6, (uint8_t*)"AT test..", 16);
    HAL_Delay(2000);
    /* USER CODE END WHILE */
}
```

串口助手应该看到：

```
--- ESP resp ---
AT

OK
```

> ✅ **检查点 5.1**: 收到 `OK` → ESP8266 通了。没收到？看下方错误表。

### 5.2 第二步：查固件版本

```c
UART_Put_AT_Cmd("AT+GMR\r\n");
```

应该返回固件版本号、SDK 版本、编译时间。**记下这个版本号**——后面 SNTP 命令在不同固件版本上语法略不同。

### 5.3 第三步：设为 Station 模式

ESP8266 有三种模式：Station（连别人 WiFi）、SoftAP（自己做热点）、Station+SoftAP。我们要连家里 WiFi，用 Station：

```c
UART_Put_AT_Cmd("AT+CWMODE_CUR=1\r\n");  // 1=Station, _CUR=不写Flash
```

> **WHY `_CUR` not `_DEF`?** `CWMODE_CUR` 只当前生效，`CWMODE_DEF` 写进 Flash 永久。调试时用 `_CUR` 避免写坏 Flash，稳定后再换 `_DEF`。

### 5.4 第四步：连 WiFi (难度: ⭐⭐)

```c
// 注意转义引号
UART_Put_AT_Cmd("AT+CWJAP_CUR=\"你的WiFi名\",\"你的密码\"\r\n");
```

这一步要 3-10 秒。成功会回：

```
WIFI CONNECTED
WIFI GOT IP

OK
```

失败常见：`+CWJAP:1`（超时，WiFi 名错或信号弱）、`+CWJAP:2`（密码错）、`+CWJAP:3`（找不到 SSID，可能是 5GHz WiFi）。

> ✅ **检查点 5.2**: 看到 `WIFI GOT IP` → ESP8266 联网了。把 IP 记下来。

### 5.5 第五步：查 IP

```c
UART_Put_AT_Cmd("AT+CIFSR\r\n");
```

返回类似 `+CIFSR:STAIP,"192.168.1.123"`。

---

## 六、常见错误 | Common Errors

| 现象 | 原因 | 解决 |
|------|------|------|
| 发 `AT` 完全无响应 | 波特率错 / TX/RX 接反 / EN 没拉高 / 供电不足 | 试 9600；交换 TX/RX；EN 接 3.3V；换独立 3.3V 电源 |
| 响应是乱码 | 波特率不匹配 | 9600↔115200 切换试 |
| `AT` 有 `OK` 但 `CWJAP` 超时 | WiFi 是 5GHz / 信号弱 / 密码错 | 换 2.4G WiFi；靠近路由器；核对密码 |
| `+CWJAP:4` connect failed | 路由器 WPA3 或限制 | 用 WPA2-PSK 的 WiFi |
| ESP-01S 反复复位（OLED 闪、AT 时通时断） | 供电不足瞬态压降 | 加 100μF 电容；换 AMS1117 独立供电 |
| 响应断断续续丢字符 | 环形缓冲区溢出 / 中断被屏蔽 | `aucUsart3_Rev_Buf` 加大到 512；确认没在中断里做重活 |
| 收到 `busy p...` | 上一条命令没回完就发下一条 | 每条 AT 后等够超时，或检测到 `OK`/`ERROR` 再发下一条 |
| `CWMODE` 报 `ERROR` | 老固件不支持 `_CUR` | 改 `AT+CWMODE=1`（老语法） |

---

## 七、调试技巧 | Debugging Tips

1. **USB-TTL 直连电脑**: 把 ESP-01S 的 TX/RX 接到 USB-TTL 转串口，用电脑串口助手直接发 AT——绕开 STM32，单独验证模块。这是排查「模块问题还是主控代码问题」的金标准。
2. **串口助手开两个**: 一个看 STM32 的 USART1 printf（调试日志），一个直连 ESP-01S（AT 交互）。但注意 ESP-01S 只有一组 TX/RX，直连时 STM32 这边就断了，二选一。
3. **响应里找关键词**: `strstr((char*)resp, "OK")` 判断成功，`strstr(resp, "ERROR")` 判断失败。KE1 源码 `main.c` 里 `strstr((char *)aucData, "+QLWEVTIND:3")` 就是这个套路。
4. **EN 脚接按钮**: RST 和 EN 接一个轻触按钮到 GND，模块卡死时按一下复位，比拔插 USB 快。
5. **看 RSSI 信号强度**: 连上后发 `AT+CWJAP?` 或 `AT+CIPSTATUS` 看连接状态。信号弱 (<-80dBm) 会不稳定。

---

## 八、今日检查点 | Day 5 Checkpoints

- [ ] ESP-01S 接好，独立 3.3V 供电，EN 拉高
- [ ] 发 `AT` 收到 `OK`
- [ ] `AT+GMR` 能看到固件版本，记下来
- [ ] `AT+CWMODE_CUR=1` 成功
- [ ] `AT+CWJAP_CUR` 连上 WiFi，收到 `WIFI GOT IP`
- [ ] 能解释「为什么 ESP-01S 要独立供电」「为什么用中断接收」
- [ ] 截图：串口显示 `WIFI GOT IP` 和 IP 地址

---

## 九、今日作业 | Homework

1. **封装连 WiFi 函数** (⭐⭐): 写一个 `int ESP8266_ConnectWiFi(const char *ssid, const char *pwd)`，内部发 `CWJAP`，等 `OK` 返回 1，超时返回 0。把你的 WiFi 信息填进 `software/src/env_clock/Core/Inc/wifi_config.h` 的宏里（这是学生唯一要编辑的配置文件；`config.template.yaml` 只是只读镜像）。**别把真实密码提交到 Git**——`wifi_config.h` 已在 `.gitignore`，提交时用 `wifi_config.h.example` 占位。
2. **断网重连** (⭐⭐): 如果 `CWJAP` 失败，每 5 秒重试，最多 6 次。OLED 显示「WiFi...」状态。
3. **Git 提交**:
   ```bash
   git add curriculum/day-05.md
   git commit -m "day05: ESP8266 AT firmware, WiFi connected"
   ```

### 理解验证问题 | Comprehension Check

**Q1** (设计权衡): 为什么 5V→3.3V 给 ESP-01S 供电用 LDO (AMS1117-3.3) 而不是 Buck（降压开关电源）？从成本/噪声/效率/ESP-01S 噪声敏感度四个角度分析。

> **参考答案**: (1) **成本**——AMS1117-3.3 淘宝 ¥1、外围只需 2 颗电容，Buck 要电感+控制芯片，BOM 贵 3-5 倍，本项目单板预算敏感；(2) **噪声**——LDO 是线性稳压，输出纹波 <10mV，Buck 是开关电源，纹波几十 mV 且带开关尖峰；(3) **效率**——LDO 效率 = Vout/Vin = 3.3/5 = 66%，Buck 可达 90%+，但 ESP-01S 平均电流才几十 mA，效率差异在总功耗上可忽略，散热也无忧；(4) **ESP-01S 敏感度**——ESP8266 射频发射时瞬态电流 300-400mA，对供电纹波极敏感，Buck 的开关尖峰容易诱发模块复位、AT 无响应，LDO 的干净电源更稳。综合：小电流、低成本、低噪声、敏感负载 → LDO 是对的；只有大电流（>500mA 连续）或电池供电才轮到 Buck。

**Q2** (设计权衡): ESP8266 的三种工作模式 (Station / SoftAP / 混合) 各是什么？我们用哪个，为什么「不用混合模式」？

> **参考答案**: Station = 连别人 WiFi（当客户端）；SoftAP = 自己开热点（当 AP，等别人连）；混合 = 同时既连 WiFi 又开热点。本项目要连家里 WiFi 对 NTP，所以用 Station。不用混合模式——虽然混合模式理论上能既联网又给手机配网页面，但本项目 WiFi 信息写死在 `wifi_config.h`、不需要运行时配网，多开一个 AP 只会增加 ESP-01S 的射频负载和功耗，反而让供电更紧张。功能够用就别开多余的东西。

**Q3** (原理追问): AT 响应用中断接收 + 环形缓冲区，而不是阻塞 `HAL_UART_Receive`。从「响应时序不定」「主循环阻塞」「数据丢失」三个角度说明。

> **参考答案**: (1) ESP8266 的 AT 响应时序不确定——可能 50ms 来、可能 2 秒来，长度也不定，阻塞接收设多短的超时都不合适；(2) 阻塞期间主循环卡死，OLED 不刷新、SHT31 不采样，整个时钟停摆；(3) 中断接收把每个字节存进环形缓冲区，主循环想看就看、不看也不丢，中断「只管塞」、主循环「只管取」互不阻塞。`volatile` 关键字保证编译器不把被中断修改的读写指针优化掉，是这套机制正确的前提。

**Q4** (故障分析): 发 `AT` 完全无响应，按可能性排序列出可能原因和对应排查动作。

> **参考答案**: 按可能性从高到低——① 供电不足（ESP-01S 反复复位）：换独立 AMS1117-3.3 + 100μF 电解电容，这是头号坑；② 波特率不匹配（新版 115200 / 老版 9600）：USART3 切 9600 重试；③ TX/RX 接反（没交叉）：交换 PB10/PB11 两根线；④ EN (CH_PD) 没拉高：EN 串 10kΩ 接 3.3V；⑤ 模块烧了（VCC 误接 5V）：换一块 ESP-01S。金标准是用 USB-TTL 直连电脑发 `AT`，绕开 STM32 单独验证模块。

### 今日评分标准 | Rubric

| 维度 | 满分 | 评分细则 |
|------|------|---------|
| 完成度 | 4 | `AT` 收 `OK`；连上 WiFi 收 `WIFI GOT IP`；封装 `ConnectWiFi` 函数 |
| 理解深度 (CC 回答) | 3 | 能讲清 LDO vs Buck、三种模式选型、中断+环形缓冲区原理 |
| 代码/接线质量 | 2 | 独立 3.3V 供电、TX/RX 交叉、`wifi_config.h` 不入库 |
| 创意拓展 | 1 | 断网重连、RSSI 显示、USB-TTL 直连验证流程等 |

> **今日产出 = 明日输入**: 跑通的 AT 收发框架 + `WIFI GOT IP` 的 ESP8266 = Day 6 SNTP 网络授时的输入（连上网才能向 NTP 服务器对时）。

---

## 十、明日预告 | Tomorrow

**Day 6: WiFi 联网 + SNTP 网络授时 —— 获取网络时间**
- 用 AT 命令配 SNTP，让 ESP8266 向 NTP 服务器对时
- 解析 ESP8266 返回的时间字符串
- 把网络时间显示到 OLED，验证它准

**前置准备**: 确认你的 WiFi 能访问互联网（NTP 要走公网）；记下 Day 5 的固件版本。

---

*最后更新: 2026-06 | Last updated: 2026-06*
