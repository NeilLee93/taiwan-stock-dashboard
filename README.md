# 📈 台股智能多維度策略分析系統 (Taiwan Stock Quant Dashboard)

這是一個基於 Python 與 Streamlit 開發的輕量級、無程式碼量化回測與進出場決策輔助系統。專為台灣股市（上市/上櫃）設計，系統會根據歷史數據自動進行超參數最佳化，從多種技術指標組合中尋找最適合該檔股票的專屬交易策略，並提供最新的實戰買賣指示。

## ✨ 核心功能 (Features)

* **🧠 智能策略最佳化引擎**：內建極短線 (10MA)、波段帶量 (20MA+Vol)、順勢 (MACD)、逆勢搶反彈 (RSI) 與雙動能聯集等多種策略，自動回測並選出歷史總報酬率最高的冠軍策略。
* **🔔 實戰決策指示燈**：提取最新一個交易日的數據，直白顯示「🟢 買進」、「🔴 賣出」或「⚪ 觀望」訊號，免除人工判讀線圖的煩惱。
* **📊 專業量化指標與權益曲線**：捨棄傳統 K 線圖，採用更能反映真實資金波動的「資金權益曲線 (Equity Curve)」，並自動計算年化報酬率、夏普比率 (Sharpe Ratio)、獲利/虧損比與勝率。
* **🛡️ 雙重防禦抓取機制**：內建瀏覽器偽裝標頭 (User-Agent Spoofing) 與動態快取管理，並結合政府 OpenAPI 與 Yahoo Finance 雙重資料源，有效降低雲端 IP 被封鎖 (Rate Limit) 的機率，確保中文股票名稱與報價精準載入。
* **📱 完美響應式設計 (RWD)**：採用現代化卡片式 UI 佈局，自動適配電腦寬螢幕與手機介面，支援深色/淺色主題自動切換。

## 🛠️ 安裝與本地端執行 (Local Installation)

1. 將本專案複製到本地端：
   ```bash
   git clone [https://github.com/你的帳號/taiwan-stock-dashboard.git](https://github.com/你的帳號/taiwan-stock-dashboard.git)
   cd taiwan-stock-dashboard
安裝必要的 Python 套件：

Bash
pip install -r requirements.txt
啟動 Streamlit 網頁伺服器：

Bash
streamlit run app.py
啟動後，瀏覽器將自動開啟 http://localhost:8501。

📱 行動裝置私有雲部署 (Termux + Tailscale)
為徹底解決公共雲端平台容易遭到財經 API 封鎖的問題，強烈建議將本系統部署於備用的 Android 裝置上，打造 24 小時運作的私有財經大腦。

在 Android 裝置安裝 Termux 與 Tailscale。

於 Termux 中執行環境建置：

Bash
pkg update && pkg upgrade
pkg install python git
下載專案並啟動：

Bash
git clone [https://github.com/你的帳號/taiwan-stock-dashboard.git](https://github.com/你的帳號/taiwan-stock-dashboard.git)
cd taiwan-stock-dashboard
pip install -r requirements.txt
streamlit run app.py
在任何登入相同 Tailscale 網路的設備上，打開瀏覽器輸入 http://<該裝置的Tailscale-IP>:8501 即可安全連線存取。

⚖️ 免責聲明 (Disclaimer)
本專案所實作之「超參數最佳化」與「多維度策略組合」及所有顯示之數據與訊號，純屬歷史數據之數學運算結果，絕不構成對任何有價證券之推介、要約或具體投資建議。
依據歷史數據自動尋找之「最高報酬」策略，存在極高之過度擬合 (Overfitting) 風險，歷史績效絕不保證未來獲利。使用者若依據本系統資訊進行任何實質之投資交易行為，所產生之所有潛在風險或財務損失，皆應由投資人自行獨立判斷並自負全責。
