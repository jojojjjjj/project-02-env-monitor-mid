# Day 8: 完善 —— 蜂鸣器整点报时 / 按键调时 / 断网回退 | Polish: Hourly Chime / Button Adjust / Offline Fallback

> **⏱ 预计耗时 | Estimated Time**: 约 5-6 小时 | ~5-6 hours

> Day 8 adds a PWM buzzer for hourly chimes, GPIO buttons for manual time adjustment, and an offline-fallback architecture so the clock keeps ticking on local tick when WiFi drops and auto-reconnects when it returns — the difference between "runs" and "product-grade".

> **学习成果 | Learning Outcomes**
> - **实现 (Implement)** PWM 驱动无源蜂鸣器整点报时，GPIO 输入按键 + 软件消抖实现手动调时
> - **解释 (Explain)** 断网回退架构：本地 tick 无条件走 + 网络只做定期校正的分离设计
> - **分析 (Analyze)** 「鲁棒性 (robustness)」——单点故障（WiFi 断）不能让整个产品挂掉
> - **设计 (Design)** 重连策略：失败快速超时、周期重试、状态指示

## 为什么学这个 | Why This Matters

前 7 天你的时钟「有网才好用」，今天要让它变成「没网也不死」。类比：手机开飞行模式时，时钟照走、闹钟照响，连上网才悄悄校时——你不会因为没信号就看不了时间。今天做的三件事（蜂鸣器报时、按键调时、断网回退）就是把时钟从「实验室原型」升级到「敢放床头每天用」的产品。鲁棒性是区分「能跑」和「产品级」的关键。

> **产出 | Deliverable**: 一个能整点报时、能按键调时、断网不死、恢复自动重连的完整时钟

---

## 一、前置检查 | Pre-flight Checklist

- [ ] Day 7 的完整时钟界面已跑通
- [ ] 手上有无源蜂鸣器（**无源**，不是有源；无源没内置振荡源，靠 PWM 出声）+ 2 个轻触按键（KEY1/KEY2）+ 杜邦线
- [ ] 主循环已用「不同数据不同刷新率」的非阻塞结构（Day 7 §3.3）

> **引脚约定（与 `hardware/wiring-guide.md` + 固件 `.ioc` 严格一致，勿改）**:
> - 蜂鸣器 = **PA1 / TIM2_CH2**（Prescaler=32-1, Period=370-1 ≈ 2.7kHz）
> - KEY1 = **PC13**，KEY2 = **PA15**（均上拉输入，下降沿触发）

---

## 二、蜂鸣器整点报时 —— PWM 出声 | Buzzer Chime: PWM Sound

### 2.1 无源蜂鸣器原理

蜂鸣器分两种：
- **有源蜂鸣器**：内置振荡源，给直流电就响（只能响一个固定频率）
- **无源蜂鸣器**：没振荡源，要给它方波信号才响，**频率决定音调**

我们用无源蜂鸣器，通过 **PWM (Pulse Width Modulation)** 输出方波。PWM 频率 = 蜂鸣器发声频率。

> **WHY passive buzzer?** 无源蜂鸣器能发不同音调，整点报时可以做成「滴—答—滴」旋律，有源只能单调响。KE1 的 `KE1_PWM` 例程就是教这个。PWM 驱动是无源蜂鸣器的标准方式。

### 2.2 PWM 是什么

PWM = 脉冲宽度调制。定时器输出一个方波，**频率**（每秒多少个脉冲）决定音调，**占空比**（高电平占比）决定音量。对蜂鸣器来说：
- 频率 2kHz → 中音「滴」
- 频率 1kHz → 低音「咚」
- 占空比 50% → 最大音量（无源蜂鸣器 50% 最响）

### 2.3 配 TIM2 产生 PWM

1. CubeMX → `Timers → TIM2`，**Channel2** 选 `PWM Generation CH2`（注意是 **CH2** 不是 CH1）。
2. 引脚锁定 **PA1**（对应 TIM2_CH2，与固件 `.ioc` 和 `wiring-guide.md` 一致）。
3. 参数（对齐 KE1 固件 `tim.c`）：L433 主频 32MHz，`Prescaler = 32-1`（→ 1MHz 计数）, `Counter Period = 370-1`（→ 1MHz/370 ≈ **2.7kHz**，适合蜂鸣器）。
4. `Generate Code`。

> **频率公式**: `f_PWM = 32MHz / (Prescaler+1) / (Period+1) = 32M / 32 / 370 ≈ 2703 Hz`。

