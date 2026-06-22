/**
  ******************************************************************************
  * @file    tim.c
  * @brief   TIM2 PWM 配置 — 驱动无源蜂鸣器 (Buzzer)
  *
  *   设计思路 (循序渐进 — 讲 WHY):
  *   - 无源蜂鸣器自己不会响 (没有内置振荡电路), 必须给它的引脚一个方波信号
  *     才能发出声音。方波的“频率”决定音调, “占空比”决定音量。
  *   - STM32 的定时器 (TIM) 的 PWM 输出模式正好能产生这样的方波: 我们配好
  *     预分频 (Prescaler) 和周期 (Period/ARR), TIM2_CH2 就会在 PA1 上输出
  *     固定频率的方波, 蜂鸣器就响了。Beep_Switch(1) 启动 PWM, Beep_Switch(0) 停。
  *   - 本文件复刻自 KE1_PWM 工程的 tim.c (UP主 乐在程上 KE1 例程)。
  ******************************************************************************
  * @attention
  * <h2><center>&copy; Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.</center></h2>
  ******************************************************************************
  */

#include "tim.h"

TIM_HandleTypeDef htim2;

/* TIM2 init function — PA1 (TIM2_CH2) PWM 输出, 驱动无源蜂鸣器 */
void MX_TIM2_Init(void)
{
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};

  htim2.Instance = TIM2;
  /* SYSCLK=32MHz (KE1 板: HSE 8MHz / PLLM1 * PLLN8 / PLLR2), APB1Tim=32MHz。
     32MHz / 32 = 1MHz 计数时钟; ARR=370 -> 约 2.7kHz 方波 (蜂鸣器可发声) */
  htim2.Init.Prescaler = 32-1;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 370-1;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  if (HAL_TIM_PWM_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 180;          /* 占空比约 50% (180/370) */
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  if (HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_2) != HAL_OK)
  {
    Error_Handler();
  }
  HAL_TIM_MspPostInit(&htim2);
}

void HAL_TIM_PWM_MspInit(TIM_HandleTypeDef* tim_pwmHandle)
{
  if(tim_pwmHandle->Instance==TIM2)
  {
    __HAL_RCC_TIM2_CLK_ENABLE();
  }
}

void HAL_TIM_MspPostInit(TIM_HandleTypeDef* timHandle)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  if(timHandle->Instance==TIM2)
  {
    __HAL_RCC_GPIOA_CLK_ENABLE();
    /**TIM2 GPIO Configuration
    PA1     ------> TIM2_CH2  (蜂鸣器信号脚)
    */
    GPIO_InitStruct.Pin = GPIO_PIN_1;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    GPIO_InitStruct.Alternate = GPIO_AF1_TIM2;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
  }
}

void HAL_TIM_PWM_MspDeInit(TIM_HandleTypeDef* tim_pwmHandle)
{
  if(tim_pwmHandle->Instance==TIM2)
  {
    __HAL_RCC_TIM2_CLK_DISABLE();
  }
}

/* USER CODE BEGIN 1 */

/* 蜂鸣器开关: 1=响, 0=停 */
void Beep_Switch(char onoff)
{
	if(1 == onoff){
		HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2);
	}else if(0 == onoff){
		HAL_TIM_PWM_Stop(&htim2, TIM_CHANNEL_2);
	}
}

/* USER CODE END 1 */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
