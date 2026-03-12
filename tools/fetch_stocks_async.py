#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
异步批量获取A股数据
使用多数据源和异步并发，大幅提升获取速度
"""

import sys
sys.path.append('..')

import asyncio
import pandas as pd
import time
from datetime import datetime
import os
from src.data.multi_source_fetcher import MultiSourceFetcher, get_stock_list_from_eastmoney


def test_speed_comparison(sample_size=20, days=300):
    """
    测试异步获取速度
    """
    print("\n" + "="*80)
    print(f"异步多数据源获取速度测试 ({sample_size}只股票)")
    print("="*80)
    
    # 获取股票列表
    print("\n正在获取股票列表...")
    stock_list = get_stock_list_from_eastmoney()
    
    if not stock_list:
        print("❌ 无法获取股票列表")
        return
    
    print(f"✅ 获取到 {len(stock_list)} 只股票")
    
    # 只取前N只测试
    test_stocks = stock_list[:sample_size]
    
    # 异步获取
    print(f"\n开始异步获取 {sample_size} 只股票...")
    fetcher = MultiSourceFetcher(max_concurrent=10)
    
    start_time = time.time()
    df = fetcher.fetch_batch_sync(test_stocks, days=days)
    elapsed_time = time.time() - start_time
    
    # 统计结果
    success_count = df['证券代码'].nunique() if not df.empty else 0
    total_records = len(df)
    
    print("\n" + "="*80)
    print("测试结果")
    print("="*80)
    print(f"成功获取: {success_count}/{sample_size} 只")
    print(f"总记录数: {total_records} 条")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    print(f"平均每只: {elapsed_time/sample_size:.2f} 秒")
    print(f"速度: {sample_size/elapsed_time:.1f} 只/秒")
    
    # 数据源统计
    if not df.empty:
        print(f"\n数据源分布:")
        source_counts = df.groupby('数据源')['证券代码'].nunique()
        for source, count in source_counts.items():
            print(f"  {source}: {count} 只")
    
    # 估算全量时间
    total_stocks = len(stock_list)
    estimated_time = (elapsed_time / sample_size) * total_stocks
    estimated_minutes = estimated_time / 60
    
    print(f"\n估算全量获取 {total_stocks} 只股票:")
    print(f"  预计耗时: {estimated_time:.0f} 秒 ({estimated_minutes:.1f} 分钟)")
    print(f"  预计数据量: {(total_records/sample_size)*total_stocks:.0f} 条记录")
    
    return df



def fetch_all_stocks_async(days=300, save_path="data/all_stocks_async.csv", 
                           batch_size=100, max_concurrent=20):
    """
    异步获取所有A股数据
    
    Args:
        days: 获取天数
        save_path: 保存路径
        batch_size: 每批次数量
        max_concurrent: 最大并发数
    """
    print("\n" + "="*80)
    print(f"异步批量获取所有A股近 {days} 日数据")
    print("="*80)
    
    # 获取股票列表
    print("\n正在获取股票列表...")
    stock_list = get_stock_list_from_eastmoney()
    
    if not stock_list:
        print("❌ 无法获取股票列表")
        return
    
    total_stocks = len(stock_list)
    print(f"✅ 获取到 {total_stocks} 只股票")
    
    # 确认
    print(f"\n配置:")
    print(f"  获取天数: {days}")
    print(f"  批次大小: {batch_size}")
    print(f"  并发数: {max_concurrent}")
    
    confirm = input(f"\n是否继续？(y/n): ")
    if confirm.lower() != 'y':
        print("已取消")
        return
    
    # 创建保存目录
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # 分批获取
    fetcher = MultiSourceFetcher(max_concurrent=max_concurrent)
    all_data = []
    
    start_time = time.time()
    total_batches = (total_stocks + batch_size - 1) // batch_size
    
    for i in range(0, total_stocks, batch_size):
        batch_num = i // batch_size + 1
        batch = stock_list[i:i+batch_size]
        
        print(f"\n批次 {batch_num}/{total_batches} (股票 {i+1}-{min(i+batch_size, total_stocks)})")
        
        batch_start = time.time()
        df = fetcher.fetch_batch_sync(batch, days=days)
        batch_time = time.time() - batch_start
        
        if not df.empty:
            all_data.append(df)
            success = df['证券代码'].nunique()
            print(f"  ✅ 成功: {success}/{len(batch)} 只, 耗时: {batch_time:.1f}秒")
        else:
            print(f"  ⚠️  本批次全部失败")
        
        # 显示进度
        elapsed = time.time() - start_time
        progress = (i + batch_size) / total_stocks
        eta = (elapsed / progress - elapsed) if progress > 0 else 0
        
        print(f"  总进度: {progress*100:.1f}%, 已耗时: {elapsed/60:.1f}分钟, 预计剩余: {eta/60:.1f}分钟")
    
    # 合并并保存
    if all_data:
        print("\n正在合并数据...")
        final_df = pd.concat(all_data, ignore_index=True)
        
        print(f"正在保存到 {save_path}...")
        final_df.to_csv(save_path, index=False, encoding='utf-8-sig')
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "="*80)
        print("完成！")
        print("="*80)
        print(f"成功获取: {final_df['证券代码'].nunique()} 只")
        print(f"总记录数: {len(final_df)} 条")
        print(f"总耗时: {elapsed_time/60:.1f} 分钟")
        print(f"平均速度: {total_stocks/(elapsed_time/60):.1f} 只/分钟")
        print(f"文件大小: {os.path.getsize(save_path)/1024/1024:.2f} MB")
        print(f"保存路径: {save_path}")
        
        # 数据源统计
        print(f"\n数据源分布:")
        source_counts = final_df.groupby('数据源')['证券代码'].nunique()
        for source, count in source_counts.items():
            print(f"  {source}: {count} 只 ({count/final_df['证券代码'].nunique()*100:.1f}%)")
    else:
        print("❌ 没有获取到任何数据")


def main():
    print("\n" + "="*80)
    print("A股异步批量数据获取工具")
    print("="*80)
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n特点:")
    print("  ✅ 异步并发，速度快")
    print("  ✅ 多数据源自动切换")
    print("  ✅ 容错能力强")
    
    print("\n请选择模式:")
    print("1. 速度测试 (获取20只股票)")
    print("2. 小批量测试 (获取100只股票)")
    print("3. 完整获取 (获取所有A股)")
    
    choice = input("\n请输入选项 (1/2/3): ")
    
    if choice == '1':
        test_speed_comparison(sample_size=20, days=300)
    elif choice == '2':
        test_speed_comparison(sample_size=100, days=300)
    elif choice == '3':
        fetch_all_stocks_async(days=300, batch_size=100, max_concurrent=20)
    else:
        print("无效选项")


if __name__ == "__main__":
    main()
