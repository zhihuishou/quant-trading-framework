#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立的异步多数据源获取器
无需依赖其他模块，可直接运行
"""

import asyncio
import aiohttp
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os


class AsyncStockFetcher:
    """异步股票数据获取器"""
    
    def __init__(self, max_concurrent=10, timeout=10):
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_eastmoney(self, session, stock_code, days=300):
        """从东方财富获取数据"""
        try:
            if stock_code.startswith('6'):
                secid = f"1.{stock_code}"
            else:
                secid = f"0.{stock_code}"
            
            url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
            params = {
                'secid': secid,
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': '101',
                'fqt': '1',
                'lmt': days,
                'end': '20500101',
            }
            
            async with self.semaphore:
                async with session.get(url, params=params, timeout=self.timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('data') and data['data'].get('klines'):
                            klines = data['data']['klines']
                            records = []
                            
                            for line in klines:
                                parts = line.split(',')
                                records.append({
                                    '证券代码': stock_code,
                                    '交易时间': parts[0],
                                    '开盘价': float(parts[1]),
                                    '收盘价': float(parts[2]),
                                    '最高价': float(parts[3]),
                                    '最低价': float(parts[4]),
                                    '成交量(手)': int(parts[5]),
                                    '成交额(千元)': float(parts[6]) / 1000,
                                    '涨跌额': float(parts[7]),
                                    '涨跌幅': float(parts[8]),
                                    '前收盘价': float(parts[2]) - float(parts[7]),
                                })
                            
                            return pd.DataFrame(records)
        except:
            pass
        return None
    
    async def fetch_stock(self, stock_code, stock_name, days=300):
        """获取单只股票数据"""
        async with aiohttp.ClientSession() as session:
            df = await self.fetch_eastmoney(session, stock_code, days)
            
            if df is not None and len(df) > 0:
                df['股票名称'] = stock_name
                df['数据源'] = 'eastmoney'
                return df
        return None
    
    async def fetch_batch(self, stock_list, days=300):
        """批量获取"""
        tasks = [self.fetch_stock(code, name, days) for code, name in stock_list]
        results = await asyncio.gather(*tasks)
        valid = [df for df in results if df is not None]
        return pd.concat(valid, ignore_index=True) if valid else pd.DataFrame()
    
    def fetch_sync(self, stock_list, days=300):
        """同步接口"""
        return asyncio.run(self.fetch_batch(stock_list, days))


def get_stock_list():
    """获取股票列表"""
    import requests
    
    url = "http://80.push2.eastmoney.com/api/qt/clist/get"
    params = {
        'pn': '1',
        'pz': '10000',
        'po': '1',
        'np': '1',
        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
        'fltt': '2',
        'invt': '2',
        'fid': 'f3',
        'fs': 'm:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23',
        'fields': 'f12,f14',
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('data') and data['data'].get('diff'):
            return [(item['f12'], item['f14']) for item in data['data']['diff']]
    except:
        pass
    return []


def test_speed(sample_size=20, days=300):
    """速度测试"""
    print("\n" + "="*80)
    print(f"异步获取速度测试 ({sample_size}只股票)")
    print("="*80)
    
    print("\n正在获取股票列表...")
    stock_list = get_stock_list()
    
    if not stock_list:
        print("❌ 无法获取股票列表")
        return
    
    print(f"✅ 获取到 {len(stock_list)} 只股票")
    
    test_stocks = stock_list[:sample_size]
    
    print(f"\n开始异步获取...")
    fetcher = AsyncStockFetcher(max_concurrent=10)
    
    start_time = time.time()
    df = fetcher.fetch_sync(test_stocks, days=days)
    elapsed_time = time.time() - start_time
    
    success_count = df['证券代码'].nunique() if not df.empty else 0
    
    print("\n" + "="*80)
    print("测试结果")
    print("="*80)
    print(f"成功获取: {success_count}/{sample_size} 只")
    print(f"总记录数: {len(df)} 条")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    print(f"平均每只: {elapsed_time/sample_size:.2f} 秒")
    print(f"速度: {sample_size/elapsed_time:.1f} 只/秒")
    
    # 估算全量
    total = len(stock_list)
    est_time = (elapsed_time / sample_size) * total
    print(f"\n估算全量获取 {total} 只股票:")
    print(f"  预计耗时: {est_time/60:.1f} 分钟")
    
    return df


def fetch_all(days=300, save_path="data/all_stocks_async.csv", batch_size=100):
    """获取所有股票"""
    print("\n" + "="*80)
    print(f"异步批量获取所有A股近 {days} 日数据")
    print("="*80)
    
    stock_list = get_stock_list()
    if not stock_list:
        print("❌ 无法获取股票列表")
        return
    
    total = len(stock_list)
    print(f"✅ 获取到 {total} 只股票")
    
    confirm = input(f"\n是否继续？(y/n): ")
    if confirm.lower() != 'y':
        return
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    fetcher = AsyncStockFetcher(max_concurrent=20)
    all_data = []
    start_time = time.time()
    
    for i in range(0, total, batch_size):
        batch = stock_list[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total + batch_size - 1) // batch_size
        
        print(f"\n批次 {batch_num}/{total_batches}")
        df = fetcher.fetch_sync(batch, days=days)
        
        if not df.empty:
            all_data.append(df)
            print(f"  ✅ 成功: {df['证券代码'].nunique()}/{len(batch)} 只")
    
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_csv(save_path, index=False, encoding='utf-8-sig')
        
        elapsed = time.time() - start_time
        print("\n" + "="*80)
        print("完成！")
        print("="*80)
        print(f"成功: {final_df['证券代码'].nunique()} 只")
        print(f"记录数: {len(final_df)} 条")
        print(f"耗时: {elapsed/60:.1f} 分钟")
        print(f"文件: {save_path}")


if __name__ == "__main__":
    print("\nA股异步批量数据获取工具")
    print("\n1. 速度测试 (20只)")
    print("2. 小批量 (100只)")
    print("3. 完整获取 (所有)")
    
    choice = input("\n选择 (1/2/3): ")
    
    if choice == '1':
        test_speed(20, 300)
    elif choice == '2':
        test_speed(100, 300)
    elif choice == '3':
        fetch_all(300)
