
"""
communication/web_server.py - 鬧鐘 Web 介面與 REST API
"""

import uasyncio
import ujson

class WebServer:
    def __init__(self, alarm_manager):
        self.alarm_mgr = alarm_manager
        self.weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    async def handle_request(self, reader, writer):
        try:
            request = await reader.read(1024)
            request = request.decode("utf-8")
            
            # 簡單解析 (只取第一行 GET /path HTTP/1.1)
            first_line = request.split("\r\n")[0]
            if not first_line:
                writer.close()
                return
                
            method, path, _ = first_line.split(" ")
            
            response_body = ""
            status = "200 OK"
            content_type = "text/html; charset=utf-8"

            # === API 路由 ===
            if path.startswith("/add?"):
                # 簡易 GET based API: /add?hour=8&minute=30&Mon=on...
                self._handle_add(path)
                response_body = "<meta http-equiv='refresh' content='0; url=/'/>"
            
            elif path.startswith("/delete?"):
                self._handle_delete(path)
                response_body = "<meta http-equiv='refresh' content='0; url=/'/>"

            elif path == "/api/alarms":
                # 真 JSON API
                content_type = "application/json"
                response_body = ujson.dumps(self.alarm_mgr.get_all())

            # === 網頁 UI ===
            else:
                response_body = self._render_html()

            # 回傳回應
            writer.write(f"HTTP/1.0 {status}\r\nContent-Type: {content_type}\r\n\r\n".encode("utf-8"))
            writer.write(response_body.encode("utf-8"))
            await writer.drain()
            await writer.aclose()
            
        except Exception as e:
            print(f"[Web] 處理錯誤: {e}")
            writer.close()

    def _handle_add(self, path):
        try:
            params = path.split("?")[1]
            kv = {k:v for k,v in [p.split("=") for p in params.split("&")]}
            hour = int(kv.get("hour", 0))
            minute = int(kv.get("minute", 0))
            days = [d for d in self.weekdays if kv.get(d) == "on"]
            self.alarm_mgr.add_alarm(hour, minute, days)
        except Exception as e:
            print(f"[Web] Add Error: {e}")

    def _handle_delete(self, path):
        try:
            params = path.split("?")[1]
            kv = {k:v for k,v in [p.split("=") for p in params.split("&")]}
            idx = int(kv.get("id", -1))
            self.alarm_mgr.delete_alarm(idx)
        except Exception as e:
            print(f"[Web] Del Error: {e}")

    def _render_html(self):
        # 這裡放入原有的 HTML 模板字串 (為節省篇幅，簡化引用)
        alarms = self.alarm_mgr.get_all()
        
        # 構建鬧鐘列表 HTML
        list_html = ""
        for i, a in enumerate(alarms):
            days = ",".join(a.get("weekdays", [])) or "每天"
            list_html += f'<li>{a["hour"]:02d}:{a["minute"]:02d} ({days}) <a class="delete" href="/delete?id={i}">刪除</a></li>'

        hour_opts = "".join([f'<option value="{i}">{i:02d}</option>' for i in range(24)])
        min_opts = "".join([f'<option value="{i}">{i:02d}</option>' for i in range(60)])
        
        day_checks = ""
        for d in self.weekdays:
            day_checks += f'<label class="day-btn"><input type="checkbox" name="{d}"><span>{d}</span></label>'

        # 回傳完整 HTML (參照 mid_fir.py 的 CSS)
        return f"""
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ESP32 鬧鐘</title>
<style>
body {{ font-family: sans-serif; background:#f2f2f7; text-align:center; padding:10px; }}
form {{ background:#fff; padding:20px; border-radius:15px; margin-bottom:20px; }}
.picker select {{ font-size:20px; padding:5px; }}
.weekdays {{ display:flex; justify-content:space-between; margin:10px 0; }}
.day-btn span {{ display:inline-block; width:35px; height:35px; line-height:35px; background:#ddd; border-radius:50%; cursor:pointer; }}
.day-btn input:checked + span {{ background:#007aff; color:white; }}
.day-btn input {{ display:none; }}
ul {{ list-style:none; padding:0; }}
li {{ background:#fff; padding:10px; margin:5px 0; border-radius:10px; display:flex; justify-content:space-between; }}
a.delete {{ color:red; text-decoration:none; }}
button {{ width:100%; padding:10px; background:#007aff; color:white; border:none; border-radius:10px; font-size:16px; }}
</style>
</head>
<body>
<h2>ESP32 智慧鬧鐘</h2>
<form action="/add">
    <div class="picker">
        <select name="hour">{hour_opts}</select> : <select name="minute">{min_opts}</select>
    </div>
    <div class="weekdays">{day_checks}</div>
    <button type="submit">新增鬧鐘</button>
</form>
<ul>{list_html}</ul>
</body></html>
"""

    async def start(self):
        print("[Web] 啟動網頁伺服器...")
        server = await uasyncio.start_server(self.handle_request, "0.0.0.0", 80)
        return server

