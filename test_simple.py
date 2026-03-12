#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简单测试"""

import sys
sys.path.insert(0, 'tools')
from fetch_stocks_multithread import MultiThreadFetcher, generate_extended_stock_list
import time

print("简单测试开始...")

# 生成股票列表
stocks = generate_extended_stock_list()
print(f"生成 {len(stocks)} 只股票代码")

# 测试前100只
test_stocks = stocks[:100]
print(f"测试前 {len(test_stocks)} 只")

# 创建获取器
fetcher = MultiThreadFetcher(max_workers=20, timeout=15)

# 获取数据
print("开始获取...")
start = time.time()
df = fetcher.fetch_batch(test_stocks, days=300)
elapsed = time.time() - start

# 结果
success = df['证券代码'].nunique() if not df.empty else 0
print(f"\n结果: {success}/{len(test_stocks)} 只")
print(f"耗时: {elapsed:.2f}秒")
print(f"记录数: {len(df)}")

if not df.empty:
    df.to_csv('data/test_simple.csv', index=False, encoding='utf-8-sig')
    print("已保存到 data/test_simple.csv")
