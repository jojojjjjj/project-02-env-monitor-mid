# software/ — 温湿度网络时钟 固件 (Firmware)

> WiFi Temp/Humidity Network Clock — STM32L433 + ESP8266 + SHT31 + OLED
> 复刻自 Bilibili 视频 [BV1tb4y1U7Du](https://www.bilibili.com/video/BV1tb4y1U7Du/) (UP主: 乐在程上)

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
- **OLED**: 开机欢迎屏 → WiFi 连接中 → 显示 `日期(顶部) + 时间(中部) + 温湿度(底部)`。
- 时间右上角 `.` 表示已 SNTP 同步; `*` 表示未同步 (用 SysTick 守时)。
- 每个整点蜂鸣器短鸣两声 (嘀-嘀) 报时。
- 按 **PA0 按键** 手动触发一次 SNTP 重新对时。
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

## 固件架构 (Architecture, 笨鸟先飞)
```
   main.c  ── 初始化 ──→  SHT31 (I2C2)  ── 温湿度
        │                OLED (软件 I2C PB8/PB9) ── 显示时间+温湿度
        │                ESP8266 (USART3, AT) ── WiFi 联网 + SNTP 授时
        │                TIM2_CH2 (PA1, PWM) ── 蜂鸣器整点报时
        │
        └─ 主循环 ─→  Clock_Tick() (SysTick 守时) → 刷屏 → 整点报时 → 定时刷新
```
- **主控 + AT 协处理器**: STM32 主控, ESP8266 当 WiFi 协处理器 (UART 发 AT 文本命令)。复用 KE1_IoT 原 NB-IoT 的 AT 框架。
- **守时 (holdover)**: NTP 校准一次后, STM32 用 SysTick (1ms) 自己往前走, 断网也不停。
