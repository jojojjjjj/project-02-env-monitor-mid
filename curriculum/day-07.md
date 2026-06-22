# Day 7: 时钟整合 —— 时间显示 + 温湿度 + 定时刷新 | Clock Integration: Time + Temp/Humidity + Refresh

> **学习目标 | Learning Objectives**
> - 把时间、日期、温湿度整合成一个完整、美观的桌面时钟 OLED 界面
> - 理解显示布局设计：信息层级、字号对比、刷新策略
> - 实现大字号时间显示（用 16×32 或拼接字模）
> - 解决「整屏刷新闪屏」问题，只刷变化的区域

> **产出 | Deliverable**: OLED 显示一个完整桌面时钟——大字号时间 `14:30` + 秒 + 日期 + 温湿度，每秒平滑刷新不闪屏

---

## 一、前置检查 | Pre-flight Checklist

- [ ] Day 6 网络时间已同步，OLED 能显示时间
- [ ] Day 3/4 的 SHT31 温湿度 + OLED 显示已跑通
- [ ] 主循环里时间 tick 和温湿度读取都已能跑（虽然可能各刷各的、有点乱）

---

## 二、界面设计 —— 像产品经理一样想 | UI Design: Think Like a PM

### 2.1 先想清楚「谁看、看什么」

这是个**桌面摆件**，使用者抬头瞄一眼要能 0.5 秒内抓到关键信息。优先级：

1. **时间 `HH:MM`**（最高优先级，最大字号）—— 摆件的核心功能
2. **秒 `:SS`**（次大字号，让用户知道在走）
3. **日期 `2026-06-22 周一`**（中等字号，偶尔看）
4. **温湿度 `25.4°C 58%`**（小字号，环境信息）

> **WHY this priority?** 「网络时钟」卖点是时间。温湿度是附加价值。如果温湿度和时间一样大，用户抓不住重点。真实产品设计都是「主功能占视觉中心，辅助功能退到角落」。Apple Watch、小米台灯时钟都是这个逻辑。

### 2.2 OLED 布局规划（128×64 像素）

```
┌────────────────────────────────────┐  ← 128 列
│  14:30:45                          │  页0-1: 大时间 (32 高)
│                                    │
│  2026-06-22 Mon                    │  页2: 日期 (8 高, 小字)
│                                    │  页3: 空
│  T:25.4'C  H:58%                   │  页4-5: 温湿度 (16 高)
│                                    │  页6: 空
│  [WiFi] ✓                          │  页7: 状态 (8 高, 小字)
└────────────────────────────────────┘  ← 64 行 = 8 页
```

- 页 0-1（32 像素高）：大字号时间，用 16×32 字模拼接，或 2 倍放大 16×16
- 页 2（8 像素高）：日期，6×8 小字
- 页 4-5（16 像素高）：温湿度，8×16 中字
- 页 7（8 像素高）：WiFi 状态、NTP 状态指示

### 2.3 为什么大字号时间要用 32 高

`OLED_ShowString` 默认 8×16 字模，时间 `14:30:45` 在 128 宽里只占 ~56 像素，太小。桌面摆件要 3 米外能看清，时间得占满半屏。

两种放大方案：
- **方案 A**：用 16×32 的大字模（要单独做字模表，只做数字 0-9 和冒号 `:`）
- **方案 B**：16×16 字模纵向×2 显示（每个像素写两遍，简单但锯齿重）

> **WHY方案A better?** 16×32 字模是手工设计的高质量点阵，清晰无锯齿。方案B像素复制会有马赛克感。但方案A要你用取模软件做 11 个字符（0-9 + `:`）的字模，加进 `oledfont.h`。复刻模式下 `software/src/oledfont.h` 可能已附大字模，检查一下。

---

## 三、实现完整时钟界面 | Implementing the Full Clock UI

### 3.1 新增 `OLED_ShowClock` 函数

在 `oled.c` 的 USER CODE 区加（如果 `software/src/oled.c` 已提供就用现成的）：

