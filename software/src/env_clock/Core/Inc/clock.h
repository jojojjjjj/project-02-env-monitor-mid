/**
  ******************************************************************************
  * @file    clock.h
  * @brief   时钟管理 (Clock management) 头文件
  *
  *   时间来源: SNTP 网络授时 (主) + SysTick 本地走时 (回退/守时)。
  *   - Clock_SyncFromSNTP(): 从 ESP8266 拿到网络时间后调用, 校准本地时钟。
  *   - Clock_Tick():          主循环里周期调用, 用 HAL_GetTick() 推进本地时间。
  *   - Clock_Format():        格式化成 OLED 显示字符串。
  ******************************************************************************
  */
#ifndef __CLOCK_H__
#define __CLOCK_H__

#ifdef __cplusplus
extern "C" {
#endif

#include "main.h"

/* 时钟时间结构体 — 年月日时分秒 */
typedef struct {
    int year;     /* 公历年 (如 2026) */
    int month;    /* 月 1-12 */
    int day;      /* 日 1-31 */
    int hour;     /* 时 0-23 */
    int min;      /* 分 0-59 */
    int sec;      /* 秒 0-59 */
    int wday;     /* 星期 0=周日, 1=周一 ... 6=周六 */
} ClockTime;

/* 初始化时钟 (上电默认 2026-01-01 00:00:00, 未同步状态) */
void Clock_Init(void);

/* 用 SNTP 拿到的时间校准本地时钟 (year..sec 全量更新, 并记录同步时刻) */
void Clock_SyncFromSNTP(int year, int month, int day, int hour, int min, int sec, int wday);

/* 主循环里调用: 用 HAL_GetTick() 推进本地时间, 处理进位 (秒→分→时→日→月→年)。
   参数 now_ms: 当前 HAL_GetTick() 的值 (避免重复调用)。 */
void Clock_Tick(uint32_t now_ms);

/* 是否已经成功同步过网络时间 (0=未同步, 1=已同步) */
int  Clock_IsSynced(void);

/* 取当前时间拷贝 */
void Clock_Get(ClockTime *out);

/* 把时间格式化进 buf (用于 OLED 显示):
   时间行: "HH:MM:SS"            (8 字节 + '\0')
   日期行: "YYYY-MM-DD W"        (W=周几缩写) */
void Clock_FormatTime(char *buf, int bufsize);
void Clock_FormatDate(char *buf, int bufsize);

#ifdef __cplusplus
}
#endif

#endif /* __CLOCK_H__ */
