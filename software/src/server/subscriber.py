# subscriber.py - PC端MQTT订阅+InfluxDB写入
# MQTT Subscriber and InfluxDB Writer (Server Side)

import paho.mqtt.client as mqtt
import json
import time
import logging
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MQTTInfluxDBBridge:
    """MQTT到InfluxDB的数据桥接器"""

    def __init__(self, config):
        """
        Args:
            config: 配置字典,包含MQTT和InfluxDB配置
        """
        # MQTT配置
        self.mqtt_broker = config.get('mqtt', {}).get('broker', 'localhost')
        self.mqtt_port = config.get('mqtt', {}).get('port', 1883)
        self.mqtt_topic = config.get('mqtt', {}).get('topic_sensors', 'home/airbutler/sensors')
        self.mqtt_client_id = config.get('mqtt', {}).get('client_id', 'server_subscriber')

        # InfluxDB配置
        self.influx_url = config.get('influxdb', {}).get('url', 'http://localhost:8086')
        self.influx_token = config.get('influxdb', {}).get('token', '')
        self.influx_org = config.get('influxdb', {}).get('org', 'airbutler')
        self.influx_bucket = config.get('influxdb', {}).get('bucket', 'sensors')

        # 初始化InfluxDB客户端
        self.influx_client = None
        self.write_api = None

        # 统计信息
        self.message_count = 0
        self.error_count = 0
        self.start_time = time.time()

    def on_connect(self, client, userdata, flags, rc):
        """MQTT连接回调"""
        if rc == 0:
            logger.info("连接MQTT Broker成功")
            client.subscribe(self.mqtt_topic)
            logger.info(f"已订阅主题: {self.mqtt_topic}")
        else:
            logger.error(f"连接失败,返回码: {rc}")

    def on_message(self, client, userdata, msg):
        """MQTT消息接收回调"""
        try:
            # 解析消息
            payload = msg.payload.decode('utf-8')
            data = json.loads(payload)

            logger.debug(f"收到消息: {data}")

            # 写入InfluxDB
            self._write_to_influxdb(data)

            self.message_count += 1

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}")
            self.error_count += 1
        except Exception as e:
            logger.error(f"消息处理错误: {e}")
            self.error_count += 1

    def _write_to_influxdb(self, data):
        """写入数据到InfluxDB"""
        if self.write_api is None:
            logger.warning("InfluxDB未连接")
            return

        try:
            # 创建数据点
            point = Point("sensor_reading") \
                .tag("device_id", data.get('device_id', 'unknown')) \
                .time(datetime.fromtimestamp(data.get('t', time.time())))

            # 添加字段(必须有值)
            if data.get('T') is not None:
                point = point.field("temperature", float(data['T']))
            if data.get('H') is not None:
                point = point.field("humidity", float(data['H']))
            if data.get('P') is not None:
                point = point.field("pressure", float(data['P']))
            if data.get('PM25') is not None:
                point = point.field("pm25", int(data['PM25']))
            if data.get('PM10') is not None:
                point = point.field("pm10", int(data['PM10']))

            # 写入数据库
            self.write_api.write(
                bucket=self.influx_bucket,
                org=self.influx_org,
                record=point
            )

            logger.info("数据已写入InfluxDB")

        except Exception as e:
            logger.error(f"InfluxDB写入错误: {e}")
            self.error_count += 1

    def connect_influxdb(self):
        """连接InfluxDB"""
        try:
            self.influx_client = InfluxDBClient(
                url=self.influx_url,
                token=self.influx_token,
                org=self.influx_org
            )
            self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)

            # 测试连接
            health = self.influx_client.health()
            logger.info(f"InfluxDB连接成功: {health.status}")

            return True

        except Exception as e:
            logger.error(f"InfluxDB连接失败: {e}")
            return False

    def start(self):
        """启动MQTT订阅器"""
        logger.info(f"连接MQTT Broker: {self.mqtt_broker}:{self.mqtt_port}")

        # 创建MQTT客户端
        client = mqtt.Client(client_id=self.mqtt_client_id)
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        try:
            # 连接Broker
            client.connect(self.mqtt_broker, self.mqtt_port, 60)

            # 启动循环
            client.loop_forever()

        except KeyboardInterrupt:
            logger.info("用户中断,停止订阅器")
            self.stop(client)
        except Exception as e:
            logger.error(f"运行错误: {e}")
            self.stop(client)

    def stop(self, client):
        """停止订阅器"""
        logger.info("停止订阅器...")
        client.disconnect()

        if self.influx_client:
            self.influx_client.close()

        # 打印统计信息
        elapsed = time.time() - self.start_time
        rate = self.message_count / elapsed if elapsed > 0 else 0

        logger.info("=" * 50)
        logger.info("运行统计:")
        logger.info(f"  运行时间: {elapsed:.1f}秒")
        logger.info(f"  接收消息: {self.message_count}条")
        logger.info(f"  错误次数: {self.error_count}次")
        logger.info(f"  消息速率: {rate:.2f}条/秒")
        logger.info("=" * 50)


def load_config(config_file='config.yaml'):
    """加载配置文件"""
    try:
        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning(f"配置文件不存在: {config_file},使用默认配置")
        return {
            'mqtt': {
                'broker': 'broker.emqx.io',
                'port': 1883,
                'topic_sensors': 'home/airbutler/sensors',
                'client_id': 'server_subscriber'
            },
            'influxdb': {
                'url': 'http://localhost:8086',
                'token': '',
                'org': 'airbutler',
                'bucket': 'sensors'
            }
        }
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        return None


def main():
    """主程序入口"""
    # 加载配置
    config = load_config()
    if config is None:
        return

    # 创建桥接器
    bridge = MQTTInfluxDBBridge(config)

    # 连接InfluxDB
    if not bridge.connect_influxdb():
        logger.error("无法连接InfluxDB,程序退出")
        return

    # 启动MQTT订阅
    bridge.start()


if __name__ == "__main__":
    main()
