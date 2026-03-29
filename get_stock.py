import yfinance as yf
import pandas as pd

# 1. 抓取資料與計算 20MA (使用你的完美修正版寫法)
stock_id = "2330.TW"
print(f"正在抓取 {stock_id} 過去一年的資料並準備回測...")
stock_data = yf.Ticker(stock_id).history(period="1y")
stock_data['20MA'] = stock_data['Close'].rolling(window=20).mean()

# 2. 產生買賣訊號
stock_data['Close_Yesterday'] = stock_data['Close'].shift(1)
stock_data['20MA_Yesterday'] = stock_data['20MA'].shift(1)

stock_data['Buy_Signal'] = (stock_data['Close'] > stock_data['20MA']) & (stock_data['Close_Yesterday'] <= stock_data['20MA_Yesterday'])
stock_data['Sell_Signal'] = (stock_data['Close'] < stock_data['20MA']) & (stock_data['Close_Yesterday'] >= stock_data['20MA_Yesterday'])

# 3. 設定回測環境 (模擬不到 10 萬元的零股交易)
initial_capital = 100000  # 初始本金 10 萬元
capital = initial_capital
position = 0              # 目前手上的股數
trade_count = 0           # 交易次數

print("\n--- 📝 歷史交易紀錄 ---")
# iterrows() 會讓程式一天一天往下掃描
for date, row in stock_data.iterrows():
    
    # 遇到買進訊號，且手上沒有股票時 (全倉買進零股)
    if row['Buy_Signal'] and position == 0:
        buy_price = row['Close']
        # 計算 10 萬元可以買幾股 (無條件捨去)
        position = int(capital // buy_price)
        capital -= (position * buy_price)
        print(f"🟢 {date.strftime('%Y-%m-%d')} | 買進 {position} 股 | 單價: {buy_price:.1f} 元")

    # 遇到賣出訊號，且手上有股票時 (全倉賣出)
    elif row['Sell_Signal'] and position > 0:
        sell_price = row['Close']
        capital += (position * sell_price)
        
        profit = (sell_price - buy_price) * position
        profit_percent = ((sell_price - buy_price) / buy_price) * 100
        
        print(f"🔴 {date.strftime('%Y-%m-%d')} | 賣出 {position} 股 | 單價: {sell_price:.1f} 元 | 本次損益: {profit:.0f} 元 ({profit_percent:.2f}%)")
        
        position = 0
        trade_count += 1

# 4. 結算：如果到今天手裡還有股票，以今天的收盤價估算總資產
if position > 0:
    final_price = stock_data.iloc[-1]['Close']
    capital += (position * final_price)
    print(f"\n⚪ 目前仍持有股票，以最新收盤價 {final_price:.1f} 估算結餘。")

# 5. 計算最終成績單
total_return = ((capital - initial_capital) / initial_capital) * 100
print("\n--- 🏆 回測總結 ---")
print(f"初始本金: {initial_capital} 元")
print(f"最終資產: {capital:.0f} 元")
print(f"總報酬率: {total_return:.2f}%")
print(f"總交易次數: {trade_count} 次")