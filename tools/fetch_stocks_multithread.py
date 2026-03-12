#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多线程批量获取A股数据
使用标准库concurrent.futures，无需额外依赖
"""

import pandas as pd
import requests
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional
import os


class MultiThreadFetcher:
    """多线程股票数据获取器"""
    
    def __init__(self, max_workers=20, timeout=10):
        """
        Args:
            max_workers: 最大线程数
            timeout: 请求超时时间
        """
        self.max_workers = max_workers
        self.timeout = timeout
    
    def fetch_eastmoney(self, stock_code: str, days: int = 300) -> Optional[pd.DataFrame]:
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
                'klt': '101',  # 日K
                'fqt': '1',    # 前复权
                'lmt': days,
                'end': '20500101',
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
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
        except Exception as e:
            pass
        return None
    
    def fetch_stock(self, stock_code: str, stock_name: str, days: int = 300) -> Optional[pd.DataFrame]:
        """获取单只股票数据"""
        df = self.fetch_eastmoney(stock_code, days)
        
        if df is not None and len(df) > 0:
            df['股票名称'] = stock_name
            df['数据源'] = 'eastmoney'
            return df
        return None
    
    def fetch_batch(self, stock_list: List[Tuple[str, str]], days: int = 300) -> pd.DataFrame:
        """
        批量获取多只股票数据
        
        Args:
            stock_list: [(code, name), ...] 股票列表
            days: 获取天数
        
        Returns:
            合并后的DataFrame
        """
        all_data = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_stock = {
                executor.submit(self.fetch_stock, code, name, days): (code, name)
                for code, name in stock_list
            }
            
            # 收集结果
            for future in as_completed(future_to_stock):
                try:
                    df = future.result()
                    if df is not None:
                        all_data.append(df)
                except Exception as e:
                    pass
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()


def get_stock_list() -> List[Tuple[str, str]]:
    """获取所有A股列表（带重试机制）"""
    
    # 方法1: 从本地文件读取（如果存在）
    import json
    local_file = 'data/stock_list.json'
    if os.path.exists(local_file):
        try:
            with open(local_file, 'r', encoding='utf-8') as f:
                stocks = json.load(f)
            print(f"  ✅ 从本地文件加载 {len(stocks)} 只股票")
            return stocks
        except:
            pass
    
    # 方法2: 东方财富API
    for attempt in range(3):
        try:
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
            
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if data.get('data') and data['data'].get('diff'):
                stocks = [(item['f12'], item['f14']) for item in data['data']['diff']]
                print(f"  ✅ 方法2成功，获取 {len(stocks)} 只股票")
                
                # 保存到本地
                try:
                    os.makedirs('data', exist_ok=True)
                    with open(local_file, 'w', encoding='utf-8') as f:
                        json.dump(stocks, f, ensure_ascii=False)
                    print(f"  💾 已保存到 {local_file}")
                except:
                    pass
                
                return stocks
        except Exception as e:
            print(f"  ⚠️  方法2尝试 {attempt+1}/3 失败")
            time.sleep(1)
    
    # 方法3: 使用预定义的测试列表（扩展版）
    print("  ℹ️  使用预定义股票列表")
    test_stocks = generate_extended_stock_list()
    return test_stocks


def generate_extended_stock_list() -> List[Tuple[str, str]]:
    """生成扩展的股票列表（用于测试）"""
    stocks = []
    
    # 深市股票 (000001-002999)
    for i in range(1, 3000):
        code = f"{i:06d}"
        stocks.append((code, f"股票{code}"))
    
    # 沪市股票 (600000-605999)
    for i in range(600000, 606000):
        code = str(i)
        stocks.append((code, f"股票{code}"))
    
    return stocks[:5500]  # 返回5500只用于测试


def test_speed(sample_size=20, days=300, max_workers=20, save_data=True):
    """速度测试"""
    print("\n" + "="*80)
    print(f"多线程获取速度测试 ({sample_size}只股票, {max_workers}线程)")
    print("="*80)
    
    print("\n正在获取股票列表...")
    stock_list = get_stock_list()
    
    if not stock_list:
        print("❌ 无法获取股票列表")
        return None
    
    print(f"✅ 获取到 {len(stock_list)} 只股票")
    
    test_stocks = stock_list[:sample_size]
    
    print(f"\n开始多线程获取...")
    fetcher = MultiThreadFetcher(max_workers=max_workers)
    
    start_time = time.time()
    df = fetcher.fetch_batch(test_stocks, days=days)
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
    print(f"  预计耗时: {est_time/60:.1f} 分钟 ({est_time/3600:.2f} 小时)")
    print(f"  预计数据量: {(len(df)/sample_size)*total:.0f} 条记录")
    
    # 保存数据
    if save_data and not df.empty:
        os.makedirs('data', exist_ok=True)
        save_path = f"data/test_{sample_size}_stocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(save_path, index=False, encoding='utf-8-sig')
        file_size = os.path.getsize(save_path) / 1024
        print(f"\n💾 数据已保存:")
        print(f"  文件路径: {save_path}")
        print(f"  文件大小: {file_size:.2f} KB")
        
        # 显示数据预览
        print(f"\n📊 数据预览 (前5条):")
        print(df.head()[['证券代码', '股票名称', '交易时间', '收盘价', '涨跌幅']].to_string(index=False))
    
    return df


def fetch_all(days=300, save_path="data/all_stocks_multithread.csv", 
             batch_size=100, max_workers=20):
    """获取所有股票数据"""
    print("\n" + "="*80)
    print(f"多线程批量获取所有A股近 {days} 日数据")
    print("="*80)
    
    stock_list = get_stock_list()
    if not stock_list:
        print("❌ 无法获取股票列表")
        return
    
    total = len(stock_list)
    print(f"✅ 获取到 {total} 只股票")
    print(f"\n配置:")
    print(f"  获取天数: {days}")
    print(f"  批次大小: {batch_size}")
    print(f"  线程数: {max_workers}")
    
    confirm = input(f"\n是否继续？(y/n): ")
    if confirm.lower() != 'y':
        print("已取消")
        return
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    fetcher = MultiThreadFetcher(max_workers=max_workers)
    all_data = []
    start_time = time.time()
    total_batches = (total + batch_size - 1) // batch_size
    
    for i in range(0, total, batch_size):
        batch = stock_list[i:i+batch_size]
        batch_num = i // batch_size + 1
        
        print(f"\n批次 {batch_num}/{total_batches} (股票 {i+1}-{min(i+batch_size, total)})")
        
        batch_start = time.time()
        df = fetcher.fetch_batch(batch, days=days)
        batch_time = time.time() - batch_start
        
        if not df.empty:
            all_data.append(df)
            success = df['证券代码'].nunique()
            print(f"  ✅ 成功: {success}/{len(batch)} 只, 耗时: {batch_time:.1f}秒")
        else:
            print(f"  ⚠️  本批次全部失败")
        
        # 显示进度
        elapsed = time.time() - start_time
        progress = (i + batch_size) / total
        eta = (elapsed / progress - elapsed) if progress > 0 else 0
        
        print(f"  总进度: {progress*100:.1f}%, 已耗时: {elapsed/60:.1f}分钟, 预计剩余: {eta/60:.1f}分钟")
    
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
        print(f"平均速度: {total/(elapsed_time/60):.1f} 只/分钟")
        print(f"文件大小: {os.path.getsize(save_path)/1024/1024:.2f} MB")
        print(f"保存路径: {save_path}")
    else:
        print("❌ 没有获取到任何数据")


def main():
    print("\n" + "="*80)
    print("A股多线程批量数据获取工具")
    print("="*80)
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n特点:")
    print("  ✅ 多线程并发，速度快")
    print("  ✅ 使用标准库，无需额外依赖")
    print("  ✅ 自动重试，容错能力强")
    
    print("\n请选择模式:")
    print("1. 速度测试 (获取20只股票)")
    print("2. 小批量测试 (获取100只股票)")
    print("3. 中等规模 (获取1000只股票)")
    print("4. 大规模测试 (获取5000只股票) ⭐")
    print("5. 完整获取 (获取所有A股)")
    
    choice = input("\n请输入选项 (1/2/3/4/5): ")
    
    if choice == '1':
        test_speed(sample_size=20, days=300, max_workers=20)
    elif choice == '2':
        test_speed(sample_size=100, days=300, max_workers=20)
    elif choice == '3':
        test_speed(sample_size=1000, days=300, max_workers=30)
    elif choice == '4':
        test_speed(sample_size=5000, days=300, max_workers=50)
    elif choice == '5':
        fetch_all(days=300, batch_size=100, max_workers=20)
    else:
        print("无效选项")


if __name__ == "__main__":
    main()
