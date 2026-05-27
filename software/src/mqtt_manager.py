# mqtt_manager.py - MQTT管理模块
# MQTT Manager Module

from umqtt.simple import MQTTClient
import time
import ujson
from config import Config


class MQTTManager:
    """MQTT通信管理器"""

    def __init__(self, broker, client_id, port=1883, user=None, passw=None):
        self.broker = broker
        self.client_id = client_id
        self.port = port
        self.user = user
        self.passw = passw

        self.connected = False
        self.last_connect = 0
        self.reconnect_interval = 10

        self._create_client()

    def _create_client(self):
        """创建MQTT客户端"""
        if self.user and self.passw:
            self.client = MQTTClient(
                self.client_id,
                self.broker,
                self.port,
                self.user,
                self.passw
            )
        else:
            self.client = MQTTClient(
                self.client_id,
                self.broker,
                self.port
            )

        # 设置Last Will
        will_topic = f"home/airbutler/{self.client_id}/status"
        self.client.set_last_will(will_topic, b"offline", retain=True)

    def connect(self, timeout=10):
        """连接MQTT Broker"""
        print(f"连接MQTT: {self.broker}")

        try:
            self.client.connect()
            self.connected = True
            self.last_connect = time.time()

            # 发布上线消息
            status_topic = f"home/airbutler/{self.client_id}/status"
            self.client.publish(status_topic, b"online", retain=True)

            print("MQTT连接成功!")
            return True

        except Exception as e:
            print(f"MQTT连接失败: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """断开连接"""
        if self.connected:
            status_topic = f"home/airbutler/{self.client_id}/status"
            self.client.publish(status_topic, b"offline", retain=True)
            self.client.disconnect()
            self.connected = False
            print("MQTT已断开")

    def check_connection(self):
        """检查连接,必要时重连"""
        if not self.connected:
            now = time.time()
            if now - self.last_connect > self.reconnect_interval:
                self.connect()
        return self.connected

    def publish_sensor_data(self, reading):
        """发布传感器数据"""
        if not self.connected:
            return False

        try:
            # 构建消息
            payload = {
                "t": int(reading.timestamp),
                "T": reading.temperature,
                "H": reading.humidity,
                "P": reading.pressure,
                "PM25": reading.pm25,
                "PM10": reading.pm10
            }

            # 转JSON
            message = ujson.dumps(payload)

            # 发布
            self.client.publish(
                Config.MQTT_TOPIC.encode(),
                message.encode(),
                qos=Config.MQTT_QOS
            )

            return True

        except Exception as e:
            print(f"发布失败: {e}")
            self.connected = False
            return False
