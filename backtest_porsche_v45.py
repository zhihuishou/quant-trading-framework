#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
保时捷 V4.5 策略回测
随机测试300支股票
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

print("\n" + "="*80)
print("保时捷 V4.5 策略回测系统")
print("="*80)

# 1. 加载数据
print("\n1. 加载数据...")
df_all = pd.read_csv('data/stocks_5000_complete.csv')
print(f"   总数据: {len(df_all):,} 条记录")
print(f"   股票数量: {df_all['证券代码'].nunique()} 只")

# 转换日期格式
df_all['交易时间'] = pd.to_datetime(df_all['交易时间'])

# 2. 随机选择300只股票
print("\n2. 随机选择300只股票...")
all_stocks = df_all['证券代码'].unique()
random.seed(42)  # 固定随机种子，保证可复现
selected_stocks = random.sample(list(all_stocks), min(300, len(all_stocks)))
df = df_all[df_all['证券代码'].isin(selected_stocks)].copy()
print(f"   选中: {len(selected_stocks)} 只股票")
print(f"   数据量: {len(df):,} 条")

# 3. 数据预处理
print("\n3. 数据预处理...")

# 按股票和日期排序
df = df.sort_values(['证券代码', '交易时间'])

# 计算均线
print("   计算均线...")
ma_windows = [5, 20, 50, 150, 200]
for w in ma_windows:
    df[f'ma{w}'] = df.groupby('证券代码')['收盘价'].transform(
        lambda x: x.rolling(w, min_periods=w).mean()
    )

# 计算乖离率
df['bias20'] = (df['收盘价'] - df['ma20']) / df['ma20'] * 100

# 计算60日和220日涨幅（用于RPS）
df['pct_60d'] = df.groupby('证券代码')['收盘价'].transform(
    lambda x: x.pct_change(60) * 100
)
df['pct_220d'] = df.groupby('证券代码')['收盘价'].transform(
    lambda x: x.pct_change(220) * 100
)

# 计算RPS（相对强度排名）
print("   计算RPS...")
df['rps60'] = df.groupby('交易时间')['pct_60d'].rank(pct=True) * 100
df['rps220'] = df.groupby('交易时间')['pct_220d'].rank(pct=True) * 100

# 计算VCP（波动挤压）
print("   计算VCP...")
df['h5'] = df.groupby('证券代码')['最高价'].transform(lambda x: x.rolling(5).max())
df['l5'] = df.groupby('证券代码')['最低价'].transform(lambda x: x.rolling(5).min())
df['h20'] = df.groupby('证券代码')['最高价'].transform(lambda x: x.rolling(20).max())
df['l20'] = df.groupby('证券代码')['最低价'].transform(lambda x: x.rolling(20).min())
df['vcp_ratio'] = (df['h5'] - df['l5']) / (df['h20'] - df['l20'] + 1e-6)

# 计算MA200的20日前值
df['ma200_20d_ago'] = df.groupby('证券代码')['ma200'].shift(20)

print(f"   预处理完成")

# 4. 应用保时捷V4.5策略筛选
print("\n4. 应用保时捷V4.5策略...")

# 欧奈尔趋势模板
cond_trend = (
    (df['收盘价'] > df['ma50']) & 
    (df['ma50'] > df['ma150']) & 
    (df['ma150'] > df['ma200']) &
    (df['ma200'] > df['ma200_20d_ago'])
)

# RPS硬指标
cond_rps = (df['rps60'] >= 95) | (df['rps220'] >= 90)

# VCP波动挤压
cond_vcp = df['vcp_ratio'] < 0.45

# 乖离率拦截
cond_bias = df['bias20'] < 12

# 当日涨幅限制
cond_chg = df['涨跌幅'] < 7

# 综合筛选
mask = cond_trend & cond_rps & cond_vcp & cond_bias & cond_chg

# 计算得分
df['score'] = (
    df['rps60'] * 0.4 + 
    df['rps220'] * 0.3 + 
    (1 - df['vcp_ratio']) * 30 +
    (12 - df['bias20']) * 2
)

# 筛选结果
df_signals = df[mask].copy()
print(f"   筛选出信号: {len(df_signals)} 个")
print(f"   涉及股票: {df_signals['证券代码'].nunique()} 只")

if len(df_signals) == 0:
    print("\n⚠️  没有符合条件的股票，策略过于严格或数据不足")
    print("   建议：")
    print("   1. 放宽RPS条件")
    print("   2. 增加回测时间范围")
    print("   3. 增加股票数量")
    exit(0)

# 5. 回测设置
print("\n5. 回测设置...")

