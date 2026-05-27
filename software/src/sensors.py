# sensors.py - 传感器读取模块
# Sensor Reading Module (BME680 + PMS5003)

from machine import Pin, I2C, UART
import bme680
import time
from config import Config


class SensorReading:
    """传感器读数数据类"""

    def __init__(self):
        self.timestamp = time.time()
        self.temperature = None
        self.humidity = None
        self.pressure = None
        self.gas = None
        self.pm25 = None
        self.pm10 = None
        self.valid = False

    def to_dict(self):
        """转换为字典"""
        return {
            "timestamp": self.timestamp,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "gas": self.gas,
            "pm25": self.pm25,
            "pm10": self.pm10,
            "valid": self.valid
        }


class BME680Sensor:
    """BME680环境传感器驱动"""

    def __init__(self, i2c=None, address=None):
        if i2c is None:
            i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

        self.i2c = i2c
        self.address = address or Config.BME680_I2C_ADDR

        try:
            self.sensor = bme680.BME680_I2C(i2c=i2c, address=self.address)
            self._configure()
            self.available = True
        except Exception as e:
            print(f"BME680初始化失败: {e}")
            self.available = False

    def _configure(self):
        """配置传感器参数"""
        self.sensor.set_humidity_oversample(bme680.OS_2X)
        self.sensor.set_pressure_oversample(bme680.OS_4X)
        self.sensor.set_temperature_oversample(bme680.OS_8X)
        self.sensor.set_filter(bme680.FILTER_SIZE_3)

    def read(self):
        """读取传感器数据"""
        if not self.available:
            return None, None, None, None

        try:
            self.sensor.get_sensor_data()
            temp = self.sensor.data.temperature
            hum = self.sensor.data.humidity
            pres = self.sensor.data.pressure
            gas = self.sensor.data.gas_resistance

            # 数据验证
            if temp and Config.TEMP_MIN <= temp <= Config.TEMP_MAX:
                temp += Config.TEMP_OFFSET  # 应用校准偏移
            else:
                temp = None

            if hum and Config.HUM_MIN <= hum <= Config.HUM_MAX:
                hum += Config.HUM_OFFSET
            else:
                hum = None

            if pres and Config.PRESS_MIN <= pres <= Config.PRESS_MAX:
                pass  # 气压通常不需要校准
            else:
                pres = None

            return temp, hum, pres, gas

        except Exception as e:
            print(f"BME680读取错误: {e}")
            return None, None, None, None


class PMS5003Sensor:
    """PMS5003 PM2.5传感器驱动"""

    def __init__(self, uart_id=None, tx_pin=None, rx_pin=None):
        uart_id = uart_id or Config.PM_UART_ID
        tx_pin = tx_pin or Config.PM_TX_PIN

        self.uart = UART(
            uart_id,
            baudrate=Config.PM_BAUDRATE,
            rx=rx_pin,
            tx=tx_pin,
            timeout=1000
        )

        self.buffer = bytearray(32)
        self.available = True

    def read(self):
        """读取PM2.5数据"""
        if not self.available:
            return None, None

        try:
            if self.uart.any() >= 32:
                self.uart.readinto(self.buffer, 32)

                # 验证帧头
                if self.buffer[0] == 0x42 and self.buffer[1] == 0x4D:
                    # 计算校验和
                    checksum = sum(self.buffer[0:30]) & 0xFFFF
                    received = (self.buffer[30] << 8) | self.buffer[31]

                    if checksum == received:
                        pm25 = (self.buffer[6] << 8) | self.buffer[7]
                        pm10 = (self.buffer[8] << 8) | self.buffer[9]

                        # 减去基准值
                        pm25 = max(0, pm25 - Config.PM_BASELINE)
                        pm10 = max(0, pm10 - Config.PM_BASELINE)

                        return pm25, pm10

            return None, None

        except Exception as e:
            print(f"PMS5003读取错误: {e}")
            return None, None


class SensorManager:
    """传感器管理器 - 整合所有传感器"""

    def __init__(self):
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

        # 初始化BME680
        self.bme = BME680Sensor(self.i2c)

        # 初始化PMS5003
        self.pm = PMS5003Sensor()

    def read_all(self):
        """读取所有传感器数据"""
        reading = SensorReading()
        reading.timestamp = time.time()

        # 读取BME680
        temp, hum, pres, gas = self.bme.read()
        reading.temperature = temp
        reading.humidity = hum
        reading.pressure = pres
        reading.gas = gas

        # 读取PMS5003
        pm25, pm10 = self.pm.read()
        reading.pm25 = pm25
        reading.pm10 = pm10

        # 验证数据有效性
        reading.valid = any([
            reading.temperature is not None,
            reading.humidity is not None,
            reading.pm25 is not None
        ])

        return reading

    def get_status(self):
        """获取传感器状态"""
        return {
            "bme680": self.bme.available,
            "pms5003": self.pm.available
        }
