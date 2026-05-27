# wifi_manager.py - WiFi管理模块
# WiFi Manager Module

from machine import Pin
import network
import time


class WiFiManager:
    """WiFi连接管理器"""

    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.connected = False
        self.last_check = 0
        self.reconnect_interval = 30  # 30秒检查一次

    def connect(self, timeout=10):
        """连接WiFi"""
        if self.wlan.isconnected():
            self.connected = True
            return True

        print(f"连接到 {self.ssid}...")
        self.wlan.connect(self.ssid, self.password)

        start = time.time()
        while not self.wlan.isconnected():
            if time.time() - start > timeout:
                print("连接超时!")
                self.connected = False
                return False
            time.sleep(0.5)
            print(".", end="")

        print("\n连接成功!")
        self._print_config()
        self.connected = True
        return True

    def _print_config(self):
        """打印网络配置"""
        ifconfig = self.wlan.ifconfig()
        print(f"IP地址: {ifconfig[0]}")
        print(f"子网掩码: {ifconfig[1]}")
        print(f"网关: {ifconfig[2]}")
        print(f"DNS: {ifconfig[3]}")

    def disconnect(self):
        """断开连接"""
        if self.wlan.isconnected():
            self.wlan.disconnect()
            self.connected = False
            print("WiFi已断开")

    def check_connection(self):
        """检查连接状态,必要时重连"""
        if not self.wlan.isconnected():
            now = time.time()
            if now - self.last_check > self.reconnect_interval:
                self.last_check = now
                return self.connect()
        return True

    def is_connected(self):
        """是否已连接"""
        return self.wlan.isconnected()

    def get_ip(self):
        """获取IP地址"""
        if self.wlan.isconnected():
            return self.wlan.ifconfig()[0]
        return None

    def get_rssi(self):
        """获取信号强度"""
        if self.wlan.isconnected():
            return self.wlan.status('rssi')
        return None
