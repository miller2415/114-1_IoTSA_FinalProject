"""
hardware/display.py - OLED 顯示模組
提供基礎繪圖介面，並暴露原始 framebuf 以供複雜 UI 使用
"""

from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import config

class OledDisplay:
    def __init__(self):
        self._i2c = I2C(config.I2C_ID, scl=Pin(config.I2C_SCL_PIN), sda=Pin(config.I2C_SDA_PIN))
        self._oled = SSD1306_I2C(config.OLED_WIDTH, config.OLED_HEIGHT, self._i2c)
        print("[OLED] 初始化完成")

    def clear(self):
        self._oled.fill(0)

    def show(self):
        self._oled.show()

    def text(self, msg, x, y):
        self._oled.text(str(msg), x, y)

    def get_raw_oled(self):
        """取得原始 SSD1306 物件以進行進階繪圖"""
        return self._oled