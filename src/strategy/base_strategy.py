from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name):
        self.name = name
        self.positions = {}
    
    @abstractmethod
    def generate_signals(self, data):
        """
        生成交易信号
        
        Args:
            data: 市场数据DataFrame
        
        Returns:
            Series: 交易信号 (1=买入, -1=卖出, 0=持有)
        """
        pass
    
    def on_bar(self, bar):
        """每个bar的回调"""
        pass
