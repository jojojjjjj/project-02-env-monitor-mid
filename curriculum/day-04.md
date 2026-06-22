# Day 4: OLED 显示 —— SSD1306 + 显示温湿度 | OLED Display: SSD1306 + Showing Temp/Humidity

> **学习目标 | Learning Objectives**
> - 理解 SSD1306 OLED 的显示原理：128×64 像素、页/列寻址、字模
> - 把 OLED 接到 KE1 板的 PB8/PB9（软件 I2C），理解为什么 OLED 用软件 I2C 而 SHT31 用硬件 I2C
> - 烧录 UP主提供的 OLED 驱动，屏幕上显示「温度 + 湿度」
> - 理解字模（font）的概念，知道怎么显示中文

> **产出 | Deliverable**: OLED 屏幕显示一行「温度 xx.xx°C 湿度 xx.xx%」，数值随 SHT31 实时更新

---

## 一、前置检查 | Pre-flight Checklist

- [ ] Day 3 的 SHT31 已跑通，串口能持续打印温湿度
- [ ] 手上有 SSD1306 OLED 模块（0.96"，128×64，I2C，4 针：VCC/GND/SCL/SDA）
- [ ] 4 根杜邦线

---

## 二、SSD1306 显示原理 —— 像素怎么亮起来 | SSD1306 Display: Lighting Up Pixels

### 2.1 OLED 是什么

OLED = Organic LED，有机发光二极管。每个像素自己发光（不像 LCD 要背光），所以黑得纯粹、对比度高、功耗低。0.96" SSD1306 是 128×64 像素的单色屏，最常见的入门显示。

### 2.2 128×64 像素怎么组织成「页 (page)」

SSD1306 把 64 行像素分成 **8 页 (page 0-7)**，每页 8 行高、128 列宽。写显示数据时按「页 + 列」寻址：

```
          列 0  1  2  3 ... 127
        ┌────────────────────────┐
页 0    │  8 行高 (bit0=上, bit7=下)│
页 1    │  8 行高                 │
...     │  ...                    │
页 7    │  8 行高                 │
        └────────────────────────┘
```

每个字节（8 bit）写入某一页的某一列，就垂直点亮 8 个像素——bit0 是最上面那行，bit7 是最下面那行。这就是为什么字模是「8 像素高一组」存的。

> **WHY page-based not pixel-based?** SSD1306 控制器芯片这么设计的，按字节写更高效（写 1 字节控制 8 像素）。配套的字模库也按 8 像素高排列。我们用现成驱动，不用深究，但要知道「显示字符 = 往某个页某个列写一串字节」。

### 2.3 字模 (Font) —— 字符怎么变像素

显示字符 `'A'`，需要知道 A 长什么样。字模就是一个数组，存每个字符对应的像素点阵。比如 8×16 字体里，'A' 的字模是 16 个字节：

```c
// KE1 参考源码 oledfont.h 里的 F8X16 数组
// 'A' = ASCII 65, 偏移 = (65-32)*16
// 每个 8x16 字符占 16 字节（上半 8 字节 + 下半 8 字节）
0x04,0x1C,0xC0,0xE0,0xE0,0xC0,0x1C,0x04,  // 上半 8 行
0x07,0x0F,0x10,0x10,0x10,0x10,0x0F,0x07,  // 下半 8 行
```

`OLED_ShowChar` 函数就干这个：算出字符在字模数组里的偏移，把对应 16 字节按「先上半页，再下半页」写到 SSD1306。

> **WHY `c - ' '`?** 字模数组从空格 `' '` (ASCII 32) 开始存，所以字符 `c` 在数组里的下标是 `c - 32`，即 `c - ' '`。KE1 源码 `OLED_ShowChar` 里 `c=chr-' '` 就是这意思。

### 2.4 中文怎么办

英文字符有 ASCII 标准编码，字模好做。中文有几千个，不能全塞进 Flash。KE1 源码 `oledfont.h` 里的 `F_Chx16` 数组**只预存了项目用到的几个汉字**（如「温」「湿」「度」「电」「压」），按编号索引：

