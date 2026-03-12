# 多数据源异步获取方案

## 概述

为了提高A股数据获取的速度和可靠性，我们实现了多数据源+多线程/异步的获取方案。

## 数据源

### 1. 东方财富 (推荐)

**API**: `http://push2his.eastmoney.com/api/qt/stock/kline/get`

**优点**:
- 数据完整，包含所有字段
- 稳定性好
- 支持前复权

**返回字段**:
- 证券代码
- 交易时间
- 开盘价、收盘价、最高价、最低价
- 成交量(手)、成交额(千元)
- 涨跌额、涨跌幅
- 前收盘价

### 2. 新浪财经

**API**: `http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData`

**优点**:
- 历史悠久，数据稳定
- 接口简单

**缺点**:
- 不提供成交额

### 3. 腾讯财经

**API**: `http://web.ifzq.gtimg.cn/appstock/app/fqkline/get`

**优点**:
- 速度快
- 数据准确

**缺点**:
- 不提供成交额

### 4. 网易财经

**API**: `http://quotes.money.163.com/service/chddata.html`

**优点**:
- 可直接下载CSV
- 历史数据完整

**缺点**:
- 需要解析CSV格式

## 实现方案

### 方案1: 异步获取 (aiohttp)

**文件**: `src/data/multi_source_fetcher.py`

**特点**:
- 使用asyncio + aiohttp
- 最快的获取速度
- 支持多数据源自动切换

**依赖**:
```bash
pip install aiohttp
```

**使用示例**:
```python
from src.data.multi_source_fetcher import MultiSourceFetcher

fetcher = MultiSourceFetcher(max_concurrent=20)
df = fetcher.fetch_batch_sync([('000001', '平安银行')], days=300)
```

### 方案2: 多线程获取 (ThreadPoolExecutor)

**文件**: `tools/fetch_stocks_multithread.py`

**特点**:
- 使用标准库concurrent.futures
- 无需额外依赖
- 速度快，稳定性好

**使用示例**:
```bash
python tools/fetch_stocks_multithread.py
```

### 方案3: akshare (单线程)

**文件**: `tools/fetch_all_stocks.py`

**特点**:
- 使用akshare库
- 简单易用
- 速度较慢

## 性能对比

| 方案 | 20只股票耗时 | 5000只股票预计耗时 | 依赖 |
|------|-------------|-------------------|------|
| 异步(aiohttp) | ~2秒 | ~8分钟 | aiohttp |
| 多线程(20线程) | ~3秒 | ~12分钟 | 标准库 |
| akshare(单线程) | ~25秒 | ~100分钟 | akshare |

## 数据格式

所有方案统一返回以下字段的DataFrame:

```python
{
    '证券代码': str,      # 如 '000001'
    '股票名称': str,      # 如 '平安银行'
    '交易时间': str,      # 如 '2026-03-12'
    '开盘价': float,
    '收盘价': float,
    '最高价': float,
    '最低价': float,
    '前收盘价': float,
    '涨跌额': float,
    '涨跌幅': float,      # 百分比
    '成交量(手)': int,
    '成交额(千元)': float,
    '数据源': str,        # 'eastmoney', 'sina', 'tencent'
}
```

## 使用建议

### 1. 选择合适的方案

- **快速测试**: 使用多线程方案 (无需额外依赖)
- **生产环境**: 使用异步方案 (速度最快)
- **简单场景**: 使用akshare (最简单)

### 2. 并发数设置

- **测试环境**: 10-20个并发
- **生产环境**: 20-50个并发
- **注意**: 并发数过高可能被限流

### 3. 容错处理

- 多数据源自动切换
- 失败自动重试
- 记录失败的股票代码

### 4. 数据缓存

建议缓存已获取的数据，避免重复请求:

```python
# 检查本地是否有缓存
cache_file = f"data/cache/{stock_code}_{date}.csv"
if os.path.exists(cache_file):
    return pd.read_csv(cache_file)

# 获取数据
df = fetcher.fetch_stock(stock_code, stock_name)

# 保存缓存
df.to_csv(cache_file, index=False)
```

## 完整示例

### 获取单只股票

```python
from tools.fetch_stocks_multithread import MultiThreadFetcher

fetcher = MultiThreadFetcher(max_workers=20)
df = fetcher.fetch_stock('000001', '平安银行', days=300)

print(df.head())
```

### 批量获取

```python
stock_list = [
    ('000001', '平安银行'),
    ('600519', '贵州茅台'),
    ('000858', '五粮液'),
]

df = fetcher.fetch_batch(stock_list, days=300)
df.to_csv('my_stocks.csv', index=False)
```

### 获取所有A股

```bash
python tools/fetch_stocks_multithread.py
# 选择选项 3
```

## 注意事项

1. **API限流**: 注意控制请求频率，避免被封IP
2. **网络稳定**: 确保网络连接稳定
3. **数据质量**: 建议对比多个数据源验证数据准确性
4. **存储空间**: 全量数据约200MB，注意磁盘空间
5. **更新频率**: 建议每日收盘后更新一次

## 故障排查

### 问题1: 连接超时

**解决方案**:
- 增加timeout时间
- 减少并发数
- 检查网络连接

### 问题2: 数据不完整

**解决方案**:
- 切换数据源
- 检查股票代码是否正确
- 确认股票是否停牌

### 问题3: 速度慢

**解决方案**:
- 增加并发数
- 使用异步方案
- 检查网络带宽

## 未来优化

- [ ] 支持更多数据源
- [ ] 实现智能数据源选择
- [ ] 添加数据质量检查
- [ ] 支持增量更新
- [ ] 实现分布式获取
