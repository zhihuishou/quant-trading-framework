import sys
sys.path.append('..')

from src.data import DataLoader
from src.strategy import BaseStrategy
from src.backtest import BacktestEngine
from src.utils import calculate_ma
import pandas as pd

class SimpleMAStrategy(BaseStrategy):
    """简单双均线策略"""
    
    def __init__(self, short_window=20, long_window=50):
        super().__init__("双均线策略")
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signals(self, data):
        """生成交易信号"""
        short_ma = calculate_ma(data['Close'], self.short_window)
        long_ma = calculate_ma(data['Close'], self.long_window)
        
        signals = pd.Series(0, index=data.index)
        signals[short_ma > long_ma] = 1  # 金叉买入
        signals[short_ma < long_ma] = -1  # 死叉卖出
        
        return signals

if __name__ == "__main__":
    # 加载数据
    loader = DataLoader()
    data = loader.load_stock_data("AAPL", "2023-01-01", "2024-01-01")
    
    # 创建策略
    strategy = SimpleMAStrategy(short_window=20, long_window=50)
    signals = strategy.generate_signals(data)
    
    # 运行回测
    engine = BacktestEngine(initial_capital=100000)
    results = engine.run(data, signals)
    
    # 打印结果
    print(f"\n{'='*50}")
    print(f"策略: {strategy.name}")
    print(f"{'='*50}")
    print(f"初始资金: ${results['initial_capital']:,.2f}")
    print(f"最终资金: ${results['final_value']:,.2f}")
    print(f"总收益率: {results['total_return']*100:.2f}%")
    print(f"夏普比率: {results['sharpe_ratio']:.2f}")
    print(f"交易次数: {results['num_trades']}")
    print(f"{'='*50}\n")