> **WHY PA1 / TIM2_CH2（而不是 PA0/CH1）?** STM32 的定时器通道和引脚是硬件绑定的（复用功能 AF）。KE1 例程 `tim.c` 把蜂鸣器接在 **TIM2_CH2 → PA1**，`Beep_Switch()` 启停。复刻固件烧上去即可直接响，**勿改成 CH1/PA0**——否则和固件引脚定义冲突，改完还得改 `HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2)` 的通道号。别和 I2C2 (PB13/14)、软件 I2C (PB8/9)、USART3 (PB10/11)、按键 (PC13/PA15) 冲突。查 `hardware/wiring-guide.md` 的引脚分配表确认。

### 2.4 蜂鸣器接线

| 蜂鸣器 | KE1 板 | 备注 |
|--------|--------|------|
| + (长脚/标识+) | PA1 (TIM2_CH2) | PWM 信号 |
| - | GND | — |

> ⚠️ **注意**: 无源蜂鸣器直接接 GPIO 电流不大，一般能响。如果声音太小或 GPIO 发热，加一个 NPN 三极管驱动（参考 `hardware/wiring-guide.md` 的蜂鸣器电路）。

### 2.5 整点报时代码

```c
// 蜂鸣器响一下，freq 频率，duration 毫秒
// 注意：TIM2_CH2，Prescaler=32-1 → 1MHz 计数（与固件 tim.c 一致）
void Buzzer_Beep(uint32_t freq, uint32_t duration) {
    // 重配 TIM2 Period 改频率（Prescaler 保持 32-1 = 1MHz 计数）
    uint32_t period = 1000000 / freq - 1;
    __HAL_TIM_SET_AUTORELOAD(&htim2, period);
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_2, period/2);  // 50% 占空比，CH2
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2);
    HAL_Delay(duration);
    HAL_TIM_PWM_Stop(&htim2, TIM_CHANNEL_2);
}

// 整点报时：每小时整点响 N 声（N = 当前小时 12 制，或固定 3 声）
void Chime_Hourly(uint8_t hour) {
    uint8_t h12 = hour % 12; if (h12 == 0) h12 = 12;
    for (uint8_t i = 0; i < h12; i++) {
        Buzzer_Beep(2700, 200);   // 滴（默认 2.7kHz，与固件 Period=370-1 一致）
        HAL_Delay(200);
    }
}
```

主循环里检测整点：

```c
static uint8_t lastMin = 0xFF;
if (now.min == 0 && now.sec == 0 && lastMin != 0) {
    Chime_Hourly(now.hour);
}
lastMin = now.min;
```

> **WHY check `lastMin != 0`?** 防止整点那一秒里主循环跑多次重复报时。只在「从非 0 分跨到 0 分 0 秒」那一刻触发一次。

---

## 三、按键调时 —— GPIO 输入 + 消抖 | Button Adjust: GPIO Input + Debounce

### 3.1 按键原理

轻触按键：按下导通、松开断开。接法：一端接 GPIO，另一端接 GND。GPIO 配置成**输入 + 上拉**，平时读 1，按下读 0。

### 3.2 CubeMX 配置

1. **KEY1 接 PC13**（调时「模式/选择」键，也常是板载 USER 键），**KEY2 接 PA15**（「加」键）——与固件 `.ioc` 和 `wiring-guide.md` 一致，勿改其他脚。
2. 都设 `GPIO_Input`（或 `GPIO_EXTI` 中断模式），Pull = `Pull-up`（上拉），按下产生下降沿。
3. Label `KEY1` / `KEY2`（固件即用此命名；调时逻辑里 KEY1=模式键，KEY2=加键）。
4. `Generate Code`。

> **WHY PC13/PA15?** KE1 例程 `gpio.c` 即用 PC13(KEY1) + PA15(KEY2) 配 `GPIO_MODE_IT_RISING` + `GPIO_PULLUP`。PC13 常是板载按键，可直接复用 USER 键，省一个外接按键。复刻固件烧上去中断已配好，轮询或中断读都行。

### 3.3 消抖（讲 WHY）

按键按下瞬间，金属簧片物理抖动，会在几毫秒内产生多次 0/1 跳变——不消抖的话按一下 CPU 看到按了 10 次。

```c
// 带消抖的按键读取：返回 1=刚按下（边沿），0=没按或按住
uint8_t Button_Read(GPIO_TypeDef *port, uint16_t pin, uint8_t *lastState) {
    uint8_t cur = (HAL_GPIO_ReadPin(port, pin) == GPIO_PIN_RESET) ? 1 : 0;
    if (cur && !*lastState) {   // 从松开到按下
        HAL_Delay(20);          // 消抖延时
        if (HAL_GPIO_ReadPin(port, pin) == GPIO_PIN_RESET) {
            *lastState = 1;
            return 1;            // 确认按下
        }
    } else if (!cur) {
        *lastState = 0;
    }
    return 0;
}
```

