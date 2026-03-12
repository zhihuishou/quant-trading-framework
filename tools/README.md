# 量化交易工具集

这个目录包含各种量化交易分析工具。

## 工具列表

### 1. analyze_real_trades.py - 真实交易分析

分析你的历史交易记录，生成全面的评估报告。

**功能**:
- 匹配买卖交易，计算盈亏
- 计算胜率、盈亏比、期望收益
- 分析持仓周期和交易风格
- 识别最佳/最差交易
- 统计各股票表现
- 诊断问题并给出改进建议

**使用方法**:
```bash
python tools/analyze_real_trades.py
```

**输入**: `dataset/交易明细近3个月.xlsx`  
**输出**: 
- 控制台打印完整报告
- `dataset/analyzed_trades.csv` - 详细交易记录

---

### 2. analyze_vs_benchmark.py - 基准对比分析

对比你的交易表现与沪深300指数，计算专业投资指标。

**功能**:
- 计算夏普比率（Sharpe Ratio）
- 计算Beta系数
- 计算Alpha（超额收益）
- 计算信息比率（Information Ratio）
- 对比收益率、波动率、最大回撤
- 综合评分和改进建议

**使用方法**:
```bash
python tools/analyze_vs_benchmark.py
```

**输入**: `dataset/交易明细近3个月.xlsx`  
**数据源**: akshare获取沪深300实时数据  
**输出**: 控制台打印完整对比报告

---

### 3. fetch_all_stocks.py - A股数据批量获取

批量获取所有A股的历史数据，用于量化回测和分析。

**功能**:
- 获取所有A股列表（5000+只）
- 批量下载近300日历史数据
- 支持测试模式、小批量模式、完整模式
- 自动保存为CSV文件

**使用方法**:
```bash
python tools/fetch_all_stocks.py
```

**模式选择**:
- 模式1: 测试模式（10只股票）
- 模式2: 小批量模式（100只股票）
- 模式3: 完整模式（所有A股，约2小时）

**输出**: `data/all_stocks_300days.csv`

---

## 依赖安装

```bash
pip install -r requirements.txt
```

主要依赖:
- pandas
- numpy
- akshare
- openpyxl

---

## 使用流程

### 个人交易分析流程

1. 准备交易数据（Excel格式）
2. 运行交易分析: `python tools/analyze_real_trades.py`
3. 运行基准对比: `python tools/analyze_vs_benchmark.py`
4. 查看生成的报告: `reports/trading-analysis/`

### 量化策略开发流程

1. 获取历史数据: `python tools/fetch_all_stocks.py`
2. 开发策略: 参考 `src/strategy/` 中的示例
3. 回测策略: 使用 `src/backtest/backtest_engine.py`
4. 评估表现: 使用 `src/utils/performance_metrics.py`

---

## 注意事项

1. **数据隐私**: 个人交易数据不会上传到GitHub（已加入.gitignore）
2. **API限制**: akshare获取数据时请注意频率限制，建议加延时
3. **数据缓存**: 建议缓存历史数据，避免重复请求
4. **网络要求**: 需要稳定的网络连接获取实时数据
