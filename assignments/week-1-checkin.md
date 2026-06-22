# 周报 1 · 第一周进度检查报告 | Week 1 Check-in Report

> 项目 02 · 温湿度网络时钟 (WiFi Temp/Humidity Network Clock) · STM32L433 + ESP8266 + SHT31 + OLED
> 复刻模型 (Replication Model) · 难度 2/5 · 覆盖 Day 1–5

---

## 📌 报告头信息 | Report Header

| 字段 | 填写 |
|------|------|
| **学生姓名 / Student Name** | _______________ |
| **学号 / Student ID** | _______________ |
| **日期 / Date** | _______________ |
| **项目 / Project** | 温湿度网络时钟 (WiFi Temp/Humidity Network Clock) |
| **本周覆盖 / Coverage** | Day 1–5 (嵌入式基础 + 工具链 + SHT31 + OLED) |
| **导师 / Instructor** | _______________ |

> **循序渐进提示 (Scaffolding Note):** 这份周报不是打分工具，而是帮你**诚实地看清自己卡在哪**。每一项打勾前，请先确认你能在 30 秒内向同学讲清楚”这是什么、为什么需要它”。讲不清楚就别打勾——那是本周剩下的发力点。

---

## 🎯 学习成果 | Learning Outcomes

完成本周（Day 1-5）后，你应该能够：

- **识别 (Identify)** STM32L433CCT6 主控、ESP8266/ESP-01S 协处理器、SHT31、SSD1306 OLED 四个核心器件的职责与电气接口
- **解释 (Explain)** GPIO/UART/I2C/AT 命令在本项目中各自的角色，以及为什么 OLED 用软件 I2C、SHT31 用硬件 I2C
- **实现 (Implement)** 串口 `printf` 重定向、SHT31 读温湿度、OLED 显示温湿度、ESP8266 `AT` 应答这四个最小可运行链路
- **分析 (Analyze)** 自己接线/烧录/通信失败的根因（接反、电压、波特率、地址），并给出验证方法

## 💡 为什么写周报 | Why This Matters

> 类比：周报像「每周体检报告」——不是给老师交差，是给自己一张**能力 X 光片**。Week 1 你搭好了四块「零件」（点灯、温湿度、显示、WiFi AT），但零件能不能转、转得稳不稳，只有当你被迫一项项现场演示时才暴露得出来。没写周报的人下周组装时会反复踩同一个坑；写了周报的人把坑记下来，下周直接绕过。**诚实自评比满分更重要**——讲不清的别打勾。

## ⏱ 预计耗时 | Estimated Time

本周总投入约 **28-30 小时**（5 天 × ~5-6h）：课程学习/读文档 8h、接线烧录实验 12h、调试 6h、写周报+Git 提交 2-4h。填表时按实际填，偏差大说明计划需要调整。

## 🔁 阶段能力签收 | Phase Ability Sign-off

> 本周（Week 1 = Day 1-5）的验收里程碑是：**能读温湿度 + OLED 显示 + ESP8266 连上 WiFi**（**不含 SNTP**，SNTP 是 Week 2 Day 6 的内容）。导师签收前请确认下表三项全绿——这是进入 Week 2 整合阶段的前提。

| 阶段能力 | 验收证据 | 自评 | 导师 |
|---------|---------|:---:|:---:|
| 能读温湿度（SHT31，硬件 I2C） | 串口每秒打印 `T:xx.xx H:xx.xx`，手捂会变 | ○ | ○ |
| OLED 显示温湿度（软件 I2C，PB8/PB9） | OLED 屏幕显示温湿度数值 | ○ | ○ |
| ESP8266 连上 WiFi（UART3，AT 应答） | 串口发 `AT` 收 `OK`，`AT+CWJAP` 后 `WIFI GOT IP` | ○ | ○ |

---

## ✅ 一、本周进度检查清单 | Progress Checklist

> 对照 `curriculum/day-01.md` ~ `day-05.md` 的检查点逐项确认。每项要能**演示**，不只是“做过了”。

### Day 1 · 项目导览 + 工具链安装 (Project Overview + Toolchain)

