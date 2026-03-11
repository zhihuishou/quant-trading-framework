import numpy as np

class RiskManager:
    """风险管理器"""
    
    def __init__(self, max_position_size=0.1, stop_loss=0.05):
        self.max_position_size = max_position_size
        self.stop_loss = stop_loss
    
    def calculate_position_size(self, capital, price):
        """计算仓位大小"""
        max_shares = int(capital * self.max_position_size / price)
        return max_shares
    
    def check_stop_loss(self, entry_price, current_price):
        """检查止损"""
        loss = (current_price - entry_price) / entry_price
        return loss <= -self.stop_loss
