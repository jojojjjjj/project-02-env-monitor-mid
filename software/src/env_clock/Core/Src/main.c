/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : 温湿度网络时钟 (WiFi Temp/Humidity Network Clock) 主程序
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * 复刻自 Bilibili 视频 BV1tb4y1U7Du (UP主: 乐在程上) 的温湿度网络时钟。
  * 硬件: STM32L433 (KE1 板) + ESP8266 (WiFi/SNTP) + SHT31 (温湿度) + SSD1306 OLED。
  *
  * 主流程 (循序渐进 — 讲 WHY):
  *   1. 上电初始化: HAL/时钟/GPIO/I2C/UART/TIM → SHT31 → OLED 欢迎屏 → ESP8266
  *   2. 连 WiFi (AT+CWJAP) → 配 SNTP (AT+CIPSNTPCFG) → 拿网络时间 (AT+CIPSNTPTIME)
  *   3. 主循环:
  *        - 每过 REFRESH_MS (10 分钟): 读 SHT31 温湿度 + 重新 SNTP 对时 + 刷屏
  *        - 每次循环: Clock_Tick() 用 SysTick 守时, 刷时间显示
  *        - 整点 (分=0, 秒<2): 蜂鸣器短鸣报时
  *        - 按键 PA0 按下: 立即重新 SNTP 对时
  *        - WiFi 连不上: OLED 提示, 回退到 SysTick 守时继续走
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "i2c.h"
#include "usart.h"
#include "tim.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdio.h>
#include <string.h>
#include "oled.h"
#include "esp8266.h"
#include "clock.h"
#include "wifi_config.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */
static void do_sntp_resync(void);
static void hourly_chime(void);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point. — 温湿度网络时钟
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */
  float fTemp = 0.0f, fHumi = 0.0f;
  uint32_t last_refresh_ms = 0;   /* 上次刷新温湿度/SNTP 的时刻 */
  uint32_t last_chime_hour = 0xFF;/* 上次报过时的整点小时 (避免重复报) */
  uint32_t now_ms;
  ClockTime ct;
  int wifi_ok = 0;

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_I2C2_Init();
  MX_USART1_UART_Init();
  MX_USART3_UART_Init();
  MX_TIM2_Init();
  /* USER CODE BEGIN 2 */

  /* printf 走 USART1 (PA9/PA10, 115200) — KE1 框架已重定向 __io_putchar */
  printf("\r\n=== EnvClock WiFi (BV1tb4y1U7Du) boot ===\r\n");

  /* 1. 初始化时钟 (本地默认时间) */
  Clock_Init();

  /* 2. SHT31 温湿度传感器初始化 (KE1 驱动) */
  KE1_I2C_SHT31_Init();
  printf("[MAIN] SHT31 init done\r\n");

  /* 3. OLED 显示欢迎屏 */
  OLED_Init();
  OLED_ShowWelcome();
  HAL_Delay(800);

  /* 4. ESP8266 初始化 + 连 WiFi + 配 SNTP */
  if (ESP8266_Init() == 0) {
      printf("[MAIN] ESP8266 ready, connecting WiFi %s\r\n", WIFI_SSID);
      if (ESP8266_ConnectWiFi(WIFI_SSID, WIFI_PASSWORD) == 0) {
          ESP8266_SNTPConfig(TIMEZONE_OFFSET, NTP_SERVER);
          HAL_Delay(1000);   /* 等 SNTP 同步生效 */
          wifi_ok = 1;
      }
  }

  /* 5. 首次拿网络时间校准时钟; 失败则回退 SysTick 守时 */
  if (wifi_ok) {
      if (ESP8266_GetSNTPTime(&ct) == 0) {
          Clock_SyncFromSNTP(ct.year, ct.month, ct.day,
                             ct.hour, ct.min, ct.sec, ct.wday);
          printf("[MAIN] SNTP sync OK: %04d-%02d-%02d %02d:%02d:%02d\r\n",
                 ct.year, ct.month, ct.day, ct.hour, ct.min, ct.sec);
      } else {
          printf("[MAIN] SNTP time fetch failed, run on SysTick\r\n");
      }
  } else {
      OLED_ShowWiFiFail();
      HAL_Delay(1500);
  }

  /* 6. 首次读温湿度, 显示完整一屏 */
  KE1_I2C_SHT31(&fTemp, &fHumi);
  printf("[MAIN] T:%.2fC H:%.2f%%\r\n", fTemp, fHumi);

  last_refresh_ms = HAL_GetTick();
  last_chime_hour = 0xFF;
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    now_ms = HAL_GetTick();

    /* ---- 守时: 用 SysTick 推进本地时钟 ---- */
    Clock_Tick(now_ms);
    Clock_Get(&ct);

    /* ---- 整点报时: 每个整点蜂鸣器短鸣一次 ---- */
    if (ct.min == 0 && ct.sec < 2) {
        if (last_chime_hour != (uint32_t)ct.hour) {
            hourly_chime();
            last_chime_hour = (uint32_t)ct.hour;
        }
    } else {
        /* 离开整点后复位标记, 下个整点再报 */
        if (ct.min != 0) last_chime_hour = 0xFF;
    }

    /* ---- 定时刷新温湿度 + 重新 SNTP 对时 (每 REFRESH_MS) ---- */
    if ((now_ms - last_refresh_ms) >= REFRESH_MS) {
        last_refresh_ms = now_ms;

        /* 读温湿度 */
        if (KE1_I2C_SHT31(&fTemp, &fHumi) == 0) {
            printf("[MAIN] T:%.2fC H:%.2f%%\r\n", fTemp, fHumi);
        }

        /* 重新 SNTP 对时 (wifi_ok 时) */
        if (wifi_ok) {
            do_sntp_resync();
        }
    }

    /* ---- 按键 PA0: 手动触发重新 SNTP 对时 ---- */
    if (BTN_KEY_PRESSED) {
        HAL_Delay(20);   /* 简单消抖 */
        if (BTN_KEY_PRESSED) {
            printf("[MAIN] Button pressed, resync SNTP\r\n");
            if (wifi_ok) do_sntp_resync();
            while (BTN_KEY_PRESSED) HAL_Delay(10);  /* 等按键释放 */
        }
    }

    /* ---- 刷新 OLED 一屏 (日期 + 时间 + 温湿度 + 同步状态) ---- */
    OLED_ShowClock(ct.year, (uint8_t)ct.month, (uint8_t)ct.day,
                   (uint8_t)ct.hour, (uint8_t)ct.min, (uint8_t)ct.sec,
                   (uint8_t)ct.wday, fTemp, fHumi, Clock_IsSynced());

    /* 串口调试输出当前时间 (每秒级) */
    {
        static uint8_t last_sec = 0xFF;
        if (last_sec != (uint8_t)ct.sec) {
            last_sec = (uint8_t)ct.sec;
            printf("[CLK] %04d-%02d-%02d %02d:%02d:%02d %s | T:%.2f H:%.2f\r\n",
                   ct.year, ct.month, ct.day, ct.hour, ct.min, ct.sec,
                   Clock_IsSynced() ? "OK" : "NO",
                   fTemp, fHumi);
        }
    }

    HAL_Delay(200);   /* 主循环节流, 约 5Hz 刷屏足够 */
    /* USER CODE END 3 */
  }
  /* USER CODE END 3 */
}