> **WHY 20ms debounce?** 按键机械抖动通常 5-15ms，20ms 延时能滤掉。太短滤不掉，太长手感迟钝。也可以用「连续 N 次读取都一致」的非阻塞消抖，但 `HAL_Delay(20)` 最简单，够用。

### 3.4 调时逻辑

进入调时模式（长按 KEY1 2 秒），循环切换「时/分/秒」字段，按 KEY2 +1：

```c
// KEY1 = PC13 (模式键)，KEY2 = PA15 (加键) —— 与固件 gpio.c 命名一致
static int adjustMode = -1;  // -1=正常, 0=调时, 1=调分, 2=调秒
static uint32_t modeHoldStart = 0;
static uint8_t key1Last = 0, key2Last = 0;

if (Button_Read(KEY1_GPIO_Port, KEY1_Pin, &key1Last)) {
    modeHoldStart = HAL_GetTick();
}
if (Button_Read(KEY1_GPIO_Port, KEY1_Pin, &key1Last) == 0 &&
    modeHoldStart && HAL_GetTick() - modeHoldStart > 2000 && adjustMode == -1) {
    adjustMode = 0;  // 进入调时
    modeHoldStart = 0;
}
// 在 adjustMode >= 0 时，KEY2 给当前字段 +1
if (adjustMode >= 0 && Button_Read(KEY2_GPIO_Port, KEY2_Pin, &key2Last)) {
    if (adjustMode == 0) now.hour = (now.hour + 1) % 24;
    if (adjustMode == 1) now.min = (now.min + 1) % 60;
    if (adjustMode == 2) { now.sec = 0; adjustMode = -1; }  // 调完退出
}
```

> **引脚宏来源**: `KEY1_GPIO_Port`/`KEY1_Pin`（PC13）、`KEY2_GPIO_Port`/`KEY2_Pin`（PA15）由 CubeMX 按 Label `KEY1`/`KEY2` 自动生成在 `main.h`。若你之前误用 `BTN_MODE`/`BTN_PLUS`，在 CubeMX 里把 Label 改回 `KEY1`/`KEY2` 重新生成即可对齐固件。

> **WHY manual adjust if we have SNTP?** SNTP 是主授时，但断网时本地 tick 会漂移，按键调时是「应急备用」。也是产品标配——任何时钟都要能手动调，不能完全依赖网络。

---

## 四、断网回退 —— 让时钟「断网不死」 | Offline Fallback: Surviving WiFi Loss

### 4.1 为什么要回退

如果 WiFi 断了（路由器重启、信号弱、拔网线），时钟不能死——它至少要继续用本地 tick 走时。这是「鲁棒性」的基本要求：**单点故障不能让整个产品挂掉**。

### 4.2 回退策略

```
正常运行：SNTP 30 分钟对时一次，本地 tick 走秒
         │
         ▼ SNTP 失败 / WiFi 断
降级运行：OLED 显示「WiFi--」，本地 tick 继续走（可能漂移）
         │
         ▼ 每 60 秒尝试重连 WiFi
恢复运行：连上后重新 SNTP 对时，OLED 恢复「WiFi OK」
```

### 4.3 实现

```c
// 封装：尝试 SNTP 对时，失败返回 0
int SNTP_Sync_WithRetry(ClockTime *now) {
    for (int retry = 0; retry < 3; retry++) {
        UART_Put_AT_Cmd("AT+CIPSNTPTIME?\r\n");
        int n = UART_Get_AT_Resp(resp, sizeof(resp)-1, 2000);
        resp[n] = 0;
        if (Clock_ParseFromAT((char*)resp, now)) return 1;
        HAL_Delay(500);
    }
    return 0;
}

// 主循环里：检测 WiFi 状态 + 重连
uint32_t lastReconnect = 0;
int wifiOk = 1;

// 每 60 秒检查一次 WiFi
if (!wifiOk && tick - lastReconnect > 60000) {
    lastReconnect = tick;
    UART_Put_AT_Cmd("AT+CIPSTATUS\r\n");
    int n = UART_Get_AT_Resp(resp, sizeof(resp)-1, 2000);
    resp[n] = 0;
    if (strstr((char*)resp, "STATUS:2") || strstr((char*)resp, "STATUS:3")) {
        // 已连接，重新对时
        if (SNTP_Sync_WithRetry(&now)) wifiOk = 1;
    } else {
        // 断了，重连 WiFi
        if (ESP8266_ConnectWiFi(SSID, PWD)) {
            if (SNTP_Sync_WithRetry(&now)) wifiOk = 1;
        }
    }
}
```

