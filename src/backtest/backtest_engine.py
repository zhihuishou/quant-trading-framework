import pandas as pd
import numpy as np

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = 0
        self.trades = []
        self.equity_curve = []
    
    def run(self, data, signals):
        """
        运行回测
        
        Args:
            data: 市场数据
            signals: 交易信号
        
        Returns:
            dict: 回测结果
        """
        self.capital = self.initial_capital
        self.positions = 0
        
        for i in range(len(data)):
            price = data['Close'].iloc[i]
            signal = signals.iloc[i]
            
            # 买入信号
            if signal == 1 and self.positions == 0:
                shares = int(self.capital / price)
                self.positions = shares
                self.capital -= shares * price
                self.trades.append({'date': data.index[i], 'action': 'BUY', 'price': price, 'shares': shares})
            
            # 卖出信号
            elif signal == -1 and self.positions > 0:
                self.capital += self.positions * price
                self.trades.append({'date': data.index[i], 'action': 'SELL', 'price': price, 'shares': self.positions})
                self.positions = 0
            
            # 记录权益
            equity = self.capital + self.positions * price
            self.equity_curve.append(equity)
        
        return self._calculate_metrics()
    
    def _calculate_metrics(self):
        """计算回测指标"""
        final_value = self.equity_curve[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        returns = pd.Series(self.equity_curve).pct_change().dropna()
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if len(returns) > 0 else 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'num_trades': len(self.trades)
        }
