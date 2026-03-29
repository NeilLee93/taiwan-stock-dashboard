import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests 
import numpy as np

# --- 1. 網頁基本設定 ---
st.set_page_config(page_title="台股智能多維度策略分析", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    div[data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 700;
        color: var(--text-color);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 16px;
        color: gray;
    }
    [data-testid="stVerticalBlock"] > div:has(> div[data-testid="stMetricValue"]) {
        background-color: var(--secondary-background-color);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. 側邊欄 (Sidebar) ---
with st.sidebar:
    st.header("⚙️ 引擎與策略設定")
    stock_input = st.text_input("輸入股票代碼 (純數字)", value="2330")
    period_dict = {"近三個月": "3mo", "近半年": "6mo", "近一年": "1y", "近兩年": "2y", "近五年": "5y"}
    period_display = st.selectbox("選擇回測區間", list(period_dict.keys()), index=2)
    period_value = period_dict[period_display]
    initial_capital = st.number_input("初始本金", min_value=10000, value=100000, step=10000)
    st.markdown("---")
    st.caption("⚖️ 系統免責聲明：本系統數據與訊號僅供歷史回測參考，不構成任何投資建議。投資人應獨立判斷並自負盈虧。")

# --- 3. 獲取中文名稱與股價資料 (🌟 升級防禦版) ---
@st.cache_data
def get_stock_chinese_name(ticker_num):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res_twse = requests.get("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL", headers=headers, timeout=10)
        if res_twse.status_code == 200:
            for item in res_twse.json():
                if item['Code'] == str(ticker_num): return item['Name']
        
        res_tpex = requests.get("https://www.tpex.org.tw/openapi/v1/t187ap03_L", headers=headers, timeout=10)
        if res_tpex.status_code == 200:
            for item in res_tpex.json():
                if item['SecuritiesCompanyCode'] == str(ticker_num): return item['CompanyName']
    except:
        pass

    try:
        tw_info = yf.Ticker(f"{ticker_num}.TW").info
        if 'shortName' in tw_info: return tw_info['shortName']
        
        two_info = yf.Ticker(f"{ticker_num}.TWO").info
        if 'shortName' in two_info: return two_info['shortName']
    except:
        pass

    return f"股票 {ticker_num}"

@st.cache_data
def load_data(ticker_num, period):
    for suffix in [".TW", ".TWO"]:
        ticker = f"{ticker_num}{suffix}"
        data = yf.Ticker(ticker).history(period=period)
        if not data.empty: return data, ticker
    return None, None

# 🌟 就是這裡！剛剛不小心消失的關鍵兩行我補回來了
stock_data_raw, real_ticker = load_data(stock_input, period_value)
stock_name = get_stock_chinese_name(stock_input)

# --- 4. 專業回測引擎 ---
if stock_data_raw is None:
    st.title("📉 台股智能多維度策略分析")
    st.error(f"❌ 找不到代碼 {stock_input} 的資料！請確認代碼是否正確。")
else:
    st.title(f"📊 {stock_name} ({real_ticker}) 進出場策略決策系統")
    
    def run_backtest_with_equity_curve(data, buy_signals, sell_signals, initial_cap):
        capital = initial_cap
        position = 0
        trade_count, win_count = 0, 0
        records = []
        equity_curve = [initial_cap] 
        gains_list, losses_list = [], []

        for i in range(len(data)):
            close_price = data['Close'].iloc[i]
            
            if buy_signals.iloc[i] and position == 0:
                position = int(capital // close_price)
                capital -= (position * close_price)
                records.append({"日期": data.index[i].strftime('%Y-%m-%d'), "動作": "買進", "成交價": round(close_price, 2)})
            elif sell_signals.iloc[i] and position > 0:
                buy_price = records[-1]["成交價"]
                profit = (close_price - buy_price) * position
                capital += (position * close_price)
                records.append({"日期": data.index[i].strftime('%Y-%m-%d'), "動作": "賣出", "成交價": round(close_price, 2), "當次損益": round(profit, 0)})
                if profit > 0:
                    win_count += 1
                    gains_list.append(profit)
                else:
                    losses_list.append(profit)
                position = 0
                trade_count += 1
            
            current_equity = capital + (position * close_price)
            if i > 0: 
                equity_curve.append(current_equity)

        if position > 0:
            capital += (position * data['Close'].iloc[-1])

        equity_series = pd.Series(equity_curve, index=data.index)
        daily_returns = equity_series.pct_change().dropna()
        
        total_return = ((equity_series.iloc[-1] - initial_cap) / initial_cap) * 100
        num_days = len(data)
        annual_return = ((equity_series.iloc[-1] / initial_cap) ** (252 / num_days) - 1) * 100 if num_days > 0 else 0
        
        volatility = daily_returns.std() * np.sqrt(252) * 100 if len(daily_returns) > 1 else 0
        sharpe = (annual_return / volatility) if volatility > 0 else 0
        
        sum_gains = sum(gains_list)
        sum_losses = abs(sum(losses_list))
        profit_loss_ratio = (sum_gains / sum_losses) if sum_losses > 0 else (999 if sum_gains > 0 else 0)

        win_rate = (win_count / trade_count * 100) if trade_count > 0 else 0
        return equity_series, total_return, annual_return, sharpe, win_rate, trade_count, profit_loss_ratio, records

    df = stock_data_raw.copy()
    
    df['10MA'] = df['Close'].rolling(window=10).mean()
    df['20MA'] = df['Close'].rolling(window=20).mean()
    df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
    
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    rs = gain.ewm(com=13, adjust=False).mean() / loss.ewm(com=13, adjust=False).mean()
    df['RSI'] = 100 - (100 / (1 + rs))
    
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    strategies = {}
    strategies['短期動能強攻 (10MA突破)'] = {'buy': (df['Close'] > df['10MA']) & (df['Close'].shift(1) <= df['10MA'].shift(1)), 'sell': (df['Close'] < df['10MA']) & (df['Close'].shift(1) >= df['10MA'].shift(1))}
    strategies['波段帶量起飛 (20MA+爆量)'] = {'buy': (df['Close'] > df['20MA']) & (df['Close'].shift(1) <= df['20MA'].shift(1)) & (df['Volume'] > df['Vol_MA20']), 'sell': (df['Close'] < df['20MA']) & (df['Close'].shift(1) >= df['20MA'].shift(1))}
    strategies['MACD 趨勢確認手'] = {'buy': (df['MACD'] > df['Signal']) & (df['MACD'].shift(1) <= df['Signal'].shift(1)), 'sell': (df['MACD'] < df['Signal']) & (df['MACD'].shift(1) >= df['Signal'].shift(1))}
    strategies['RSI 震盪狙擊手'] = {'buy': (df['RSI'] < 30), 'sell': (df['RSI'] > 70)}
    strategies['雙動能聯集突擊部隊'] = {'buy': (df['RSI'] < 30) | ((df['MACD'] > df['Signal']) & (df['MACD'].shift(1) <= df['Signal'].shift(1))), 'sell': (df['RSI'] > 70) | ((df['MACD'] < df['Signal']) & (df['MACD'].shift(1) >= df['Signal'].shift(1)))}

    leaderboard = []
    best_return = -999
    best_equity_curve, best_records, best_strategy_name, best_trades, best_annual_return, best_sharpe, best_profit_loss_ratio, best_win_rate = None, None, None, None, None, None, None, None
    best_buy_signals, best_sell_signals = None, None

    for name, logic in strategies.items():
        buy_sig = logic['buy'] & (~logic['buy'].shift(1).fillna(False))
        sell_sig = logic['sell'] & (~logic['sell'].shift(1).fillna(False))
        
        equity_c, total_ret, ann_ret, sharpe_r, win_rt, trades, pl_ratio, recs = run_backtest_with_equity_curve(df, buy_sig, sell_sig, initial_capital)
        leaderboard.append({"策略名稱": name, "總報酬率 (%)": round(total_ret, 2), "年化報酬率 (%)": round(ann_ret, 1), "勝率 (%)": round(win_rt, 1), "交易次數": trades})
        
        if total_ret > best_return:
            best_return, best_strategy_name = total_ret, name
            best_equity_curve, best_records, best_trades, best_annual_return, best_sharpe, best_profit_loss_ratio, best_win_rate = equity_c, recs, trades, ann_ret, sharpe_r, pl_ratio, win_rt
            best_buy_signals, best_sell_signals = buy_sig, sell_sig

    # --- 5. 實戰決策引擎：最新一日訊號判定 ---
    st.markdown("---")
    latest_date = df.index[-1].strftime('%Y-%m-%d')
    latest_close = df['Close'].iloc[-1]
    is_buy_today = best_buy_signals.iloc[-1]
    is_sell_today = best_sell_signals.iloc[-1]

    if is_buy_today:
        st.success(f"### 🔔 最新實戰指示 ({latest_date} 收盤價 {latest_close:.2f} 元)\n**🟢 觸發強烈買進訊號！** 依據最佳策略【{best_strategy_name}】，目前已符合進場條件。")
    elif is_sell_today:
        st.error(f"### 🔔 最新實戰指示 ({latest_date} 收盤價 {latest_close:.2f} 元)\n**🔴 觸發強烈賣出訊號！** 依據最佳策略【{best_strategy_name}】，目前已符合出場（獲利了結或停損）條件。")
    else:
        st.info(f"### 🔔 最新實戰指示 ({latest_date} 收盤價 {latest_close:.2f} 元)\n**⚪ 維持觀望 (Hold)**。依據最佳策略【{best_strategy_name}】，今日未觸發任何進退場訊號，請維持目前部位或空手等待。")

    # --- 6. 網頁視覺化呈現 ---
    st.success(f"👑 **系統自動選定最佳策略：【{best_strategy_name}】** (此為該股票在【{period_display}】內歷史報酬最高之配置)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("年化報酬率 (專業獲利指標)", f"{best_annual_return:.1f}%")
    with col2: st.metric("夏普比率 (風險收益比)", f"{best_sharpe:.2f}")
    with col3: st.metric("獲利/虧損比 (賺賠比)", f"{best_profit_loss_ratio:.2f}")
    with col4: st.metric("策略勝率 (歷史數據)", f"{best_win_rate:.1f}%", f"{best_trades} 次交易")

    st.markdown("---")
    st.info("💧 **資金權益曲線 (Equity Curve)** —— 反映帳戶總資產（現金 + 股票市值）隨時間的變動情況")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=best_equity_curve.index, y=best_equity_curve, 
                             mode='lines', name='帳戶總資產', 
                             line=dict(color='#3B82F6', width=3),
                             opacity=0.8,
                             hovertemplate='日期: %{x}<br>資產總額: %{y:,.0f} 元<extra></extra>'))

    fig.update_layout(height=450, 
                      hovermode='x unified', 
                      margin=dict(l=0, r=0, t=10, b=0),
                      xaxis=dict(gridcolor='rgba(128,128,128,0.2)'), 
                      yaxis=dict(gridcolor='rgba(128,128,128,0.2)', range=[initial_capital * 0.8, best_equity_curve.max() * 1.1]),
                      paper_bgcolor='rgba(0,0,0,0)', 
                      plot_bgcolor='rgba(0,0,0,0)')  
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader(f"📊 各維度策略排行榜 (區間：{period_display})")
    df_leaderboard = pd.DataFrame(leaderboard).sort_values(by="總報酬率 (%)", ascending=False)
    st.dataframe(df_leaderboard, use_container_width=True, hide_index=True)

    st.subheader("📝 詳細交易紀錄")
    if best_records:
        st.dataframe(pd.DataFrame(best_records).iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("此策略區間無交易紀錄。")
