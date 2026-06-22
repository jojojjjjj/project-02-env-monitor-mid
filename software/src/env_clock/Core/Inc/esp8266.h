/**
  ******************************************************************************
  * @file    esp8266.h
  * @brief   ESP8266 WiFi + SNTP over UART AT 命令 头文件
  *
  *   设计思路 (循序渐进 — 讲 WHY):
  *   - STM32L433 本身没有 WiFi, 我们用一片 ESP-01S (ESP8266) 当“WiFi 协处理器”:
  *     STM32 通过 UART (串口) 给 ESP8266 发 AT 文本命令, ESP8266 帮我们连 WiFi、
  *     向 NTP 服务器对时间, 再把结果用文本回传给 STM32。
  *   - 这种“主控 + AT 协处理器”是嵌入式里非常通用的架构 (NB-IoT/4G/WiFi/蓝牙
  *     模块都常用 AT)。我们把 KE1_IoT 原工程里发 NB-IoT AT 命令的那套框架
  *     (UART_Put_AT_Cmd / UART_Get_AT_Resp) 直接复用, 只是把命令字符串换成
  *     ESP8266 的 WiFi/SNTP 命令而已。
  ******************************************************************************
  */
#ifndef __ESP8266_H__
#define __ESP8266_H__

#ifdef __cplusplus
extern "C" {
#endif

#include "main.h"
#include "clock.h"

/* ESP8266 初始化: 使能 USART3 接收中断, 发 AT 测试连通, 关回显 */
int  ESP8266_Init(void);

/* 发一条 AT 命令, 等响应, 返回响应字节数 (<=0 表示超时无响应)。
   expect: 期望在响应里出现的字符串 (如 "OK"), 命中返回 1, 否则 0。
   timeout_ms: 超时毫秒。 */
int  ESP8266_SendAT(const char *at_cmd, const char *expect,
                    uint8_t *resp_buf, uint16_t resp_size,
                    uint32_t timeout_ms);

/* 连 WiFi: AT+CWJAP="ssid","password" (阻塞直到拿到 IP 或超时)。
   成功返回 0, 失败返回 -1。 */
int  ESP8266_ConnectWiFi(const char *ssid, const char *password);

/* 配置 SNTP: AT+CIPSNTPCFG=1,<timezone>,"<ntp_server>" */
int  ESP8266_SNTPConfig(int timezone, const char *ntp_server);

/* 拿当前网络时间: AT+CIPSNTPTIME -> "+CIPSNTPTIME:Thu Jan 01 12:00:00 2026"
   解析后写入 out。成功返回 0, 失败返回 -1。
   注意: ESP8266 返回的是 UTC+timezone 后的本地时间字符串。 */
int  ESP8266_GetSNTPTime(ClockTime *out);

#ifdef __cplusplus
}
#endif

#endif /* __ESP8266_H__ */
