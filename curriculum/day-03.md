# Day 3: SHT31 温湿度传感器 —— I2C 原理 + 接线 + 读数值 | SHT31 Sensor: I2C + Wiring + Reading Values

> **学习目标 | Learning Objectives**
> - 理解 I2C 总线协议：为什么两根线能挂多个设备、SCL/SDA/地址/ACK 各是什么
> - 把 SHT31 接到 KE1 板的 PB13/PB14（硬件 I2C2），理解为什么需要上拉电阻
> - 烧录 UP主提供的 SHT31 驱动，串口打印真实的温度湿度数值
> - 理解 CRC 校验和 SHT31 的「周期测量模式」

> **产出 | Deliverable**: 串口稳定每秒打印一行 `T=25.43'C H=58.20%`，用手捂传感器能看到温度上升

---

## 一、前置检查 | Pre-flight Checklist

- [ ] Day 2 的点灯 + printf 已跑通（串口能看到 `tick`）
- [ ] 手上有 SHT31 模块（4 针：VCC/GND/SCL/SDA）+ 4 根母对母杜邦线
- [ ] 工程里已经能 `printf`（USART1 调试串口就绪）

---

## 二、I2C 协议原理 —— 两根线挂一堆设备 | I2C Protocol: Many Devices on Two Wires

### 2.1 I2C 是什么

I2C（读作 "I-squared-C"）= Inter-Integrated Circuit，飞利浦发明的两线制串行总线。**两根线**：

- **SCL**（Serial Clock）：时钟线，主控拉节奏
- **SDA**（Serial Data）：数据线，双向传数据

**一根总线可以挂多个设备**（SHT31、OLED、MPU6050……都挂在同一对 SCL/SDA 上），靠**设备地址**区分。这就是 I2C 最大的优点——省引脚。

> **WHY I2C not SPI/UART for sensors?** SPI 要 4 根线+每个从设备一根片选，挂多了引脚爆炸；UART 是点对点，挂不了多个。I2C 两根线挂一堆，是传感器的首选。

### 2.2 开漏 + 上拉（I2C 最关键的概念，讲 WHY）

I2C 的 SCL/SDA 必须配置成**开漏 (Open-Drain)** + 外接**上拉电阻 (通常 4.7kΩ)**。为什么这么反常？

因为 I2C 是**多设备共享总线**，如果两个设备同时驱动同一根线——一个拉高一个拉低——会短路烧芯片。开漏输出的特点是：

- 任何设备只能把线**拉低 (0)**，或**松手 (高阻态)**
- 没人拉低时，上拉电阻把线**拉回高 (1)**

这样即使多个设备「同时发言」，线也只是被拉低，不会短路。这叫**线与 (wired-AND)**。

> **WHY external pull-up?** 开漏自己拉不回高，必须靠上拉电阻。SHT31/OLED 模块通常板载了 4.7kΩ 上拉，所以你直接接 VCC/GND/SCL/SDA 就能跑。如果总线上挂多个模块，上拉电阻会并联变小（4.7k//4.7k≈2.35k），一般没事，挂超过 4-6 个才可能出问题。

### 2.3 I2C 一次通信的时序

主控要读 SHT31，大致这样：

```
主控: [START] [地址+W]      [CMD高] [CMD低]     [RESTART] [地址+R]           [NACK/STOP]
从机:                  [ACK]         [ACK] [ACK]                   [ACK][数据][ACK]...
```

- **START**: SCL 高时 SDA 由高变低（特殊信号，告诉所有从机「开始了」）
- **地址+W/R**: 7 位地址 + 1 位方向（0=写，1=读）。SHT31 地址是 `0x44`，写时发 `0x88`，读时发 `0x89`（地址左移 1 位 + 方向位）
- **ACK**: 每发完 1 字节，接收方拉低 SDA 一个周期表示「收到了」
- **STOP**: SCL 高时 SDA 由低变高，结束

> **WHY 7-bit address shifted?** STM32 HAL 的 `HAL_I2C_Master_Transmit` 第二个参数 `DevAddress` 要的是**已经左移 1 位的 8 位地址**（低 1 位是 R/W）。SHT31 的 7 位地址 `0x44` → 写地址 `0x44<<1 = 0x88`，读地址 `0x88|0x01 = 0x89`。KE1 源码 `sht3x.h` 里 `SHT30_ADDR_WR 0x88 / SHT30_ADDR_RD 0x89` 就是这么来的——这是第一个真实代码点。

