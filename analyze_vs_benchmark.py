#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
对比个人交易表现与沪深300基准
计算夏普比率、Beta系数、超额收益等指标
"""

import pandas as pd
import numpy as np
from datetime import datetime
import akshare as ak
from collections import defaultdict


def load_trades(file_path):
    """加载交易数据"""
    df = pd.read_excel(file_path)
    df['发生日期'] = pd.to_datetime(df['发生日期'], format='%Y%m%d')
    df = df[df['买卖类别'].isin(['证券买入', '证券卖出'])].copy()
    df = df.sort_values('发生日期')
    return df


def calculate_daily_portfolio_value(trades_df, start_date, end_date):
    """
    计算每日组合价值
    简化版本：基于已完成交易计算累计收益
    """
    # 匹配买卖交易
    holdings = defaultdict(list)
    daily_cash = {}
    initial_cash = 100000  # 假设初始资金10万
    
    # 生成日期序列
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 初始化每日现金
    for date in date_range:
        daily_cash[date] = initial_cash
    
    cumulative_pnl = 0
    
    for _, row in trades_df.iterrows():
        date = row['发生日期']
        price = row['成交价格']
        quantity = abs(row['成交数量'])
        code = row['证券代码']
        
        if row['买卖类别'] == '证券买入':
            holdings[code].append({
                'price': price,
                'quantity': quantity,
                'date': date
            })
        elif row['买卖类别'] == '证券卖出':
            # 计算盈亏
            remaining = quantity
            while remaining > 0 and holdings[code]:
                buy = holdings[code][0]
                if buy['quantity'] <= remaining:
                    pnl = (price - buy['price']) * buy['quantity']
                    cumulative_pnl += pnl
                    remaining -= buy['quantity']
                    holdings[code].pop(0)
                else:
                    pnl = (price - buy['price']) * remaining
                    cumulative_pnl += pnl
                    buy['quantity'] -= remaining
                    remaining = 0
        
        # 更新该日期之后的所有现金
        for d in date_range:
            if d >= date:
                daily_cash[d] = initial_cash + cumulative_pnl
    
    return pd.Series(daily_cash)


def get_hs300_data(start_date, end_date):
    """
    获取沪深300指数数据
    """
    try:
        print("正在获取沪深300指数数据...")
        # 使用akshare获取沪深300指数
        df = ak.stock_zh_index_daily(symbol="sh000300")
        
        # 转换日期格式
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # 筛选日期范围
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        
        print(f"✅ 成功获取 {len(df)} 天的沪深300数据")
        return df['close']
    except Exception as e:
        print(f"❌ 获取沪深300数据失败: {e}")
        print("提示: 请确保已安装akshare: pip install akshare")
        return None


def calculate_returns(prices):
    """计算收益率序列"""
    return prices.pct_change().dropna()


def calculate_sharpe_ratio(returns, risk_free_rate=0.03):
    """
    计算夏普比率
    
    Args:
        returns: 收益率序列
        risk_free_rate: 无风险利率（年化）
    """
    if len(returns) == 0 or returns.std() == 0:
        return 0.0
    
    # 年化收益率
    annual_return = returns.mean() * 252
    # 年化波动率
    annual_std = returns.std() * np.sqrt(252)
    
    # 夏普比率
    sharpe = (annual_return - risk_free_rate) / annual_std
    return sharpe


def calculate_beta(portfolio_returns, benchmark_returns):
    """
    计算Beta系数
    
    Beta = Cov(组合收益, 基准收益) / Var(基准收益)
    """
    # 对齐数据
    aligned = pd.DataFrame({
        'portfolio': portfolio_returns,
        'benchmark': benchmark_returns
    }).dropna()
    
    if len(aligned) < 2:
        return 0.0
    
    covariance = aligned['portfolio'].cov(aligned['benchmark'])
    benchmark_variance = aligned['benchmark'].var()
    
    if benchmark_variance == 0:
        return 0.0
    
    beta = covariance / benchmark_variance
    return beta


def calculate_alpha(portfolio_returns, benchmark_returns, risk_free_rate=0.03):
    """
    计算Alpha（超额收益）
    
    Alpha = 组合收益 - [无风险利率 + Beta × (基准收益 - 无风险利率)]
    """
    # 计算年化收益率
    portfolio_annual = portfolio_returns.mean() * 252
    benchmark_annual = benchmark_returns.mean() * 252
    
    # 计算Beta
    beta = calculate_beta(portfolio_returns, benchmark_returns)
    
    # 计算Alpha
    alpha = portfolio_annual - (risk_free_rate + beta * (benchmark_annual - risk_free_rate))
    
    return alpha


def calculate_max_drawdown(prices):
    """计算最大回撤"""
    cummax = prices.cummax()
    drawdown = (prices - cummax) / cummax
    return drawdown.min()


def calculate_information_ratio(portfolio_returns, benchmark_returns):
    """
    计算信息比率
    IR = (组合收益 - 基准收益) / 跟踪误差
    """
    aligned = pd.DataFrame({
        'portfolio': portfolio_returns,
        'benchmark': benchmark_returns
    }).dropna()
    
    if len(aligned) < 2:
        return 0.0
    
    excess_returns = aligned['portfolio'] - aligned['benchmark']
    
    if excess_returns.std() == 0:
        return 0.0
    
    ir = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    return ir


def main():
    print("\n" + "="*100)
    print("个人交易表现 vs 沪深300基准对比分析".center(100))
    print("="*100)
    
    # 加载交易数据
    file_path = "dataset/交易明细近3个月.xlsx"
    print("\n正在加载交易数据...")
    trades_df = load_trades(file_path)
    
    start_date = trades_df['发生日期'].min()
    end_date = trades_df['发生日期'].max()
    
    print(f"✅ 交易数据加载完成")
    print(f"   分析周期: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
    print(f"   交易天数: {(end_date - start_date).days} 天")
    
    # 计算个人组合价值
    print("\n正在计算个人组合表现...")
    portfolio_values = calculate_daily_portfolio_value(trades_df, start_date, end_date)
    portfolio_returns = calculate_returns(portfolio_values)
    
    # 获取沪深300数据
    hs300_prices = get_hs300_data(start_date, end_date)
    
    if hs300_prices is None:
        print("\n⚠️  无法获取沪深300数据，分析终止")
        return
    
    # 归一化沪深300（以初始值为基准）
    hs300_normalized = hs300_prices / hs300_prices.iloc[0] * 100000
    hs300_returns = calculate_returns(hs300_prices)
    
    # 对齐日期
    common_dates = portfolio_values.index.intersection(hs300_normalized.index)
    portfolio_values_aligned = portfolio_values[common_dates]
    hs300_aligned = hs300_normalized[common_dates]
    
    print(f"✅ 数据对齐完成，共 {len(common_dates)} 个交易日")
    
    # ==================== 计算指标 ====================
    print("\n" + "="*100)
    print("【一、收益率对比】")
    print("-"*100)
    
    # 总收益率
    portfolio_total_return = (portfolio_values_aligned.iloc[-1] - portfolio_values_aligned.iloc[0]) / portfolio_values_aligned.iloc[0]
    hs300_total_return = (hs300_aligned.iloc[-1] - hs300_aligned.iloc[0]) / hs300_aligned.iloc[0]
    excess_return = portfolio_total_return - hs300_total_return
    
    print(f"个人组合总收益率    : {portfolio_total_return:>8.2%}")
    print(f"沪深300总收益率     : {hs300_total_return:>8.2%}")
    print(f"超额收益率          : {excess_return:>8.2%}", end="")
    if excess_return > 0:
        print(" ✅ 跑赢大盘")
    else:
        print(" ⚠️  跑输大盘")
    
    # 年化收益率
    days = (end_date - start_date).days
    portfolio_annual = (1 + portfolio_total_return) ** (365 / days) - 1
    hs300_annual = (1 + hs300_total_return) ** (365 / days) - 1
    
    print(f"\n个人组合年化收益率  : {portfolio_annual:>8.2%}")
    print(f"沪深300年化收益率   : {hs300_annual:>8.2%}")
    
    # ==================== 风险指标 ====================
    print("\n" + "="*100)
    print("【二、风险指标对比】")
    print("-"*100)
    
    # 波动率
    portfolio_volatility = portfolio_returns.std() * np.sqrt(252)
    hs300_volatility = hs300_returns.std() * np.sqrt(252)
    
    print(f"个人组合年化波动率  : {portfolio_volatility:>8.2%}")
    print(f"沪深300年化波动率   : {hs300_volatility:>8.2%}")
    
    # 最大回撤
    portfolio_mdd = calculate_max_drawdown(portfolio_values_aligned)
    hs300_mdd = calculate_max_drawdown(hs300_aligned)
    
    print(f"\n个人组合最大回撤    : {portfolio_mdd:>8.2%}")
    print(f"沪深300最大回撤     : {hs300_mdd:>8.2%}")
    
    # ==================== 夏普比率 ====================
    print("\n" + "="*100)
    print("【三、夏普比率对比】")
    print("-"*100)
    
    portfolio_sharpe = calculate_sharpe_ratio(portfolio_returns)
    hs300_sharpe = calculate_sharpe_ratio(hs300_returns)
    
    print(f"个人组合夏普比率    : {portfolio_sharpe:>8.2f}")
    print(f"沪深300夏普比率     : {hs300_sharpe:>8.2f}")
    
    print(f"\n💡 解读:")
    if portfolio_sharpe > hs300_sharpe:
        print(f"   ✅ 你的夏普比率({portfolio_sharpe:.2f})高于沪深300({hs300_sharpe:.2f})")
        print(f"   说明你的风险调整后收益更优")
    else:
        print(f"   ⚠️  你的夏普比率({portfolio_sharpe:.2f})低于沪深300({hs300_sharpe:.2f})")
        print(f"   说明承担的风险相对收益不够理想")
    
    if portfolio_sharpe > 1:
        print(f"   ✅ 夏普比率>1，风险收益比良好")
    elif portfolio_sharpe > 0.5:
        print(f"   ⚡ 夏普比率在0.5-1之间，风险收益比一般")
    else:
        print(f"   ⚠️  夏普比率<0.5，需要优化风险控制")
    
    # ==================== Beta系数 ====================
    print("\n" + "="*100)
    print("【四、Beta系数分析】")
    print("-"*100)
    
    beta = calculate_beta(portfolio_returns, hs300_returns)
    
    print(f"Beta系数            : {beta:>8.2f}")
    
    print(f"\n💡 解读:")
    if beta > 1:
        print(f"   ⚡ Beta={beta:.2f} > 1，你的组合波动大于市场")
        print(f"   市场涨1%，你的组合预期涨{beta:.2f}%")
        print(f"   市场跌1%，你的组合预期跌{beta:.2f}%")
        print(f"   属于进攻型组合，适合牛市")
    elif beta > 0.8:
        print(f"   ✅ Beta={beta:.2f}，你的组合与市场波动接近")
        print(f"   市场涨1%，你的组合预期涨{beta:.2f}%")
        print(f"   属于均衡型组合")
    else:
        print(f"   ✅ Beta={beta:.2f} < 0.8，你的组合波动小于市场")
        print(f"   市场涨1%，你的组合预期涨{beta:.2f}%")
        print(f"   属于防御型组合，适合震荡市")
    
    # ==================== Alpha ====================
    print("\n" + "="*100)
    print("【五、Alpha（超额收益）分析】")
    print("-"*100)
    
    alpha = calculate_alpha(portfolio_returns, hs300_returns)
    
    print(f"Alpha（年化）       : {alpha:>8.2%}")
    
    print(f"\n💡 解读:")
    if alpha > 0:
        print(f"   ✅ Alpha={alpha:.2%} > 0，你创造了超额收益")
        print(f"   扣除市场风险后，你每年额外获得{alpha:.2%}的收益")
        print(f"   说明你的选股能力或择时能力优秀")
    else:
        print(f"   ⚠️  Alpha={alpha:.2%} < 0，未能创造超额收益")
        print(f"   扣除市场风险后，你每年损失{abs(alpha):.2%}的收益")
        print(f"   建议优化选股策略或直接买指数基金")
    
    # ==================== 信息比率 ====================
    print("\n" + "="*100)
    print("【六、信息比率（IR）分析】")
    print("-"*100)
    
    ir = calculate_information_ratio(portfolio_returns, hs300_returns)
    
    print(f"信息比率（IR）      : {ir:>8.2f}")
    
    print(f"\n💡 解读:")
    print(f"   信息比率衡量单位跟踪误差带来的超额收益")
    if ir > 0.5:
        print(f"   ✅ IR={ir:.2f} > 0.5，主动管理能力优秀")
    elif ir > 0:
        print(f"   ⚡ IR={ir:.2f}，主动管理能力一般")
    else:
        print(f"   ⚠️  IR={ir:.2f} < 0，主动管理未创造价值")
    
    # ==================== 综合评价 ====================
    print("\n" + "="*100)
    print("【七、综合评价】")
    print("-"*100)
    
    score = 0
    
    # 收益率评分
    if excess_return > 0.05:
        score += 3
        print("✅ 收益率: 显著跑赢大盘 (+3分)")
    elif excess_return > 0:
        score += 2
        print("✅ 收益率: 跑赢大盘 (+2分)")
    else:
        score += 0
        print("⚠️  收益率: 跑输大盘 (0分)")
    
    # 夏普比率评分
    if portfolio_sharpe > hs300_sharpe and portfolio_sharpe > 1:
        score += 3
        print("✅ 夏普比率: 优于大盘且>1 (+3分)")
    elif portfolio_sharpe > hs300_sharpe:
        score += 2
        print("✅ 夏普比率: 优于大盘 (+2分)")
    else:
        score += 0
        print("⚠️  夏普比率: 不如大盘 (0分)")
    
    # Alpha评分
    if alpha > 0.05:
        score += 3
        print("✅ Alpha: 显著正超额收益 (+3分)")
    elif alpha > 0:
        score += 2
        print("✅ Alpha: 正超额收益 (+2分)")
    else:
        score += 0
        print("⚠️  Alpha: 负超额收益 (0分)")
    
    # 最大回撤评分
    if portfolio_mdd > hs300_mdd:
        score += 0
        print("⚠️  最大回撤: 大于大盘 (0分)")
    else:
        score += 1
        print("✅ 最大回撤: 小于大盘 (+1分)")
    
    print(f"\n{'='*100}")
    print(f"综合得分: {score}/10 分")
    
    if score >= 8:
        print("🏆 评级: 优秀 - 你的交易表现显著优于市场")
    elif score >= 6:
        print("✅ 评级: 良好 - 你的交易表现优于市场")
    elif score >= 4:
        print("⚡ 评级: 一般 - 你的交易表现与市场持平")
    else:
        print("⚠️  评级: 需改进 - 建议优化策略或考虑指数投资")
    
    # ==================== 建议 ====================
    print("\n" + "="*100)
    print("【八、改进建议】")
    print("-"*100)
    
    if alpha < 0:
        print("1. Alpha为负，建议:")
        print("   - 优化选股策略，提高选股质量")
        print("   - 或考虑直接投资沪深300指数基金")
    
    if portfolio_sharpe < hs300_sharpe:
        print("2. 夏普比率低于大盘，建议:")
        print("   - 降低组合波动率（分散投资、控制仓位）")
        print("   - 提高收益率（优化止盈止损策略）")
    
    if beta > 1.2:
        print("3. Beta较高，建议:")
        print("   - 降低高波动股票的仓位")
        print("   - 增加防御性股票配置")
    
    if portfolio_mdd < -0.15:
        print("4. 最大回撤较大，建议:")
        print("   - 设置严格止损线")
        print("   - 控制单笔交易仓位")
        print("   - 增加仓位管理纪律")
    
    print("\n" + "="*100)
    print(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