```c
// OLED_ShowCHinese(x, y, no) 里的 no 就是汉字在 F_Chx16 里的编号
OLED_ShowCHinese(0, 0, 0);  // 显示编号 0 的汉字（比如「温」）
OLED_ShowCHinese(17, 0, 1); // 显示编号 1 的汉字（比如「湿」）
```

> **WHY not use a full Chinese font?** 一个 16×16 全字库要 ~250KB，STM32L433 的 Flash 虽然有 256KB 但要放程序。只存用到的几十个字（叫「点阵字库子集」）最省。如果以后要显示任意中文，要么外挂 SPI Flash 存全字库，要么用 GT30L32S4W 字库芯片——本项目不需要。

---

## 三、为什么 OLED 用软件 I2C | Why Software I2C for OLED

KE1 的设计：
- **SHT31 → 硬件 I2C2 (PB13/PB14)**：稳定、准、省 CPU
- **OLED → 软件 I2C (PB8/PB9)**：用 GPIO 手动拉 SCL/SDA 时序

为什么 OLED 用软件 I2C？三个原因：

1. **OLED 驱动是老代码移植**：UP主的 OLED 驱动从早期 8051/STM32F1 项目搬来，本来就是软件 I2C，移植过来不改最省事。
2. **I2C2 已经被 SHT31 占了**：硬件 I2C 同一时刻只能一套时序。虽然 I2C 理论上能挂多设备，但 OLED 刷整屏数据量大、时序长，和 SHT31 的小数据包混在一条硬件 I2C 上容易互相阻塞。分开两条总线最干净。
3. **软件 I2C 灵活**：任意两个 GPIO 都能跑，不挑引脚，方便布局。

> **WHY not put both on I2C2?** 完全可以，SHT31 (0x44) 和 OLED (0x78) 地址不冲突，理论能共存。但 UP主 选择分开，复刻就照搬——这也教了你一个真实工程习惯：「同类型高速设备和低速大块数据设备分总线」。

软件 I2C 的实现就是 Day 3 讲的 START/STOP/ACK 时序，用 `HAL_GPIO_WritePin` 手动拉。看参考源码 `oled.c` 的 `IIC_Start`/`IIC_Stop`/`Write_IIC_Byte` 就是手摇时序。

---

## 四、接线 —— OLED 接到 PB8/PB9 | Wiring OLED to PB8/PB9

### 4.1 接线表

| OLED 模块 | KE1 板引脚 | 说明 |
|-----------|-----------|------|
| VCC | 3.3V | OLED 3.3V 供电（部分模块兼容 5V，但接 3.3V 最安全） |
| GND | GND | 共地 |
| SCL | PB8 | 软件 I2C 时钟（`oled.h` 里 `OLED_SCLK_Clr/Set` 操作的就是 PB8） |
| SDA | PB9 | 软件 I2C 数据 |

### 4.2 CubeMX 配置 PB8/PB9 为 GPIO 输出

1. `.ioc` 里把 PB8 设为 `GPIO_Output`，Label = `OLED_SCL`；PB9 设为 `GPIO_Output`，Label = `OLED_SDA`。
2. 两个都选 **Push-Pull** 输出（软件 I2C 自己控制电平，不用开漏——因为总线上就一个主控一个从机，且 OLED 模块板载有上拉）。**注意：这里和硬件 I2C 不同，硬件 I2C 必须开漏+上拉，软件 I2C 用推挽也可以**（只要总线上没有别的设备争抢）。
3. 速度选 High。
4. `Generate Code`。

> **检查点 4.1**: 看 `oled.h` 顶部那几个宏：
> ```c
> #define OLED_SCLK_Clr() HAL_GPIO_WritePin(GPIOB,GPIO_PIN_8, GPIO_PIN_RESET);
> #define OLED_SCLK_Set() HAL_GPIO_WritePin(GPIOB,GPIO_PIN_8, GPIO_PIN_SET);
> #define OLED_SDIN_Clr() HAL_GPIO_WritePin(GPIOB,GPIO_PIN_9, GPIO_PIN_RESET);
> #define OLED_SDIN_Set() HAL_GPIO_WritePin(GPIOB,GPIO_PIN_9, GPIO_PIN_SET);
> ```
> 你的 CubeMX 配的引脚必须和这些宏一致。如果用别的引脚，改宏或改 CubeMX。

