import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class PortfolioAnalyzer:
    """持仓组合分析器"""
    
    def __init__(self, holdings_df, market_data_dict):
        """
        初始化持仓分析器
        
        Args:
            holdings_df: 持仓DataFrame，需包含列：
                        ['symbol', 'shares', 'cost_price', 'current_price', 'buy_date']
            market_data_dict: 市场数据字典 {symbol: price_series}
        """
        self.holdings = holdings_df.copy()
        self.market_data = market_data_dict
        self._calculate_basic_metrics()
    
    def _calculate_basic_metrics(self):
        """计算基础指标"""
        # 持仓市值
        self.holdings['market_value'] = self.holdings['shares'] * self.holdings['current_price']
        
        # 成本
        self.holdings['cost'] = self.holdings['shares'] * self.holdings['cost_price']
        
        # 盈亏
        self.holdings['pnl'] = self.holdings['market_value'] - self.holdings['cost']
        
        # 收益率
        self.holdings['return_pct'] = (self.holdings['current_price'] / self.holdings['cost_price'] - 1) * 100
        
        # 持仓天数
        self.holdings['holding_days'] = (datetime.now() - pd.to_datetime(self.holdings['buy_date'])).dt.days
        
        # 权重
        total_value = self.holdings['market_value'].sum()
        self.holdings['weight'] = self.holdings['market_value'] / total_value * 100
    
    def get_overview(self):
        """获取持仓概览"""
        total_cost = self.holdings['cost'].sum()
        total_value = self.holdings['market_value'].sum()
        total_pnl = self.holdings['pnl'].sum()
        
        overview = {
            '持仓数量': len(self.holdings),
            '总成本': f"¥{total_cost:,.2f}",
            '总市值': f"¥{total_value:,.2f}",
            '总盈亏': f"¥{total_pnl:,.2f}",
            '总收益率': f"{(total_pnl/total_cost*100):.2f}%",
            '盈利股票数': len(self.holdings[self.holdings['pnl'] > 0]),
            '亏损股票数': len(self.holdings[self.holdings['pnl'] < 0]),
        }
        
        return overview
    
    def get_position_details(self):
        """获取个股持仓明细"""
        details = self.holdings[[
            'symbol', 'shares', 'cost_price', 'current_price', 
            'market_value', 'pnl', 'return_pct', 'weight', 'holding_days'
        ]].copy()
        
        # 按收益率排序
        details = details.sort_values('return_pct', ascending=False)
        
        return details
    
    def analyze_concentration(self):
        """分析持仓集中度"""
        # 按权重排序
        sorted_holdings = self.holdings.sort_values('weight', ascending=False)
        
        top3_weight = sorted_holdings.head(3)['weight'].sum()
        top5_weight = sorted_holdings.head(5)['weight'].sum()
        
        concentration = {
            '最大持仓股票': sorted_holdings.iloc[0]['symbol'],
            '最大持仓权重': f"{sorted_holdings.iloc[0]['weight']:.2f}%",
            'Top3持仓占比': f"{top3_weight:.2f}%",
            'Top5持仓占比': f"{top5_weight:.2f}%",
            '集中度评价': self._evaluate_concentration(top3_weight),
        }
        
        return concentration
    
    def _evaluate_concentration(self, top3_weight):
        """评估集中度"""
        if top3_weight > 70:
            return "⚠️ 过度集中，风险较高"
        elif top3_weight > 50:
            return "⚡ 较为集中，需注意风险"
        elif top3_weight > 30:
            return "✅ 适度集中，较为合理"
        else:
            return "📊 分散持仓，风险较低"
    
    def analyze_risk(self):
        """风险分析"""
        # 计算组合波动率
        portfolio_volatility = self._calculate_portfolio_volatility()
        
        # 最大单股亏损
        max_loss_stock = self.holdings.loc[self.holdings['pnl'].idxmin()]
        
        # 浮亏股票占比
        losing_stocks = self.holdings[self.holdings['pnl'] < 0]
        losing_value = losing_stocks['market_value'].sum()
        total_value = self.holdings['market_value'].sum()
        
        risk_metrics = {
            '组合波动率': f"{portfolio_volatility:.2f}%",
            '最大单股亏损': f"{max_loss_stock['symbol']} ({max_loss_stock['return_pct']:.2f}%)",
            '浮亏股票占比': f"{(losing_value/total_value*100):.2f}%",
            '风险评级': self._evaluate_risk(portfolio_volatility, losing_value/total_value),
        }
        
        return risk_metrics
    
    def _calculate_portfolio_volatility(self):
        """计算组合波动率"""
        if not self.market_data:
            return 0
        
        # 计算各股票收益率
        returns_list = []
        weights = []
        
        for _, row in self.holdings.iterrows():
            symbol = row['symbol']
            if symbol in self.market_data:
                price_series = self.market_data[symbol]
                returns = price_series.pct_change().dropna()
                returns_list.append(returns)
                weights.append(row['weight'] / 100)
        
        if not returns_list:
            return 0
        
        # 构建收益率矩阵
        returns_df = pd.concat(returns_list, axis=1)
        
        # 计算协方差矩阵
        cov_matrix = returns_df.cov() * 252  # 年化
        
        # 计算组合波动率
        weights = np.array(weights)
        portfolio_var = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_vol = np.sqrt(portfolio_var) * 100
        
        return portfolio_vol
    
    def _evaluate_risk(self, volatility, losing_ratio):
        """评估风险等级"""
        risk_score = 0
        
        # 波动率评分
        if volatility > 30:
            risk_score += 3
        elif volatility > 20:
            risk_score += 2
        elif volatility > 15:
            risk_score += 1
        
        # 亏损占比评分
        if losing_ratio > 0.5:
            risk_score += 3
        elif losing_ratio > 0.3:
            risk_score += 2
        elif losing_ratio > 0.1:
            risk_score += 1
        
        if risk_score >= 5:
            return "🔴 高风险"
        elif risk_score >= 3:
            return "🟡 中等风险"
        else:
            return "🟢 低风险"
    
    def analyze_holding_period(self):
        """持仓周期分析"""
        avg_days = self.holdings['holding_days'].mean()
        max_days = self.holdings['holding_days'].max()
        min_days = self.holdings['holding_days'].min()
        
        # 按持仓时间分类
        short_term = len(self.holdings[self.holdings['holding_days'] <= 30])
        medium_term = len(self.holdings[(self.holdings['holding_days'] > 30) & (self.holdings['holding_days'] <= 90)])
        long_term = len(self.holdings[self.holdings['holding_days'] > 90])
        
        period_analysis = {
            '平均持仓天数': f"{avg_days:.0f}天",
            '最长持仓': f"{max_days}天",
            '最短持仓': f"{min_days}天",
            '短期持仓(≤30天)': f"{short_term}只",
            '中期持仓(31-90天)': f"{medium_term}只",
            '长期持仓(>90天)': f"{long_term}只",
            '持仓风格': self._evaluate_holding_style(avg_days),
        }
        
        return period_analysis
    
    def _evaluate_holding_style(self, avg_days):
        """评估持仓风格"""
        if avg_days < 10:
            return "超短线交易"
        elif avg_days < 30:
            return "短线交易"
        elif avg_days < 90:
            return "中线持仓"
        else:
            return "长线投资"
    
    def get_recommendations(self):
        """获取优化建议"""
        recommendations = []
        
        # 集中度建议
        concentration = self.analyze_concentration()
        top3_weight = float(concentration['Top3持仓占比'].rstrip('%'))
        if top3_weight > 60:
            recommendations.append("⚠️ 持仓过于集中，建议分散投资降低风险")
        
        # 亏损股票建议
        losing_stocks = self.holdings[self.holdings['return_pct'] < -20]
        if len(losing_stocks) > 0:
            recommendations.append(f"⚠️ 有{len(losing_stocks)}只股票亏损超过20%，建议评估是否止损")
        
        # 长期套牢建议
        long_losing = self.holdings[(self.holdings['holding_days'] > 180) & (self.holdings['pnl'] < 0)]
        if len(long_losing) > 0:
            recommendations.append(f"⚠️ 有{len(long_losing)}只股票长期套牢(>180天)，建议重新评估")
        
        # 盈利股票建议
        high_profit = self.holdings[self.holdings['return_pct'] > 50]
        if len(high_profit) > 0:
            recommendations.append(f"✅ 有{len(high_profit)}只股票盈利超过50%，可考虑部分止盈")
        
        # 仓位建议
        total_value = self.holdings['market_value'].sum()
        if len(self.holdings) < 3:
            recommendations.append("📊 持仓股票数量较少，可适当增加分散度")
        elif len(self.holdings) > 15:
            recommendations.append("📊 持仓股票数量较多，可能难以管理，建议精简")
        
        if not recommendations:
            recommendations.append("✅ 当前持仓结构较为合理，继续保持")
        
        return recommendations
    
    def print_full_report(self):
        """打印完整分析报告"""
        print("\n" + "="*70)
        print("持仓分析报告".center(70))
        print("="*70)
        
        # 1. 持仓概览
        print("\n【持仓概览】")
        print("-"*70)
        overview = self.get_overview()
        for key, value in overview.items():
            print(f"{key:15s}: {value}")
        
        # 2. 集中度分析
        print("\n【集中度分析】")
        print("-"*70)
        concentration = self.analyze_concentration()
        for key, value in concentration.items():
            print(f"{key:15s}: {value}")
        
        # 3. 风险分析
        print("\n【风险分析】")
        print("-"*70)
        risk = self.analyze_risk()
        for key, value in risk.items():
            print(f"{key:15s}: {value}")
        
        # 4. 持仓周期分析
        print("\n【持仓周期分析】")
        print("-"*70)
        period = self.analyze_holding_period()
        for key, value in period.items():
            print(f"{key:15s}: {value}")
        
        # 5. 个股明细（Top5和Bottom5）
        print("\n【个股表现 - Top5】")
        print("-"*70)
        details = self.get_position_details()
        print(details.head(5).to_string(index=False))
        
        print("\n【个股表现 - Bottom5】")
        print("-"*70)
        print(details.tail(5).to_string(index=False))
        
        # 6. 优化建议
        print("\n【优化建议】")
        print("-"*70)
        recommendations = self.get_recommendations()
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        print("\n" + "="*70)
        print(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")


def quick_analyze(holdings_data, market_data=None):
    """
    快速分析持仓
    
    Args:
        holdings_data: 持仓数据，可以是：
                      - DataFrame
                      - dict列表: [{'symbol': 'AAPL', 'shares': 100, ...}, ...]
        market_data: 市场数据字典（可选）
    
    Example:
        holdings = [
            {'symbol': '600519', 'shares': 100, 'cost_price': 1800, 
             'current_price': 1650, 'buy_date': '2024-01-15'},
            {'symbol': '000858', 'shares': 500, 'cost_price': 45, 
             'current_price': 52, 'buy_date': '2024-02-20'},
        ]
        quick_analyze(holdings)
    """
    if isinstance(holdings_data, list):
        holdings_df = pd.DataFrame(holdings_data)
    else:
        holdings_df = holdings_data
    
    analyzer = PortfolioAnalyzer(holdings_df, market_data or {})
    analyzer.print_full_report()
    
    return analyzer
