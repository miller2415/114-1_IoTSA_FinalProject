
"""
main.py - 智慧鬧鐘系統主程式 (Refactored)
整合 MQTT (Decorator Pattern), Web Server, Hardware Tasks
"""

import uasyncio
import config
from communication.wifi import connect_wifi, sync_time
from communication.mqtt_client import MqttManager
from communication.web_server import WebServer
from utils.alarm_manager import AlarmManager

# 硬體
from hardware.display import OledDisplay
from hardware.buzzer import Buzzer
from hardware.button import Button
from hardware.sensors import Dht11Sensor

# 任務
import tasks
# import config
# print(f"Topic: [{config.TOPIC_PREFIX}]")
# print(f"Length: {len(config.TOPIC_PREFIX)}")

async def main():
    print("\n=== ESP32 Smart Alarm System Starting ===\n")

    # 1. 硬體初始化
    print("[Init] 初始化硬體...")
    oled = OledDisplay()
    buzzer = Buzzer(config.BUZZER_PIN)
    btn_stop = Button(config.BUTTON_STOP_PIN)
    btn_next = Button(config.BUTTON_NEXT_PIN)
    dht_sensor = Dht11Sensor() # 內部已讀取 Pin 18
    
    # 2. 資料管理器初始化
    alarm_mgr = AlarmManager()
    
    # 3. 網路連線
    ssid, pwd = await connect_wifi() # 使用既有的 wifi.py 邏輯
    await sync_time()                # 同步 NTP
    
    # 更新全域狀態 IP (給 OLED 顯示用)
    try:
        import network
        sta = network.WLAN(network.STA_IF)
        tasks.sys_state["ip"] = sta.ifconfig()[0]
    except:
        tasks.sys_state["ip"] = "No WiFi"

    # 4. 服務初始化
    # MQTT
    mqtt_manager = MqttManager(ssid, pwd, broker=config.MQTT_BROKER)
    
    # [修正點] 這裡原本誤寫為 asyncio.create_task，修正為 uasyncio
    uasyncio.create_task(mqtt_manager.connect()) # 非同步連線

    # Web Server
    web_server = WebServer(alarm_mgr)
    
    print("[Init] 啟動任務協程...")
    
    try:
        await uasyncio.gather(
            # 硬體任務
            #tasks.sensor_task(dht_sensor),
            tasks.display_task(oled, alarm_mgr, btn_next),
            tasks.alarm_check_task(alarm_mgr, buzzer, btn_stop),
            
            # 通訊任務
            tasks.mqtt_dispatch_task(mqtt_manager, alarm_mgr), # 包含 CRUD Router
            web_server.start() # 啟動 Web Server
        )
    except KeyboardInterrupt:
        print("使用者中斷")
    except Exception as e:
        print(f"主程式錯誤: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("系統關閉")

if __name__ == '__main__':
    uasyncio.run(main())
    