"""
分析我的真实交易记录
读取Excel文件并进行全面评估
"""

import sys
import os

# 检查依赖
try:
    import pandas as pd
    import numpy as np
    from datetime import datetime
except ImportError as e:
    print(f"\n❌ 缺少必要的库: {e}")
    print("\n请先安装依赖:")
    print("pip install pandas numpy openpyxl")
    sys.exit(1)

def load_trade_data(file_path):
    """加载交易数据"""
    try:
        df = pd.read_excel(file_path)
        print(f"\n✅ 成功读取文件: {file_path}")
        print(f"📊 数据行数: {len(df)}")
        print(f"📋 列名: {df.columns.tolist()}")
        return df
    except Exception as e:
        print(f"\n❌ 读取文件失败: {e}")
        return None

def analyze_trades_comprehensive(df):
    """全面分析交易记录"""
    
    print("\n" + "="*100)
    print("你的交易全面评估报告".center(100))
    print("="*100)
    
    # 先显示原始数据的前几行
    print("\n【原始数据预览】")
    print("-"*100)
    print(df.head(10).to_string())
    
    # 根据实际列名进行分析
    # 这里需要根据你的Excel文件的实际列名来调整
    print("\n" + "="*100)
    print("\n⚠️  请根据上面的列名，告诉我以下信息对应哪些列：")
    print("1. 股票代码/名称")
    print("2. 买入日期")
    print("3. 卖出日期")
    print("4. 买入价格")
    print("5. 卖出价格")
    print("6. 交易数量")
    print("7. 盈亏金额")
    print("\n然后我可以为你做详细分析。")
    
    return df

def main():
    """主函数"""
    file_path = "dataset/交易明细近3个月.xlsx"
    
    if not os.path.exists(file_path):
        print(f"\n❌ 文件不存在: {file_path}")
        return
    
    # 加载数据
    df = load_trade_data(file_path)
    
    if df is not None:
        # 分析数据
        analyze_trades_comprehensive(df)

if __name__ == "__main__":
    main()
