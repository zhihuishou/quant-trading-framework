#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
保时捷 V4.5 策略回测可视化
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

print("\n" + "="*80)
print("保时捷 V4.5 策略回测可视化")
print("="*80)

# 1. 加载数据
print("\n1. 加载数据...")
df_daily = pd.read_csv('data/porsche_v45_daily.csv')
df_trades = pd.read_csv('data/porsche_v45_trades.csv')

df_daily['日期'] = pd.to_datetime(df_daily['日期'])
df_trades['买入日期'] = pd.to_datetime(df_trades['买入日期'])
df_trades['卖出日期'] = pd.to_datetime(df_trades['卖出日期'])

print(f"   每日数据: {len(df_daily)} 条")
print(f"   交易记录: {len(df_trades)} 笔")

# 2. 计算关键指标
initial_capital = df_daily.iloc[0]['总资产']
df_daily['累计收益率'] = (df_daily['总资产'] / initial_capital - 1) * 100
df_daily['累计最高'] = df_daily['总资产'].cummax()
df_daily['回撤'] = (df_daily['总资产'] - df_daily['累计最高']) / df_daily['累计最高'] * 100

# 3. 创建图表
fig = plt.figure(figsize=(16, 12))

# ========== 图1: 资产曲线 ==========
ax1 = plt.subplot(3, 2, 1)
ax1.plot(df_daily['日期'], df_daily['总资产'], linewidth=2, color='#2E86AB', label='总资产')
ax1.axhline(y=initial_capital, color='gray', linestyle='--', alpha=0.5, label='初始资金')
ax1.fill_between(df_daily['日期'], initial_capital, df_daily['总资产'], 
                  where=(df_daily['总资产'] >= initial_capital), 
                  alpha=0.3, color='green', label='盈利区')
ax1.fill_between(df_daily['日期'], initial_capital, df_daily['总资产'], 
                  where=(df_daily['总资产'] < initial_capital), 
                  alpha=0.3, color='red', label='亏损区')
ax1.set_title('资产曲线', fontsize=14, fontweight='bold')
ax1.set_xlabel('日期')
ax1.set_ylabel('资产 (¥)')
ax1.legend(loc='best')
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

# ========== 图2: 累计收益率 ==========
ax2 = plt.subplot(3, 2, 2)
ax2.plot(df_daily['日期'], df_daily['累计收益率'], linewidth=2, color='#A23B72')
ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax2.fill_between(df_daily['日期'], 0, df_daily['累计收益率'], 
                  where=(df_daily['累计收益率'] >= 0), 
                  alpha=0.3, color='green')
ax2.fill_between(df_daily['日期'], 0, df_daily['累计收益率'], 
                  where=(df_daily['累计收益率'] < 0), 
                  alpha=0.3, color='red')
ax2.set_title('累计收益率', fontsize=14, fontweight='bold')
ax2.set_xlabel('日期')
ax2.set_ylabel('收益率 (%)')
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

# ========== 图3: 回撤曲线 ==========
ax3 = plt.subplot(3, 2, 3)
ax3.fill_between(df_daily['日期'], 0, df_daily['回撤'], alpha=0.5, color='#F18F01')
ax3.plot(df_daily['日期'], df_daily['回撤'], linewidth=2, color='#C73E1D')
ax3.axhline(y=-8, color='red', linestyle='--', alpha=0.7, label='止损线 -8%')
max_dd = df_daily['回撤'].min()
ax3.axhline(y=max_dd, color='darkred', linestyle=':', alpha=0.7, label=f'最大回撤 {max_dd:.2f}%')
ax3.set_title('回撤曲线', fontsize=14, fontweight='bold')
ax3.set_xlabel('日期')
ax3.set_ylabel('回撤 (%)')
ax3.legend(loc='best')
ax3.grid(True, alpha=0.3)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)

# ========== 图4: 持仓数量变化 ==========
ax4 = plt.subplot(3, 2, 4)
ax4.plot(df_daily['日期'], df_daily['持仓数'], linewidth=2, color='#06A77D', marker='o', markersize=2)
ax4.axhline(y=10, color='red', linestyle='--', alpha=0.5, label='最大持仓 10只')
ax4.fill_between(df_daily['日期'], 0, df_daily['持仓数'], alpha=0.3, color='#06A77D')
ax4.set_title('持仓数量变化', fontsize=14, fontweight='bold')
ax4.set_xlabel('日期')
ax4.set_ylabel('持仓数 (只)')
ax4.legend(loc='best')
ax4.grid(True, alpha=0.3)
ax4.set_ylim(0, 12)
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)