### 2.4 I2C 在 STM32L433 上的两种实现

| 方式 | 说明 | KE1 用在哪 |
|------|------|-----------|
| **硬件 I2C**（I2C1/2/3 外设） | 有专用寄存器，HAL 库封装好，稳定快 | **I2C2 (PB13/PB14) 连 SHT31** |
| **软件 I2C**（GPIO 模拟） | 任意两个 GPIO 手动拉时序，灵活但慢 | **PB8/PB9 连 OLED**（Day 4） |

> **WHY both?** UP主的 KE1 例程里，SHT31 走硬件 I2C2（准、省 CPU），OLED 走软件 I2C（因为 OLED 库是从老代码移植的软件 I2C 版本，且和 SHT31 分开避免时序互扰）。我们复刻，照搬即可。

---

## 三、接线 —— SHT31 接到 I2C2 | Wiring SHT31 to I2C2

### 3.1 接线表

| SHT31 模块 | KE1 板引脚 | 说明 |
|-----------|-----------|------|
| VCC | 3.3V | **绝对不能接 5V**（SHT31 3.3V 供电；KE1 的 GPIO 也是 3.3V 电平） |
| GND | GND | 共地 |
| SCL | PB13 | I2C2_SCL（CubeMX 里要配成 I2C2_SCL 复用） |
| SDA | PB14 | I2C2_SDA |

### 3.2 在 CubeMX 里配置 I2C2

1. 打开工程的 `.ioc`，在引脚图点 PB13 → 选 `I2C2_SCL`，PB14 → `I2C2_SDA`。
2. 左侧 `Connectivity → I2C2`，Mode 选 `I2C`，参数默认（Speed Mode 选 Standard 100kHz 或 Fast 400kHz 都行，SHT31 支持 1MHz，我们用 100kHz 稳妥）。
3. `Generate Code`。

> **检查点 3.1**: Generate 后 `i2c.c` 里应该有 `MX_I2C2_Init()`，`hi2c2.Instance = I2C2`。和参考源码 `inspect/nbth/KE1_IoT/Core/Src/i2c.c` 对比，引脚和时钟配置要一致。

---

## 四、烧录 UP主提供的 SHT31 驱动 | Flashing the Provided SHT31 Driver

复刻模式的核心来了：**驱动代码已经写好，在 `software/src/sht31.c` 和 `i2c.c`**。你不用写，你要读懂 + 接对线 + 烧进去。

### 4.1 把驱动文件加进工程

1. 把 `software/src/sht3x.h` 复制到工程的 `Core/Inc/`。
2. 把 `software/src/i2c.c` 里 `/* USER CODE BEGIN 1 */` 之后那段 SHT31 驱动函数（`CheckCrc8` / `i2c_write_cmd` / `KE1_I2C_SHT31_Init` / `KE1_I2C_SHT31`）复制到你自己工程 `i2c.c` 的 `USER CODE BEGIN 1` 区。
3. `#include "sht3x.h"` 加到 `i2c.c` 顶部 USER CODE 区。

### 4.2 读懂驱动（讲 WHY，每个函数干嘛）

打开参考源码 `i2c.c`，我们逐个看：

**(1) CRC8 校验** —— SHT31 每个测量值后面跟一个 CRC 字节，防止数据传输出错：

```c
uint8_t CheckCrc8(uint8_t* message, uint8_t initial_value) {
    // 多项式 0x31，标准 CRC-8，Sensirion 官方算法
    ...
}
```

> **WHY CRC?** I2C 上如果有干扰，数据位可能翻转。CRC 校验失败就丢弃这次读数，保证你看到的温湿度是真的。真实工程几乎都有 CRC。

**(2) 写命令** —— SHT31 的命令是 16 位（两个字节的「指令码」），比如软复位 `0x30A2`：