```c
// 显示大字号时间 HH:MM:SS
void OLED_ShowClockBig(uint8_t hour, uint8_t min, uint8_t sec) {
    char buf[9];
    snprintf(buf, sizeof(buf), "%02d:%02d:%02d", hour, min, sec);
    // 用 16x32 大字模逐字符显示，x 从 8 开始留边
    for (int i = 0; i < 8; i++) {
        OLED_ShowCharBig(8 + i*16, 0, buf[i]);  // 16x32 字模函数
    }
}

// 完整时钟界面
void OLED_ShowClockFull(const ClockTime *c, float t, float h, int wifiOk) {
    char line[17];

    // 第 1-2 页：大时间
    OLED_ShowClockBig(c->hour, c->min, c->sec);

    // 第 3 页：日期 + 星期
    const char *wk[] = {"Sun","Mon","Tue","Wed","Thu","Fri","Sat"};
    snprintf(line, sizeof(line), "%04d-%02d-%02d %s",
             c->year, c->month, c->day, wk[c->weekday]);
    OLED_ShowString(0, 3, (uint8_t*)line, 8);

    // 第 4-5 页：温湿度
    snprintf(line, sizeof(line), "T:%.1f'C H:%.0f%%", t, h);
    OLED_ShowString(0, 4, (uint8_t*)line, 16);

    // 第 7 页：状态
    OLED_ShowString(0, 7, (uint8_t*)(wifiOk ? "WiFi OK" : "WiFi --"), 8);
}
```

### 3.2 星期怎么来

ESP8266 的 `CIPSNTPTIME` 返回里有英文星期 (Mon/Tue/...)，`Clock_ParseFromAT` 一并存进 `ClockTime.weekday` (0=Sun..6=Sat)。如果没存，从年月日算：

```c
// Zeller 公式算星期（0=Sunday）
int day_of_week(int y, int m, int d) {
    if (m < 3) { m += 12; y -= 1; }
    int k = y % 100, j = y / 100;
    int h = (d + 13*(m+1)/5 + k + k/4 + j/4 + 5*j) % 7;
    return (h + 6) % 7;  // 转成 0=Sun
}
```

> **WHY not just trust ESP's weekday?** ESP 返回的星期来自 NTP，通常准。但如果想本地 `Clock_Tick` 跨午夜时星期自动 +1，需要从日期反算或手动进位。`day_of_week` 让你任何时候从年月日推出星期，最稳。Zeller 公式看着吓人，照抄即可。

### 3.3 整合主循环

```c
/* USER CODE BEGIN WHILE */
ClockTime now = {0};
float t = 0, h = 0;
uint32_t lastSync = 0, lastSensor = 0, lastDisplay = 0;
int wifiOk = 0;

while (1)
{
    uint32_t tick = HAL_GetTick();

    // ① 每 30 分钟重新 SNTP 对时
    if (tick - lastSync > 30*60*1000 || lastSync == 0) {
        wifiOk = SNTP_Sync(&now);  // 封装了 Day 6 的逻辑
        if (wifiOk) lastSync = tick;
    }

    // ② 每 1 秒：本地 tick + 读传感器 + 刷显示
    if (tick - lastDisplay >= 1000) {
        lastDisplay = tick;
        Clock_Tick(&now);

        if (tick - lastSensor > 5000) {  // 温湿度 5 秒读一次
            if (KE1_I2C_SHT31(&t, &h) == HAL_OK) lastSensor = tick;
        }

        OLED_ShowClockFull(&now, t, h, wifiOk);
        printf("%02d:%02d:%02d T=%.1f H=%.0f\r\n",
               now.hour, now.min, now.sec, t, h);
    }
    /* USER CODE END WHILE */
}
```

### 3.4 刷新策略：为什么温湿度 5 秒、时间 1 秒（讲 WHY）

- **时间 1 秒刷**：秒数必须每秒变，不然不像时钟
- **温湿度 5 秒刷**：温湿度变化慢，每秒读浪费 I2C 带宽、且数值抖动
- **SNTP 30 分钟刷**：网络对时重操作

这种「不同数据不同刷新率」是真实系统的标配——不是所有东西都要一个频率。

> **WHY not refresh everything every second?** ①省 I2C 总线（SHT31 频繁读影响寿命和稳定性）②省 CPU ③温湿度秒级变化无意义（人体感知不到 0.1°C 变化）④减少 OLED 写入次数延长寿命（OLED 烧屏）。

---

## 四、防闪屏 —— 只刷变化的区域 | Anti-flicker: Only Redraw What Changed

### 4.1 闪屏怎么来的

如果你每秒 `OLED_Clear()` + 整屏重绘，屏幕会黑一下再亮——肉眼可见闪屏。原因是整屏清写要几十毫秒，期间像素灭再亮。

### 4.2 解决：局部刷新

**永远不要在主循环里调 `OLED_Clear()`**。改用「只重画变化的行」：

- 时间行：每秒都变，必须刷——但只刷时间那一行（页 0-1），不动其他
- 日期行：跨午夜才变，平时不刷
- 温湿度行：5 秒刷一次
- 状态行：WiFi 状态变化时才刷

实现：用一个 `lastShownMin` / `lastShownSec` 变量记录上次显示的值，只在变化时刷对应区域。

