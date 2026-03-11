"""
交易分析演示 - 展示你会得到什么信息
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 模拟一些交易数据作为示例
demo_trades = [
    # 盈利交易
    {'symbol': '比亚迪', 'entry_date': '2024-01-10', 'exit_date': '2024-02-15', 
     'entry_price': 250, 'exit_price': 280, 'shares': 300, 'pnl': 9000},
    
    {'symbol': '宁德时代', 'entry_date': '2024-01-20', 'exit_date': '2024-03-05', 
     'entry_price': 180, 'exit_price': 195, 'shares': 500, 'pnl': 7500},
    
    {'symbol': '隆基绿能', 'entry_date': '2024-02-01', 'exit_date': '2024-02-20', 
     'entry_price': 22, 'exit_price': 25, 'shares': 1000, 'pnl': 3000},
    
    # 亏损交易
    {'symbol': '贵州茅台', 'entry_date': '2024-01-15', 'exit_date': '2024-03-10', 
     'entry_price': 1800, 'exit_price': 1650, 'shares': 100, 'pnl': -15000},
    
    {'symbol': '五粮液', 'entry_date': '2024-02-20', 'exit_date': '2024-03-15', 
     'entry_price': 180, 'exit_price': 165, 'shares': 500, 'pnl': -7500},
    
    {'symbol': '中国平安', 'entry_date': '2024-02-10', 'exit_date': '2024-02-25', 
     'entry_price': 45, 'exit_price': 42, 'shares': 800, 'pnl': -2400},
    
    # 小盈利
    {'symbol': '招商银行', 'entry_date': '2024-03-01', 'exit_date': '2024-03-20', 
     'entry_price': 35, 'exit_price': 36, 'shares': 1000, 'pnl': 1000},
]

def analyze_trades_detailed(trades_list):
    """详细分析交易记录"""
    
    df = pd.DataFrame(trades_list)
    df['entry_date'] = pd.to_datetime(df['entry_date'])
    df['exit_date'] = pd.to_datetime(df['exit_date'])
    df['holding_days'] = (df['exit_date'] - df['entry_date']).dt.days
    df['return_pct'] = (df['exit_price'] / df['entry_price'] - 1) * 100
    df['trade_value'] = df['entry_price'] * df['shares']
    
    # 分类
    winning_trades = df[df['pnl'] > 0]
    losing_trades = df[df['pnl'] < 0]
    
    print("\n" + "="*80)
    print("交易分析报告 - 你会得到这些信息".center(80))
    print("="*80)
    
    # ==================== 1. 整体表现 ====================
    print("\n【一、整体交易表现】")
    print("-"*80)
    
    total_pnl = df['pnl'].sum()
    total_invested = df['trade_value'].sum()
    avg_return = total_pnl / total_invested * 100 if total_invested > 0 else 0
    
    print(f"总交易次数        : {len(df)} 笔")
    print(f"盈利交易次数      : {len(winning_trades)} 笔 ({len(winning_trades)/len(df)*100:.1f}%)")
    print(f"亏损交易次数      : {len(losing_trades)} 笔 ({len(losing_trades)/len(df)*100:.1f}%)")
    print(f"总盈亏金额        : ¥{total_pnl:,.2f}")
    print(f"总投入资金        : ¥{total_invested:,.2f}")
    print(f"平均收益率        : {avg_return:.2f}%")
    
    # ==================== 2. 胜率与盈亏比 ====================
    print("\n【二、胜率与盈亏比分析】")
    print("-"*80)
    
    win_rate = len(winning_trades) / len(df) * 100
    avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
    avg_loss = abs(losing_trades['pnl'].mean()) if len(losing_trades) > 0 else 0
    profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
    
    print(f"胜率              : {win_rate:.2f}%")
    print(f"平均盈利          : ¥{avg_win:,.2f}")
    print(f"平均亏损          : ¥{avg_loss:,.2f}")
    print(f"盈亏比            : {profit_loss_ratio:.2f}")
    
    # 评价
    print(f"\n💡 评价:")
    if win_rate >= 60:
        print(f"   ✅ 胜率{win_rate:.1f}%，选股能力较强")
    elif win_rate >= 50:
        print(f"   ⚡ 胜率{win_rate:.1f}%，选股能力一般")
    else:
        print(f"   ⚠️  胜率{win_rate:.1f}%，选股能力需要提升")
    
    if profit_loss_ratio >= 2:
        print(f"   ✅ 盈亏比{profit_loss_ratio:.2f}，盈利交易质量高")
    elif profit_loss_ratio >= 1.5:
        print(f"   ⚡ 盈亏比{profit_loss_ratio:.2f}，盈利交易质量尚可")
    else:
        print(f"   ⚠️  盈亏比{profit_loss_ratio:.2f}，需要提高单笔盈利或减少单笔亏损")
    
    # ==================== 3. 持仓周期分析 ====================
    print("\n【三、持仓周期分析】")
    print("-"*80)
    
    avg_holding = df['holding_days'].mean()
    max_holding = df['holding_days'].max()
    min_holding = df['holding_days'].min()
    
    print(f"平均持仓天数      : {avg_holding:.1f} 天")
    print(f"最长持仓          : {max_holding} 天 ({df[df['holding_days']==max_holding]['symbol'].values[0]})")
    print(f"最短持仓          : {min_holding} 天 ({df[df['holding_days']==min_holding]['symbol'].values[0]})")
    
    # 持仓风格判断
    print(f"\n💡 交易风格:")
    if avg_holding < 10:
        print(f"   📊 超短线交易者（平均{avg_holding:.0f}天）")
    elif avg_holding < 30:
        print(f"   📊 短线交易者（平均{avg_holding:.0f}天）")
    elif avg_holding < 90:
        print(f"   📊 中线投资者（平均{avg_holding:.0f}天）")
    else:
        print(f"   📊 长线投资者（平均{avg_holding:.0f}天）")
    
    # ==================== 4. 最佳与最差交易 ====================
    print("\n【四、最佳与最差交易】")
    print("-"*80)
    
    best_trade = df.loc[df['pnl'].idxmax()]
    worst_trade = df.loc[df['pnl'].idxmin()]
    
    print(f"最佳交易:")
    print(f"  股票: {best_trade['symbol']}")
    print(f"  盈利: ¥{best_trade['pnl']:,.2f} ({best_trade['return_pct']:.2f}%)")
    print(f"  持仓: {best_trade['holding_days']} 天")
    
    print(f"\n最差交易:")
    print(f"  股票: {worst_trade['symbol']}")
    print(f"  亏损: ¥{worst_trade['pnl']:,.2f} ({worst_trade['return_pct']:.2f}%)")
    print(f"  持仓: {worst_trade['holding_days']} 天")
    
    # ==================== 5. 交易明细 ====================
    print("\n【五、所有交易明细】")
    print("-"*80)
    
    display_df = df[['symbol', 'entry_date', 'exit_date', 'holding_days', 
                     'entry_price', 'exit_price', 'return_pct', 'pnl']].copy()
    display_df['entry_date'] = display_df['entry_date'].dt.strftime('%Y-%m-%d')
    display_df['exit_date'] = display_df['exit_date'].dt.strftime('%Y-%m-%d')
    display_df = display_df.sort_values('pnl', ascending=False)
    
    print(display_df.to_string(index=False))
    
    # ==================== 6. 问题诊断 ====================
    print("\n【六、问题诊断与建议】")
    print("-"*80)
    
    issues = []
    recommendations = []
    
    # 胜率问题
    if win_rate < 50:
        issues.append(f"⚠️  胜率偏低（{win_rate:.1f}%）")
        recommendations.append("建议：加强选股研究，提高买入时机把握")
    
    # 盈亏比问题
    if profit_loss_ratio < 1.5:
        issues.append(f"⚠️  盈亏比偏低（{profit_loss_ratio:.2f}）")
        recommendations.append("建议：让利润奔跑，及时止损，避免小赚大亏")
    
    # 大额亏损
    big_losses = df[df['pnl'] < -10000]
    if len(big_losses) > 0:
        issues.append(f"⚠️  有{len(big_losses)}笔大额亏损（>¥10,000）")
        recommendations.append("建议：设置严格止损线，单笔亏损不超过总资金的5%")
    
    # 长期套牢
    long_losing = df[(df['holding_days'] > 60) & (df['pnl'] < 0)]
    if len(long_losing) > 0:
        issues.append(f"⚠️  有{len(long_losing)}笔长期亏损交易（>60天）")
        recommendations.append("建议：避免死扛，及时认错止损")
    
    # 频繁交易
    if avg_holding < 5:
        issues.append(f"⚠️  持仓周期过短（平均{avg_holding:.1f}天）")
        recommendations.append("建议：减少交易频率，降低交易成本")
    
    if issues:
        print("发现的问题:")
        for issue in issues:
            print(f"  {issue}")
        print("\n改进建议:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    else:
        print("✅ 交易表现良好，继续保持！")
    
    # ==================== 7. 期望收益计算 ====================
    print("\n【七、期望收益分析】")
    print("-"*80)
    
    expected_return = (win_rate/100) * avg_win - ((100-win_rate)/100) * avg_loss
    
    print(f"期望收益          : ¥{expected_return:.2f}")
    print(f"\n💡 解读:")
    if expected_return > 0:
        print(f"   ✅ 你的交易系统具有正期望，长期来看会盈利")
        print(f"   每交易一次，平均期望赚 ¥{expected_return:.2f}")
    else:
        print(f"   ⚠️  你的交易系统期望为负，长期来看会亏损")
        print(f"   需要提高胜率或盈亏比，才能实现稳定盈利")
    
    print("\n" + "="*80)
    print(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n这是一个演示，展示你输入历史交易后会得到什么信息\n")
    analyze_trades_detailed(demo_trades)
    
    print("\n" + "="*80)
    print("如何使用？".center(80))
    print("="*80)
    print("""
1. 打开 my_trades.py 文件
2. 填入你的真实交易记录
3. 运行：python my_trades.py
4. 你会得到类似上面的详细分析报告

报告会告诉你：
✅ 你的胜率和盈亏比
✅ 交易风格（短线/中线/长线）
✅ 最赚钱和最亏钱的交易
✅ 期望收益（你的交易系统是否赚钱）
✅ 存在的问题和改进建议
    """)
