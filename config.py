
"""
config.py - 全域配置文件 (Refactored for Alarm System)
整合 mid_fir.py 腳位與 MQTT CRUD 設定
"""

# ==================== 硬體腳位配置 (基於 mid_fir.py) ====================

# 按鈕 (Input + PullUp)
BUTTON_STOP_PIN = 17    # 原 button
BUTTON_NEXT_PIN = 21    # 原 button_next

# 蜂鳴器 (PWM)
BUZZER_PIN = 6

# 感測器
DHT11_PIN = 18

# I2C 配置 (OLED)
I2C_ID = 0
I2C_SCL_PIN = 7
I2C_SDA_PIN = 5
OLED_WIDTH = 128
OLED_HEIGHT = 64

# ==================== 系統參數 ====================

# 按鈕參數 (修正補上)
BUTTON_DEBOUNCE_MS = 20         # 按鈕穩定判定時間
BUTTON_POLL_INTERVAL_MS = 30    # 按鈕輪詢間隔

# 鬧鐘設定
ALARM_FILE = "alarms.json"
SNOOZE_MINUTES = 5
MAX_RING_TIME = 60  # 秒

# DHT11 量測間隔
DHT11_POLL_INTERVAL_SEC = 10

# OLED 更新間隔
OLED_UPDATE_INTERVAL_SEC = 0.5

# ==================== WiFi 配置 ====================

# 已知 WiFi 網路清單
WIFI_PROFILES = {
    #'CSIE406_DEV': '406406406',
    '444': 'obaba664',
    'YourSSID': 'YourPassword'
}

# AP 模式設定 (當連線失敗時)
AP_SSID = "ESP32_Alarm_Setup"
AP_PASSWORD = "password123"

# 時區設定 (UTC+8)
TIMEZONE_OFFSET_SEC = 8 * 3600

# ==================== MQTT 配置 ====================
import random

# MQTT_BROKER = 'broker.emqx.io'
MQTT_BROKER = 'test.mosquitto.org'

MQTT_PORT = 1883
# Client ID
# DEVICE_ID = 'M1324001_AlarmClock_V2'
DEVICE_ID = f'M1324001_Alarm_{random.randint(1000, 9999)}'

# Topic 前綴
# TOPIC_PREFIX = f"nuu/csie/{DEVICE_ID}"
TOPIC_PREFIX = f"nuu/csie/{DEVICE_ID}"

# 定義 CRUD Topics
# 使用者透過這些 Topic 發送指令
MQTT_TOPICS = {
    'subscribe_wildcard': f"{TOPIC_PREFIX}/#",  # 訂閱所有指令
    'alarm_add': f"{TOPIC_PREFIX}/alarm_add",       # Payload: JSON {"h": 8, "m": 30, "days": [...]}
    'alarm_del': f"{TOPIC_PREFIX}/alarm_delete",    # Payload: JSON {"index": 0}
    'alarm_list': f"{TOPIC_PREFIX}/alarm_list",     # Payload: 空 (觸發回傳)
    'alarm_response': f"{TOPIC_PREFIX}/response",   # 裝置回傳結果
    'status_pub': f"{TOPIC_PREFIX}/status",         # 定期發送溫濕度與狀態
}

# ==================== 字體配置 ====================
# 若不使用外部字型，將自動使用內建 8x8
FONT_PATH = './lib/fonts/fusion_bdf.12'
