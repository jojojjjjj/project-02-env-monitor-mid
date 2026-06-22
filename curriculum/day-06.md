# Day 6: WiFi 联网 + SNTP 网络授时 —— 获取网络时间 | WiFi + SNTP Time Sync

> **学习目标 | Learning Objectives**
> - 理解 NTP/SNTP 协议：网络对时的原理、时区、UTC
> - 用 ESP8266 AT 命令配 SNTP，向 NTP 服务器获取当前时间
> - 解析 ESP8266 返回的时间字符串（`+CIPSNTPTIME:`），转换成北京时间
> - 把网络时间显示到 OLED，验证它和手机时间一致

> **产出 | Deliverable**: OLED 显示从网络同步的北京时间 `2026-06-22 14:30:05`，和手机时间对得上

---

## 一、前置检查 | Pre-flight Checklist

- [ ] Day 5 的 ESP8266 已连上 WiFi（`WIFI GOT IP`）
- [ ] 你的 WiFi 能访问公网（NTP 服务器在公网上，校园网/公司内网可能封 UDP 123）
- [ ] 固件版本记下来了（Day 5 的 `AT+GMR`）——SNTP 命令语法随版本略有差异

---

## 二、NTP/SNTP 原理 —— 网络怎么对时 | NTP/SNTP: How the Network Syncs Time

### 2.1 为什么需要网络授时

普通 RTC（实时时钟）芯片靠 32.768kHz 晶振计时，一天可能慢/快 1-2 秒，一年累积几分钟误差。**NTP (Network Time Protocol)** 让设备向互联网上的时间服务器「对表」，精度可达几十毫秒。

**SNTP** (Simple NTP) 是 NTP 的简化版，够嵌入式用。ESP8266 AT 固件内置了 SNTP 客户端——你只要告诉它用哪个 NTP 服务器、哪个时区，它自动对时。

> **WHY SNTP over a hardware RTC?** 选项 A：加一颗 DS3231 RTC 芯片（¥8），精度高但要硬件、要 I2C、要电池保持走时。选项 B：用现成的 ESP8266 联网 SNTP 对时，零额外硬件、永远准——只要联网。UP主 选 B，这正是「网络时钟」的精髓。代价：断网就没法对时（Day 8 解决断网回退）。

### 2.2 UTC、时区、北京时间

- **UTC** (Coordinated Universal Time)：世界协调时，全球时间基准（≈格林威治时间）
- **时区**：地球分 24 个时区，每个相差 1 小时。北京在东八区，**北京时间 = UTC + 8**
- NTP 服务器返回的是 **UTC 时间**，ESP8266 根据你设的时区自动加偏移

常用 NTP 服务器：
- `ntp.aliyun.com`（阿里云，国内快）
- `cn.ntp.org.cn`（国家授时中心）
- `pool.ntp.org`（全球池，但国内可能慢）

> **WHY a China NTP server?** `pool.ntp.org` 会 DNS 解析到最近的服务器，但国内解析可能不准、慢。用 `ntp.aliyun.com` 国内延迟 <50ms，稳定。这是真实工程选型——不是技术能跑就行，要在你的部署环境跑得稳。

### 2.3 ESP8266 SNTP 的 AT 命令序列

乐鑫 AT 固件的 SNTP 流程（V2.x 固件）：

```
AT+CIPSNTPCFG=1,8,"ntp.aliyun.com"   // 开 SNTP，时区 8，用阿里 NTP
        → OK
AT+CIPSNTPTIME?                        // 查当前时间
        → +CIPSNTPTIME:Mon Jun 22 14:30:05 2026
          OK
```

- `CIPSNTPCFG=1,8,...`：参数 1=启用 SNTP，8=时区（东八区），后面是 NTP 服务器（可填 3 个）
- `CIPSNTPTIME?`：返回已经换算好时区的本地时间字符串

> ⚠️ **固件版本差异**: 老版 AT 固件 (V1.x) 用 `AT+CIPSNTPCFG` 语法略不同，或没有内置 SNTP。如果这条命令报 `ERROR`，先 `AT+GMR` 查版本，去乐鑫官网查对应版本的 SNTP 命令。本项目假设 V2.x。

---

## 三、配置 SNTP 并获取时间 | Configuring SNTP and Getting Time

### 3.1 连 WiFi 后配 SNTP

在 `main.c` 里，连 WiFi 成功后（Day 5 的 `ConnectWiFi` 返回 1）追加：

```c
/* USER CODE BEGIN 2 */
// ... Day 5 的 ConnectWiFi ...

HAL_Delay(1000);
// 配 SNTP：启用，时区 8（北京时间），NTP 服务器
UART_Put_AT_Cmd("AT+CIPSNTPCFG=1,8,\"ntp.aliyun.com\"\r\n");
UART_Get_AT_Resp(resp, sizeof(resp)-1, 2000);
printf("SNTP cfg: %s\r\n", resp);

HAL_Delay(2000);  // 给 SNTP 几秒去对时
printf("Requesting time...\r\n");
/* USER CODE END 2 */
```

