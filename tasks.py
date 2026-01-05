
"""
tasks.py - 任務協程
整合 MQTT 路由裝飾器、OLED 顯示、鬧鐘邏輯與感測器
"""

import uasyncio
import time
import config
import ujson

# 引入通訊與工具
from communication.wifi import get_current_time
from communication.mqtt_router import MqttRouter

# 引入硬體
from hardware.display import OledDisplay
from hardware.buzzer import Buzzer
from hardware.button import Button
from hardware.sensors import Dht11Sensor

# 全域狀態 (用於 UI 顯示)
sys_state = {
    "ip": "0.0.0.0",
    "temp": 0,
    "humi": 0,
    "alarm_idx": 0  # 顯示第幾個鬧鐘
}

# ==================== 任務 1: 感測器讀取 ====================
async def sensor_task(dht_sensor):
    while True:
        res = dht_sensor.measure()
        if res:
            sys_state["temp"], sys_state["humi"] = res
        await uasyncio.sleep(config.DHT11_POLL_INTERVAL_SEC)

# ==================== 任務 2: OLED UI 顯示 ====================
async def display_task(oled_display, alarm_mgr, btn_next):
    oled = oled_display.get_raw_oled()
    while True:
        if btn_next.pin.value() == 0:
            await btn_next.debounce_read()
            alarms = alarm_mgr.get_all()
            if alarms:
                sys_state["alarm_idx"] = (sys_state["alarm_idx"] + 1) % len(alarms)
            await btn_next.wait_release()
        
        current_time = get_current_time()
        try:
            date_s, _, time_s = current_time
        except:
            date_s, time_s = "--/--", "--:--"
            
        alarms = alarm_mgr.get_all()
        oled.fill(0)
        oled.text(str(sys_state["ip"]), 0, 0)
        oled.text(date_s, 0, 10)
        oled.text(time_s[:8], 0, 20)
        oled.text(f"T:{sys_state['temp']}C H:{sys_state['humi']}%", 0, 30)
        
        if alarms:
            if sys_state["alarm_idx"] >= len(alarms): sys_state["alarm_idx"] = 0
            a = alarms[sys_state["alarm_idx"]]
            oled.text(f"Alarm:{a['hour']:02d}:{a['minute']:02d}", 0, 45)
            days = ",".join(a.get("weekdays", [])) or "Once"
            oled.text(days[:16], 0, 55)
        else:
            oled.text("No Alarms", 0, 48)
            
        oled.show()
        await uasyncio.sleep(config.OLED_UPDATE_INTERVAL_SEC)


# ==================== 任務 3: 鬧鐘偵測與響鈴 ====================
async def alarm_check_task(alarm_mgr, buzzer, btn_stop):
    """每秒檢查一次鬧鐘"""
    weekdays_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    while True:
        # 取得系統時間 (tuple: year, month, mday, hour, minute, second, weekday, yearday)
        # 注意：get_current_time 返回的是字串，這裡需要數值，使用 time.localtime
        now = time.localtime() 
        h, m, s, wd = now[3], now[4], now[5], now[6]
        today_str = weekdays_map[wd]

        # 每一秒檢查所有鬧鐘
        if s == 0: # 只在每分鐘的第0秒觸發
            alarms = alarm_mgr.get_all()
            for idx, a in enumerate(alarms):
                if not a.get("enabled", True):
                    continue
                
                # 檢查時間
                if a["hour"] == h and a["minute"] == m:
                    # 檢查星期
                    days = a.get("weekdays", [])
                    if not days or today_str in days:
                        print(f"[Alarm] 鬧鐘響起! {h}:{m}")
                        
                        # 觸發響鈴
                        await _ring_alarm(buzzer, btn_stop)
                        
                        # 如果是單次鬧鐘，停用它
                        if not days:
                            alarm_mgr.disable_single_shot(idx)
        
        await uasyncio.sleep(1)

async def _ring_alarm(buzzer, btn_stop):
    """響鈴處理邏輯：播放音樂直到按下停止或超時"""
    start_time = time.time()
    
    # 啟動音樂任務
    play_task = uasyncio.create_task(buzzer.play_song())
    
    print(">>> 鬧鐘響鈴中，按按鈕停止...")
    
    while True:
        # 1. 檢查停止按鈕
        if btn_stop.pin.value() == 0:
            print("[Alarm] 使用者手動停止")
            buzzer.stop()
            break
        
        # 2. 檢查超時
        if time.time() - start_time > config.MAX_RING_TIME:
            print("[Alarm] 響鈴超時自動停止")
            buzzer.stop()
            break
            
        await uasyncio.sleep_ms(100)
        
        # 如果音樂播完了（小星星播完），重新播放
        if not buzzer.is_playing and not buzzer._stop_flag:
             play_task = uasyncio.create_task(buzzer.play_song())

    # 確保完全停止
    buzzer.stop()
    await uasyncio.sleep(2) # 避免按鈕誤觸


# ==================== 任務 4: MQTT 訂閱處理 (使用 Decorator) ====================
async def mqtt_dispatch_task(mqtt_manager, alarm_mgr):
    """設定 MQTT 路由並開始監聽"""
    
    router = MqttRouter(mqtt_manager)

    # --- 定義 MQTT 路由 ---
    
    @router.route(config.MQTT_TOPICS['alarm_add'])
    async def handle_add(payload):
        print(f"[MQTT CMD] 收到新增指令: {payload}")
        if isinstance(payload, dict):
            h = payload.get("h")
            m = payload.get("m")
            days = payload.get("days", [])
            if h is not None and m is not None:
                idx = alarm_mgr.add_alarm(h, m, days)
                await _reply(f"Added alarm at {h}:{m}, index={idx}")

    @router.route(config.MQTT_TOPICS['alarm_del'])
    async def handle_del(payload):
        print(f"[MQTT CMD] 收到刪除指令: {payload}")
        if isinstance(payload, dict):
            idx = payload.get("index")
            if idx is not None:
                removed = alarm_mgr.delete_alarm(idx)
                res = "Deleted" if removed else "Index Error"
                await _reply(f"Delete result: {res}")

    @router.route(config.MQTT_TOPICS['alarm_list'])
    async def handle_list(payload):
        print("[MQTT CMD] 收到查詢列表指令")
        alarms = alarm_mgr.get_all()
        json_str = ujson.dumps(alarms)
        await mqtt_manager.publish(config.MQTT_TOPICS['alarm_response'], json_str)

    async def _reply(msg):
        await mqtt_manager.publish(config.MQTT_TOPICS['alarm_response'], msg)

    # --- 啟動連線與訂閱 ---
    print("[Task] 等待 MQTT 連線...")
    await mqtt_manager.wait_connected()
    
    mqtt_manager.set_callback(router.dispatch)
    
    # 1. 訂閱
    target_topic = config.MQTT_TOPICS['subscribe_wildcard'] # 這裡通常是 ".../#"
    await mqtt_manager.subscribe(target_topic)
    print(f"[Task] 已訂閱: {target_topic}")
#     await mqtt_manager.subscribe("test/debug/123") 
#     print("[Debug] 強制訂閱: test/debug/123")
    
    # 2. 【新增】自我測試：發送一條訊息給自己
    # 使用一個絕對簡單、不會打錯的 topic，例如測試 topic 的子路徑
    test_topic = f"{config.TOPIC_PREFIX}/self_test"
    print(f"[Debug] 嘗試發送測試訊息到: {test_topic}")
    await mqtt_manager.publish(test_topic, '{"msg": "Hello ESP32"}')

    while True:
        await uasyncio.sleep(10)
