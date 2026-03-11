"""
持仓分析示例
演示如何使用PortfolioAnalyzer分析你的持仓情况
"""

import sys
sys.path.append('..')

from src.analysis import quick_analyze

# 示例：你的持仓数据
# 你需要替换成你的实际持仓
my_holdings = [
    {
        'symbol': '贵州茅台',
        'shares': 100,           # 持股数量
        'cost_price': 1800,      # 成本价
        'current_price': 1650,   # 当前价
        'buy_date': '2024-01-15' # 买入日期
    },
    {
        'symbol': '五粮液',
        'shares': 500,
        'cost_price': 180,
        'current_price': 165,
        'buy_date': '2024-02-20'
    },
    {
        'symbol': '宁德时代',
        'shares': 200,
        'cost_price': 200,
        'current_price': 185,
        'buy_date': '2024-03-01'
    },
    {
        'symbol': '比亚迪',
        'shares': 300,
        'cost_price': 250,
        'current_price': 280,
        'buy_date': '2024-01-10'
    },
    {
        'symbol': '隆基绿能',
        'shares': 1000,
        'cost_price': 25,
        'current_price': 22,
        'buy_date': '2023-12-15'
    },
]

if __name__ == "__main__":
    print("\n开始分析持仓...")
    
    # 快速分析
    analyzer = quick_analyze(my_holdings)
    
    # 如果需要更详细的分析，可以单独调用各个方法
    # print("\n详细持仓明细：")
    # print(analyzer.get_position_details())
    
    # print("\n优化建议：")
    # for rec in analyzer.get_recommendations():
    #     print(f"- {rec}")