- [ ] 看完 Bilibili 视频BV1tb4y1U7Du，能用一句话说清“这个时钟在做什么”
- [ ] 认识 KE1 板的主控芯片 **STM32L433CCT6**（LQFP48, 256KB Flash，ARM Cortex-M4，无 WiFi）—— 与固件 `.ioc` (`Mcu.UserName=STM32L433CCTx`) 一致；CBT6 (128KB) 是引脚兼容的替代型号
- [ ] 已安装 **STM32CubeIDE**（1.6.1+），能正常打开
- [ ] 已安装 **STM32CubeProgrammer**（或确认能用 CubeIDE 自带烧录器）
- [ ] 已安装 USB 串口驱动（CH340 / CP210x，取决于你的板子）
- [ ] 用 USB 线连接板子，电脑能识别出串口（设备管理器里能看到 COMx）
- [ ] 已建好 Git 仓库（本地 + GitHub），并完成首次提交

### Day 2 · 第一个程序 — 点灯 + 串口 printf (GPIO + UART)

- [ ] 能在 CubeIDE 里新建 / 导入工程，编译通过（0 error）
- [ ] 烧录固件到 STM32L433 成功（看到下载完成提示）
- [ ] LED 点灯实验成功（能控制一个 GPIO 翻转，看到灯闪）
- [ ] 串口 printf 实验成功：在 **USART1 (PA9/PA10, 115200)** 上用串口助手看到 `printf` 输出
- [ ] 理解“为什么用 printf 要重定向 `__io_putchar`”（讲得出 HAL_UART_Transmit 的作用）

### Day 3 · SHT31 温湿度传感器 (I2C + Sensor)

- [ ] 理解 I2C 通信的基本概念（两根线 SDA/SCL、主从、地址 0x44）
- [ ] SHT31 已按接线表接好：**VCC=3.3V, GND, SDA, SCL**（确认没接 5V）
- [ ] 调用 `KE1_I2C_SHT31_Init()` 初始化成功
- [ ] 调用 `KE1_I2C_SHT31(&fTemp, &fHumi)` 能读到温湿度
- [ ] 在串口看到合理的数值（温度 ~20–30°C，湿度 ~40–70%，不是 -40 或 0）
- [ ] 用手捂住传感器，数值会变化（证明读的是真数据）

### Day 4 · OLED 显示 (SSD1306)

- [ ] SSD1306 OLED 接好：软件 I2C 在 **PB8=SCL / PB9=SDA**
- [ ] 调用 `OLED_Init()` 后屏幕有点亮（不是全黑 / 不是全亮雪花）
- [ ] `OLED_ShowString()` 能在屏幕上显示英文字符
- [ ] `OLED_ShowT_H(fTemp, fHumi)` 能在 OLED 上显示温湿度
- [ ] OLED 与 SHT31 能同时工作（不会互相冲突——因为用了不同的 I2C 总线/软件 I2C）

### Day 5 · ESP8266 WiFi 模块接线 + AT 试通 (ESP-01S)

- [ ] 理解 ESP8266 在本项目中是 **WiFi 协处理器**，STM32L433 本身无 WiFi
- [ ] ESP-01S 已接好：**VCC=3.3V, GND, TX→PB11(USART3_RX), RX→PB10(USART3_TX)**
- [ ] ESP-01S 烧录了 **AT 固件**（确认是乐鑫官方 AT 固件，不是 Lua/NodeMCU）
- [ ] 在 **USART3 (9600 或 115200，取决于 AT 固件版本)** 上发送 `AT\r\n`，收到 `OK`
- [ ] 调用 `UART_Put_AT_Cmd("AT\r\n")` + `UART_Get_AT_Resp(...)` 框架跑通
- [ ] 理解 AT 命令的“一问一答”模型（发送 → 等响应 → 解析）

---

## 🎯 二、本周功能演示清单 | Functionality Demo

> 导师检查时，**现场演示**以下功能（不是看截图）：