# 确定回测时间范围 - 仅回测近300个交易日
all_dates_sorted = sorted(df['交易时间'].unique())
if len(all_dates_sorted) > 300:
    backtest_start = all_dates_sorted[-300]
else:
    backtest_start = all_dates_sorted[0]
backtest_end = all_dates_sorted[-1]

# 过滤数据到回测时间范围
df = df[df['交易时间'] >= backtest_start].copy()
df_signals = df_signals[df_signals['交易时间'] >= backtest_start].copy()

print(f"   回测时间: {backtest_start.date()} 至 {backtest_end.date()}")
print(f"   回测天数: {(backtest_end - backtest_start).days} 天")
print(f"   信号数量: {len(df_signals)} 个")

# 回测参数
initial_capital = 500000  # 初始资金50万
max_positions = 10  # 最大持仓数
position_size = 0.1  # 每只股票10%仓位
stop_loss = -0.08  # 止损-8%
take_profit = 0.20  # 止盈+20%

print(f"   初始资金: ¥{initial_capital:,}")
print(f"   最大持仓: {max_positions} 只")
print(f"   单只仓位: {position_size*100}%")
print(f"   止损: {stop_loss*100}%")
print(f"   止盈: {take_profit*100}%")

print("\n6. 开始回测...")

# 回测逻辑
capital = initial_capital
positions = {}  # {股票代码: {'shares': 股数, 'buy_price': 买入价, 'buy_date': 买入日期}}
trades = []  # 交易记录
daily_value = []  # 每日资产价值

# 获取所有交易日
all_dates = sorted(df['交易时间'].unique())
backtest_dates = [d for d in all_dates if backtest_start <= d <= backtest_end]

print(f"   回测交易日: {len(backtest_dates)} 天")

# 按日期回测
for i, current_date in enumerate(backtest_dates):
    if i % 50 == 0:
        print(f"   进度: {i}/{len(backtest_dates)} ({i/len(backtest_dates)*100:.1f}%)")
    
    # 当日数据
    today_data = df[df['交易时间'] == current_date]
    # 去重，保留每只股票最新的一条记录
    today_data = today_data.drop_duplicates(subset='证券代码', keep='last').set_index('证券代码')
    today_signals = df_signals[df_signals['交易时间'] == current_date].sort_values('score', ascending=False)
    
    # 1. 检查现有持仓，执行止盈止损
    for stock_code in list(positions.keys()):
        if stock_code not in today_data.index:
            continue
            
        pos = positions[stock_code]
        current_price = float(today_data.loc[stock_code, '收盘价'])
        buy_price = float(pos['buy_price'])
        pnl_pct = (current_price - buy_price) / buy_price
        
        # 止损条件：-8%
        if pnl_pct <= stop_loss:
            sell_value = pos['shares'] * current_price
            capital += sell_value
            trades.append({
                '股票代码': stock_code,
                '买入日期': pos['buy_date'],
                '买入价': buy_price,
                '卖出日期': current_date,
                '卖出价': current_price,
                '收益率': pnl_pct,
                '卖出原因': '止损'
            })
            del positions[stock_code]
            continue
        
        # 止盈条件：+20%
        if pnl_pct >= take_profit:
            sell_value = pos['shares'] * current_price
            capital += sell_value
            trades.append({
                '股票代码': stock_code,
                '买入日期': pos['buy_date'],
                '买入价': buy_price,
                '卖出日期': current_date,
                '卖出价': current_price,
                '收益率': pnl_pct,
                '卖出原因': '止盈'
            })
            del positions[stock_code]
            continue
        
        # 跌破MA50
        if 'ma50' in today_data.columns and not pd.isna(today_data.loc[stock_code, 'ma50']):
            ma50_value = float(today_data.loc[stock_code, 'ma50'])
            if current_price < ma50_value:
                sell_value = pos['shares'] * current_price
                capital += sell_value
                trades.append({
                    '股票代码': stock_code,
                    '买入日期': pos['buy_date'],
                    '买入价': buy_price,
                    '卖出日期': current_date,
                    '卖出价': current_price,
                    '收益率': pnl_pct,
                    '卖出原因': '跌破MA50'
                })
                del positions[stock_code]
    
    # 2. 买入新信号（如果有空仓位）
    if len(positions) < max_positions and len(today_signals) > 0:
        for _, signal in today_signals.iterrows():
            stock_code = signal['证券代码']
            
            # 已持仓则跳过
            if stock_code in positions:
                continue
            
            # 检查是否有足够资金
            buy_amount = capital * position_size
            if buy_amount < 1000:  # 最小买入金额
                break
            
            buy_price = signal['收盘价']
            shares = int(buy_amount / buy_price / 100) * 100  # 买入整手
            
            if shares >= 100:
                actual_cost = shares * buy_price
                capital -= actual_cost
                positions[stock_code] = {
                    'shares': shares,
                    'buy_price': buy_price,
                    'buy_date': current_date
                }
            
            # 达到最大持仓数
            if len(positions) >= max_positions:
                break
    
    # 3. 计算当日总资产
    position_value = 0
    for stock_code, pos in positions.items():
        if stock_code in today_data.index:
            position_value += pos['shares'] * today_data.loc[stock_code, '收盘价']
    
    total_value = capital + position_value
    daily_value.append({
        '日期': current_date,
        '现金': capital,
        '持仓市值': position_value,
        '总资产': total_value,
        '持仓数': len(positions)
    })

