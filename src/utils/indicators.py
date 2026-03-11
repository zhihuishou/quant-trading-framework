import pandas as pd
import numpy as np

# ==================== 趋势指标 ====================

def calculate_ma(data, window):
    """
    移动平均线 (Moving Average)
    用途：识别趋势方向，支撑/阻力位
    """
    return data.rolling(window=window).mean()

def calculate_ema(data, window):
    """
    指数移动平均线 (Exponential Moving Average)
    用途：对近期价格更敏感，更快反应趋势变化
    """
    return data.ewm(span=window, adjust=False).mean()

def calculate_macd(data, fast=12, slow=26, signal=9):
    """
    MACD指标 (Moving Average Convergence Divergence)
    返回：(MACD线, 信号线, 柱状图)
    用途：判断趋势强度和买卖时机
    """
    ema_fast = calculate_ema(data, fast)
    ema_slow = calculate_ema(data, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(data, window=20, num_std=2):
    """
    布林带 (Bollinger Bands)
    返回：(上轨, 中轨, 下轨)
    用途：判断超买超卖，波动率分析
    """
    middle = calculate_ma(data, window)
    std = data.rolling(window=window).std()
    upper = middle + (std * num_std)
    lower = middle - (std * num_std)
    return upper, middle, lower

# ==================== 动量指标 ====================

def calculate_rsi(data, window=14):
    """
    相对强弱指标 (Relative Strength Index)
    范围：0-100，>70超买，<30超卖
    用途：判断超买超卖状态
    """
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_kdj(high, low, close, n=9, m1=3, m2=3):
    """
    KDJ指标 (Stochastic Oscillator)
    返回：(K值, D值, J值)
    用途：判断超买超卖，背离分析
    """
    lowest_low = low.rolling(window=n).min()
    highest_high = high.rolling(window=n).max()
    
    rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
    k = rsv.ewm(com=m1-1, adjust=False).mean()
    d = k.ewm(com=m2-1, adjust=False).mean()
    j = 3 * k - 2 * d
    
    return k, d, j

def calculate_momentum(data, window=10):
    """
    动量指标 (Momentum)
    用途：衡量价格变化速度
    """
    return data.diff(window)

# ==================== 成交量指标 ====================

def calculate_obv(close, volume):
    """
    能量潮指标 (On Balance Volume)
    用途：通过成交量变化预测价格趋势
    """
    obv = pd.Series(index=close.index, dtype=float)
    obv.iloc[0] = volume.iloc[0]
    
    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
        elif close.iloc[i] < close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]
    
    return obv

def calculate_vwap(high, low, close, volume):
    """
    成交量加权平均价 (Volume Weighted Average Price)
    用途：判断当日交易的平均成本
    """
    typical_price = (high + low + close) / 3
    return (typical_price * volume).cumsum() / volume.cumsum()

# ==================== 波动率指标 ====================

def calculate_atr(high, low, close, window=14):
    """
    平均真实波幅 (Average True Range)
    用途：衡量市场波动性，设置止损位
    """
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=window).mean()
    return atr

def calculate_volatility(data, window=20):
    """
    历史波动率 (Historical Volatility)
    用途：衡量价格波动程度
    """
    log_returns = np.log(data / data.shift(1))
    volatility = log_returns.rolling(window=window).std() * np.sqrt(252)
    return volatility