---

## 五、烧录 UP主提供的 OLED 驱动 | Flashing the Provided OLED Driver

### 5.1 加文件

1. `software/src/oled.c` → 工程的 `Core/Src/`
2. `software/src/oled.h` + `software/src/oledfont.h` → `Core/Inc/`
3. `main.c` 顶部 `#include "oled.h"`

### 5.2 读懂驱动关键函数

参考源码 `oled.c`：

- **`OLED_Init()`**: 发一串初始化命令（对比度、扫描方向、显示模式…）。SSD1306 上电要先初始化才能正常显示。
- **`OLED_Clear()`**: 清屏（全写 0）。
- **`OLED_ShowString(x, y, "abc", 16)`**: 在 (x, y) 显示 ASCII 字符串，16 号字体。
- **`OLED_ShowNum(x, y, 12345, 5, 16)`**: 显示数字，5 位数。
- **`OLED_ShowT_H(float T, float H)`**: KE1 专门写的「显示温湿度」函数：

```c
void OLED_ShowT_H(float T, float H) {
    char acOledLineMsg[17] = {0};
    // 先显示「温度」两个汉字（编号 7,8 在 F_Chx16 里）
    OLED_ShowCHinese(0, 0, 7);  OLED_ShowCHinese(17, 0, 8);
    // ...再用 snprintf 格式化数字，ShowString 显示
    snprintf(acOledLineMsg, sizeof(acOledLineMsg), "%.2f'C %.2f%%", T, H);
    OLED_ShowString(0, 2, (uint8_t *)acOledLineMsg, 16);
}
```

> **WHY snprintf not sprintf?** `snprintf` 限制最大长度，防止缓冲区溢出。嵌入式上 `sprintf` 溢出是经典崩溃源——`acOledLineMsg` 只有 17 字节，超了就踩内存。`snprintf(buf, sizeof(buf), ...)` 永远安全。

### 5.3 在 main 里调用

`USER CODE BEGIN 2`（初始化区）：

```c
/* USER CODE BEGIN 2 */
KE1_I2C_SHT31_Init();
OLED_Init();
OLED_Clear();
printf("OLED ready\r\n");
/* USER CODE END 2 */
```

`USER CODE BEGIN WHILE`：

```c
/* USER CODE BEGIN WHILE */
float t = 0, h = 0;
while (1)
{
    if (KE1_I2C_SHT31(&t, &h) == HAL_OK) {
        OLED_ShowT_H(t, h);          // 屏幕显示
        printf("T=%.2f H=%.2f\r\n", t, h);  // 串口同步
    }
    HAL_Delay(1000);
    /* USER CODE END WHILE */
}
```

### 5.4 编译烧录，看屏幕

OLED 应该显示：

```
温湿度      （第一行，汉字）
25.43'C 58.20%   （第三行，数字）
```

数值每秒刷新。**注意**：汉字显示需要 `oledfont.h` 里有对应字模。KE1 源码预存的汉字编号要和你想显示的对上，如果显示乱码，说明 `F_Chx16` 里没那个字——要么改用英文，要么用取模软件（PCtoLCD2002）加字模。

> ✅ **检查点 4.2**: OLED 显示温湿度数值，每秒刷新，手捂传感器屏幕数值跟着变。

---

## 六、常见错误 | Common Errors

