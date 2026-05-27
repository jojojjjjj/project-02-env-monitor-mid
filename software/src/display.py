# display.py - OLED显示模块
# OLED Display Module (SSD1306)

from machine import Pin, I2C
import ssd1306
import time
from config import Config


class DisplayManager:
    """OLED显示管理器"""

    def __init__(self, i2c=None, width=None, height=None):
        if i2c is None:
            i2c = I2C(0, scl=Pin(22), sda=Pin(21))

        width = width or Config.OLED_WIDTH
        height = height or Config.OLED_HEIGHT

        try:
            self.oled = ssd1306.SSD1306_I2C(width, height, i2c)
            self.width = width
            self.height = height
            self.available = True
            self.clear()
            self._show_splash()
        except Exception as e:
            print(f"OLED初始化失败: {e}")
            self.available = False

    def _show_splash(self):
        """显示启动画面"""
        if not self.available:
            return

        self.oled.fill(0)
        self.oled.text("AIR BUTLER", 30, 10)
        self.oled.text("Starting...", 30, 30)
        self.oled.show()
        time.sleep(1)

    def clear(self):
        """清空显示"""
        if self.available:
            self.oled.fill(0)
            self.oled.show()

    def update(self, reading, wifi_status=False, mqtt_status=False):
        """更新显示内容

        Args:
            reading: SensorReading对象
            wifi_status: WiFi连接状态
            mqtt_status: MQTT连接状态
        """
        if not self.available or not reading.valid:
            return

        self.oled.fill(0)

        # 标题栏
        self.oled.text("AIR BUTLER", 30, 0)

        # 温度
        if reading.temperature is not None:
            temp_str = f"T:{reading.temperature:5.1f}C"
            self.oled.text(temp_str, 0, 12)

        # 湿度
        if reading.humidity is not None:
            hum_str = f"H:{reading.humidity:5.1f}%"
            self.oled.text(hum_str, 70, 12)

        # PM2.5
        if reading.pm25 is not None:
            pm_str = f"PM:{reading.pm25:3d}"
            self.oled.text(pm_str, 0, 24)

        # 气压
        if reading.pressure is not None:
            pres_str = f"P:{reading.pressure:4.0f}"
            self.oled.text(pres_str, 60, 24)

        # WiFi状态
        wifi_text = "W:ON " if wifi_status else "W:OFF"
        self.oled.text(wifi_text, 0, 56)

        # MQTT状态
        mqtt_text = "M:ON" if mqtt_status else "M:OFF"
        self.oled.text(mqtt_text, 50, 56)

        # 时间戳(最后4位)
        time_str = f"{int(reading.timestamp) % 10000:04d}"
        self.oled.text(time_str, 90, 56)

        self.oled.show()

    def show_message(self, message, line=0):
        """显示单行消息

        Args:
            message: 要显示的消息(最多10个字符)
            line: 行号(0-7)
        """
        if not self.available:
            return

        self.oled.text(message[:10], 0, line * 8)
        self.oled.show()

    def show_progress(self, percent, width=100):
        """显示进度条

        Args:
            percent: 进度百分比(0-100)
            width: 进度条宽度(像素)
        """
        if not self.available:
            return

        # 清除进度条区域
        self.oled.fill_rect(0, 50, 127, 60, 0)

        # 绘制边框
        self.oled.rect(0, 50, width, 10, 1)

        # 绘制填充
        fill_width = int(width * percent / 100)
        if fill_width > 0:
            self.oled.fill_rect(1, 51, fill_width - 1, 8, 1)

        self.oled.show()

    def show_error(self, error_code):
        """显示错误代码

        Args:
            error_code: 错误代码(字符串)
        """
        if not self.available:
            return

        self.oled.fill(0)
        self.oled.text("ERROR:", 0, 10)
        self.oled.text(error_code[:10], 0, 30)
        self.oled.show()

    def show_wifi_config(self):
        """显示WiFi配置提示"""
        if not self.available:
            return

        self.oled.fill(0)
        self.oled.text("WiFi Setup", 25, 10)
        self.oled.text("Connect to", 20, 25)
        self.oled.text("AP and", 35, 35)
        self.oled.text("configure", 25, 45)
        self.oled.show()

    def scroll_text(self, text, delay=100):
        """滚动显示长文本

        Args:
            text: 要滚动的文本
            delay: 滚动延迟(毫秒)
        """
        if not self.available:
            return

        # 清屏
        self.oled.fill(0)

        # 计算文本宽度
        text_width = len(text) * 8

        # 滚动显示
        for offset in range(text_width, -self.width, -1):
            self.oled.fill(0)
            self.oled.text(text, -offset, 28)
            self.oled.show()
            time.sleep_ms(delay)

    def show_data_table(self, data_dict):
        """显示数据表格

        Args:
            data_dict: 数据字典 {标签: 值}
        """
        if not self.available:
            return

        self.oled.fill(0)

        y = 0
        for label, value in data_dict.items():
            if y >= self.height:
                break

            # 格式化显示
            text = f"{label[:3]}:{str(value)[:6]}"
            self.oled.text(text, 0, y)
            y += 10

        self.oled.show()

    def invert_display(self, invert=True):
        """反转显示颜色

        Args:
            invert: True为反转,False为正常
        """
        if self.available:
            self.oled.invert(invert)

    def contrast(self, value):
        """设置对比度

        Args:
            value: 对比度值(0-255)
        """
        if self.available:
            self.oled.contrast(value)

    def off(self):
        """关闭显示"""
        if self.available:
            self.oled.fill(0)
            self.oled.show()

    def on(self):
        """打开显示"""
        if self.available:
            self.oled.show()