# ========== 图5: 收益率分布 ==========
ax5 = plt.subplot(3, 2, 5)
returns = df_trades['收益率'] * 100
bins = np.linspace(returns.min(), returns.max(), 30)
n, bins, patches = ax5.hist(returns, bins=bins, edgecolor='black', alpha=0.7)

# 给盈利和亏损的柱子上色
for i, patch in enumerate(patches):
    if bins[i] < 0:
        patch.set_facecolor('#E63946')
    else:
        patch.set_facecolor('#06A77D')

ax5.axvline(x=0, color='black', linestyle='--', linewidth=2, alpha=0.7)
ax5.axvline(x=returns.mean(), color='blue', linestyle=':', linewidth=2, alpha=0.7, label=f'平均 {returns.mean():.2f}%')
ax5.set_title('交易收益率分布', fontsize=14, fontweight='bold')
ax5.set_xlabel('收益率 (%)')
ax5.set_ylabel('交易次数')
ax5.legend(loc='best')
ax5.grid(True, alpha=0.3, axis='y')

# ========== 图6: 胜率与盈亏统计 ==========
ax6 = plt.subplot(3, 2, 6)

# 统计数据
win_trades = df_trades[df_trades['收益率'] > 0]
loss_trades = df_trades[df_trades['收益率'] <= 0]
win_rate = len(win_trades) / len(df_trades) * 100
loss_rate = 100 - win_rate

avg_win = win_trades['收益率'].mean() * 100 if len(win_trades) > 0 else 0
avg_loss = loss_trades['收益率'].mean() * 100 if len(loss_trades) > 0 else 0
profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0

# 创建柱状图
categories = ['胜率', '败率']
values = [win_rate, loss_rate]
colors = ['#06A77D', '#E63946']
bars = ax6.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')

# 添加数值标签
for bar, val in zip(bars, values):
    height = bar.get_height()
    ax6.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:.1f}%',
             ha='center', va='bottom', fontsize=12, fontweight='bold')

ax6.set_title('胜率统计', fontsize=14, fontweight='bold')
ax6.set_ylabel('比例 (%)')
ax6.set_ylim(0, 100)
ax6.grid(True, alpha=0.3, axis='y')

# 添加文本信息
info_text = f'总交易: {len(df_trades)}笔\n'
info_text += f'盈利: {len(win_trades)}笔\n'
info_text += f'亏损: {len(loss_trades)}笔\n'
info_text += f'平均盈利: {avg_win:.2f}%\n'
info_text += f'平均亏损: {avg_loss:.2f}%\n'
info_text += f'盈亏比: {profit_factor:.2f}'

ax6.text(0.98, 0.97, info_text,
         transform=ax6.transAxes,
         fontsize=10,
         verticalalignment='top',
         horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('data/backtest_visualization.png', dpi=300, bbox_inches='tight')
print("\n✅ 图表已保存: data/backtest_visualization.png")

# 4. 打印关键指标
print("\n" + "="*80)
print("关键指标汇总")
print("="*80)

final_value = df_daily.iloc[-1]['总资产']
total_return = (final_value / initial_capital - 1) * 100
max_drawdown = df_daily['回撤'].min()

print(f"\n📊 收益指标:")
print(f"   初始资金: ¥{initial_capital:,.2f}")
print(f"   最终资金: ¥{final_value:,.2f}")
print(f"   总收益率: {total_return:.2f}%")

print(f"\n📈 交易统计:")
print(f"   总交易: {len(df_trades)} 笔")
print(f"   胜率: {win_rate:.2f}%")
print(f"   平均盈利: {avg_win:.2f}%")
print(f"   平均亏损: {avg_loss:.2f}%")
print(f"   盈亏比: {profit_factor:.2f}")

print(f"\n⚠️  风险指标:")
print(f"   最大回撤: {max_drawdown:.2f}%")

# 卖出原因统计
print(f"\n🔍 卖出原因:")
sell_reasons = df_trades['卖出原因'].value_counts()
for reason, count in sell_reasons.items():
    pct = count / len(df_trades) * 100
    print(f"   {reason}: {count}笔 ({pct:.1f}%)")

print("\n" + "="*80)
print("可视化完成！")
print("="*80)

plt.show()
