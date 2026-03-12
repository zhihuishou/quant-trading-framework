#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
找出缺失的股票并重新获取
"""

import sys
sys.path.insert(0, 'tools')

import pandas as pd
from fetch_stocks_multithread import MultiThreadFetcher, generate_extended_stock_list
import time
import os

print("\n" + "="*80)
print("分析缺失股票并重新获取")
print("="*80)

# 1. 读取已获取的数据
print("\n1. 读取已获取的数据...")
df_existing = pd.read_csv('data/stocks_5000_final.csv')
existing_codes = set(df_existing['证券代码'].unique())
print(f"   已获取: {len(existing_codes)} 只股票")

# 2. 生成目标列表
print("\n2. 生成目标股票列表...")
all_stocks = generate_extended_stock_list()
target_stocks = all_stocks[:5000]
target_codes = set([code for code, name in target_stocks])
print(f"   目标: {len(target_codes)} 只股票")

# 3. 找出缺失的
print("\n3. 找出缺失的股票...")
missing_codes = target_codes - existing_codes
missing_stocks = [(code, name) for code, name in target_stocks if code in missing_codes]
print(f"   缺失: {len(missing_stocks)} 只股票")

if len(missing_stocks) == 0:
    print("\n✅ 没有缺失的股票！")
    exit(0)

# 显示部分缺失股票
print(f"\n   前20只缺失股票:")
for i, (code, name) in enumerate(missing_stocks[:20], 1):
    print(f"   {i}. {code} - {name}")

if len(missing_stocks) > 20:
    print(f"   ... 还有 {len(missing_stocks)-20} 只")

# 4. 重新获取缺失的股票
print(f"\n4. 重新获取缺失的 {len(missing_stocks)} 只股票...")
print(f"   配置: 20线程, 超时20秒")

fetcher = MultiThreadFetcher(max_workers=20, timeout=20)

# 分批获取
batch_size = 500
all_new_data = []
total_success = 0

for i in range(0, len(missing_stocks), batch_size):
    batch = missing_stocks[i:i+batch_size]
    batch_num = i // batch_size + 1
    total_batches = (len(missing_stocks) + batch_size - 1) // batch_size
    
    print(f"\n批次 {batch_num}/{total_batches} (股票 {i+1}-{min(i+batch_size, len(missing_stocks))})")
    
    batch_start = time.time()
    df = fetcher.fetch_batch(batch, days=300)
    batch_time = time.time() - batch_start
    
    if not df.empty:
        all_new_data.append(df)
        success = df['证券代码'].nunique()
        total_success += success
        print(f"  ✅ 成功: {success}/{len(batch)} 只, 耗时: {batch_time:.1f}秒")
    else:
        print(f"  ⚠️  本批次失败")
    
    # 批次间延时
    if i + batch_size < len(missing_stocks):
        time.sleep(1)

# 5. 合并新旧数据
print(f"\n5. 合并数据...")
if all_new_data:
    df_new = pd.concat(all_new_data, ignore_index=True)
    print(f"   新获取: {total_success} 只, {len(df_new):,} 条记录")
    
    # 合并
    df_final = pd.concat([df_existing, df_new], ignore_index=True)
    
    print("\n" + "="*80)
    print("完成！")
    print("="*80)
    print(f"原有股票: {len(existing_codes)} 只")
    print(f"新增股票: {total_success} 只")
    print(f"总计股票: {df_final['证券代码'].nunique()} 只")
    print(f"总记录数: {len(df_final):,} 条")
    
    # 保存
    save_path = 'data/stocks_5000_complete.csv'
    df_final.to_csv(save_path, index=False, encoding='utf-8-sig')
    file_size = os.path.getsize(save_path) / 1024 / 1024
    
    print(f"\n💾 完整数据已保存:")
    print(f"   文件: {save_path}")
    print(f"   大小: {file_size:.2f} MB")
    
    # 统计
    final_codes = set(df_final['证券代码'].unique())
    still_missing = target_codes - final_codes
    
    print(f"\n📊 最终统计:")
    print(f"   目标: {len(target_codes)} 只")
    print(f"   已获取: {len(final_codes)} 只 ({len(final_codes)/len(target_codes)*100:.1f}%)")
    print(f"   仍缺失: {len(still_missing)} 只")
    
    if len(still_missing) > 0:
        print(f"\n   仍缺失的股票 (前20只):")
        missing_list = sorted(list(still_missing))[:20]
        for code in missing_list:
            print(f"   - {code}")
        
        # 保存缺失列表
        with open('data/still_missing_stocks.txt', 'w') as f:
            for code in sorted(still_missing):
                f.write(f"{code}\n")
        print(f"\n   完整缺失列表已保存到: data/still_missing_stocks.txt")
    
    print(f"\n✅ 全部完成！")
else:
    print("\n⚠️  没有获取到新数据")
    print(f"   仍缺失 {len(missing_stocks)} 只股票")
