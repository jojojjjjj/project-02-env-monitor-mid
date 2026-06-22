# 作业说明 | Assignments Overview

> Project 02 — 温湿度网络时钟 (WiFi Temp/Humidity Network Clock) · 复刻 (replication) model · 10 days · 难度 2/5

本项目采用「复刻」学习模式：UP主「乐在程上」的固件代码已提供（`software/src/`），学员负责接线 + 烧录 + 配置 + 调试 + 组装。作业围绕**工程流程**而非从零写代码。所有作业中英双语，遵循「笨鸟先飞」原则——解释 WHY，不只 HOW。

---

## 一、作业总览 | Assignment Overview

| 作业 | 类型 | 占分 | 关联天数 | 提交位置 |
|------|------|------|---------|---------|
| Week-1 Check-in 周报 | 进度报告 | 10 分 | Day 1-5 | `assignments/week-1-checkin.md` |
| Week-2 Check-in 周报 | 进度报告 | 10 分 | Day 6-10 | `assignments/week-2-checkin.md` |
| Final Presentation 最终演示 | 演示 + 答疑 | 20 分 | Day 10 | `assignments/final-presentation.md` |
| Retrospective 复盘报告 | 总结反思 | 10 分 | Day 10 | `assignments/retrospective.md` |
| 复刻完成度 + 工程交付 | 实物 + 代码 | 50 分 | 全程 | 成品 + `software/src/` + Git |
| **合计** | | **100 分** | | |

> 加分项（最多 +10）：PCB 打样、加 RTC/MQTT 扩展、演示视频、开源贡献。

详细评分细则见 [`grading-rubric.md`](./grading-rubric.md)。

---

## 二、Week-1 Check-in 周报（Day 5 末提交）| Week-1 Check-in Report

**模板文件**: `assignments/week-1-checkin.md`

**覆盖 Day 1-5 进展**，需包含：

### Day 1 — 工具链就绪
- [ ] COM 口号: ________
- [ ] CubeIDE 版本: ________
- [ ] `day01_blink` 工程编译 0 error（截图）
- [ ] 遇到的 1 个坑及解决方法: ________

### Day 2 — 点灯 + 串口 printf + 烧录
- [ ] LED 闪烁（照片）
- [ ] 串口收到 `tick`（截图）
- [ ] 能解释波特率必须一致 / printf 重定向原理（是/否）
- [ ] 调试断点会用了（是/否）

### Day 3 — SHT31 温湿度
- [ ] `KE1_I2C_SHT31_Init()` 返回 OK
- [ ] 串口每秒打印 `T=xx.xx H=xx.xx`（截图）
- [ ] 手捂温度上升（是/否）
- [ ] 10 分钟温湿度记录表（每分钟 1 条）

### Day 4 — OLED 显示
- [ ] OLED 显示温湿度（照片）
- [ ] 大字号/布局是否自定义了？描述: ________
- [ ] 软件I2C vs 硬件I2C 区别能讲清（是/否）

### Day 5 — ESP8266 WiFi
- [ ] 发 `AT` 收到 `OK`（截图）
- [ ] 固件版本 (`AT+GMR`): ________
- [ ] `WIFI GOT IP`（截图）
- [ ] ESP-01S 供电方案（板载/独立AMS1117）: ________

### Week 1 自评
- 本周最大收获: ________
- 本周最大困难: ________
- Git 提交记录（`git log --oneline` 截图）: ________

---

## 三、Week-2 Check-in 周报（Day 9 末提交）| Week-2 Check-in Report

**模板文件**: `assignments/week-2-checkin.md`

**覆盖 Day 6-10 进展**，需包含：

### Day 6 — SNTP 网络授时
- [ ] `CIPSNTPCFG=1,8,"ntp.aliyun.com"` 成功
- [ ] OLED 显示网络时间，和手机一致（对比照）
- [ ] NTP 服务器: ________，时区: 8

### Day 7 — 时钟整合
- [ ] 完整界面（时间+日期+温湿度+状态）照片: ________
- [ ] 刷新策略（时间X秒/温湿度X秒/SNTP X分钟）: ________
- [ ] 防闪屏方案: ________

### Day 8 — 蜂鸣器 + 按键 + 断网回退
- [ ] 蜂鸣器整点报时响（是/否，音调方案: ________）
- [ ] 按键调时成功（是/否）
- [ ] 断网回退测试：断网__秒后显示「WiFi--」，恢复__秒后重连

### Day 9 — 组装
- [ ] 焊接完成（焊点特写照片）
- [ ] 通电前 VCC-GND 电阻: ________Ω（非 0）
- [ ] 外壳方案（3D打印/亚克力/盒子）: ________
- [ ] 成品正面/侧面照片
- [ ] 连续运行 30 分钟稳定（是/否），ESP-01S 温度手感: ________

### Week 2 自评
- 本周最大收获: ________
- 本周最大困难: ________
- 和 Week 1 相比，哪些能力提升了: ________

---

