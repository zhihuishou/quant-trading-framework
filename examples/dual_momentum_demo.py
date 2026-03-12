"""
二八轮动策略示例
演示如何使用DualMomentumStrategy进行回测
"""

import sys
sys.path.append('..')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.strategy.dual_momentum_strategy import DualMomentumStrategy


def generate_sample_data(start_date='2020-01-01', end_date='2024-01-01'):
    """
    生成示例数据（实际使用时应该从真实数据源获取）
    """
    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    
    # 模拟沪深300数据
    hs300 = pd.DataFrame({
        'close': np.cumsum(np.random.randn(len(dates)) * 0.015 + 0.0003) + 4000
    }, index=dates)
    
    # 模拟中证500数据
    zz500 = pd.DataFrame({
        'close': np.cumsum(np.random.randn(len(dates)) * 0.018 + 0.0002) + 6000
    }, index=dates)
    
    # 模拟国债数据（波动较小）
    bond = pd.DataFrame({
        'close': np.cumsum(np.random.randn(len(dates)) * 0.002 + 0.0001) + 100
    }, index=dates)
    
    return {'hs300': hs300, 'zz500': zz500, 'bond': bond}


def main():
    print("=" * 60)
    print("二八轮动策略回测示例")
    print("=" * 60)
    
    # 生成示例数据
    print("\n1. 生成示例数据...")
    data = generate_sample_data()
    print(f"   数据期间: {data['hs300'].index[0]} 至 {data['hs300'].index[-1]}")
    print(f"   交易日数: {len(data['hs300'])}")
    
    # 初始化策略
    print("\n2. 初始化策略...")
    strategy = DualMomentumStrategy(lookback_period=20)
    print(f"   策略名称: {strategy.name}")
    print(f"   回看周期: {strategy.lookback_period}个交易日")
    
    # 运行回测
    print("\n3. 运行回测...")
    results = strategy.backtest(data, initial_capital=100000)
    
    # 显示结果
    print("\n" + "=" * 60)
    print("回测结果")
    print("=" * 60)
    
    stats = results['stats']
    print(f"\n总收益率:     {stats['total_return']:.2%}")
    print(f"年化收益率:   {stats['annual_return']:.2%}")
    print(f"最大回撤:     {stats['max_drawdown']:.2%}")
    print(f"夏普比率:     {stats['sharpe_ratio']:.2f}")
    print(f"胜率:         {stats['win_rate']:.2%}")
    print(f"年化换手率:   {stats['turnover']:.2f}次")
    
    # 持仓分布
    print("\n" + "-" * 60)
    print("持仓分布:")
    print("-" * 60)
    position_counts = results['results']['position'].value_counts()
    for pos, count in position_counts.items():
        pct = count / len(results['results']) * 100
        print(f"{pos:10s}: {count:4d}天 ({pct:.1f}%)")
    
    # 显示最近10天的信号
    print("\n" + "-" * 60)
    print("最近10天的交易信号:")
    print("-" * 60)
    recent = results['results'].tail(10)
    print(recent[['date', 'position', 'hs300_momentum', 'zz500_momentum', 'portfolio_value']].to_string(index=False))
    
    print("\n" + "=" * 60)
    print("提示: 这是使用模拟数据的示例")
    print("实际使用时请替换为真实的市场数据")
    print("=" * 60)


if __name__ == '__main__':
    main()