### 3.2 解析时间字符串

ESP8266 返回的时间格式（V2.x）：

```
+CIPSNTPTIME:Mon Jun 22 14:30:05 2026
```

这是英文星期 + 月 + 日 + 时分秒 + 年。我们需要把它解析成结构化的 `年/月/日/时/分/秒`。**复刻模式**：解析函数已提供在 `software/src/clock.c`，你照用：

```c
// clock.c 提供的解析函数
typedef struct {
    int year, month, day, hour, min, sec;
} ClockTime;

int Clock_ParseFromAT(const char *atResp, ClockTime *out);
// 成功返回 1，失败返回 0
```

解析思路（讲 WHY 用 `sscanf`）：

```c
// ESP 返回: "+CIPSNTPTIME:Mon Jun 22 14:30:05 2026"
// 用 sscanf 提取
char mon[4] = {0};
int day, hh, mm, ss, year;
if (sscanf(atResp, "+CIPSNTPTIME:%3s %3s %d %d:%d:%d %d",
           weekday, mon, &day, &hh, &mm, &ss, &year) == 7) {
    // 月份是英文缩写，要转成数字
    out->month = month_str_to_num(mon);  // "Jun"->6
    out->day = day; out->hour = hh; out->min = mm; out->sec = ss; out->year = year;
    return 1;
}
```

> **WHY `sscanf` not strtok?** `sscanf` 一行匹配固定格式，比 `strtok` 切分简单不易错。但 `sscanf` 占代码空间较大（~6KB），L433 的 256KB Flash 够用。如果 Flash 紧张再改手写解析。

### 3.3 主循环定期对时 + 显示

```c
/* USER CODE BEGIN WHILE */
ClockTime now = {0};
uint32_t lastSync = 0;
float t = 0, h = 0;

while (1)
{
    // 每 30 分钟重新对时一次（平时靠本地 tick 累加）
    if (HAL_GetTick() - lastSync > 30*60*1000 || lastSync == 0) {
        UART_Put_AT_Cmd("AT+CIPSNTPTIME?\r\n");
        int n = UART_Get_AT_Resp(resp, sizeof(resp)-1, 2000);
        resp[n] = 0;
        if (Clock_ParseFromAT((char*)resp, &now)) {
            printf("Synced: %04d-%02d-%02d %02d:%02d:%02d\r\n",
                   now.year, now.month, now.day, now.hour, now.min, now.sec);
            lastSync = HAL_GetTick();
        }
    }

    // 本地秒级 tick（用 HAL_Delay 简化）
    Clock_Tick(&now);  // 秒+1，自动进位分时日月

    // 读温湿度 + 显示
    if (KE1_I2C_SHT31(&t, &h) == HAL_OK) {
        OLED_ShowClock(&now);    // 显示时间（第一行）
        OLED_ShowT_H(t, h);      // 显示温湿度（第三行）
    }
    HAL_Delay(1000);
    /* USER CODE END WHILE */
}
```

> **WHY sync every 30 min not every second?** 每次 `CIPSNTPTIME?` 要走一次网络往返，几百毫秒，还占串口。对时一次后，STM32 自己用 `HAL_GetTick()` 维护秒级计数就够准（L433 内部 RTC 短期精度够 30 分钟）。每 30 分钟重新对一次，校正累积漂移。这是真实系统的「同步 + 本地维护」模式。

### 3.4 编译烧录，验证

OLED 应该显示：

```
14:30:05         （第一行，时间）
2026-06-22       （第二行，日期）
温湿度
25.43'C 58.20%   （第三行）
```

**和手机时间对比**——应该一致（误差 <2 秒）。如果不准，检查时区是不是设成了 8。

> ✅ **检查点 6.1**: OLED 时间和手机时间一致，过 1 分钟秒数在涨。

---

## 四、时间本地维护 —— Clock 模块 | Local Time Keeping: The Clock Module

### 4.1 为什么需要本地 tick

SNTP 对时是「瞬间」事件，但时钟要每秒走。两种做法：

| 做法 | 说明 | 缺点 |
|------|------|------|
| **每秒查 NTP** | 简单 | 网络往返几百 ms，OLED 卡顿；频繁请求 NTP 服务器会被 ban |
| **对时一次 + 本地 tick** | 对时后用 `HAL_GetTick()` 本地维护秒计数 | 30 分钟内可能漂移 1-2 秒，定期重对时即可 |

我们用第二种。`clock.c` 的 `Clock_Tick` 函数：

```c
void Clock_Tick(ClockTime *c) {
    if (++c->sec >= 60) { c->sec = 0; if (++c->min >= 60) { c->min = 0;
        if (++c->hour >= 24) { c->hour = 0; /* 日期进位，省略 */ } } }
}
```

> **WHY not use STM32's hardware RTC?** L433 其实有硬件 RTC 外设，配个纽扣电池能断电走时。但本项目复刻视频，视频没用 RTC（用 SNTP+软件 tick），我们照搬。如果你想加 RTC 作为扩展，是很好的 Day 10 优化方向。

### 4.2 闰年和月份天数（讲 WHY）

