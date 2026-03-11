import pandas as pd

def calculate_ma(data, window):
    """计算移动平均线"""
    return data.rolling(window=window).mean()

def calculate_rsi(data, window=14):
    """计算RSI指标"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
