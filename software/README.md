# software/ — 温湿度网络时钟 固件 (Firmware)

> WiFi Temp/Humidity Network Clock — STM32L433CCT6 + ESP8266 + SHT31 + OLED
> 复刻自 Bilibili 视频 [BV1tb4y1U7Du](https://www.bilibili.com/video/BV1tb4y1U7Du/) (UP主: 乐在程上)
>
> **主控芯片 = STM32L433CCT6**（LQFP48，256KB Flash）。固件 `.ioc` 中 `Mcu.UserName=STM32L433CCTx`；链接脚本文件名沿用 CubeIDE 生成的 `STM32L433CCTX_FLASH.ld`（`X` = 通配，CCT6/CBT6 通用，无需改名）。CBT6（128KB Flash）为引脚兼容备选。

## 学习成果 | Learning Outcomes

读完本文档并完成构建/烧录/配置后，你应当能够：

- **识别 (Identify)** 固件工程目录结构，指出学生唯一要改的文件是 `Core/Inc/wifi_config.h`
- **解释 (Explain)** STM32 主控 + ESP8266 WiFi 协处理器的分工，以及 SNTP 授时 + SysTick 守时的「断网照走」架构
- **实现 (Implement)** 用 CubeIDE 编译出 `env_clock.elf`、烧录到板子、在串口看到正常启动日志
- **分析 (Analyze)** 串口输出与 OLED 显示，判断固件是否工作正常

## 为什么学这个 | Why This Matters

> 类比：**这份固件是一份写好的菜谱，你的工作是把它端上桌。** 厨师（UP 主）已经把菜谱写好、食材配齐（源码 + KE1 例程），你要做的是读懂菜谱、按步骤开火（编译/烧录）、尝味道（串口看输出）、咸了淡了自己调味（改 `wifi_config.h` 配置）。复刻模式下你不写菜谱，但你必须懂「这道菜为什么这么烧」——否则一出问题就抓瞎。

## 目录结构 (Directory)

```
software/
├── src/
│   └── env_clock/            # ← STM32CubeIDE 工程 (本目录就是固件本体)
│       ├── .project / .cproject / .settings/   # CubeIDE 工程文件
│       ├── env_clock.ioc     # CubeMX 配置 (引脚/时钟/外设)
│       ├── STM32L433CCTX_FLASH.ld   # 链接脚本
│       ├── Drivers/          # ST HAL + CMSIS (CubeIDE 生成, 勿手改)
│       └── Core/
│           ├── Inc/          # 头文件
│           │   ├── wifi_config.h   ★ 学生唯一要改的文件 (WiFi 账号密码)
│           │   ├── esp8266.h       # ESP8266 WiFi+SNTP AT 驱动
│           │   ├── clock.h         # 时钟管理 (SNTP 同步 + SysTick 守时)
│           │   ├── oled.h          # SSD1306 OLED 驱动 (含时间显示)
│           │   ├── i2c.h / sht3x.h # SHT31 温湿度驱动 (硬件 I2C2)
│           │   ├── usart.h         # UART/AT 框架 (printf 重定向)
│           │   ├── tim.h           # TIM2 PWM 蜂鸣器
│           │   └── ...
│           └── Src/          # 源文件 (与上面头文件一一对应)
│               ├── main.c          ★ 主程序 (初始化 + 主循环)
│               ├── esp8266.c / clock.c / oled.c / i2c.c / usart.c / tim.c
│               └── gpio.c / stm32l4xx_it.c / stm32l4xx_hal_msp.c / system_stm32l4xx.c
├── config.template.yaml      # 配置模板 (对照 wifi_config.h, 供阅读)
├── requirements.txt          # 工具链清单
├── tests/
│   └── test_basic.py         # 串口集成测试 (pyserial)
└── README.md                 # 本文件
```

## 构建 + 烧录 + 配置 (Build / Flash / Configure)

### 1. 用 CubeIDE 打开工程
- 安装 **STM32CubeIDE 1.6.1+** (含 GCC arm 交叉编译器 + ST-Link 烧录器)。
- `File → Open Projects from File System…` → 选 `software/src/env_clock/` 目录 → Finish。
- 工程名 `env_clock` 会自动识别 (Core/ 和 Drivers/ 为源码目录)。

### 2. 编辑 WiFi 配置 ★
打开 `Core/Inc/wifi_config.h`, 修改:
```c
#define WIFI_SSID             "YOUR_SSID"       ← 改成你的 2.4GHz WiFi 名
#define WIFI_PASSWORD         "YOUR_PASSWORD"   ← 改成你的 WiFi 密码
```
> ESP8266 **不支持 5GHz**, 请确认路由器开了 2.4GHz 频段。

### 3. Build
- `Project → Build All` (或 Ctrl+B)。
- 预期输出: `env_clock.elf` 生成在 `Debug/` 下, 0 errors, 0 warnings (或仅个别 KE1 原工程 warning)。

### 4. 烧录 (Flash)
- 用 **ST-Link** 或 **USB** 连接 STM32L433 板。
- `Run → Debug/Run` (CubeIDE 自动调 CubeProgrammer 烧录), 或独立用 STM32CubeProgrammer 烧 `env_clock.elf`。

### 5. 串口监视器看输出
- 用 USB 转串口模块接 **PA9(TX)/PA10(RX)**, 或用板载 ST-Link 虚拟串口。
- 打开串口工具 (波特率 **115200**, 8 数据位, 无校验, 1 停止位)。
- 预期输出:
  ```
  === EnvClock WiFi (BV1tb4y1U7Du) boot ===
  [MAIN] SHT31 init done
  [ESP8266] init OK
  [ESP8266] WiFi connected to YOUR_SSID
  [ESP8266] SNTP configured (tz=8, ntp.aliyun.com)
  [MAIN] SNTP sync OK: 2026-06-22 12:00:00
  [MAIN] T:23.45C H:56.78%
  [CLK] 2026-06-22 12:00:01 OK | T:23.45 H:56.78
  [CLK] 2026-06-22 12:00:02 OK | T:23.45 H:56.78
  ...
  ```

### 6. 预期行为 (Expected)
- **OLED**: 开机欢迎屏 → WiFi 连接中 → 显示 `日期(顶部) + 时间(中部) + 温湿度(底部)`（由 `OLED_ShowClock(year,month,day,hour,min,sec,wday,temp,humi,synced)` 刷一屏）。
- 时间右上角 `.` 表示已 SNTP 同步; `*` 表示未同步 (用 SysTick 守时)。
- 每个整点蜂鸣器短鸣两声 (嘀-嘀) 报时（TIM2_CH2 / PA1 PWM）。
- **按键**：提供的固件用 **PA0** 做手动触发一次 SNTP 重新对时（`BTN_KEY`，输入上拉，按下接地）。Day 8 的「按键调时」拓展则用 **PC13 (KEY1) / PA15 (KEY2)** 接 EXTI 做模式切换 / 加减调时——详见 `../hardware/wiring-guide.md` 的按键接线表。
- 每 10 分钟自动刷新温湿度 + 重新 SNTP 对时。

## 跑串口测试 (Run serial test)

```bash
pip install pyserial
python tests/test_basic.py --port COM3            # Windows
python tests/test_basic.py --port /dev/ttyUSB0    # Linux/Mac
```
通过: 读到的行同时包含 时间(HH:MM:SS) + 温度(T:xx C) + 湿度(H:xx %)。

## 相关文档
- 接线见 `../hardware/wiring-guide.md`
- 排错见 `../hardware/troubleshooting.md`
- 课程见 `../curriculum/`

## 固件架构 (Architecture, 循序渐进)
```
   main.c  ── 初始化 ──→  SHT31 (I2C2, PB13/PB14)  ── 温湿度
        │                OLED (软件 I2C PB8/PB9)    ── OLED_ShowClock() 刷一屏
        │                ESP8266 (USART3, AT)        ── WiFi 联网 + SNTP 授时
        │                TIM2_CH2 (PA1, PWM)         ── 蜂鸣器整点报时
        │                PA0 (BTN_KEY, 输入上拉)     ── 手动触发 SNTP 重新对时
        │
        └─ 主循环 ─→  Clock_Tick() (SysTick 守时) → OLED_ShowClock() → 整点报时 → 定时刷新
```
- **主控 + AT 协处理器**: STM32 主控, ESP8266 当 WiFi 协处理器 (UART 发 AT 文本命令)。复用 KE1_IoT 原 NB-IoT 的 AT 框架。
- **守时 (holdover)**: NTP 校准一次后, STM32 用 SysTick (1ms) 自己往前走, 断网也不停。
- **OLED 主显示函数**: `OLED_ShowClock(year,month,day,hour,min,sec,wday,temp,humi,synced)` —— 由 `main.c` 主循环每周期调用刷一屏。辅助函数 `OLED_ShowTime(h,m,s)` / `OLED_ShowDate(...)` 供分段显示。

---

## 理解验证问题 | Comprehension Check

**Q1: 为什么 STM32 主控不直接做 WiFi，而要外挂一个 ESP8266 当「协处理器」？这种分工架构的好处是什么？**

> **参考答案**: STM32L433 本身没有 WiFi 射频硬件。ESP8266 是带 WiFi 射频 + TCP/IP 协议栈的 SoC，出厂烧了 AT 固件，能通过 UART 文本命令（`AT+CWJAP` 等）完成联网。把 WiFi 交给 ESP8266 的好处：(1) **解耦**——主控专注实时时钟 + 传感器采集，不被阻塞式网络栈拖累；(2) **复用**——ESP8266 的 AT 固件替主控处理了 TCP/IP/DNS/SNTP 等复杂协议栈，主控只需解析文本响应；(3) **可替换**——以后换 NB-IoT/4G 模块只需改 AT 命令集，主控逻辑不动。代价是多一个 UART 通信环节、多一个芯片。

**Q2: 固件里 `Clock_Tick()` 为什么必须无条件每秒跑，而不是放在 `if (wifi_ok)` 里？**

> **参考答案**: `Clock_Tick()` 是本地 SysTick 守时——靠 MCU 内部 1ms 滴答计时累加秒/分/时。如果把它放进 `if (wifi_ok)`，WiFi 一断时钟就停了，这是产品级时钟不能接受的。正确架构是 **本地 tick 永远走 + 网络定期校正**：SNTP 只负责「定期把本地时间拉准」，不是时间的唯一来源。这样断网时时钟照走（可能漂移几秒/天），联网后自动校准。类比手机飞行模式时钟照走、连网才悄悄校时。

**Q3: 学生唯一要改的文件为什么是 `wifi_config.h` 而不是 `main.c`？这反映了复刻模式的什么设计？**

> **参考答案**: `wifi_config.h` 是纯配置头文件（`#define WIFI_SSID` / `WIFI_PASSWORD` / NTP 服务器 / 时区），改它不需要懂 C 逻辑、不会引入编译错误、不会破坏固件架构。把「因人而异」的部分（每个人的 WiFi 账号密码不同）隔离到一个配置文件，是工程上「**配置与代码分离**」的标准做法。复刻模式下学生不动 `main.c` / 驱动层，既保护了固件稳定性，又让学生聚焦在「配置 + 调试」而非「写代码」。

---

## 评分标准 | Rubric (构建/烧录/配置环节)

| 维度 | 满分 | 评分细则 |
|------|------|---------|
| 完成度 | 4 | 0 error 编译通过 + 烧录成功 + 串口看到正常启动日志（SHT31/ESP8266/SNTP 三段 OK）|
| 理解深度 (CC 回答) | 3 | 能答对 Q1-Q3 中至少 2 个，说清「协处理器分工」「本地 tick 无条件跑」「配置与代码分离」|
| 配置质量 | 2 | `wifi_config.h` 填对（2.4GHz SSID + 密码 + 国内 NTP + tz=8）；OLED 正常显示时间+温湿度 |
| 创意拓展 | 1 | 改了 NTP 服务器对比同步速度、或调了刷屏节流、或跑了 `tests/test_basic.py` 串口集成测试 |

---

> **今日产出 = 明日输入**: 编译出的 `env_clock.elf` + 烧录到板子后串口/OLED 的正常输出 = 后续每天调试、拓展功能的起点。固件跑不起来，后面 9 天都无从谈起。
