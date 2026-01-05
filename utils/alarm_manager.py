
"""
utils/alarm_manager.py - 鬧鐘資料管理員
負責 alarms.json 的 CRUD 操作，供 Web 與 MQTT 共用
"""

import ujson
import os
import config

class AlarmManager:
    def __init__(self, filepath=config.ALARM_FILE):
        self.filepath = filepath
        self.alarms = []
        self.load()

    def load(self):
        """從檔案讀取鬧鐘"""
        try:
            with open(self.filepath, "r") as f:
                self.alarms = ujson.load(f)
            print(f"[AlarmMgr] 載入 {len(self.alarms)} 個鬧鐘")
        except:
            self.alarms = []
            print("[AlarmMgr] 無設定檔或載入失敗，初始化為空")

    def save(self):
        """寫入鬧鐘到檔案"""
        try:
            with open(self.filepath, "w") as f:
                ujson.dump(self.alarms, f)
            print("[AlarmMgr] 鬧鐘設定已儲存")
        except Exception as e:
            print(f"[AlarmMgr] 儲存失敗: {e}")

    def add_alarm(self, hour, minute, weekdays=None, enabled=True):
        """
        新增鬧鐘
        weekdays: list of strings ["Mon", "Tue"...] 或 None (單次)
        """
        if weekdays is None:
            weekdays = []
        
        new_alarm = {
            "hour": int(hour),
            "minute": int(minute),
            "weekdays": weekdays,
            "enabled": enabled
        }
        self.alarms.append(new_alarm)
        self.save()
        return len(self.alarms) - 1

    def delete_alarm(self, index):
        """刪除指定索引的鬧鐘"""
        if 0 <= index < len(self.alarms):
            removed = self.alarms.pop(index)
            self.save()
            return removed
        return None

    def get_all(self):
        return self.alarms

    def disable_single_shot(self, index):
        """停用單次鬧鐘 (響鈴後呼叫)"""
        if 0 <= index < len(self.alarms):
            if not self.alarms[index].get("weekdays"):
                self.alarms[index]["enabled"] = False
                self.save()

