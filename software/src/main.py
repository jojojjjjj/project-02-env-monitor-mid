# main.py - 环境监测站主程序
# Environmental Monitor Main Program

from machine import Pin, I2C, UART, reset
import time
import gc
import sys

# 导入项目模块
from config import Config
from wifi_manager import WiFiManager
from mqtt_manager import MQTTManager
from sensor_manager import SensorManager
from display import DisplayManager
from data_logger import DataLogger


class AirButler:
    """空气管家 - 主控制类"""

    def __init__(self):
        print("=" * 50)
        print("  空气管家 Environmental Monitor")
        print("  版本: 2.0")
        print("=" * 50)

        # 初始化状态
        self.running = True
        self.error_count = 0
        self.max_errors = 10

        # 初始化各模块
        self._init_modules()

    def _init_modules(self):
        """初始化所有模块"""
        try:
            # WiFi管理器
            self.wifi = WiFiManager(
                Config.WIFI_SSID,
                Config.WIFI_PASS
            )

            # MQTT管理器
            self.mqtt = MQTTManager(
                broker=Config.MQTT_BROKER,
                client_id=Config.MQTT_CLIENT_ID,
                port=Config.MQTT_PORT
            )

            # 传感器管理器
            self.sensors = SensorManager()

            # 显示管理器
            self.display = DisplayManager()

            # 数据记录器
            self.logger = DataLogger()

            print("所有模块初始化成功")

        except Exception as e:
            print(f"模块初始化失败: {e}")
            sys.exit(1)

    def connect_network(self):
        """连接网络"""
        print("\n连接WiFi...")
        if not self.wifi.connect(timeout=Config.WIFI_TIMEOUT):
            print("WiFi连接失败!")
            return False

        print("连接MQTT...")
        if not self.mqtt.connect():
            print("MQTT连接失败!")
            return False

        return True

    def run(self):
        """主循环"""
        print("\n主程序启动...")

        # 定时器
        last_display = 0
        last_upload = 0
        last_log = 0

        while self.running:
            try:
                # 检查网络连接
                if not self.wifi.is_connected():
                    self.wifi.check_connection()

                if not self.mqtt.connected:
                    self.mqtt.check_connection()

                # 读取传感器
                reading = self.sensors.read_all()

                if reading.valid:
                    now = time.ticks_ms()

                    # 更新显示
                    if time.ticks_diff(now, last_display) > Config.DISPLAY_INTERVAL:
                        self.display.update(reading)
                        last_display = now

                    # 上传数据
                    if time.ticks_diff(now, last_upload) > Config.UPLOAD_INTERVAL:
                        if self.mqtt.publish_sensor_data(reading):
                            last_upload = now
                            self.error_count = 0  # 重置错误计数

                    # 记录数据
                    if time.ticks_diff(now, last_log) > Config.LOG_INTERVAL:
                        self.logger.log(reading)
                        last_log = now

                # 内存管理
                if gc.mem_free() < 10000:
                    gc.collect()

                time.sleep(0.1)

            except Exception as e:
                self.error_count += 1
                print(f"错误 #{self.error_count}: {e}")

                if self.error_count >= self.max_errors:
                    print("错误过多,系统重启!")
                    reset()

                time.sleep(5)

    def stop(self):
        """停止程序"""
        print("\n停止程序...")
        self.mqtt.disconnect()
        self.running = False


def main():
    """程序入口"""
    try:
        # 创建应用实例
        app = AirButler()

        # 连接网络
        if not app.connect_network():
            print("无法连接网络,进入离线模式")
            # 可以在离线模式下继续运行

        # 运行主循环
        app.run()

    except KeyboardInterrupt:
        print("\n用户中断")
        app.stop()

    except Exception as e:
        print(f"致命错误: {e}")
        reset()


if __name__ == "__main__":
    main()
