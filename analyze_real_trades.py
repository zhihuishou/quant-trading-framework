#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析真实交易记录 - 全面评估
"""

import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict

def load_and_clean_data(file_path):
    """加载并清洗数据"""
    df = pd.read_excel(file_path)
    
    # 转换日期格式
    df['发生日期'] = pd.to_datetime(df['发生日期'], format='%Y%m%d')
    
    # 只保留证券买入和卖出
    df = df[df['买卖类别'].isin(['证券买入', '证券卖出'])].copy()
    
    # 按日期排序
    df = df.sort_values('发生日期')
    
    return df

def match_trades(df):
    """匹配买入卖出，计算每笔交易的盈亏"""
    trades = []
    holdings = defaultdict(list)  # {证券代码: [(买入价, 数量, 日期), ...]}
    
    for _, row in df.iterrows():
        code = row['证券代码']
        name = row['证券名称']
        date = row['发生日期']
        price = row['成交价格']
        quantity = abs(row['成交数量'])
        
        if row['买卖类别'] == '证券买入':
            # 记录买入
            holdings[code].append({
                'price': price,
                'quantity': quantity,
                'date': date,
                'name': name
            })
        
        elif row['买卖类别'] == '证券卖出':
            # 匹配卖出
            remaining = quantity
            
            while remaining > 0 and holdings[code]:
                buy = holdings[code][0]
                
                if buy['quantity'] <= remaining:
                    # 全部卖出这笔买入
                    pnl = (price - buy['price']) * buy['quantity']
                    trades.append({
                        'symbol': name,
                        'code': code,
                        'entry_date': buy['date'],
                        'exit_date': date,
                        'entry_price': buy['price'],
                        'exit_price': price,
                        'shares': buy['quantity'],
                        'pnl': pnl,
                        'return_pct': (price / buy['price'] - 1) * 100
                    })
                    
                    remaining -= buy['quantity']
                    holdings[code].pop(0)
                else:
                    # 部分卖出
                    pnl = (price - buy['price']) * remaining
                    trades.append({
                        'symbol': name,
                        'code': code,
                        'entry_date': buy['date'],
                        'exit_date': date,
                        'entry_price': buy['price'],
                        'exit_price': price,
                        'shares': remaining,
                        'pnl': pnl,
                        'return_pct': (price / buy['price'] - 1) * 100
                    })
                    
                    buy['quantity'] -= remaining
                    remaining = 0
    
    return pd.DataFrame(trades), holdings

def analyze_comprehensive(trades_df, holdings):
    """全面分析"""
    
    print("\n" + "="*100)
    print("你的交易全面评估报告".center(100))
    print("="*100)
    
    if len(trades_df) == 0:
        print("\n⚠️  没有找到完整的买卖配对交易")
        return
    
    # 计算持仓天数
    trades_df['holding_days'] = (trades_df['exit_date'] - trades_df['entry_date']).dt.days
    
    # 分类
    winning_trades = trades_df[trades_df['pnl'] > 0]
    losing_trades = trades_df[trades_df['pnl'] < 0]
    
    # ==================== 1. 整体表现 ====================
    print("\n【一、整体交易表现】")
    print("-"*100)
    
    total_pnl = trades_df['pnl'].sum()
    total_trades = len(trades_df)
    win_count = len(winning_trades)
    loss_count = len(losing_trades)
    win_rate = win_count / total_trades * 100 if total_trades > 0 else 0
    
    print(f"总交易次数        : {total_trades} 笔")
    print(f"盈利交易次数      : {win_count} 笔 ({win_rate:.1f}%)")
    print(f"亏损交易次数      : {loss_count} 笔 ({100-win_rate:.1f}%)")
    print(f"总盈亏金额        : ¥{total_pnl:,.2f}")
    
    if total_pnl > 0:
        print(f"                    ✅ 总体盈利")
    else:
        print(f"                    ⚠️  总体亏损")
    
    # ==================== 2. 胜率与盈亏比 ====================
    print("\n【二、胜率与盈亏比分析】")
    print("-"*100)
    
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
    
    # ==================== 3. 期望收益 ====================
    print("\n【三、期望收益分析】")
    print("-"*100)
    
    expected_return = (win_rate/100) * avg_win - ((100-win_rate)/100) * avg_loss
    
    print(f"期望收益          : ¥{expected_return:.2f}")
    print(f"\n💡 解读:")
    if expected_return > 0:
        print(f"   ✅ 你的交易系统具有正期望，长期来看会盈利")
        print(f"   每交易一次，平均期望赚 ¥{expected_return:.2f}")
    else:
        print(f"   ⚠️  你的交易系统期望为负，长期来看会亏损")
        print(f"   需要提高胜率或盈亏比，才能实现稳定盈利")
    
    # ==================== 4. 持仓周期 ====================
    print("\n【四、持仓周期分析】")
    print("-"*100)
    
    avg_holding = trades_df['holding_days'].mean()
    max_holding = trades_df['holding_days'].max()
    min_holding = trades_df['holding_days'].min()
    
    print(f"平均持仓天数      : {avg_holding:.1f} 天")
    print(f"最长持仓          : {max_holding} 天")
    print(f"最短持仓          : {min_holding} 天")
    
    print(f"\n💡 交易风格:")
    if avg_holding < 10:
        print(f"   📊 超短线交易者（平均{avg_holding:.0f}天）")
    elif avg_holding < 30:
        print(f"   📊 短线交易者（平均{avg_holding:.0f}天）")
    elif avg_holding < 90:
        print(f"   📊 中线投资者（平均{avg_holding:.0f}天）")
    else:
        print(f"   📊 长线投资者（平均{avg_holding:.0f}天）")
    
    # ==================== 5. 最佳与最差交易 ====================
    print("\n【五、最佳与最差交易】")
    print("-"*100)
    
    best_trade = trades_df.loc[trades_df['pnl'].idxmax()]
    worst_trade = trades_df.loc[trades_df['pnl'].idxmin()]
    
    print(f"最佳交易:")
    print(f"  股票: {best_trade['symbol']} ({best_trade['code']})")
    print(f"  盈利: ¥{best_trade['pnl']:,.2f} ({best_trade['return_pct']:.2f}%)")
    print(f"  持仓: {best_trade['holding_days']} 天")
    print(f"  买入: {best_trade['entry_date'].strftime('%Y-%m-%d')} @ ¥{best_trade['entry_price']:.2f}")
    print(f"  卖出: {best_trade['exit_date'].strftime('%Y-%m-%d')} @ ¥{best_trade['exit_price']:.2f}")
    
    print(f"\n最差交易:")
    print(f"  股票: {worst_trade['symbol']} ({worst_trade['code']})")
    print(f"  亏损: ¥{worst_trade['pnl']:,.2f} ({worst_trade['return_pct']:.2f}%)")
    print(f"  持仓: {worst_trade['holding_days']} 天")
    print(f"  买入: {worst_trade['entry_date'].strftime('%Y-%m-%d')} @ ¥{worst_trade['entry_price']:.2f}")
    print(f"  卖出: {worst_trade['exit_date'].strftime('%Y-%m-%d')} @ ¥{worst_trade['exit_price']:.2f}")
    
    # ==================== 6. 股票表现统计 ====================
    print("\n【六、各股票表现统计】")
    print("-"*100)
    
    stock_stats = trades_df.groupby('symbol').agg({
        'pnl': ['sum', 'count', 'mean'],
        'return_pct': 'mean'
    }).round(2)
    stock_stats.columns = ['总盈亏', '交易次数', '平均盈亏', '平均收益率%']
    stock_stats = stock_stats.sort_values('总盈亏', ascending=False)
    
    print(stock_stats.head(10).to_string())
    
    # ==================== 7. 当前持仓 ====================
    if holdings:
        print("\n【七、当前持仓】")
        print("-"*100)
        print("以下股票还有未卖出的仓位：")
        for code, positions in holdings.items():
            if positions:
                total_shares = sum(p['quantity'] for p in positions)
                avg_price = sum(p['price'] * p['quantity'] for p in positions) / total_shares
                print(f"\n{positions[0]['name']} ({code})")
                print(f"  持仓数量: {total_shares:.0f} 股")
                print(f"  平均成本: ¥{avg_price:.2f}")
                print(f"  最早买入: {min(p['date'] for p in positions).strftime('%Y-%m-%d')}")
    
    # ==================== 8. 问题诊断 ====================
    print("\n【八、问题诊断与建议】")
    print("-"*100)
    
    issues = []
    recommendations = []
    
    if win_rate < 50:
        issues.append(f"⚠️  胜率偏低（{win_rate:.1f}%）")
        recommendations.append("建议：加强选股研究，提高买入时机把握")
    
    if profit_loss_ratio < 1.5:
        issues.append(f"⚠️  盈亏比偏低（{profit_loss_ratio:.2f}）")
        recommendations.append("建议：让利润奔跑，及时止损，避免小赚大亏")
    
    big_losses = trades_df[trades_df['pnl'] < -5000]
    if len(big_losses) > 0:
        issues.append(f"⚠️  有{len(big_losses)}笔大额亏损（>¥5,000）")
        recommendations.append("建议：设置严格止损线，控制单笔亏损")
    
    if avg_holding < 3:
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
    
    print("\n" + "="*100)
    print(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100 + "\n")
    
    # 保存详细交易记录
    trades_df.to_csv('dataset/analyzed_trades.csv', index=False, encoding='utf-8-sig')
    print("✅ 详细交易记录已保存到: dataset/analyzed_trades.csv\n")

def main():
    file_path = "dataset/交易明细近3个月.xlsx"
    
    print("\n正在加载交易数据...")
    df = load_and_clean_data(file_path)
    print(f"✅ 成功加载 {len(df)} 条交易记录")
    
    print("\n正在匹配买卖交易...")
    trades_df, holdings = match_trades(df)
    print(f"✅ 成功匹配 {len(trades_df)} 笔完整交易")
    
    # 全面分析
    analyze_comprehensive(trades_df, holdings)

if __name__ == "__main__":
    main()
