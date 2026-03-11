import pandas as pd
import numpy as np

class PerformanceMetrics:
    """量化策略性能评估指标"""
    
    def __init__(self, returns, benchmark_returns=None, risk_free_rate=0.03):
        """
        初始化
        
        Args:
            returns: 策略收益率序列
            benchmark_returns: 基准收益率序列（可选）
            risk_free_rate: 无风险利率（年化）
        """
        self.returns = returns
        self.benchmark_returns = benchmark_returns
        self.risk_free_rate = risk_free_rate
        self.trading_days = 252
    
    def total_return(self):
        """总收益率"""
        return (1 + self.returns).prod() - 1
    
    def annualized_return(self):
        """年化收益率"""
        total_ret = self.total_return()
        n_days = len(self.returns)
        return (1 + total_ret) ** (self.trading_days / n_days) - 1
    
    def volatility(self):
        """年化波动率"""
        return self.returns.std() * np.sqrt(self.trading_days)
    
    def sharpe_ratio(self):
        """夏普比率"""
        excess_return = self.annualized_return() - self.risk_free_rate
        vol = self.volatility()
        return excess_return / vol if vol != 0 else 0
    
    def max_drawdown(self):
        """最大回撤"""
        cumulative = (1 + self.returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def calmar_ratio(self):
        """卡玛比率"""
        max_dd = abs(self.max_drawdown())
        return self.annualized_return() / max_dd if max_dd != 0 else 0
    
    def sortino_ratio(self):
        """索提诺比率"""
        excess_return = self.annualized_return() - self.risk_free_rate
        downside_returns = self.returns[self.returns < 0]
        downside_vol = downside_returns.std() * np.sqrt(self.trading_days)
        return excess_return / downside_vol if downside_vol != 0 else 0
    
    def var(self, confidence=0.95):
        """风险价值 (Value at Risk)"""
        return np.percentile(self.returns, (1 - confidence) * 100)
    
    def cvar(self, confidence=0.95):
        """条件风险价值 (Conditional VaR)"""
        var_threshold = self.var(confidence)
        return self.returns[self.returns <= var_threshold].mean()
    
    def alpha(self):
        """Alpha - 相对基准的超额收益"""
        if self.benchmark_returns is None:
            return None
        strategy_ret = self.annualized_return()
        benchmark_ret = (1 + self.benchmark_returns).prod() ** (self.trading_days / len(self.benchmark_returns)) - 1
        return strategy_ret - benchmark_ret
    
    def beta(self):
        """Beta系数"""
        if self.benchmark_returns is None:
            return None
        covariance = np.cov(self.returns, self.benchmark_returns)[0][1]
        benchmark_variance = np.var(self.benchmark_returns)
        return covariance / benchmark_variance if benchmark_variance != 0 else 0
    
    def information_ratio(self):
        """信息比率"""
        if self.benchmark_returns is None:
            return None
        active_returns = self.returns - self.benchmark_returns
        tracking_error = active_returns.std() * np.sqrt(self.trading_days)
        return active_returns.mean() * self.trading_days / tracking_error if tracking_error != 0 else 0
    
    def win_rate(self):
        """胜率"""
        winning_days = (self.returns > 0).sum()
        total_days = len(self.returns)
        return winning_days / total_days if total_days > 0 else 0
    
    def profit_loss_ratio(self):
        """盈亏比"""
        winning_returns = self.returns[self.returns > 0]
        losing_returns = self.returns[self.returns < 0]
        
        avg_win = winning_returns.mean() if len(winning_returns) > 0 else 0
        avg_loss = abs(losing_returns.mean()) if len(losing_returns) > 0 else 0
        
        return avg_win / avg_loss if avg_loss != 0 else 0
    
    def expected_return(self):
        """期望收益"""
        win_rate = self.win_rate()
        pl_ratio = self.profit_loss_ratio()
        
        winning_returns = self.returns[self.returns > 0]
        losing_returns = self.returns[self.returns < 0]
        
        avg_win = winning_returns.mean() if len(winning_returns) > 0 else 0
        avg_loss = abs(losing_returns.mean()) if len(losing_returns) > 0 else 0
        
        return win_rate * avg_win - (1 - win_rate) * avg_loss
    
    def get_all_metrics(self):
        """获取所有指标"""
        metrics = {
            '总收益率': f"{self.total_return()*100:.2f}%",
            '年化收益率': f"{self.annualized_return()*100:.2f}%",
            '年化波动率': f"{self.volatility()*100:.2f}%",
            '夏普比率': f"{self.sharpe_ratio():.2f}",
            '最大回撤': f"{self.max_drawdown()*100:.2f}%",
            '卡玛比率': f"{self.calmar_ratio():.2f}",
            '索提诺比率': f"{self.sortino_ratio():.2f}",
            'VaR(95%)': f"{self.var(0.95)*100:.2f}%",
            'CVaR(95%)': f"{self.cvar(0.95)*100:.2f}%",
            '胜率': f"{self.win_rate()*100:.2f}%",
            '盈亏比': f"{self.profit_loss_ratio():.2f}",
            '期望收益': f"{self.expected_return()*100:.2f}%",
        }
        
        if self.benchmark_returns is not None:
            metrics.update({
                'Alpha': f"{self.alpha()*100:.2f}%",
                'Beta': f"{self.beta():.2f}",
                '信息比率': f"{self.information_ratio():.2f}",
            })
        
        return metrics
    
    def print_report(self):
        """打印性能报告"""
        print("\n" + "="*60)
        print("策略性能评估报告")
        print("="*60)
        
        metrics = self.get_all_metrics()
        for key, value in metrics.items():
            print(f"{key:15s}: {value}")
        
        print("="*60 + "\n")


def calculate_trade_metrics(trades_df):
    """
    计算交易相关指标
    
    Args:
        trades_df: 交易记录DataFrame，需包含列：
                  ['entry_date', 'exit_date', 'entry_price', 'exit_price', 'shares', 'pnl']
    
    Returns:
        dict: 交易指标字典
    """
    if len(trades_df) == 0:
        return {}
    
    # 盈利交易
    winning_trades = trades_df[trades_df['pnl'] > 0]
    losing_trades = trades_df[trades_df['pnl'] < 0]
    
    # 持仓时间
    trades_df['holding_days'] = (trades_df['exit_date'] - trades_df['entry_date']).dt.days
    
    metrics = {
        '总交易次数': len(trades_df),
        '盈利交易次数': len(winning_trades),
        '亏损交易次数': len(losing_trades),
        '胜率': len(winning_trades) / len(trades_df) * 100,
        '平均盈利': winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0,
        '平均亏损': abs(losing_trades['pnl'].mean()) if len(losing_trades) > 0 else 0,
        '最大单笔盈利': trades_df['pnl'].max(),
        '最大单笔亏损': trades_df['pnl'].min(),
        '平均持仓天数': trades_df['holding_days'].mean(),
        '最长持仓天数': trades_df['holding_days'].max(),
        '最短持仓天数': trades_df['holding_days'].min(),
    }
    
    # 盈亏比
    if metrics['平均亏损'] != 0:
        metrics['盈亏比'] = metrics['平均盈利'] / metrics['平均亏损']
    else:
        metrics['盈亏比'] = 0
    
    return metrics
