# utils.py - 工具函数模块
# Utility Functions Module

import time
import ujson
import gc
from config import Config


class DataValidator:
    """数据验证器"""

    @staticmethod
    def validate_temperature(temp):
        """验证温度数据"""
        if temp is None:
            return False
        return Config.TEMP_MIN <= temp <= Config.TEMP_MAX

    @staticmethod
    def validate_humidity(hum):
        """验证湿度数据"""
        if hum is None:
            return False
        return Config.HUM_MIN <= hum <= Config.HUM_MAX

    @staticmethod
    def validate_pressure(pres):
        """验证气压数据"""
        if pres is None:
            return False
        return Config.PRESS_MIN <= pres <= Config.PRESS_MAX

    @staticmethod
    def validate_pm25(pm25):
        """验证PM2.5数据"""
        if pm25 is None:
            return False
        return 0 <= pm25 <= 500


class AQICalculator:
    """空气质量指数计算器"""

    @staticmethod
    def calculate_aqi(pm25):
        """根据PM2.5计算AQI

        Args:
            pm25: PM2.5浓度(μg/m³)

        Returns:
            tuple: (AQI值, 等级, 颜色)
        """
        if pm25 is None:
            return None, "未知", "灰色"

        if pm25 <= 35:
            aqi = int((50 / 35) * pm25)
            level = "优"
            color = "绿色"
        elif pm25 <= 75:
            aqi = int(50 + (50 / 40) * (pm25 - 35))
            level = "良"
            color = "黄色"
        elif pm25 <= 115:
            aqi = int(100 + (50 / 40) * (pm25 - 75))
            level = "轻度污染"
            color = "橙色"
        elif pm25 <= 150:
            aqi = int(150 + (50 / 35) * (pm25 - 115))
            level = "中度污染"
            color = "红色"
        elif pm25 <= 250:
            aqi = int(200 + (100 / 100) * (pm25 - 150))
            level = "重度污染"
            color = "紫色"
        else:
            aqi = int(300 + (100 / 150) * (pm25 - 250))
            level = "严重污染"
            color = "褐红色"

        return aqi, level, color

    @staticmethod
    def get_health_advice(aqi_level):
        """获取健康建议

        Args:
            aqi_level: AQI等级

        Returns:
            str: 健康建议
        """
        advice_map = {
            "优": "空气很好,适合户外活动",
            "良": "空气质量可接受,正常活动",
            "轻度污染": "敏感人群减少户外活动",
            "中度污染": "减少户外活动,佩戴口罩",
            "重度污染": "避免户外活动,关闭门窗",
            "严重污染": "所有人避免户外活动"
        }
        return advice_map.get(aqi_level, "未知等级")


class StatisticsCalculator:
    """统计计算器"""

    def __init__(self, max_samples=100):
        self.max_samples = max_samples
        self.samples = []

    def add_sample(self, value):
        """添加样本"""
        if value is not None:
            self.samples.append(value)
            if len(self.samples) > self.max_samples:
                self.samples.pop(0)

    def get_stats(self):
        """获取统计信息

        Returns:
            dict: {min, max, avg, count}
        """
        if not self.samples:
            return None

        return {
            "min": min(self.samples),
            "max": max(self.samples),
            "avg": sum(self.samples) / len(self.samples),
            "count": len(self.samples),
            "latest": self.samples[-1]
        }

    def clear(self):
        """清空样本"""
        self.samples.clear()


class JSONHelper:
    """JSON处理辅助类"""

    @staticmethod
    def dumps(obj):
        """序列化为JSON字符串"""
        try:
            return ujson.dumps(obj)
        except Exception as e:
            print(f"JSON序列化失败: {e}")
            return "{}"

    @staticmethod
    def loads(s):
        """从JSON字符串解析"""
        try:
            return ujson.loads(s)
        except Exception as e:
            print(f"JSON解析失败: {e}")
            return {}


