# AI 智能輿情分析系統 (AI Sentiment Analysis System)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask-green.svg)
![AI](https://img.shields.io/badge/Model-Mistral%20AI-orange.svg)

這是一個基於 **Mistral AI** 大型語言模型開發的專業輿情分析工具。系統支援多種檔案格式匯入，能自動進行深度的情感分類、強度評分、核心議題提取及關鍵詞標籤生成。

## 核心特色

* **AI 深度分析**：利用 Mistral-7B/Large 模型進行分析，包含情感分類（正面/中立/負面）、1-10分情感強度、核心議題歸納及關鍵詞標籤。
* **強大資料載入能力**：支援 `TXT`、`JSON`、`CSV`、及 `Excel (xlsx/xls)` 檔案格式。
* **完整 Web 介面**：基於 Flask 構建，支援手動輸入文字分析與實體檔案上傳分析。
* **自動化報告與統計**：自動計算正負面評論比例，生成環圈圖顯示文本正負面比例、總數與統計摘要的完整報告。
  * 詳細分析結果則產出：
    - 情感分類（正面、中立、負面）
    - 情緒強度分數
    - 核心議題
    - 關鍵詞標籤
    - 輿情特徵說明
* **匯出功能**：支援將分析結果匯出為 `JSON` 報告或 `CSV` 資料表。

## 技術運用

* **核心引擎**: Mistral AI API (`mistralai`)
* **網頁框架**: Flask, Flask-CORS
* **數據處理**: Pandas, Openpyxl
* **中文處理**: Jieba 分詞

## 使用準備

### 1. 環境準備
確保已安裝 Python 3.8+，並取得 [Mistral AI API Key](https://console.mistral.ai/)。

### 2. 安裝依賴
```bash
pip install flask flask-cors mistralai pandas jieba python-dotenv openpyxl