| # | 演示项 | 验收标准 | 自评 (✓/✗) | 导师 |
|---|--------|---------|:---:|:---:|
| 1 | 串口 printf | 打开串口助手，看到板子开机打印的欢迎信息 | | |
| 2 | SHT31 读数 | 串口每秒打印 `T:25.30,H:60.50` 这样的行 | | |
| 3 | OLED 显示温湿度 | OLED 屏幕上看到温度和湿度数值，手捂会变 | | |
| 4 | ESP8266 AT 应答 | 串口发送 `AT`，ESP8266 回 `OK` | | |
| 5 | 串口 + OLED + SHT31 同时工作 | 三者互不干扰，稳定运行 ≥1 分钟 | | |

**总体自评 (Self Rating):**

| 维度 | 1星 | 2星 | 3星 | 4星 | 5星 |
|------|:---:|:---:|:---:|:---:|:---:|
| 功能完整度 (Completeness) | ○ | ○ | ○ | ○ | ○ |
| 接线质量 (Wiring Quality) | ○ | ○ | ○ | ○ | ○ |
| 理解程度 (Understanding) | ○ | ○ | ○ | ○ | ○ |
| 系统稳定性 (Stability) | ○ | ○ | ○ | ○ | ○ |

---

## 💻 三、Git 提交记录 | Git Commit History

> **大学级规范 (College-level Rigor):** 提交信息必须用 **Conventional Commits** 格式。这不是装腔作势——它让任何人在不读代码的情况下，扫一眼 `git log` 就知道每个提交“是什么类型、改了什么”。复刻项目里你不是在写新功能，而是在**逐步搭建与验证硬件链路**，所以 `feat:` 较少，更多是 `chore:`/`build:`/`docs:`/`fix:`。

### 提交规范 (Commit Message Convention)

```
<type>(<scope>): <subject>

type 取值 (我们用到的):
  feat     新功能 (例如: 串口重定向成功、SHT31 驱动跑通)
  fix      修 bug (例如: OLED 引脚接反导致花屏)
  build    构建/工具链 (例如: CubeIDE 工程导入、ioc 配置)
  chore    杂项 (例如: 填 WiFi 配置模板)
  docs     文档 (例如: 更新周报、补接线笔记)
  refactor 重构 (例如: 整理 main.c 的 case 结构)

scope 取值 (建议): toolchain | gpio | uart | sht31 | oled | esp8266 | wiring | docs

示例:
  feat(uart): 串口 printf 重定向到 USART1
  feat(sht31): SHT31 驱动初始化 + 读温湿度成功
  fix(oled): 修正 OLED SCL/SDA 接反导致的屏幕花屏
  build(toolchain): 导入 KE1 参考工程，编译通过
  chore(esp8266): AT 固件烧录完成，AT 命令试通
  docs: 填写 week-1-checkin.md
```

### 本周提交记录 (Paste Your `git log`)

```bash
# 在你的仓库根目录运行，把输出贴在下面：
git log --oneline --since="1 week ago"
```

```
<!-- 把 git log 输出贴在这里 -->
```

**Git 自检:**

- [ ] 提交信息都用了 Conventional Commits 格式
- [ ] 每个提交聚焦一件事（没有把“装驱动 + 改接线 + 写文档”塞进一个 commit）
- [ ] 提交频率合理（不是一天一次大提交，也不是改一行就 commit）
- [ ] 已推送到 GitHub 远程仓库（`git push` 成功）
- [ ] `.gitignore` 排除了 CubeIDE 的 `Debug/`、`Release/` 编译产物

---

## 🐛 四、本周遇到的问题 | Issues Encountered

> **循序渐进原则:** 把卡住你的问题写下来，比“假装做完了”更有价值。下周你 (或同学) 会再次遇到它。

### 问题记录表 (Issue Log)

| # | 问题描述 (What happened) | 根本原因 (Root cause) | 解决方案 (How you fixed it) | 经验总结 (Lesson) |
|---|-------------------------|----------------------|---------------------------|------------------|
| 示例 | OLED 全屏雪花点 | SCL/SDA 接反了 | 对调 PB8/PB9 两根线 | 接线前先对照接线表逐根核对，不要凭记忆 |
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |

### 本周最多遇到的问题类型 (Most Common Issue Type)

