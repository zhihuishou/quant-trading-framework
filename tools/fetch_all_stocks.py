#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
获取所有A股近300日的历史数据
测试akshare批量获取能力
"""

import akshare as ak
import pandas as pd
import time
from datetime import datetime, timedelta
import os

def get_all_stock_list():
    """获取所有A股列表"""
    print("正在获取所有A股列表...")
    try:
        # 方法1: 使用stock_zh_a_spot_em
        df = ak.stock_zh_a_spot_em()
        print(f"✅ 成功获取 {len(df)} 只A股")
        return df[['代码', '名称']].values.tolist()
    except Exception as e:
        print(f"⚠️  方法1失败: {e}")
        
        # 方法2: 使用stock_info_a_code_name
        try:
            df = ak.stock_info_a_code_name()
            print(f"✅ 成功获取 {len(df)} 只A股")
            return df[['code', 'name']].values.tolist()
        except Exception as e2:
            print(f"❌ 方法2也失败: {e2}")
            return None

def fetch_stock_data(code, name, days=300):
    """获取单只股票的历史数据"""
    try:
        # 获取历史数据
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
        
        if df is not None and len(df) > 0:
            # 只保留最近N天
            df = df.tail(days)
            return df
        return None
    except Exception as e:
        print(f"  ⚠️  {name}({code}) 获取失败: {e}")
        return None


def test_batch_fetch(sample_size=10, days=300):
    """测试批量获取（小样本）"""
    print("\n" + "="*80)
    print(f"测试批量获取 {sample_size} 只股票近 {days} 日数据")
    print("="*80)
    
    # 获取股票列表
    stock_list = get_all_stock_list()
    
    if stock_list is None:
        print("❌ 无法获取股票列表")
        return
    
    # 只取前N只作为测试
    test_stocks = stock_list[:sample_size]
    
    print(f"\n开始获取数据...")
    start_time = time.time()
    
    success_count = 0
    fail_count = 0
    total_records = 0
    
    for i, (code, name) in enumerate(test_stocks, 1):
        print(f"\n[{i}/{sample_size}] 正在获取 {name}({code})...")
        
        df = fetch_stock_data(code, name, days)
        
        if df is not None:
            success_count += 1
            total_records += len(df)
            print(f"  ✅ 成功获取 {len(df)} 条记录")
            print(f"     日期范围: {df['日期'].min()} ~ {df['日期'].max()}")
        else:
            fail_count += 1
        
        # 避免请求过快
        time.sleep(0.5)
    
    elapsed_time = time.time() - start_time
    
    # 统计结果
    print("\n" + "="*80)
    print("测试结果统计")
    print("="*80)
    print(f"成功获取: {success_count} 只")
    print(f"获取失败: {fail_count} 只")
    print(f"总记录数: {total_records} 条")
    print(f"耗时: {elapsed_time:.2f} 秒")
    print(f"平均每只股票: {elapsed_time/sample_size:.2f} 秒")
    
    # 估算全量获取时间
    total_stocks = len(stock_list)
    estimated_time = (elapsed_time / sample_size) * total_stocks
    estimated_hours = estimated_time / 3600
    
    print(f"\n估算全量获取 {total_stocks} 只股票:")
    print(f"  预计耗时: {estimated_time:.0f} 秒 ({estimated_hours:.2f} 小时)")
    print(f"  预计数据量: {(total_records/sample_size)*total_stocks:.0f} 条记录")


def fetch_all_stocks_full(days=300, save_path="data/all_stocks_300days.csv"):
    """完整获取所有A股数据（慎用！）"""
    print("\n" + "="*80)
    print(f"⚠️  警告: 即将获取所有A股近 {days} 日数据")
    print("="*80)
    
    # 获取股票列表
    stock_list = get_all_stock_list()
    
    if stock_list is None:
        print("❌ 无法获取股票列表")
        return
    
    total_stocks = len(stock_list)
    print(f"\n总共需要获取 {total_stocks} 只股票")
    
    # 确认
    confirm = input("\n是否继续？这可能需要数小时 (y/n): ")
    if confirm.lower() != 'y':
        print("已取消")
        return
    
    # 创建保存目录
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    print(f"\n开始获取数据...")
    start_time = time.time()
    
    all_data = []
    success_count = 0
    fail_count = 0
    
    for i, (code, name) in enumerate(stock_list, 1):
        if i % 100 == 0:
            elapsed = time.time() - start_time
            print(f"\n进度: {i}/{total_stocks} ({i/total_stocks*100:.1f}%)")
            print(f"已耗时: {elapsed/60:.1f} 分钟")
            print(f"成功: {success_count}, 失败: {fail_count}")
        
        df = fetch_stock_data(code, name, days)
        
        if df is not None:
            df['股票代码'] = code
            df['股票名称'] = name
            all_data.append(df)
            success_count += 1
        else:
            fail_count += 1
        
        # 避免请求过快
        time.sleep(0.3)
    
    # 合并数据
    if all_data:
        print("\n正在合并数据...")
        final_df = pd.concat(all_data, ignore_index=True)
        
        # 保存
        print(f"正在保存到 {save_path}...")
        final_df.to_csv(save_path, index=False, encoding='utf-8-sig')
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "="*80)
        print("完成！")
        print("="*80)
        print(f"成功获取: {success_count} 只")
        print(f"获取失败: {fail_count} 只")
        print(f"总记录数: {len(final_df)} 条")
        print(f"总耗时: {elapsed_time/60:.1f} 分钟")
        print(f"文件大小: {os.path.getsize(save_path)/1024/1024:.2f} MB")
        print(f"保存路径: {save_path}")
    else:
        print("❌ 没有获取到任何数据")

def main():
    print("\n" + "="*80)
    print("A股批量数据获取工具")
    print("="*80)
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n请选择模式:")
    print("1. 测试模式 (获取10只股票)")
    print("2. 小批量模式 (获取100只股票)")
    print("3. 完整模式 (获取所有A股，需要数小时)")
    
    choice = input("\n请输入选项 (1/2/3): ")
    
    if choice == '1':
        test_batch_fetch(sample_size=10, days=300)
    elif choice == '2':
        test_batch_fetch(sample_size=100, days=300)
    elif choice == '3':
        fetch_all_stocks_full(days=300)
    else:
        print("无效选项")

if __name__ == "__main__":
    main()