| 现象 | 原因 | 解决 |
|------|------|------|
| OLED 完全不亮 | VCC/GND 接反或没接 / 初始化没跑 | 检查供电；确认 `OLED_Init()` 被调用，有 `HAL_Delay(200)` 等启动 |
| OLED 亮但全屏雪花 | SCL/SDA 接反 / 软件时序错 | 交换 PB8/PB9 的线试试；确认 `oled.h` 宏和接线一致 |
| 显示乱码（英文） | 字模偏移错 / 字体选错 | 确认 `OLED_ShowChar` 用 `F8X16`（16号）或 `F6x8`（小号）对应 |
| 汉字显示成方块或乱码 | `oledfont.h` 里没那个字模 | 用取模软件加字模到 `F_Chx16`，或改显示英文 |
| 显示抖动/闪屏 | 每次刷新整屏导致 | 只刷新变化的行（KE1 的 `OLED_ShowT_H` 已经只刷一行） |
| 字符重叠 | 坐标算错，没换行 | `ShowString` 的 y 是页号(0-7)，每行隔 2 页（16号字高=2页） |
| I2C2 和软件 I2C 互相干扰 | 共用 GPIO 或中断冲突 | 确认 SHT31 在 PB13/14，OLED 在 PB8/9，完全分开 |

---

## 七、调试技巧 | Debugging Tips

1. **先显示固定字符串**: 别急着显示传感器数据。先 `OLED_ShowString(0,0,"Hello",16);` 能显示再接传感器，分离「显示问题」和「数据问题」。
2. **OLED 地址确认**: SSD1306 地址通常是 `0x78`（SA0=0）或 `0x7A`（SA0=1）。KE1 源码写死 `0x78`。如果你的模块地址是 `0x7A`，改 `oled.c` 里 `Write_IIC_Byte(0x78)` 为 `0x7A`。
3. **字模取模工具**: PCtoLCD2002 / LCD 字模提取工具，输入汉字自动生成 16×16 字模，粘贴到 `oledfont.h`。
4. **刷新策略**: 整屏 `OLED_Clear` + 重绘会闪。更好的做法是只重画变化的区域。KE1 的 `OLED_ShowT_H` 直接覆盖同一行，靠数字位数一致掩盖旧值——简单有效。
5. **示波器看软件 I2C**: 逻辑分析仪抓 PB8/PB9，能看到手摇的 START/字节/STOP。如果时序不对（比如 `IIC_Wait_Ack` 没等够），波形会乱。

---

## 八、今日检查点 | Day 4 Checkpoints

- [ ] OLED 接好，`OLED_Init()` 后屏幕能显示内容
- [ ] 屏幕显示温湿度，每秒刷新
- [ ] 能解释「为什么 OLED 用软件 I2C，SHT31 用硬件 I2C」
- [ ] 能解释「字模是什么，`c - ' '` 为什么是字模数组下标」
- [ ] 截图：OLED 显示温湿度的照片

---

## 九、今日作业 | Homework

1. **改显示布局**: 把温湿度分两行显示——第一行「T: 25.43'C」，第二行「H: 58.20%」。需要用 `OLED_ShowString` 分别定位 y=2 和 y=4。
2. **加标题**: 第一行显示「EnvClock」或「环境时钟」（后者需要加字模），温湿度下移。
3. **断电记忆测试**: 断电再上电，OLED 是否能正常初始化显示？记录启动到出画的时间（应该 <1 秒）。
4. **回答**:
   - SSD1306 的「页」是什么概念？为什么 64 行分成 8 页？
   - 软件用 `snprintf` 而不是 `sprintf` 的原因？
   - 为什么 OLED 用推挽、SHT31 的硬件 I2C 用开漏？
5. **Git 提交**:
   ```bash
   git add curriculum/day-04.md
   git commit -m "day04: SSD1306 OLED driver, displaying temp/humidity"
   ```

---

## 十、明日预告 | Tomorrow

**Day 5: ESP8266 WiFi 模块 —— AT 固件 + 接线 + AT 命令试通**
- 认识 ESP-01S（ESP8266），理解它为什么通过 AT 命令和主控通信
- 接 ESP-01S 到 KE1 的 USART3 (PB10/PB11)，注意 3.3V 电平
- 用串口发 `AT`、`AT+CWJAP` 试通，收到 `OK` 和 WiFi 连接成功

**前置准备**: 找到 ESP-01S 模块 + 一个 3.3V 供电（ESP-01S 峰值电流大，KE1 板的 3.3V 可能不够，准备一个外部 3.3V 或 AMS1117 模块）。

---

*最后更新: 2026-06 | Last updated: 2026-06*
