# ESP32 智慧鬧鐘系統 (Asyncio AIoT Alarm Clock)

本專案是一款基於 **MicroPython** 開發的智慧鬧鐘系統，專為 **資工系大學部學生** 設計，用於展示以下核心能力的整合應用：

* 非同步程式設計（`uasyncio`）
* 物件導向封裝（OOP）
* 多通道通訊（**MQTT** 與 **Web**）

系統可同時處理鬧鐘邏輯、感測器資料、OLED 顯示與網路通訊，具備良好的教學示範與實務價值。

---

## 🚀 核心特色

### 1. 非同步多工處理

* 採用 `uasyncio` 作為核心排程器
* 同時執行：

  * 鬧鐘時間檢查
  * OLED 畫面更新
  * Web Server 請求處理
  * MQTT 指令監聽
* 避免阻塞，系統運作流暢不卡頓

### 2. 雙軌控制架構

* **本地 Web 控制介面**：透過瀏覽器管理鬧鐘
* **遠端 MQTT 指令集**：支援自動化或跨裝置控制
* 兩種通道會同步更新鬧鐘狀態

### 3. 資料持久化設計

* 使用 `alarms.json` 儲存鬧鐘設定
* 裝置重啟或斷電後設定不遺失

### 4. 環境監控

* 整合 **DHT11 溫濕度感測器**
* 即時顯示於 **OLED (128x64)** 螢幕

### 5. 路由裝飾器設計（MQTT）

* MQTT 指令採用類似 Flask 的路由風格：`@router.route()`
* 提升程式可讀性、模組化程度與擴充性

---

## 🛠 硬體配置（Pin Map）

> 所有硬體腳位皆集中定義於 `config.py`，方便後續維護與修改。

| 組件            | GPIO            | 功能說明       |
| ------------- | --------------- | ---------- |
| Buzzer        | 6               | 鬧鐘響鈴（PWM）  |
| DHT11         | 18              | 溫濕度數據採集    |
| Button (Stop) | 17              | 停止響鈴按鈕     |
| Button (Next) | 21              | OLED 畫面切換  |
| OLED (I2C)    | SCL: 7 / SDA: 5 | 128x64 顯示器 |

---

## 📂 專案檔案架構

```text
.
├── main.py                  # 系統入口，初始化硬體並啟動所有非同步任務
├── config.py                # 全域設定（WiFi、MQTT、GPIO 腳位）
├── tasks.py                 # 非同步任務定義（顯示、鬧鐘檢查、MQTT 路由）
├── alarms.json              # 鬧鐘設定檔（自動產生）
├── hardware/                # 硬體抽象層（HAL）
│   ├── buzzer.py
│   ├── buttons.py
│   ├── dht_sensor.py
│   └── oled.py
├── communication/           # 通訊模組
│   ├── wifi.py
│   ├── mqtt_client.py
│   └── web_server.py
└── utils/
    └── alarm_manager.py     # 鬧鐘 CRUD 核心邏輯
```

---

## 🌐 通訊介面說明

### 1. Web 介面

* 連線至 ESP32 的 IP 位址（預設 **Port 80**）
* 透過視覺化網頁：

  * 新增鬧鐘
  * 刪除鬧鐘
  * 即時同步狀態

### 2. MQTT 指令集

* 訂閱 Topic：

```text
nuu/csie/{DEVICE_ID}/#
```

#### 新增鬧鐘

```text
Topic: .../alarm_add
Payload:
{
  "h": 8,
  "m": 30,
  "days": ["Mon", "Tue"]
}
```

#### 刪除鬧鐘

```text
Topic: .../alarm_delete
Payload:
{
  "index": 0
}
```

#### 查詢鬧鐘列表

```text
Topic: .../alarm_list
```

---

## ⚠️ 開發者筆記：MQTT 除錯重點（必讀）

在 IoT 專案中，常見情況為 **MQTTX 顯示已連線，但 ESP32 卻收不到訊息**。請依序檢查以下項目：

### 1. Client ID 唯一性

* MQTT Broker 會自動中斷相同 Client ID 的連線
* 請確認 `config.py` 中的 `DEVICE_ID` 為全域唯一

### 2. Topic 嚴格比對

* 注意是否有多餘的 `/` 或空白字元
* 本系統所有 Topic 皆由 `config.py` 中的 Prefix 統一定義

### 3. JSON 格式正確性

* Payload 必須為 **標準 JSON 格式**
* 系統內建 **[Debug RAW]** 記錄功能，可查看原始封包內容

### 4. 非同步阻塞問題

* **禁止使用 `time.sleep()`**
* 若誤用同步延遲，將導致 MQTT 與網路底層無法接收資料
* 請一律使用：

```python
await uasyncio.sleep(seconds)
```

---

## 🛠 快速上手指南

1. 確認 ESP32 已燒錄 **MicroPython 韌體**
2. 編輯 `config.py`

   * 設定 `WIFI_PROFILES`
   * 設定 `MQTT_BROKER` 與 `DEVICE_ID`
3. 上傳所有 `.py` 檔案與必要的 `lib` 資料夾至 ESP32
4. 執行 `main.py`
5. 觀察 REPL 終端機輸出是否正常
6. 使用：

   * 瀏覽器（Web UI）或
   * MQTTX
     進行功能測試

---

## 📌 適用情境

* 資工系「物聯網 / 嵌入式系統 / 非同步程式設計」課程展示
* AIoT 系統架構實作範例
* MicroPython + uasyncio 教學專案

---

## 📄 授權說明

本專案適用於教學與研究用途，可自由修改與延伸應用。
