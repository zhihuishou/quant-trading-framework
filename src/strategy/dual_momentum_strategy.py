"""
二八轮动策略实现
Dual Momentum Strategy (28 Rotation)
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from .base_strategy import BaseStrategy


class DualMomentumStrategy(BaseStrategy):
    """
    二八轮动策略
    
    策略逻辑：
    1. 比较沪深300和中证500过去N个交易日的涨跌幅
    2. 选择涨幅较大的指数持有
    3. 如果两个指数均下跌，则持有国债指数
    """
    
    def __init__(self, lookback_period: int = 20):
        """
        初始化策略
        
        Args:
            lookback_period: 回看周期，默认20个交易日
        """
        super().__init__()
        self.lookback_period = lookback_period
        self.name = f"二八轮动策略(N={lookback_period})"
        
    def calculate_momentum(self, prices: pd.Series) -> float:
        """
        计算动量（涨跌幅）
        
        Args:
            prices: 价格序列
            
        Returns:
            涨跌幅百分比
        """
        if len(prices) < self.lookback_period + 1:
            return 0.0
            
        current_price = prices.iloc[-1]
        past_price = prices.iloc[-(self.lookback_period + 1)]
        
        if past_price == 0:
            return 0.0
            
        momentum = (current_price - past_price) / past_price
        return momentum
    
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        生成交易信号
        
        Args:
            data: 字典，包含各指数的价格数据
                  {'hs300': DataFrame, 'zz500': DataFrame, 'bond': DataFrame}
                  每个DataFrame需要包含'close'列
                  
        Returns:
            信号DataFrame，包含position列（'hs300', 'zz500', 'bond'）
        """
        # 确保数据对齐
        hs300 = data.get('hs300')
        zz500 = data.get('zz500')
        bond = data.get('bond')
        
        if hs300 is None or zz500 is None:
            raise ValueError("必须提供沪深300和中证500的数据")
        
        # 对齐日期
        dates = hs300.index.intersection(zz500.index)
        if bond is not None:
            dates = dates.intersection(bond.index)
        
        signals = pd.DataFrame(index=dates)
        signals['hs300_momentum'] = 0.0
        signals['zz500_momentum'] = 0.0
        signals['position'] = 'bond'  # 默认持有债券
        
        # 计算每日的动量和持仓
        for i in range(self.lookback_period, len(dates)):
            current_date = dates[i]
            
            # 获取过去N+1天的数据（包括当前日）
            hs300_prices = hs300.loc[:current_date, 'close'].iloc[-(self.lookback_period + 1):]
            zz500_prices = zz500.loc[:current_date, 'close'].iloc[-(self.lookback_period + 1):]
            
            # 计算动量
            hs300_mom = self.calculate_momentum(hs300_prices)
            zz500_mom = self.calculate_momentum(zz500_prices)
            
            signals.loc[current_date, 'hs300_momentum'] = hs300_mom
            signals.loc[current_date, 'zz500_momentum'] = zz500_mom
            
            # 决定持仓
            if hs300_mom < 0 and zz500_mom < 0:
                # 两者均下跌，持有债券
                position = 'bond'
            elif hs300_mom >= zz500_mom:
                # 沪深300涨幅更大
                position = 'hs300'
            else:
                # 中证500涨幅更大
                position = 'zz500'
            
            signals.loc[current_date, 'position'] = position
        
        return signals
    
    def backtest(self, data: Dict[str, pd.DataFrame], 
                 initial_capital: float = 100000.0) -> Dict:
        """
        回测策略
        
        Args:
            data: 各指数的价格数据
            initial_capital: 初始资金
            
        Returns:
            回测结果字典
        """
        signals = self.generate_signals(data)
        
        # 计算每日收益
        portfolio_value = [initial_capital]
        positions = []
        
        for i in range(1, len(signals)):
            prev_position = signals['position'].iloc[i-1]
            current_date = signals.index[i]
            prev_date = signals.index[i-1]
            
            # 获取对应资产的收益率
            if prev_position == 'hs300':
                asset_data = data['hs300']
            elif prev_position == 'zz500':
                asset_data = data['zz500']
            else:  # bond
                asset_data = data.get('bond')
                if asset_data is None:
                    # 如果没有债券数据，假设收益率为0
                    daily_return = 0.0
                else:
                    prev_price = asset_data.loc[prev_date, 'close']
                    current_price = asset_data.loc[current_date, 'close']
                    daily_return = (current_price - prev_price) / prev_price
            
            if prev_position != 'bond' or data.get('bond') is not None:
                if prev_position != 'bond':
                    asset_data = data[prev_position]
                    prev_price = asset_data.loc[prev_date, 'close']
                    current_price = asset_data.loc[current_date, 'close']
                    daily_return = (current_price - prev_price) / prev_price
            
            # 更新组合价值
            new_value = portfolio_value[-1] * (1 + daily_return)
            portfolio_value.append(new_value)
            positions.append(prev_position)
        
        # 添加第一天的持仓
        positions.insert(0, signals['position'].iloc[0])
        
        # 构建结果
        results = pd.DataFrame({
            'date': signals.index,
            'portfolio_value': portfolio_value,
            'position': positions,
            'hs300_momentum': signals['hs300_momentum'].values,
            'zz500_momentum': signals['zz500_momentum'].values
        })
        
        # 计算统计指标
        returns = results['portfolio_value'].pct_change().dropna()
        
        stats = {
            'total_return': (portfolio_value[-1] - initial_capital) / initial_capital,
            'annual_return': self._calculate_annual_return(results),
            'max_drawdown': self._calculate_max_drawdown(results['portfolio_value']),
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'win_rate': self._calculate_win_rate(returns),
            'turnover': self._calculate_turnover(positions)
        }
        
        return {
            'results': results,
            'stats': stats,
            'signals': signals
        }
    
    def _calculate_annual_return(self, results: pd.DataFrame) -> float:
        """计算年化收益率"""
        total_days = (results['date'].iloc[-1] - results['date'].iloc[0]).days
        total_return = (results['portfolio_value'].iloc[-1] - results['portfolio_value'].iloc[0]) / results['portfolio_value'].iloc[0]
        annual_return = (1 + total_return) ** (365 / total_days) - 1
        return annual_return
    
    def _calculate_max_drawdown(self, portfolio_values: pd.Series) -> float:
        """计算最大回撤"""
        cummax = portfolio_values.cummax()
        drawdown = (portfolio_values - cummax) / cummax
        return drawdown.min()
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.03) -> float:
        """计算夏普比率"""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        excess_return = returns.mean() * 252 - risk_free_rate
        return excess_return / (returns.std() * np.sqrt(252))
    
    def _calculate_win_rate(self, returns: pd.Series) -> float:
        """计算胜率"""
        if len(returns) == 0:
            return 0.0
        return (returns > 0).sum() / len(returns)
    
    def _calculate_turnover(self, positions: list) -> float:
        """计算换手率（年化）"""
        changes = sum(1 for i in range(1, len(positions)) if positions[i] != positions[i-1])
        return changes / len(positions) * 252