/* USER CODE BEGIN 4 */

/* 重新向 NTP 服务器对一次时 */
static void do_sntp_resync(void)
{
    ClockTime ct;
    if (ESP8266_GetSNTPTime(&ct) == 0) {
        Clock_SyncFromSNTP(ct.year, ct.month, ct.day,
                           ct.hour, ct.min, ct.sec, ct.wday);
        printf("[SNTP] resync OK: %04d-%02d-%02d %02d:%02d:%02d\r\n",
               ct.year, ct.month, ct.day, ct.hour, ct.min, ct.sec);
    } else {
        printf("[SNTP] resync FAILED (keep SysTick time)\r\n");
    }
}

/* 整点报时: 蜂鸣器短鸣两声 (嘀-嘀) */
static void hourly_chime(void)
{
    Beep_Switch(1);
    HAL_Delay(120);
    Beep_Switch(0);
    HAL_Delay(80);
    Beep_Switch(1);
    HAL_Delay(120);
    Beep_Switch(0);
    printf("[BEEP] hourly chime\r\n");
}

/* USER CODE END 4 */

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 1;
  RCC_OscInitStruct.PLL.PLLN = 8;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV7;
  RCC_OscInitStruct.PLL.PLLQ = RCC_PLLQ_DIV2;
  RCC_OscInitStruct.PLL.PLLR = RCC_PLLR_DIV2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_USART1|RCC_PERIPHCLK_USART3
                              |RCC_PERIPHCLK_I2C2;
  PeriphClkInit.Usart1ClockSelection = RCC_USART1CLKSOURCE_PCLK2;
  PeriphClkInit.Usart3ClockSelection = RCC_USART3CLKSOURCE_PCLK1;
  PeriphClkInit.I2c2ClockSelection = RCC_I2C2CLKSOURCE_PCLK1;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
  /** Configure the main internal regulator output voltage
  */
  if (HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
