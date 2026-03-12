#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接测试5000只股票获取（降低并发，避免限流）
"""

import sys
sys.path.insert(0, 'tools')

from fetch_stocks_multithread import MultiThreadFetcher, get_stock_list
import time

print("\n开始测试5000只股票获取...")
print("="*80)

# 获取股票列表
print("\n1. 获取股票列表...")
stock_list = get_stock_list()
print(f"   总共: {len(stock_list)} 只")

# 取前5000只
test_stocks = stock_list[:5000]
print(f"   测试: {len(test_stocks)} 只")

# 创建获取器（降低并发，增加超时）
print("\n2. 创建多线程获取器...")
print("   配置: 20线程, 超时20秒")
fetcher = MultiThreadFetcher(max_workers=20, timeout=20)

# 分批获取，避免一次性请求过多
print("\n3. 分批获取数据 (每批500只)...")
batch_size = 500
all_data = []
total_success = 0

for i in range(0, len(test_stocks), batch_size):
    batch = test_stocks[i:i+batch_size]
    batch_num = i // batch_size + 1
    total_batches = (len(test_stocks) + batch_size - 1) // batch_size
    
    print(f"\n   批次 {batch_num}/{total_batches} (股票 {i+1}-{min(i+batch_size, len(test_stocks))})")
    
    batch_start = time.time()
    df = fetcher.fetch_batch(batch, days=300)
    batch_time = time.time() - batch_start
    
    if not df.empty:
        all_data.append(df)
        success = df['证券代码'].nunique()
        total_success += success
        print(f"   ✅ 成功: {success}/{len(batch)} 只, 耗时: {batch_time:.1f}秒")
    else:
        print(f"   ⚠️  本批次失败")
    
    # 批次间延时，避免限流
    if i + batch_size < len(test_stocks):
        print(f"   ⏸️  等待2秒...")
        time.sleep(2)

# 合并数据
print("\n4. 合并数据...")
if all_data:
    import pandas as pd
    df = pd.concat(all_data, ignore_index=True)
    records = len(df)
    
    print("\n" + "="*80)
    print("测试结果")
    print("="*80)
    print(f"成功获取: {total_success}/{len(test_stocks)} 只 ({total_success/len(test_stocks)*100:.1f}%)")
    print(f"总记录数: {records:,} 条")
    
    # 保存数据
    import os
    os.makedirs('data', exist_ok=True)
    save_path = 'data/test_5000_stocks_final.csv'
    df.to_csv(save_path, index=False, encoding='utf-8-sig')
    file_size = os.path.getsize(save_path) / 1024 / 1024
    print(f"\n💾 数据已保存:")
    print(f"   文件: {save_path}")
    print(f"   大小: {file_size:.2f} MB")
    
    # 数据预览
    print(f"\n📊 数据预览:")
    print(df.head(10)[['证券代码', '股票名称', '交易时间', '收盘价', '涨跌幅']])
    
    print(f"\n✅ 测试完成！")
else:
    print("\n❌ 没有获取到数据")
