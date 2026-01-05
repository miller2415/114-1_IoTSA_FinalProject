
"""
hardware/sensors.py - 感測器模組 (Refactored for Alarm System)
只保留 DHT11 溫濕度感測器，移除 mid_fir.py 用不到的光感測器
"""

from machine import Pin
import dht
import config

class Dht11Sensor:
    """DHT11 溫濕度感測器控制類別"""
    
    def __init__(self):
        """初始化 DHT11 感測器"""
        # 使用 config.py 中的腳位定義
        self.sensor = dht.DHT11(Pin(config.DHT11_PIN))
        self.temperature = 0.0
        self.humidity = 0.0
    
    def measure(self):
        """
        執行一次量測
        返回: (temperature, humidity) 元組，或在異常時返回 None
        """
        try:
            self.sensor.measure()
            self.temperature = self.sensor.temperature()
            self.humidity = self.sensor.humidity()
            return (self.temperature, self.humidity)
        except Exception as e:
            print(f"[DHT11] 量測錯誤: {e}")
            # 發生錯誤時保持舊值或回傳 None，視需求而定
            # 這裡回傳 None 讓呼叫端知道失敗
            return None
    
    def get_data(self):
        """取得最後一次成功量測的資料"""
        return (self.temperature, self.humidity)
    
    def __str__(self):
        return f"溫度: {self.temperature}℃, 濕度: {self.humidity}%"