- [ ] 硬件接线 (Wiring) — 接反 / 松动 / 接错引脚
- [ ] 工具链 (Toolchain) — 驱动没装 / 编译报错 / 烧录失败
- [ ] 电源问题 (Power) — 电压不对 / 供电不足
- [ ] I2C 设备地址 / 时序 (I2C addressing/timing)
- [ ] AT 命令不响应 (AT no response)
- [ ] 其他 (Other): _______________

---

## ❓ 理解验证问题 | Comprehension Check

> 本周最核心的「为什么」题。写周报前先自答——讲不清的项，对应的就是没真懂的地方。参考答案见每题下方引用块。

**Q1（设计权衡题）**：为什么 OLED 用软件 I2C（PB8/PB9）、SHT31 用硬件 I2C2，而不是统一用一条硬件 I2C 总线？从移植成本、总线干扰、地址冲突三角度分析。

> **参考答案**：(1) 移植成本——UP主参考工程 OLED 驱动是老的软件 I2C 实现（`OLED_Init`/`OLED_ShowString` 按位翻转 GPIO），改成硬件 I2C 要重写底层，复刻项目「忠实原设计」原则下不动；(2) 总线干扰——SHT31 每秒读一次、OLED 每秒刷新，分两条物理总线互不阻塞，且 OLED 软件 I2C 时序抖动不会拖累 SHT31 硬件 I2C 的精确时序；(3) 地址冲突——即使地址不同（SHT31=0x44, OLED=0x3C），同总线也能共存，但分总线从物理上杜绝了任何地址/时序冲突风险。结论：复刻+稳优先，分总线是更省心的选择。

**Q2（原理追问题）**：`printf` 为什么能从串口输出？跟踪 `printf("hello")` 到 HAL_UART_Transmit 的完整路径，并解释 `__io_putchar` 的作用。

> **参考答案**：`printf` 是 C 标准库函数，内部最终调用 `_write`（newlib）→ `__io_putchar`（CubeMX 生成的弱定义）。工程里把 `__io_putchar` 重定向成 `HAL_UART_Transmit(&huart1, (uint8_t*)ch, 1, timeout)`，于是每个要打印的字符就被推到 USART1 (PA9/PA10, 115200)。所以「printf 走串口」= 用重定向钩子把标准输出接到 UART 外设。波特率必须和串口助手一致，否则收到的就是乱码。

**Q3（故障分析题）**：SHT31 读出来全是 0 或全是 -40，按可能性从高到低列出 3 个原因及验证方法。

> **参考答案**：(1) **I2C 接线错（最常见）**——SDA/SCL 接反或接到 5V，验证：万用表测 SHT31 VCC 是 3.3V、用 I2C 扫描器扫不到 0x44；(2) **地址/命令错**——SHT31 默认 ADDR 引脚拉低时地址 0x44，拉高 0x45；测量命令应是 0x2C06（单次高重复性），验证：对照驱动 `KE1_I2C_SHT31()` 里发的命令字节；(3) **上拉电阻缺失**——SHT31 模块通常自带 4.7k 上拉，但裸芯片没上拉时 SDA/SCL 悬空读全 0，验证：示波器看 SCL 有没有方波、SDA 有没有应答位。

**Q4（类比迁移题）**：把 ESP8266 的 AT 命令「一问一答」模型类比成去银行柜台办业务，AT 命令、`OK`/`ERROR` 响应、超时分别对应什么？

> **参考答案**：AT 命令 = 你递给柜台的申请单（`AT+CWJAP="ssid","pwd"`）；`OK`/`ERROR` 响应 = 柜台回的「受理成功/资料有误」回执；超时 = 柜台迟迟不回话你等多久放弃。STM32 用 `UART_Put_AT_Cmd()` 发单 + `UART_Get_AT_Resp()` 等回执，必须设超时——否则柜台卡住（ESP8266 死机）主控会跟着死等，整个系统挂起。

---

## 📊 五、本周学习数据 | Week 1 Data

### 学习时间统计 (Study Time)

| 活动 (Activity) | 预计 (Planned) | 实际 (Actual) |
|----------------|:--------------:|:-------------:|
| 课程学习 / 读文档 | 8 小时 | _____ 小时 |
| 动手实验 / 接线烧录 | 12 小时 | _____ 小时 |
| 调试问题 (Debugging) | 6 小时 | _____ 小时 |
| 写周报 + Git 提交 | 2 小时 | _____ 小时 |
| **总计 (Total)** | **28 小时** | **_____ 小时** |