class MemoryManager:
    """内存管理器"""

    @staticmethod
    def get_free_memory():
        """获取剩余内存"""
        return gc.mem_free()

    @staticmethod
    def get_alloc_memory():
        """获取已分配内存"""
        return gc.mem_alloc()

    @staticmethod
    def collect():
        """执行垃圾回收"""
        gc.collect()

    @staticmethod
    def check_and_collect(threshold=10000):
        """检查内存并在必要时回收

        Args:
            threshold: 内存阈值(字节)
        """
        if MemoryManager.get_free_memory() < threshold:
            MemoryManager.collect()
            return True
        return False


class TimeHelper:
    """时间辅助类"""

    @staticmethod
    def get_timestamp():
        """获取当前时间戳"""
        return time.time()

    @staticmethod
    def get_iso_time(timestamp=None):
        """获取ISO格式时间

        Args:
            timestamp: 时间戳,默认为当前时间
        """
        if timestamp is None:
            timestamp = time.time()

        # MicroPython没有完整datetime,使用简化格式
        return f"{int(timestamp)}"

    @staticmethod
    def sleep_ms(ms):
        """休眠指定毫秒"""
        time.sleep_ms(ms)

    @staticmethod
    def sleep(seconds):
        """休眠指定秒数"""
        time.sleep(seconds)


class RingBuffer:
    """环形缓冲区"""

    def __init__(self, size):
        self.size = size
        self.buffer = [None] * size
        self.head = 0
        self.tail = 0
        self.count = 0

    def put(self, item):
        """添加元素"""
        self.buffer[self.tail] = item
        self.tail = (self.tail + 1) % self.size

        if self.count < self.size:
            self.count += 1
        else:
            self.head = (self.head + 1) % self.size

    def get(self):
        """获取元素"""
        if self.count == 0:
            return None

        item = self.buffer[self.head]
        self.head = (self.head + 1) % self.size
        self.count -= 1
        return item

    def peek(self, n=0):
        """查看元素但不移除"""
        if n >= self.count:
            return None
        index = (self.head + n) % self.size
        return self.buffer[index]

    def is_empty(self):
        """是否为空"""
        return self.count == 0

    def is_full(self):
        """是否已满"""
        return self.count == self.size

    def __len__(self):
        return self.count


def format_sensor_data(reading):
    """格式化传感器数据为字符串

    Args:
        reading: SensorReading对象

    Returns:
        str: 格式化的字符串
    """
    parts = []
    if reading.temperature is not None:
        parts.append(f"T:{reading.temperature:.1f}C")
    if reading.humidity is not None:
        parts.append(f"H:{reading.humidity:.1f}%")
    if reading.pm25 is not None:
        parts.append(f"PM:{reading.pm25}")
    return " ".join(parts)


def calculate_dew_point(temp, hum):
    """计算露点温度

    Args:
        temp: 温度(°C)
        hum: 相对湿度(%)

    Returns:
        float: 露点温度(°C)
    """
    if temp is None or hum is None:
        return None

    # Magnus公式近似计算
    a = 17.27
    b = 237.7

    alpha = ((a * temp) / (b + temp)) + (hum / 100.0)
    dew_point = (b * alpha) / (a - alpha)

    return dew_point


def calculate_heat_index(temp, hum):
    """计算体感温度(热指数)

    Args:
        temp: 温度(°C,需转换为°F计算)
        hum: 相对湿度(%)

    Returns:
        float: 体感温度(°C)
    """
    if temp is None or hum is None:
        return None

    # 转换为华氏度
    temp_f = temp * 9 / 5 + 32

    # Rothfusz回归方程
    if temp_f >= 80:
        c1 = -42.379
        c2 = 2.04901523
        c3 = 10.14333127
        c4 = -0.22475541
        c5 = -0.00683783
        c6 = -0.05481717
        c7 = 0.00122874
        c8 = 0.00085282
        c9 = -0.00000199

        hi = (c1 + c2 * temp_f + c3 * hum +
              c4 * temp_f * hum + c5 * temp_f ** 2 +
              c6 * hum ** 2 + c7 * temp_f ** 2 * hum +
              c8 * temp_f * hum ** 2 +
              c9 * temp_f ** 2 * hum ** 2)
    else:
        hi = temp_f

    # 转换回摄氏度
    return (hi - 32) * 5 / 9
