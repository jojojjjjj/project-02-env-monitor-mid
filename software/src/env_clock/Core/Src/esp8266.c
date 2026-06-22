/**
  ******************************************************************************
  * @file    esp8266.c
  * @brief   ESP8266 WiFi + SNTP over UART AT 命令 实现
  *
  *   复用 KE1_IoT 的 UART AT 框架 (usart.c 里的 UART_Put_AT_Cmd /
  *   UART_Get_AT_Resp / 中断接收环形缓冲), 把 NB-IoT 命令替换为 ESP8266 的:
  *     AT                         — 测试模块响应
  *     ATE0                       — 关回显 (让响应更干净)
  *     AT+CWMODE=1                — 设为 STA 模式 (做 WiFi 终端)
  *     AT+CWJAP="ssid","pwd"      — 连接 AP (路由器)
  *     AT+CIPSNTPCFG=1,tz,"ntp"   — 开启 SNTP, 设时区 + NTP 服务器
  *     AT+CIPSNTPTIME             — 查询当前 SNTP 时间
  ******************************************************************************
  */
#include "esp8266.h"
#include "usart.h"
#include "wifi_config.h"
#include <stdio.h>
#include <string.h>

/* AT 响应缓冲 (够装一条 SNTP 时间响应) */
#define ESP_RESP_BUF_SIZE  256

/* 月份英文缩写 -> 数字, 用于解析 +CIPSNTPTIME 返回的 "Jan".."Dec" */
static int month_from_str(const char *mon)
{
    const char *months[] = {"Jan","Feb","Mar","Apr","May","Jun",
                            "Jul","Aug","Sep","Oct","Nov","Dec"};
    int i;
    for (i = 0; i < 12; i++) {
        if (strncmp(mon, months[i], 3) == 0) return i + 1;
    }
    return 0;
}

int ESP8266_Init(void)
{
    uint8_t resp[ESP_RESP_BUF_SIZE];

    /* 使能 USART3 中断接收 (KE1 框架) */
    UART_Enable_Receive_IT();

    /* 1. AT 测试连通 — 期望 "OK" */
    if (ESP8266_SendAT("AT\r\n", "OK", resp, sizeof(resp), 1000) <= 0) {
        printf("[ESP8266] AT no response, check wiring/baud\r\n");
        return -1;
    }

    /* 2. 关回显 ATE0, 让后续响应干净 */
    ESP8266_SendAT("ATE0\r\n", "OK", resp, sizeof(resp), 1000);

    /* 3. 设为 STA 模式 (WiFi 终端) */
    if (ESP8266_SendAT("AT+CWMODE=1\r\n", "OK", resp, sizeof(resp), 1000) <= 0) {
        printf("[ESP8266] CWMODE=1 failed\r\n");
        return -1;
    }

    printf("[ESP8266] init OK\r\n");
    return 0;
}

int ESP8266_SendAT(const char *at_cmd, const char *expect,
                   uint8_t *resp_buf, uint16_t resp_size,
                   uint32_t timeout_ms)
{
    int len;

    /* 清空接收环形缓冲的残留 (KE1 框架: 把 Out 拉齐到 In) */
    extern volatile uint8_t ucUsart3_In;
    extern volatile uint8_t ucUsart3_Out;
    ucUsart3_Out = ucUsart3_In;

    /* 发送 AT 命令 (复用 KE1 的 UART_Put_AT_Cmd) */
    UART_Put_AT_Cmd((char *)at_cmd);

    /* 收响应 (复用 KE1 的 UART_Get_AT_Resp) */
    if (resp_buf && resp_size > 0) {
        memset(resp_buf, 0, resp_size);
    }
    len = UART_Get_AT_Resp(resp_buf, resp_size, (uint16_t)timeout_ms);
    if (len <= 0) return 0;   /* 超时无响应 */

    /* 终止字符串, 方便 strstr */
    if (resp_buf && resp_size > 0) {
        resp_buf[resp_size - 1] = 0;
        if (len < (int)resp_size) resp_buf[len] = 0;
    }

    /* 命中期望字符串? */
    if (expect && resp_buf) {
        if (strstr((char *)resp_buf, expect) != NULL) return 1;
        return 0;
    }
    return len;
}

int ESP8266_ConnectWiFi(const char *ssid, const char *password)
{
    uint8_t resp[ESP_RESP_BUF_SIZE];
    char cmd[128];

    /* AT+CWJAP="ssid","password" — 连接可能要几秒, 给 15s 超时 */
    snprintf(cmd, sizeof(cmd), "AT+CWJAP=\"%s\",\"%s\"\r\n", ssid, password);

    /* 成功会返回 "WIFI CONNECTED"\n"WIFI GOT IP"\n"OK" */
    if (ESP8266_SendAT(cmd, "OK", resp, sizeof(resp), 15000) <= 0) {
        printf("[ESP8266] WiFi connect FAILED:\r\n%s\r\n", (char *)resp);
        return -1;
    }

    printf("[ESP8266] WiFi connected to %s\r\n", ssid);
    return 0;
}

int ESP8266_SNTPConfig(int timezone, const char *ntp_server)
{
    uint8_t resp[ESP_RESP_BUF_SIZE];
    char cmd[128];

    /* AT+CIPSNTPCFG=1,<tz>,"<server>" — 开启 SNTP, 设时区和服务器 */
    snprintf(cmd, sizeof(cmd), "AT+CIPSNTPCFG=1,%d,\"%s\"\r\n",
             timezone, ntp_server);

    if (ESP8266_SendAT(cmd, "OK", resp, sizeof(resp), 2000) <= 0) {
        printf("[ESP8266] SNTP config failed\r\n");
        return -1;
    }

    printf("[ESP8266] SNTP configured (tz=%d, %s)\r\n", timezone, ntp_server);
    return 0;
}

int ESP8266_GetSNTPTime(ClockTime *out)
{
    uint8_t resp[ESP_RESP_BUF_SIZE];
    char *p;
    char wday_str[8] = {0}, mon_str[8] = {0};
    int day, hour, min, sec, year;

    /* 查询 SNTP 时间 */
    if (ESP8266_SendAT("AT+CIPSNTPTIME\r\n", "+CIPSNTPTIME",
                       resp, sizeof(resp), 2000) <= 0) {
        return -1;
    }

    /* 响应格式: "+CIPSNTPTIME:Thu Jan 01 12:00:00 2026"
       sscanf 解析: 星期 月 日 时:分:秒 年 */
    p = strstr((char *)resp, "+CIPSNTPTIME:");
    if (!p) return -1;
    p += strlen("+CIPSNTPTIME:");

    if (sscanf(p, "%3s %3s %d %d:%d:%d %d",
               wday_str, mon_str, &day, &hour, &min, &sec, &year) != 7) {
        return -1;
    }

    /* 星期英文 -> 数字 (0=Sun) */
    const char *wdays[] = {"Sun","Mon","Tue","Wed","Thu","Fri","Sat"};
    int wday = 0, i;
    for (i = 0; i < 7; i++) {
        if (strncmp(wday_str, wdays[i], 3) == 0) { wday = i; break; }
    }

    out->year  = year;
    out->month = month_from_str(mon_str);
    out->day   = day;
    out->hour  = hour;
    out->min   = min;
    out->sec   = sec;
    out->wday  = wday;

    return 0;
}