```c
HAL_StatusTypeDef i2c_write_cmd(uint16_t cmd) {
    uint8_t cmd_buff[2] = { cmd>>8, cmd };  // 高字节在前
    return HAL_I2C_Master_Transmit(&hi2c2, SHT30_ADDR_WR, cmd_buff, 2, 0xffff);
}
```

**(3) 初始化** —— 软复位 + 设为周期测量模式（每秒测 2 次，中等精度）：

```c
HAL_StatusTypeDef KE1_I2C_SHT31_Init() {
    i2c_write_cmd(CMD_SOFT_RESET);    // 0x30A2 复位
    HAL_Delay(25);
    i2c_write_cmd(CMD_MEAS_PERI_2_M); // 0x2220 周期 2mps 中精度
    HAL_Delay(25);
}
```

> **WHY periodic mode not single-shot?** 周期模式让 SHT31 自己在后台每 0.5 秒测一次，主控要的时候 `CMD_FETCH_DATA` 拿最新结果即可，不阻塞。比每次都发测量命令等 15ms 高效。

**(4) 读温湿度** —— 发 fetch 命令 → 收 6 字节 → CRC 校验 → 换算：

```c
int KE1_I2C_SHT31(float *pfTemp, float *pfHumi) {
    uint8_t read_buff[6] = {0};
    i2c_write_cmd(CMD_FETCH_DATA);  // 0xE000 取周期模式结果
    HAL_I2C_Master_Receive(&hi2c2, SHT30_ADDR_RD, read_buff, 6, 0xffff);
    // 6 字节 = [T高,T低,T的CRC, H高,H低,H的CRC]
    if (CheckCrc8(read_buff, 0xFF) != read_buff[2] ||
        CheckCrc8(&read_buff[3], 0xFF) != read_buff[5]) return HAL_ERROR;
    uint16_t t = (read_buff[0]<<8) | read_buff[1];
    *pfTemp = -45 + 175 * (t / 65535.0f);   // 官方换算公式
    uint16_t h = (read_buff[3]<<8) | read_buff[4];
    *pfHumi = 100 * (h / 65535.0f);
    return HAL_OK;
}
```

> **WHY that formula?** SHT31 输出 16 位原始值 (0~65535)，线性映射到物理量：温度 -45~130°C，湿度 0~100%。公式来自 Sensirion 数据手册，背下来没意义，知道「原始 16 位 → 物理值」是线性映射即可。

### 4.3 在 main 里调用

`main.c` 的 `USER CODE BEGIN 2`（初始化区）：

```c
/* USER CODE BEGIN 2 */
printf("SHT31 demo start\r\n");
if (KE1_I2C_SHT31_Init() != HAL_OK) {
    printf("SHT31 init FAIL! check wiring\r\n");
} else {
    printf("SHT31 init OK\r\n");
}
/* USER CODE END 2 */
```

`USER CODE BEGIN WHILE`（主循环）：

```c
/* USER CODE BEGIN WHILE */
float t = 0, h = 0;
while (1)
{
    if (KE1_I2C_SHT31(&t, &h) == HAL_OK) {
        printf("T=%.2f'C H=%.2f%%\r\n", t, h);
    } else {
        printf("read fail (CRC or I2C)\r\n");
    }
    HAL_Delay(1000);
    /* USER CODE END WHILE */
}
```

### 4.4 编译烧录，看结果

串口助手 115200 打开，应该每秒一行：

```
SHT31 demo start
SHT31 init OK
T=25.43'C H=58.20%
T=25.41'C H=58.18%
...
```

**用手捂住 SHT31**（体温 ~36°C），温度应该缓慢上升 1-3°C，湿度也会变（手上有水汽）。这就证明读到了真实物理量。

> ✅ **检查点 3.2**: 温度在室温附近（20-30°C），湿度 30-70%，手捂会升 → SHT31 全链路通了。

---

## 五、常见错误 | Common Errors

