# config.py - 配置文件
# Configuration File

# WiFi配置
WIFI_SSID = "Your_WiFi_Name"
WIFI_PASS = "Your_WiFi_Password"
WIFI_TIMEOUT = 10  # 秒

# MQTT配置
MQTT_BROKER = "broker.emqx.io"  # 或使用本地IP "192.168.1.100"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "airbutler_001"
MQTT_USER = ""  # 如需认证
MQTT_PASS = ""  # 填写用户名和密码
MQTT_TOPIC = "home/airbutler/sensors"
MQTT_QOS = 0

# 传感器配置
# BME680
BME680_I2C_ADDR = 0x76  # 或0x77
TEMP_MIN = -40
TEMP_MAX = 80
HUM_MIN = 0
HUM_MAX = 100
PRESS_MIN = 300
PRESS_MAX = 1100

# PMS5003
PM_UART_ID = 2
PM_TX_PIN = 16
PM_RX_PIN = 17  # 不使用
PM_BAUDRATE = 9600

# OLED配置
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_I2C_ADDR = 0x3C  # 或0x3D

# 时间间隔(毫秒)
DISPLAY_INTERVAL = 1000  # 1秒
UPLOAD_INTERVAL = 60000  # 60秒
LOG_INTERVAL = 300000  # 5分钟
RECONNECT_INTERVAL = 10000  # 10秒

# 数据保留
DATA_BUFFER_SIZE = 100
MAX_LOG_FILES = 7  # 天

# 调试
DEBUG = True
VERBOSE = False

# AQI计算
AQI_PM25_BREAKPOINTS = [
    (35, 0, 50),    # 优
    (75, 50, 100),  # 良
    (115, 100, 150), # 轻度污染
    (150, 150, 200), # 中度污染
    (250, 200, 300), # 重度污染
]

# 系统配置
DEVICE_ID = "AIR_001"
DEVICE_NAME = "AirButler"
VERSION = "2.0"
