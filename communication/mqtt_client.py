
"""
communication/mqtt_client.py - MQTT 客戶端管理 (Debug Version)
增加 set_callback 方法，並在收到訊息時強制列印 Log
"""

import uasyncio
from mqtt_as import MQTTClient, config as mqtt_config

class MqttManager:
    def __init__(self, ssid, password, broker='broker.emqx.io'):
        self.ssid = ssid
        self.password = password
        self.broker = broker
        
        # MQTT 配置
        mqtt_config['ssid'] = ssid
        mqtt_config['wifi_pw'] = password
        mqtt_config['server'] = broker
        mqtt_config['subs_cb'] = self.on_message       # 預設回調指向自己的 on_message
        mqtt_config['connect_coro'] = self.on_connected
        
        self._connected = False
        self._connected_event = uasyncio.Event()
        
        # 外部注入的處理函式 (Router)
        self._external_handler = None
        
        self.client = MQTTClient(mqtt_config)
        print("[MQTT] 客戶端已初始化")
    
    def set_callback(self, handler):
        """設定外部訊息處理函式 (例如 Router.dispatch)"""
        self._external_handler = handler

    async def connect(self):
        try:
            print(f"[MQTT] 嘗試連線到 {self.broker}...")
            await self.client.connect()
            # 等待連線狀態確認
            await uasyncio.sleep(1)
            return True
        except Exception as e:
            print(f"[MQTT] 連線失敗: {e}")
            return False

    async def wait_connected(self):
        await self._connected_event.wait()
        return True

    async def publish(self, topic, message, qos=0):
        try:
            if isinstance(topic, str): topic = topic.encode()
            if isinstance(message, str): message = message.encode()
            await self.client.publish(topic, message, qos=qos)
            print(f"[MQTT Pub] 已發送 -> {topic.decode()}: {message.decode()}")
            return True
        except Exception as e:
            print(f"[MQTT Pub] 發送失敗: {e}")
            return False

    async def subscribe(self, topic, qos=0):
        try:
            if isinstance(topic, str): topic = topic.encode()
            await self.client.subscribe(topic, qos=qos)
            print(f"[MQTT] 已訂閱: {topic.decode()}")
            return True
        except Exception as e:
            print(f"[MQTT] 訂閱失敗: {e}")
            return False

    async def on_connected(self, client):
        self._connected = True
        self._connected_event.set()
        print("[MQTT] 已連線成功 (on_connected)")

    async def on_message(self, *args):
        """
        絕對防禦版的訊息接收函數
        """
        try:
            print(f"\n[Debug RAW] 收到原始參數: {args}")
            
            # 1. 動態解析參數 (解決參數數量不一致問題)
            topic = args[0]
            msg = args[1]
            # 如果有第3個參數就用，沒有就預設 False
            retained = args[2] if len(args) > 2 else False
            
            # 2. 安全解碼 (解決 Encoding 崩潰問題)
            topic_str = "Decode_Error"
            msg_str = "Decode_Error"
            
            try:
                # 嘗試解碼，如果失敗則保留原始 Bytes 的字串表示
                topic_str = topic.decode('utf-8') if isinstance(topic, bytes) else str(topic)
                msg_str = msg.decode('utf-8') if isinstance(msg, bytes) else str(msg)
            except Exception as e:
                print(f"[Encoding Error] 解碼失敗: {e}")
                topic_str = str(topic) # 強制轉成 byte string 顯示 b'...'
                msg_str = str(msg)

            print(f"[MQTT Safe] Topic: {topic_str}")
            print(f"[MQTT Safe] Msg: {msg_str}")
            
            # 3. 轉交給 Router
            if self._external_handler:
                # 注意：這裡我們傳遞處理過的參數，或者根據 Router 的定義傳遞
                # 為了保險，這裡我們傳遞原始 args 的前三個 (模擬標準行為)
                await self._external_handler(topic, msg, retained)
                
        except Exception as e:
            print(f"[Critical] on_message 內部發生嚴重錯誤: {e}")
            import sys
            sys.print_exception(e)