日期进位要处理闰年和各月天数：

```c
static const uint8_t days_in_month[] = {31,28,31,30,31,30,31,31,30,31,30,31};
int is_leap(int y) { return (y%4==0 && y%100!=0) || (y%400==0); }
// 2 月：闰年 29 天，平年 28 天
```

> **WHY care about leap years?** 2 月 28 日 23:59:59 过 1 秒，如果不是闰年应该到 3 月 1 日 00:00:00，闰年应该到 2 月 29 日 00:00:00。算错会让日期跳一天。`Clock_Tick` 里日期进位必须考虑这个。虽然时钟大多时候在月内走，但跨月跨年那一刻算错就很丑。

---

## 五、常见错误 | Common Errors

| 现象 | 原因 | 解决 |
|------|------|------|
| `CIPSNTPCFG` 报 `ERROR` | 固件版本不支持 / 没连上 WiFi | `AT+GMR` 查版本；确认先 `CWJAP` 连上网再配 SNTP |
| `CIPSNTPTIME` 返回 `1970-01-01` | SNTP 还没对上时 | 配完 SNTP 后 `HAL_Delay(3000)` 再查；检查 NTP 服务器域名 |
| 时间对，但差 8 小时 | 时区没设或设错 | `CIPSNTPCFG=1,8,...` 第 2 参数必须是 `8`（北京） |
| 时间是 UTC（差 8 小时） | 时区设成 0 了 | 改成 8 |
| 月份显示成 `6` 但应是 `Jun` | 解析没转月份缩写 | `Clock_ParseFromAT` 里有 `month_str_to_num`，确认调了 |
| 秒数不动 | `Clock_Tick` 没被调用 / `HAL_Delay` 卡死 | 确认主循环里 `Clock_Tick(&now)` 在 `HAL_Delay(1000)` 前 |
| 跨 0 点日期不进位 | 日期进位逻辑漏了 | 检查 `Clock_Tick` 的 hour>=24 分支里有没有处理 day++ |
| 频繁对时被 NTP 服务器拒 | 1 秒查一次太频繁 | 改成 30 分钟一次 |

---

## 六、调试技巧 | Debugging Tips

1. **先串口看原始响应**: `printf("RAW: %s\r\n", resp)` 把 ESP8266 原始返回打出来，确认格式，再写解析。
2. **手动验证解析**: 把一条真实响应字符串硬编码进测试代码，单独调 `Clock_ParseFromAT`，解析对了再接真实数据。
3. **时区一次性验证**: 故意把时区设 0（UTC），看时间是不是比北京少 8 小时——验证时区参数真生效。
4. **NTP 服务器备用**: `ntp.aliyun.com` 不通？换 `cn.ntp.org.cn` 或 `time.windows.com`。`CIPSNTPCFG` 支持填 3 个服务器：`=1,8,"s1","s2","s3"`。
5. **SNTP 对时失败排查链**: ① WiFi 连上了吗 (`CIFSR` 有 IP) → ② 能 ping 通 NTP 服务器吗 (`AT+PING="ntp.aliyun.com"`) → ③ SNTP 配了吗 (`CIPSNTPCFG?` 查) → ④ 等够时间了吗 (至少 2 秒)。

---

## 七、今日检查点 | Day 6 Checkpoints

- [ ] `AT+CIPSNTPCFG=1,8,"ntp.aliyun.com"` 返回 `OK`
- [ ] `AT+CIPSNTPTIME?` 返回合理的北京时间
- [ ] OLED 显示网络时间，和手机一致（误差 <2 秒）
- [ ] 秒数每秒在涨，跨分钟正确进位
- [ ] 能解释「为什么 30 分钟对时一次而不是每秒」
- [ ] 截图：OLED 时间 + 手机时间同框对比

---

## 八、今日作业 | Homework

1. **日期显示**: 在时间下方一行显示 `2026-06-22` 日期。
2. **星期显示**: 解析 ESP 返回的星期 (Mon/Tue/...)，在 OLED 角落显示中文或英文星期。
3. **对时失败处理**: 如果连续 3 次 `CIPSNTPTIME` 返回 `1970` 年，OLED 显示「NTP FAIL」并每 10 秒重试。
4. **回答**:
   - NTP 服务器返回的是 UTC 还是本地时间？北京时间怎么换算？
   - 为什么不每秒都查 NTP？
   - 闰年的判断规则是什么？2100 年是闰年吗？
5. **Git 提交**:
   ```bash
   git add curriculum/day-06.md
   git commit -m "day06: SNTP time sync, network clock on OLED"
   ```

---

## 九、明日预告 | Tomorrow

**Day 7: 时钟整合 —— 时间 + 温湿度 + 定时刷新**
- 把时间、温湿度、日期整合成一个完整的桌面时钟界面
- 设计 OLED 显示布局（时间大字号 + 温湿度小字号）
- 实现定时刷新策略，避免闪屏

**前置准备**: Day 6 的时间显示跑通；想好你想要的时钟界面布局。

---

*最后更新: 2026-06 | Last updated: 2026-06*
