
"""
communication/mqtt_router.py - MQTT 訊息路由 (Debug Version)
"""

import ujson
import uasyncio

class MqttRouter:
    def __init__(self, mqtt_manager):
        self.mqtt = mqtt_manager
        self.routes = {} 

    def route(self, topic):
        if isinstance(topic, bytes):
            topic = topic.decode()
        def decorator(func):
            self.routes[topic] = func
            return func
        return decorator

    async def dispatch(self, topic, msg, retained):
        """
        處理訊息分發
        """
        # 注意：這裡的 topic/msg 可能已經被 MqttManager decode 過，也可能還是 bytes
        # 為了保險，我們再檢查一次
        
        topic_str = ""
        try:
            if hasattr(topic, 'decode'):
                topic_str = topic.decode()
            else:
                topic_str = str(topic)
        except:
            topic_str = str(topic)

        msg_str = ""
        try:
            if hasattr(msg, 'decode'):
                msg_str = msg.decode()
            else:
                msg_str = str(msg)
        except:
            msg_str = str(msg)
        
#         topic_str = topic.decode() if isinstance(topic, bytes) else topic
#         msg_str = msg.decode() if isinstance(msg, bytes) else msg
        
        print(f"[Router] 開始匹配路由: {topic_str}")

        payload = None
        try:
            payload = ujson.loads(msg_str)
        except:
            payload = msg_str 

        if topic_str in self.routes:
            try:
                print(f"[Router] 命中規則! 執行對應函式...")
                handler = self.routes[topic_str]
                await handler(payload)
            except Exception as e:
                print(f"[Router] 執行函式失敗: {e}")
                import sys
                sys.print_exception(e)
        else:
            print(f"[Router] 沒找到對應規則，現有規則如下:")
            for r in self.routes:
                print(f" - {r}")
