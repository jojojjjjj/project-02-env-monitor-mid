/**
  ******************************************************************************
  * @file    tim.h
  * @brief   This file contains all the function prototypes for
  *          the tim.c file — TIM2 PWM (无源蜂鸣器 Buzzer)
  ******************************************************************************
  * @attention
  * <h2><center>&copy; Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.</center></h2>
  * 本文件复刻自 KE1_PWM 工程的 tim.c/.h (UP主 乐在程上 KE1 例程)。
  ******************************************************************************
  */
#ifndef __TIM_H__
#define __TIM_H__

#ifdef __cplusplus
extern "C" {
#endif

#include "main.h"

extern TIM_HandleTypeDef htim2;

void MX_TIM2_Init(void);
void HAL_TIM_MspPostInit(TIM_HandleTypeDef *htim);

/* 蜂鸣器开关: 1=响, 0=停 */
void Beep_Switch(char onoff);

#ifdef __cplusplus
}
#endif

#endif /* __TIM_H__ */