### 4.4 本地 tick 永远在走（讲 WHY）

关键设计：**无论 WiFi 状态如何，`Clock_Tick(&now)` 每秒都在主循环里跑**。WiFi 只负责「定期校正」本地时间，不是时间的唯一来源。

> **WHY this separation?** 如果时间完全依赖 WiFi（每秒查 NTP），断网时钟就停了。本地 tick + 网络校正的分离设计，让时钟「断网照走、联网校正」，这是网络时钟的正确架构。类比手机：飞行模式下时钟照样走，连上网才悄悄校时。

---

## 五、常见错误 | Common Errors

| 现象 | 原因 | 解决 |
|------|------|------|
| 蜂鸣器不响 | 有源/无源搞混 / PWM 没启动 / 引脚错 | 确认是无源；`HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2)` 调了；引脚是 **PA1 / TIM2_CH2**（不是 CH1/PA0） |
| 蜂鸣器声音太小 | 占空比不是 50% / 电压不够 | `SET_COMPARE` 设 period/2；用 3.3V 供电；加三极管驱动 |
| 蜂鸣器频率不对 | Prescaler/Period 算错 | 用示波器或逻辑分析仪量；公式 `freq = 32M/(Prescaler+1)/(Period+1)`；固件基准 Prescaler=32-1, Period=370-1 ≈ 2.7kHz |
| 按键按一下跳很多 | 没消抖 | 加 `HAL_Delay(20)` 消抖 |
| 按键无反应 | 上拉没配 / 引脚错 / Label 不对 | CubeMX 配 Pull-up；确认 KEY1=PC13、KEY2=PA15；Label 必须是 `KEY1`/`KEY2`（固件命名） |
| 整点报时响个不停 | `lastMin` 检测逻辑错 | 加 `&& lastMin != 0` 只在跨整点瞬间触发 |
| 断网后时钟停了 | `Clock_Tick` 被放在 `if (wifiOk)` 里 | `Clock_Tick` 必须无条件每秒跑 |
| 断网恢复后不重连 | 重连逻辑没周期触发 | 每 60 秒主动 `CIPSTATUS` 查 + 重连 |
| 重连时主循环卡死 | `ConnectWiFi` 阻塞太久 | 重连失败要快速超时返回，别死等 |

---

## 六、调试技巧 | Debugging Tips

1. **蜂鸣器单独测**: 先写死 `Buzzer_Beep(2000, 500);` 循环，确认能响再接整点逻辑。
2. **按键用串口看**: `if (Button_Read(...)) printf("BTN pressed\r\n");` 按一下看打印几次，>1 次就是没消抖好。
3. **模拟断网**: 直接拔路由器电源或改错 SSID，观察时钟是否继续走、OLED 是否显示「WiFi--」、恢复后是否自动重连。这是验收鲁棒性的关键测试。
4. **整点报时测试**: 不想等到整点？临时把触发条件改成 `now.min == 30`，半小时点就能测。
5. **长时间运行测试**: 让时钟跑 2 小时，观察是否稳定、内存是否泄漏（`printf` 出 `HAL_GetTick()` 看是否线性增长）。

---

## 七、今日检查点 | Day 8 Checkpoints

- [ ] 蜂鸣器能响，整点（可手动触发）报时
- [ ] 按键能进入调时模式并调整时/分
- [ ] 拔 WiFi 后时钟继续走，OLED 显示「WiFi--」
- [ ] 恢复 WiFi 后自动重连重对时，OLED 恢复「WiFi OK」
- [ ] 能解释「为什么本地 tick 要无条件跑」
- [ ] 截图/录屏：断网→继续走→恢复→自动重连的完整过程

---

## 八、今日作业 | Homework

1. **报时旋律** (⭐⭐): 整点报时改成「东方红」或「威斯敏斯特」旋律（用不同频率的 beep 串起来），比单调滴答好听。
2. **按键减法** (⭐⭐⭐): 加第三个按键 BTN_MINUS 做减法，调时更方便（需另选一个空闲 GPIO，别和 PC13/PA15 冲突）。
3. **闹钟功能** (⭐⭐⭐): 长按 KEY1 进入闹钟设置，到点蜂鸣器响 10 秒，按任意键停。
4. **理解验证问题 | Comprehension Check**: 见下一节。
5. **Git 提交**:
   ```bash
   git add curriculum/day-08.md
   git commit -m "day08: buzzer chime, button adjust, offline fallback"
   ```