| 现象 | 原因 | 解决 |
|------|------|------|
| `SHT31 init FAIL` | 接线错 / 没接上拉 / VCC 没接 | 检查 4 根线；模块板载有上拉则别重复加；确认 3.3V |
| 一直读到 `T=-45.00 H=0.00` | I2C 收到全 0 → 地址错 / SCL/SDA 接反 | 确认 `SHT30_ADDR_WR=0x88`；检查 PB13 是 SCL、PB14 是 SDA |
| 一直 `read fail (CRC)` | 接线接触不良 / 上拉太弱 / 线太长 | 换短杜邦线；加一个 4.7kΩ 上拉到 3.3V |
| 温度一直是固定值如 `T=25.00` | 周期模式没启动 / 没 delay | 确认 `KE1_I2C_SHT31_Init` 里 `CMD_MEAS_PERI_2_M` 发了，且后面有 25ms delay |
| 数值乱跳（忽高忽低） | 电源不稳 / SDA/SCL 串扰 | VCC 加个 0.1μF 去耦电容；线别绕一起 |
| 编译报错 `hi2c2 undeclared` | `i2c.c` 没引用到 `hi2c2` | 确认 `#include "i2c.h"` 在前 |

---

## 六、调试技巧 | Debugging Tips

1. **I2C 扫描器**: 怀疑地址不对？写个循环 `for(addr=1; addr<128; addr++)` 用 `HAL_I2C_IsDeviceReady(&hi2c2, addr<<1, 3, 100)` 扫，能应答的地址就是接上的设备。SHT31 应该在 `0x44`。
2. **先读寄存器再读数据**: 串口打印 `read_buff[0..5]` 的原始 hex，对照「T高T低CRC H高H低CRC」看，数据合理再信公式。
3. **I2C 卡死怎么办**: STM32 的 I2C 有「总线锁死」老毛病——如果上次通信中途复位，从机可能一直拉低 SDA。解决：上电时把 SCL 手动 toggle 9-16 次（用 GPIO 模拟）释放总线。HAL 没现成函数，参考 `hardware/troubleshooting.md`。
4. **示波器/逻辑分析仪**: ¥30 的 USB 逻辑分析仪 + PulseView 软件，能直接抓 I2C 波形看 START/ACK/数据，I2C 调试终极武器。
5. **用 `HAL_I2C_Master_Transmit` 的返回值**: 它返回 `HAL_OK/HAL_ERROR/HAL_BUSY/HAL_TIMEOUT`。每次都检查返回值并 `printf` 出来，比啥都不查强一百倍。

---

## 七、今日检查点 | Day 3 Checkpoints

- [ ] 能讲清楚 I2C 为什么用开漏+上拉（「线与」概念）
- [ ] SHT31 接好，`KE1_I2C_SHT31_Init()` 返回 `HAL_OK`
- [ ] 串口每秒打印 `T=xx.xx'C H=xx.xx%`，数值合理
- [ ] 手捂传感器，温度能上升
- [ ] 能指出 `0x88` 是怎么从 `0x44` 来的（7 位地址左移 1 位）
- [ ] 截图存档：串口温湿度输出 + 手捂前后对比

---

## 八、今日作业 | Homework

1. **数据记录**: 让程序跑 10 分钟，记录每分钟一条温湿度到 `week-1-checkin.md` 的表格里。观察室温波动范围。
2. **改刷新率**: 把 `HAL_Delay(1000)` 改成 `5000`（5 秒一次），看 SHT31 周期模式是否还是准的。
3. **加异常处理**: 当 `KE1_I2C_SHT31` 连续返回 `HAL_ERROR` 3 次，串口打印 `SENSOR LOST` 并点亮板载 LED 报警。
4. **回答**:
   - I2C 的 SCL 和 SDA 各是什么作用？为什么可以多设备共用？
   - SHT31 地址 0x44，为什么 HAL 函数里传 0x88？
   - CRC 校验失败为什么要丢弃这次读数，不能凑合用？
5. **Git 提交**:
   ```bash
   git add curriculum/day-03.md
   git commit -m "day03: SHT31 I2C driver, reading temp/humidity"
   ```

---

## 九、明日预告 | Tomorrow

**Day 4: OLED 显示 —— SSD1306 + 显示温湿度**
- 把温湿度从串口搬到 OLED 屏幕上
- SSD1306 显示原理（页/列、字模、软件 I2C）
- 烧 UP主的 OLED 驱动，屏幕显示「温度 湿度」

**前置准备**: 找到 SSD1306 OLED 模块（4 针 I2C 版），4 根杜邦线。

---

*最后更新: 2026-06 | Last updated: 2026-06*
