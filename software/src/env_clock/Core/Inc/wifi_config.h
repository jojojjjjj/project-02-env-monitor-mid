/**
  ******************************************************************************
  * @file    wifi_config.h
  * @brief   WiFi / SNTP / 刷新周期 等可配置参数 (学生请修改此处)
  *
  *   复刻学生请修改此处 WiFi 账号密码 —— 把 YOUR_SSID / YOUR_PASSWORD
  *   改成你自己 2.4GHz 路由器的 WiFi 名称和密码即可。
  *   (ESP8266 不支持 5GHz WiFi, 请务必使用 2.4GHz 频段。)
  ******************************************************************************
  * @attention
  * 复刻自 Bilibili 视频 BV1tb4y1U7Du (UP主: 乐在程上) 的温湿度网络时钟。
  * 本头文件是“学生唯一需要动手改”的配置文件。
  ******************************************************************************
  */
#ifndef __WIFI_CONFIG_H__
#define __WIFI_CONFIG_H__

#ifdef __cplusplus
extern "C" {
#endif

/* ===================== WiFi 账号密码 (必改) ===================== */
/* 复刻学生请修改此处 WiFi 账号密码 */
#define WIFI_SSID             "YOUR_SSID"
#define WIFI_PASSWORD         "YOUR_PASSWORD"

/* ===================== NTP / 时区 ===================== */
/* NTP 服务器 (SNTP 时间源) — 用阿里云 NTP, 国内速度快 */
#define NTP_SERVER            "ntp.aliyun.com"
/* 时区偏移 (小时) — 中国北京时间 = UTC+8 */
#define TIMEZONE_OFFSET       8

/* ===================== 刷新周期 ===================== */
/* 温湿度 + 时间 的屏幕刷新间隔 (毫秒)
   600000 = 10 分钟刷一次温湿度 (时间靠 systick 自己走, 每次刷新都更新) */
#define REFRESH_MS            600000

/* SNTP 重新同步间隔 (毫秒) — 每 1 小时重新向 NTP 服务器对一次时 */
#define SNTP_RESYNC_MS        3600000

/* ===================== 串口 ===================== */
/* ESP8266 AT 固件默认波特率, 一般为 115200 (老固件可能是 9600) */
#define ESP8266_UART_BAUD     115200

/* AT 命令默认超时 (毫秒) */
#define ESP8266_AT_TIMEOUT    2000

#ifdef __cplusplus
}
#endif

#endif /* __WIFI_CONFIG_H__ */