---

## 九、理解验证问题 | Comprehension Check

> 答题前回顾本文 §2.1-2.2（无源 vs 有源 + PWM）、§3.3（消抖 WHY）、§4.4（本地 tick 无条件跑 WHY）。

**Q1（设计权衡题）** 这个项目为什么用**无源蜂鸣器 + PWM** 驱动，而不是**有源蜂鸣器给直流电就响**？从音调可编程性、整点报时体验、成本三个角度分析。

> **参考答案**: ①音调可编程——无源蜂鸣器靠 PWM 频率决定音调，能编程出「滴—答—滴」旋律甚至整点报时数（几点响几声）；有源蜂鸣器内置振荡源，给电只能响一个固定频率，没法调音。②整点报时体验——无源可做成不同旋律（东方红/威斯敏斯特），有源只能单调响。③成本——两者价格相近，无源稍便宜且省一个振荡电路。KE1 的 `KE1_PWM` 例程就是教 PWM 驱动无源蜂鸣器，是标准方式。代价是无源需要占用一个定时器通道（TIM2_CH2），有源只需一个 GPIO 拉高——但换来的可编程旋律值得。

**Q2（原理追问题）** 按键为什么要消抖？为什么 `HAL_Delay(20)` 这个值（而不是 2ms 或 200ms）？太短或太长各有什么问题？

> **参考答案**: 按键按下瞬间金属簧片物理抖动，几毫秒内产生多次 0/1 跳变，不消抖按一下 CPU 看到按了 10 次。20ms 的依据：机械抖动通常 5-15ms，20ms 能可靠滤掉。太短（如 2ms）滤不完抖动 → 还是跳多次；太长（如 200ms）手感迟钝，连按响应慢、甚至漏按。`HAL_Delay(20)` 最简单够用；进阶可用「连续 N 次读取都一致」的非阻塞消抖，不阻塞主循环，但代码复杂。对本项目（主循环已有非阻塞结构），阻塞式 20ms 可接受，因为按键不是高频操作。

**Q3（设计权衡题）** 断网时为什么时钟要靠**本地 tick 无条件走 + 网络只做定期校正**，而不是**每秒查 NTP 取时间**（完全依赖网络）？从「断网行为」和「网络开销」两个角度分析。

> **参考答案**: ①断网行为——若每秒查 NTP，WiFi 一断时钟立刻停（没时间源了）；本地 tick + 网络校正的分离设计让时钟「断网照走、联网校正」，断网只损失精度（30 分钟漂移 <2 秒），核心功能不挂。类比手机飞行模式：时钟照样走，连上网才悄悄校时。②网络开销——每秒查 NTP 是网络重操作（AT 命令往返 + NTP 请求），占满 UART 和主循环，CPU 干不了别的；30 分钟校正一次既保证精度（SNTP 毫秒级 + 本地 tick 短期稳定）又把网络开销降到最低。这是网络时钟的正确架构——本地维护为主、网络校正为辅，单点故障（WiFi 断）不让整个产品挂掉，即「鲁棒性」。

### 今日评分标准 | Rubric

| 维度 | 满分 | 评分细则 |
|------|------|---------|
| 完成度 | 4 | 蜂鸣器整点报时 + 按键调时 + 断网回退三项全通得 4；缺一项扣 1-2 |
| 理解深度（CC 回答） | 3 | Q1-Q3 能讲清 A 而不是 B 的权衡得 3；只讲是什么得 1-2 |
| 代码/接线质量 | 2 | 引脚 PA1/PC13/PA15 正确、消抖实现、Clock_Tick 无条件跑得 2；引脚错或 tick 进了 if(wifiOk) 扣 1-2 |
| 创意拓展 | 1 | 旋律/减法键/闹钟任一完成得 1 |

---

## 十、明日预告 | Tomorrow

**Day 9: 组装 —— 焊接 / 外壳 / 桌面摆件化**
- 把面包板原型转成焊接版（万用板或定制 PCB）
- 设计/制作外壳（3D 打印 / 亚克力 / 木盒）
- 组装成桌面摆件形态

**前置准备**: 万用板或 PCB、电烙铁、焊锡、外壳材料。

---

> **今日产出 = 明日输入**: 今天完成的「产品级」固件（蜂鸣器 + 按键 + 断网回退，PA1/PC13/PA15 引脚定稿）是 Day 9 组装的软件基线——Day 9 把面包板原型转焊接版时，引脚分配不再变动，只把杜邦线换成焊点。

---

*最后更新: 2026-06 | Last updated: 2026-06*