# 清仓所有剩余持仓
final_date = backtest_dates[-1]
final_data = df[df['交易时间'] == final_date]
final_data = final_data.drop_duplicates(subset='证券代码', keep='last').set_index('证券代码')
for stock_code, pos in positions.items():
    if stock_code in final_data.index:
        current_price = final_data.loc[stock_code, '收盘价']
        sell_value = pos['shares'] * current_price
        capital += sell_value
        pnl_pct = (current_price - pos['buy_price']) / pos['buy_price']
        trades.append({
            '股票代码': stock_code,
            '买入日期': pos['buy_date'],
            '买入价': pos['buy_price'],
            '卖出日期': final_date,
            '卖出价': current_price,
            '收益率': pnl_pct,
            '卖出原因': '回测结束'
        })

positions.clear()

print(f"\n✅ 回测完成")
print(f"   总交易次数: {len(trades)}")

# 7. 计算评估指标
print("\n7. 计算评估指标...")

df_trades = pd.DataFrame(trades)
df_daily = pd.DataFrame(daily_value)

# 总收益率
final_value = df_daily.iloc[-1]['总资产']
total_return = (final_value - initial_capital) / initial_capital

# 胜率
if len(df_trades) > 0:
    win_rate = len(df_trades[df_trades['收益率'] > 0]) / len(df_trades)
else:
    win_rate = 0

# 日收益率
df_daily['日收益率'] = df_daily['总资产'].pct_change()

# 波动率（年化）
volatility = df_daily['日收益率'].std() * np.sqrt(252)

# Sharpe比率（假设无风险利率3%）
risk_free_rate = 0.03
avg_daily_return = df_daily['日收益率'].mean()
sharpe = (avg_daily_return * 252 - risk_free_rate) / (volatility + 1e-6)

# Beta（相对沪深300，这里简化为1，需要实际基准数据）
beta = 1.0  # 简化处理

print("\n" + "="*80)
print("回测结果")
print("="*80)
print(f"\n📊 收益指标:")
print(f"   初始资金: ¥{initial_capital:,.2f}")
print(f"   最终资金: ¥{final_value:,.2f}")
print(f"   总收益率: {total_return*100:.2f}%")
print(f"   年化收益率: {total_return / ((backtest_end - backtest_start).days / 365) * 100:.2f}%")

print(f"\n📈 交易统计:")
print(f"   总交易次数: {len(df_trades)}")
print(f"   胜率: {win_rate*100:.2f}%")
if len(df_trades) > 0:
    print(f"   平均收益: {df_trades['收益率'].mean()*100:.2f}%")
    print(f"   最大单笔收益: {df_trades['收益率'].max()*100:.2f}%")
    print(f"   最大单笔亏损: {df_trades['收益率'].min()*100:.2f}%")

print(f"\n⚠️  风险指标:")
print(f"   波动率(年化): {volatility*100:.2f}%")
print(f"   Sharpe比率: {sharpe:.2f}")
print(f"   Beta系数: {beta:.2f}")

# 最大回撤
df_daily['累计最高'] = df_daily['总资产'].cummax()
df_daily['回撤'] = (df_daily['总资产'] - df_daily['累计最高']) / df_daily['累计最高']
max_drawdown = df_daily['回撤'].min()
print(f"   最大回撤: {max_drawdown*100:.2f}%")

# 保存结果
df_trades.to_csv('data/porsche_v45_trades.csv', index=False, encoding='utf-8-sig')
df_daily.to_csv('data/porsche_v45_daily.csv', index=False, encoding='utf-8-sig')

print(f"\n💾 结果已保存:")
print(f"   交易记录: data/porsche_v45_trades.csv")
print(f"   每日资产: data/porsche_v45_daily.csv")

print("\n" + "="*80)
print("回测完成！")
print("="*80)
