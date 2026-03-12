#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
获取5000只股票 - 最终版本
分批获取，避免限流
"""

import sys
sys.path.insert(0, 'tools')

from fetch_stocks_multithread import MultiThreadFetcher, generate_extended_stock_list
import pandas as pd
import time
import os

print("\n" + "="*80)
print("获取5000只股票数据")
print("="*80)

# 生成股票列表
print("\n1. 生成股票列表...")
stocks = generate_extended_stock_list()
test_stocks = stocks[:5000]
print(f"   目标: {len(test_stocks)} 只股票")

# 配置
batch_size = 500
max_workers = 20
timeout = 15

print(f"\n2. 配置:")
print(f"   批次大小: {batch_size} 只/批")
print(f"   线程数: {max_workers}")
print(f"   超时: {timeout}秒")
print(f"   总批次: {(len(test_stocks) + batch_size - 1) // batch_size}")

# 创建获取器
fetcher = MultiThreadFetcher(max_workers=max_workers, timeout=timeout)

# 分批获取
print(f"\n3. 开始分批获取...")
all_data = []
total_success = 0
overall_start = time.time()

for i in range(0, len(test_stocks), batch_size):
    batch = test_stocks[i:i+batch_size]
    batch_num = i // batch_size + 1
    total_batches = (len(test_stocks) + batch_size - 1) // batch_size
    
    print(f"\n批次 {batch_num}/{total_batches} (股票 {i+1}-{min(i+batch_size, len(test_stocks))})")
    
    batch_start = time.time()
    df = fetcher.fetch_batch(batch, days=300)
    batch_time = time.time() - batch_start
    
    if not df.empty:
        all_data.append(df)
        success = df['证券代码'].nunique()
        total_success += success
        print(f"  ✅ 成功: {success}/{len(batch)} 只")
        print(f"  ⏱️  耗时: {batch_time:.1f}秒")
        print(f"  📊 记录: {len(df):,} 条")
    else:
        print(f"  ⚠️  本批次失败")
    
    # 显示总进度
    progress = (i + batch_size) / len(test_stocks) * 100
    elapsed = time.time() - overall_start
    eta = (elapsed / (i + batch_size)) * (len(test_stocks) - i - batch_size)
    print(f"  📈 总进度: {progress:.1f}%, 已耗时: {elapsed:.0f}秒, 预计剩余: {eta:.0f}秒")
    
    # 批次间延时
    if i + batch_size < len(test_stocks):
        time.sleep(1)

overall_time = time.time() - overall_start

# 合并数据
print(f"\n4. 合并数据...")
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    
    print("\n" + "="*80)
    print("完成！")
    print("="*80)
    print(f"成功获取: {total_success}/{len(test_stocks)} 只 ({total_success/len(test_stocks)*100:.1f}%)")
    print(f"总记录数: {len(final_df):,} 条")
    print(f"总耗时: {overall_time:.1f} 秒 ({overall_time/60:.2f} 分钟)")
    print(f"平均速度: {total_success/overall_time:.1f} 只/秒")
    
    # 保存数据
    os.makedirs('data', exist_ok=True)
    save_path = 'data/stocks_5000_final.csv'
    final_df.to_csv(save_path, index=False, encoding='utf-8-sig')
    file_size = os.path.getsize(save_path) / 1024 / 1024
    
    print(f"\n💾 数据已保存:")
    print(f"   文件: {save_path}")
    print(f"   大小: {file_size:.2f} MB")
    
    # 数据统计
    print(f"\n📊 数据统计:")
    print(f"   股票数量: {final_df['证券代码'].nunique()}")
    print(f"   日期范围: {final_df['交易时间'].min()} ~ {final_df['交易时间'].max()}")
    print(f"   数据源: {final_df['数据源'].unique()}")
    
    # 预览
    print(f"\n📋 数据预览 (前5条):")
    print(final_df.head()[['证券代码', '股票名称', '交易时间', '收盘价', '涨跌幅']])
    
    print(f"\n✅ 全部完成！")
else:
    print("\n❌ 没有获取到任何数据")
