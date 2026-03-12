#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速读取Excel文件"""

try:
    import pandas as pd
    df = pd.read_excel('dataset/交易明细近3个月.xlsx')
    
    print("\n文件读取成功！")
    print(f"\n数据行数: {len(df)}")
    print(f"\n列名: {list(df.columns)}")
    print("\n前10行数据:")
    print(df.head(10))
    
    # 保存为CSV方便查看
    df.to_csv('dataset/trades_preview.csv', index=False, encoding='utf-8-sig')
    print("\n已保存预览到: dataset/trades_preview.csv")
    
except Exception as e:
    print(f"\n错误: {e}")
    print("\n请确保已安装: pip install pandas openpyxl")
