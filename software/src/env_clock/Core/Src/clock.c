/**
  ******************************************************************************
  * @file    clock.c
  * @brief   时钟管理 (Clock management) 实现
  *
  *   设计思路 (循序渐进 — 讲 WHY):
  *   - STM32 内部没有电池供电的实时时钟 (我们没接 LSE 电池), 所以每次上电时间
  *     都是未知的。必须靠 ESP8266 联网向 NTP 服务器“对一次时”, 之后 STM32 用
  *     自己的 SysTick (1ms 中断) 自己往前走, 这个叫“守时 (holdover)”。
  *   - 这样即使 WiFi 断了, 时钟也不会停 —— 只要不重启, 时间就继续走, 只是不
  *     再被 NTP 校准, 会有几秒/几小时的漂移。
  *   - Clock_Tick() 用 HAL_GetTick() 的差值来推进秒数, 而不是 HAL_Delay(), 这
  *     样主循环里可以同时干别的事 (比如刷 OLED、读传感器), 时间精度不受影响。
  ******************************************************************************
  */
#include "clock.h"
#include <stdio.h>
#include <string.h>

/* 全局时钟状态 */
static ClockTime g_clock = {2026, 1, 1, 0, 0, 0, 4}; /* 默认 2026-01-01 周四 */
static uint32_t  g_last_tick_ms = 0;   /* 上次 Clock_Tick 记录的 HAL_GetTick() */
static int       g_synced = 0;         /* 是否已同步过网络时间 */

/* 星期缩写表 (wday: 0=Sun .. 6=Sat) */
static const char *g_wday_str[] = {"Sun","Mon","Tue","Wed","Thu","Fri","Sat"};

/* 月份天数表 (非闰年) */
static const int g_month_days[] = {31,28,31,30,31,30,31,31,30,31,30,31};

/* 判断是否闰年 */
static int is_leap_year(int y)
{
    return ((y % 4 == 0) && (y % 100 != 0)) || (y % 400 == 0);
}

/* 计算某年某月的天数 */
static int days_in_month(int y, int m)
{
    if (m == 2 && is_leap_year(y)) return 29;
    if (m < 1 || m > 12) return 30;
    return g_month_days[m - 1];
}

/* 用 Zeller 公式从年月日算星期 (0=周日 .. 6=周六) */
static int calc_weekday(int y, int m, int d)
{
    int w, c, yy;
    if (m < 3) { m += 12; y -= 1; }
    c = y / 100;
    yy = y % 100;
    w = (d + (13*(m+1))/5 + yy + yy/4 + c/4 + 5*c) % 7;
    /* Zeller 标准公式结果: 0=周六, 调整为 0=周日 */
    return (w + 6) % 7;
}

void Clock_Init(void)
{
    memset(&g_clock, 0, sizeof(g_clock));
    g_clock.year = 2026; g_clock.month = 1; g_clock.day = 1;
    g_clock.hour = 0; g_clock.min = 0; g_clock.sec = 0;
    g_clock.wday = calc_weekday(g_clock.year, g_clock.month, g_clock.day);
    g_last_tick_ms = 0;  /* 首次 Tick 会用当前 HAL_GetTick() 初始化 */
    g_synced = 0;
}

void Clock_SyncFromSNTP(int year, int month, int day, int hour, int min, int sec, int wday)
{
    /* 基本合法性校验, 防止 NTP 返回乱码把时钟改坏 */
    if (year < 2020 || year > 2099) return;
    if (month < 1 || month > 12) return;
    if (day < 1 || day > 31) return;
    if (hour < 0 || hour > 23) return;
    if (min < 0 || min > 59) return;
    if (sec < 0 || sec > 59) return;

    g_clock.year  = year;
    g_clock.month = month;
    g_clock.day   = day;
    g_clock.hour  = hour;
    g_clock.min   = min;
    g_clock.sec   = sec;
    /* 若 SNTP 给了星期就用, 否则自己算 */
    g_clock.wday  = (wday >= 0 && wday <= 6) ? wday
                                            : calc_weekday(year, month, day);
    g_last_tick_ms = 0;   /* 重置 tick 基准, 避免校准瞬间多走秒 */
    g_synced = 1;
}

void Clock_Tick(uint32_t now_ms)
{
    int32_t delta;

    if (g_last_tick_ms == 0) {
        /* 首次或刚同步过 —— 以当前 tick 为基准, 不推进 */
        g_last_tick_ms = now_ms;
        return;
    }

    delta = (int32_t)(now_ms - g_last_tick_ms);
    if (delta < 1000) return;   /* 不足 1 秒, 不动 */

    /* 把 delta 折算成整秒数推进, 余数留给下次 */
    int add_sec = delta / 1000;
    g_last_tick_ms += (uint32_t)add_sec * 1000;

    g_clock.sec += add_sec;
    while (g_clock.sec >= 60) {
        g_clock.sec -= 60;
        g_clock.min++;
        if (g_clock.min >= 60) {
            g_clock.min = 0;
            g_clock.hour++;
            if (g_clock.hour >= 24) {
                g_clock.hour = 0;
                g_clock.day++;
                g_clock.wday = (g_clock.wday + 1) % 7;
                if (g_clock.day > days_in_month(g_clock.year, g_clock.month)) {
                    g_clock.day = 1;
                    g_clock.month++;
                    if (g_clock.month > 12) {
                        g_clock.month = 1;
                        g_clock.year++;
                    }
                }
            }
        }
    }
}

int Clock_IsSynced(void)
{
    return g_synced;
}

void Clock_Get(ClockTime *out)
{
    if (out) *out = g_clock;
}

void Clock_FormatTime(char *buf, int bufsize)
{
    snprintf(buf, bufsize, "%02d:%02d:%02d",
             g_clock.hour, g_clock.min, g_clock.sec);
}

void Clock_FormatDate(char *buf, int bufsize)
{
    snprintf(buf, bufsize, "%04d-%02d-%02d %s",
             g_clock.year, g_clock.month, g_clock.day,
             g_wday_str[g_clock.wday]);
}
