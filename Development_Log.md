# HW2 Development Log (氣溫預報 Web App)

## HW2-1 獲取天氣預報資料 & HW2-2 分析並提取氣溫資料
* **執行目標**：使用 CWA API (`F-A0010-001`) 獲取台灣北、中、南、東北、東部及東南部地區一週天氣資料，並以 JSON 解析提取最高與最低氣溫。
* **實作細節**：
  * 在 `fetch_data.py` 中，使用 Python 的 `requests` 套件發送 HTTP GET 請求。
  * 因為 CWA 資料開放平台的檔案型 API (fileapi) 有時會有 SSL 憑證驗證的問題，所以我實作了 `verify=False` 並使用了 `urllib3.disable_warnings` 進行安全忽略，確保程式能順利執行。
  * 透過環境變數 `dotenv` 載入 `CWA_API_KEY`，符合「了解原理並意識到資安問題」的標準，避免 Token 寫死在程式碼中外洩。
  * **JSON 解析分析**：分析了回傳資料的階層，深入 `.get("cwaopendata").get("resources").get("resource").get("data").get("agrWeatherForecasts").get("weatherForecasts").get("location")` 提取出每天的 `MinT` 和 `MaxT` 數值。
  * 將資料萃取後，以 Pandas DataFrame 儲存並輸出為 `weather_data.csv`，方便後續觀察。

## HW2-3 將氣溫資料儲存到 SQLite3 資料庫
* **執行目標**：將整理好的氣溫資料寫入名為 `data.db` 的 SQLite3 資料庫中的 `TemperatureForecasts` Table。
* **實作細節**：
  * 在 `fetch_data.py` 的後半段，利用內建的 `sqlite3` 套件與 `data.db` 建立連線。
  * 設計了符合規定的 Table Schema，包含：主鍵 (`id` INTEGER PRIMARY KEY AUTOINCREMENT)、地區名稱 (`regionName` TEXT)、時間 (`dataDate` TEXT)、最低氣溫 (`mint` INTEGER)、最高氣溫 (`maxt` INTEGER)。
  * **資料驗證**：程式最後會自動執行 SELECT 語法，印出「所有存入的地區名稱」以及「中部地區的氣溫資料」，確保資料正確寫入且可被查詢。

## HW2-4 實作氣溫預報 Web App
* **執行目標**：使用 Streamlit 實作一個視覺化的 Web App，包含下拉選單與圖表，且必須從 SQLite3 讀取資料。
* **實作細節**：
  * **資料連結**：在 `app.py` 中撰寫 `load_data()` 函式，直接執行 SQL `SELECT regionName, dataDate, mint as MinT, maxt as MaxT FROM TemperatureForecasts`，將資料轉換為 DataFrame 提供給前端使用。
  * **版面設計**：採用 Streamlit 的 `st.columns([1, 1])` 進行左右雙視窗佈局，並透過 Markdown 與 CSS 提升深色模式的美觀度。
  * **左側 (地圖視覺化)**：整合 `folium` 與 `streamlit-folium` 套件。結合地區的經緯度與一個**日期下拉選單**，將各區的平均氣溫計算出來並用動態圓點標示於地圖上（低於20度為藍色，20-25為綠色，25-30為橘色，高於30為紅色）。
  * **右側 (數據圖表與表格)**：實作**地區下拉選單** (Select a Region)。使用者選擇地區後，會同步渲染該地區未來一週氣溫的「折線圖 (`st.line_chart`)」與「資料表格 (`st.dataframe`)」。

## 自我評估總結
✅ 成功串接 CWA API (F-A0010-001) 並正確解析 JSON 結構。
✅ 成功透過 `.env` 隱藏 API Token 實踐資安觀念。
✅ 成功建置 SQLite3 DB 並支援完整的氣溫紀錄表。
✅ 成功使用 Streamlit 建構美觀、雙欄位佈局且具互動性下拉選單的 Web 應用。
✅ 準備好上傳 GitHub 並可無縫部署至 Streamlit Community Cloud。