### 传感器数据样本 (Sample Sensor Data)

> 贴一段你串口实际输出的温湿度数据（至少 5 行）：

```
<!-- 例:
T:24.80,H:58.20
T:24.90,H:58.40
T:25.10,H:58.70
T:25.30,H:59.10
T:25.50,H:59.50
-->
```

**数据合理性自检:**

- [ ] 温度在 15–35°C 范围内（室温合理区间）
- [ ] 湿度在 30–80% 范围内
- [ ] 连续两次读数差值不大（不是跳变）
- [ ] 手捂传感器后温湿度上升

---

## 🎯 六、下周目标 | Week 2 Goals

### 预期完成 (Expected for Week 2, Day 6–10)

- [ ] Day 6: ESP8266 WiFi 联网（Week 1 已通）+ SNTP 网络授时拿到时间
- [ ] Day 7: 时钟整合 — `OLED_ShowClock(...)` 同时显示时间 + 温湿度
- [ ] Day 8: 蜂鸣器整点报时 (PA1/TIM2_CH2) / 按键调时 (PC13/PA15) / 断网回退（无 WiFi 时用本地计时）
- [ ] Day 9: 组装 — 焊接 / 外壳 / 桌面摆件化
- [ ] Day 10: 调试 + 最终展示 + 复盘 (`retrospective.md`)

### 担心的问题 (Concerns for Week 2)

1. __________________________________________________
2. __________________________________________________
3. __________________________________________________

> **今日产出 = 明日输入（周维度）**: Week 1 的产出 = Day1-5 四块零件（点灯+串口 / SHT31 温湿度 / OLED 显示 / ESP8266 WiFi AT）= Week 2 的输入。Week 2 Day 6 在此基础上加 SNTP 对时，Day 7 用 `OLED_ShowClock(...)` 把时间和温湿度整合到一块屏幕上。**如果本周 ESP8266 AT 没通，下周 SNTP 一定做不出来**——这是硬依赖。所以本周签收三件套（温湿度 + OLED + WiFi AT）是进入 Week 2 的门槛。

---

## 💬 七、反思与反馈 | Reflection & Feedback

### 进度反思 (Progress Reflection)

> 本周你的计划完成度如何？卡在哪里？下周怎么补？

__________________________________________________
__________________________________________________
__________________________________________________

### 对课程的反馈 (Course Feedback)

**最有收获的内容 (Most valuable):** __________________________________

**最困惑的内容 (Most confusing):** __________________________________

**建议改进 (Suggested improvements):** __________________________________

### 自我评估 (Self Assessment)

- [ ] 超出预期 (Exceeded expectations)
- [ ] 达到预期 (Met expectations)
- [ ] 基本达到 (Mostly met)
- [ ] 未达到预期 (Below expectations)

**信心指数 (Confidence):** ⭐⭐⭐⭐⭐ (1–5 星，圈一个)

**需要帮助的领域 (Areas needing help):**

- [ ] 工具链安装 / 烧录
- [ ] 接线焊接
- [ ] I2C / UART 通信原理
- [ ] AT 命令调试
- [ ] Git 使用

---

## ✍️ 八、导师评语 | Instructor Comments

| 评分项 | 得分 | 满分 |
|--------|:----:|:----:|
| 进度完成度 (Progress completion) | _____ | 40 |
| 功能演示 (Functionality demo) | _____ | 30 |
| 问题分析深度 (Issue analysis) | _____ | 20 |
| Git 规范 (Git discipline) | _____ | 10 |
| **本周合计 (Week 1 Total)** | _____ | **100** |

**总体评价 (Overall comments):**

__________________________________________________
__________________________________________________
__________________________________________________

**下周建议 (Suggestions for next week):**

__________________________________________________
__________________________________________________

**导师签名 (Instructor):** _______________  **日期 (Date):** _______________

---

*提交日期 (Submitted): __________ | 审阅日期 (Reviewed): __________*