```c
static uint8_t lastSec = 0xFF, lastMin = 0xFF;
if (now.sec != lastSec) {
    // 只刷新秒部分（x 偏移到秒的位置）
    OLED_ShowCharBig(SECONDS_X, 0, '0' + now.sec/10);
    OLED_ShowCharBig(SECONDS_X+16, 0, '0' + now.sec%10);
    lastSec = now.sec;
}
```

> **WHY this matters?** OLED 烧屏 (burn-in) 是真实问题——同一个静态画面显示几小时，像素老化不均。局部刷新既防闪屏又防烧屏。KE1 的 `OLED_ShowT_H` 也是这个思路（覆盖同一行，靠数字位数掩盖旧值）。

---

## 五、常见错误 | Common Errors

| 现象 | 原因 | 解决 |
|------|------|------|
| 整屏闪一下每秒 | 主循环里 `OLED_Clear()` 了 | 删掉 Clear，改局部刷新 |
| 大字号显示乱码 | 16×32 字模没做 / 索引错 | 用取模软件做 0-9 和 `:` 的字模加进 `oledfont.h` |
| 时间和温湿度重叠 | 坐标算错，页号冲突 | 规划好页分配：时间页0-1，日期页2-3，温湿度页4-5，状态页7 |
| 秒数不动但分钟能进 | 只刷了分钟没刷秒 | 检查 `lastSec` 分支 |
| 跨秒时秒位残留旧数字 | 没清掉旧字符 | 刷新值前先写两个空格 `'  '` 覆盖，或保证新值位数和旧值一样 |
| WiFi 断了界面不更新 | `SNTP_Sync` 阻塞太久卡住主循环 | SNTP 失败要快速超时返回，别死等 |
| OLED 烧屏痕迹 | 长时间同一画面 | 加「像素偏移」：每小时整体左右移 1 像素；或降低亮度 (`OLED_WR_Byte(0x81,0); OLED_WR_Byte(0x80,1);`) |

---

## 六、调试技巧 | Debugging Tips

1. **画在纸上先**: 拿方格纸画出 128×64 网格，标好每行每列放什么，再写代码——比对着屏幕调快。
2. **静态画面调试**: 先把时间写死 `14:30:00`，调布局到好看，再接真实动态数据。
3. **`OLED_ShowString` 坐标系**: x 是列 (0-127)，y 是**页号 (0-7)**不是像素行。8 号字高 8 像素占 1 页，16 号字高 16 像素占 2 页。
4. **截图存档**: 用手机拍下最终界面，存到 `week-2-checkin.md`——这是 Day 7 的核心交付物。
5. **对比手机**: 把 OLED 时间和手机时间并排拍一张，证明准。

---

## 七、今日检查点 | Day 7 Checkpoints

- [ ] OLED 显示完整界面：大时间 + 日期 + 温湿度 + WiFi 状态
- [ ] 时间每秒刷新，不闪屏
- [ ] 温湿度 5 秒刷新一次，数值合理
- [ ] 跨分钟、跨小时、跨 0 点（可手动改时间测）正确进位
- [ ] 能解释「为什么不同数据用不同刷新率」
- [ ] 截图：完整时钟界面 + 和手机时间对比

---

## 八、今日作业 | Homework

1. **界面美化**: 加一个「冒号闪烁」效果——`:` 每秒亮灭一次（秒为奇数显示 `:`，偶数显示 ` `），像真电子钟。
2. **温湿度超限提示**: 温度 >30°C 或 <10°C 时，温湿度那行反白显示（或加 `!` 标记）。
3. **启动画面**: 上电先显示 2 秒「EnvClock / WiFi 对时中...」，对时成功后再切主界面。
4. **回答**:
   - 为什么主循环里不能 `OLED_Clear()`？
   - 时间 1 秒刷、温湿度 5 秒刷、SNTP 30 分钟刷——这样设计的依据是什么？
   - OLED 烧屏是什么，怎么避免？
5. **Git 提交**:
   ```bash
   git add curriculum/day-07.md
   git commit -m "day07: integrated clock UI, time+temp/humidity+status"
   ```

---

## 九、明日预告 | Tomorrow

**Day 8: 完善 —— 蜂鸣器整点报时 / 按键调时 / 断网回退**
- 加蜂鸣器用 PWM 实现整点报时（滴答声）
- 加按键手动调时（断网备用）
- 实现断网回退：WiFi 断了用本地 tick 继续走，恢复后自动重对时

**前置准备**: 找无源蜂鸣器 + 1 个轻触按键 + 杜邦线。

---

*最后更新: 2026-06 | Last updated: 2026-06*