## 四、Final Presentation 最终演示（Day 10）| Final Presentation

**规格文件**: `assignments/final-presentation.md`

**10 分钟演示**，结构：

| 时间 | 内容 |
|------|------|
| 0:00-0:30 | 开场：项目一句话介绍 |
| 0:30-3:00 | 实物演示：时间/温湿度/整点报时/断网回退 |
| 3:00-5:30 | 架构讲解：STM32L433+ESP8266 分工、系统架构图 |
| 5:30-7:30 | 复刻历程：面包板→成品、踩坑、关键决策 |
| 7:30-9:00 | 技术细节：I2C/UART/AT/SNTP 选一个深入讲 |
| 9:00-10:00 | 答疑 + 下一步优化方向 |

**演示必须现场实物运行**，不接受纯 PPT。需准备备用手机热点（2.4G）应对现场 WiFi 不确定性。

**评分要点**: 实物功能完整、架构讲解清晰、能回答评委技术问题、时间控制。详见 `final-presentation.md`。

---

## 五、Retrospective 复盘报告（Day 10）| Retrospective Report

**模板文件**: `assignments/retrospective.md`

按 KISS 框架写（不少于 800 字）：

1. **Keep（做成了什么）**: 完成的功能、掌握的技能、满意的设计
2. **Improve（没做好/遗憾）**: 要改进的地方
3. **Struggles（踩了什么坑）**: 3-5 个最大的坑及解决过程
4. **Start（下一步）**: 如果再做一周会怎么优化

附**技能矩阵自评**（前/后 1-5 分 + 证据），见 Day 10 §5.2。

末尾写一句「给 3 个月后的自己」的话。

---

## 六、复刻完成度 + 工程交付（全程，50 分）| Replication Completion & Engineering Deliverables

这是占比最大的部分，考察**真实工程能力**而非代码原创性：

### 6.1 实物成品（25 分）
- 焊接质量（虚焊/连锡/整洁度）
- 外壳完成度（OLED 可见、按键可按、通风）
- 全功能运行（时间/温湿度/蜂鸣器/按键/断网回退全部正常）
- 稳定性（连续 30 分钟无崩溃）

### 6.2 代码与配置（15 分）
- `software/src/` 固件能编译能烧录
- `config.h` WiFi/NTP 配置正确（真实密码不提交，用占位）
- 对 UP主 固件做的适配/整合/优化有迹可循（注释、commit message）

### 6.3 Git 工程素养（10 分）
- 每天 1+ commit，`git log` 能看出 10 天的推进
- commit message 规范（`day0X: xxx`）
- `.gitignore` 没漏大文件
- README 更新到最终状态

---

## 七、提交规则 | Submission Rules

1. **每日作业当天提交**：Day N 的作业在 Day N 结束前 push 到 Git。
2. **周报按时交**：Week-1 周报 Day 5 末交，Week-2 周报 Day 9 末交。迟交扣 2 分/天。
3. **演示必须现场**：Day 10 现场演示，缺席按 0 分。
4. **真实密码别提交**：`config.h` 里 WiFi 密码用 `#define WIFI_PWD "YOUR_PASSWORD_HERE"` 占位，真实密码只在本地改不 push。
5. **复刻诚实**：固件基础是 UP主 代码，自己做的整合/调试/优化要如实说明，不冒充从零原创。
6. **Git 是命根子**：代码丢失、成品损坏不交 = 不及格。每天 push 到远程备份。

---

## 八、评分标准 | Grading Criteria

详见 [`grading-rubric.md`](./grading-rubric.md)。六大维度：

1. 复刻完成度 (20 分)
2. 架构理解 (15 分)
3. 接线焊接质量 (20 分)
4. 调试能力 (15 分)
5. 演示展示 (20 分)
6. 文档与工程素养 (10 分)

**基础总分 100，加分项最多 +10，最高 110 分。**

---

## 九、时间线一览 | Timeline

```
Week 1 (Day 1-5): 工具链 + GPIO/UART + SHT31 + OLED + ESP8266 WiFi
  └─ Day 5 末: Week-1 Check-in 提交，硬件原型能读温湿度+联网

Week 2 (Day 6-10): SNTP 对时 + 时钟整合 + 完善 + 组装 + 演示
  └─ Day 9 末: Week-2 Check-in 提交，成品完成
  └─ Day 10: Final Presentation + Retrospective，全部交付
```

---

## 十、求助与诚信 | Help & Integrity

- **卡住了先查文档再问人**：报错信息 Google/Bing 先搜，培养独立解决能力
- **可以讨论，不能抄袭**：和同学讨论思路 OK，但代码/报告要自己写
- **复刻要诚实标注**：哪些是 UP主 原码、哪些是你改的、哪些是你原创，在代码注释和报告里说清
- **老师/助教答疑**：优先在答疑群提问，带上报错截图和你试过的方法

---

*笨鸟先飞 · Explain WHY, not just HOW · 复刻是为了学会真实工程流程*

*最后更新: 2026-06 | Last updated: 2026-06*
