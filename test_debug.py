#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

print("Step 1: 添加路径")
sys.path.insert(0, 'tools')
print(f"  sys.path: {sys.path[:3]}")

print("\nStep 2: 导入模块")
try:
    from fetch_stocks_multithread import MultiThreadFetcher, generate_extended_stock_list
    print("  ✅ 导入成功")
except Exception as e:
    print(f"  ❌ 导入失败: {e}")
    sys.exit(1)

print("\nStep 3: 生成股票列表")
try:
    stocks = generate_extended_stock_list()
    print(f"  ✅ 生成 {len(stocks)} 只")
except Exception as e:
    print(f"  ❌ 失败: {e}")
    sys.exit(1)

print("\nStep 4: 取前10只测试")
test_stocks = stocks[:10]
print(f"  测试股票: {test_stocks[:3]}")

print("\nStep 5: 创建获取器")
try:
    fetcher = MultiThreadFetcher(max_workers=5, timeout=10)
    print("  ✅ 创建成功")
except Exception as e:
    print(f"  ❌ 失败: {e}")
    sys.exit(1)

print("\nStep 6: 获取数据")
try:
    import time
    start = time.time()
    df = fetcher.fetch_batch(test_stocks, days=10)
    elapsed = time.time() - start
    print(f"  ✅ 完成，耗时 {elapsed:.2f}秒")
    print(f"  记录数: {len(df)}")
    print(f"  成功: {df['证券代码'].nunique() if not df.empty else 0}/{len(test_stocks)}")
except Exception as e:
    print(f"  ❌ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n测试完成")
