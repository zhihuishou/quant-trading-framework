# 量化交易框架

一个简洁高效的Python量化交易框架，支持策略开发、回测和风险管理。

## 功能特性

- 📊 多数据源支持（股票、期货、加密货币）
- 🎯 灵活的策略开发接口
- 📈 完整的回测引擎
- ⚠️ 风险管理模块
- 📉 性能分析和可视化
- 💼 持仓分析工具

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 分析你的持仓

编辑 `my_portfolio.py` 文件，填入你的持仓数据：

```python
my_holdings = [
    {
        'symbol': '贵州茅台',
        'shares': 100,
        'cost_price': 1800,
        'current_price': 1650,
        'buy_date': '2024-01-15'
    },
    # 添加更多持仓...
]
```

然后运行：

```bash
python my_portfolio.py
```

你会得到一份完整的持仓分析报告，包括：
- ✅ 持仓概览（总成本、总市值、总盈亏）
- ✅ 集中度分析（风险评估）
- ✅ 风险分析（波动率、风险评级）
- ✅ 持仓周期分析
- ✅ 个股表现排名
- ✅ 优化建议

### 3. 分析你的真实交易记录

将你的交易明细Excel文件放到 `dataset/` 目录下，然后运行：

```bash
python tools/analyze_real_trades.py
```

你会得到一份全面的交易分析报告，包括：
- ✅ 胜率、盈亏比、期望收益
- ✅ 最佳/最差交易分析
- ✅ 各股票表现统计
- ✅ 当前持仓分析
- ✅ 问题诊断和改进建议

### 4. 对比基准表现

分析你的交易表现与沪深300指数的对比：

```bash
python tools/analyze_vs_benchmark.py
```

你会得到专业的投资指标：
- ✅ 夏普比率（Sharpe Ratio）
- ✅ Beta系数
- ✅ Alpha（超额收益）
- ✅ 信息比率（IR）
- ✅ 综合评分和改进建议

### 5. 批量获取A股数据

获取所有A股的历史数据用于量化回测：

```bash
python tools/fetch_all_stocks.py
```

支持三种模式：
- 测试模式（10只股票）
- 小批量模式（100只股票）
- 完整模式（5000+只股票，约2小时）

### 6. 运行示例策略

```bash
python examples/simple_ma_strategy.py
python examples/dual_momentum_demo.py
```

## 项目结构

```
quant-framework/
├── src/                # 核心框架代码
│   ├── data/          # 数据获取和处理模块
│   ├── strategy/      # 策略基类和实现
│   ├── backtest/      # 回测引擎
│   ├── risk/          # 风险管理工具
│   ├── analysis/      # 持仓分析工具
│   └── utils/         # 工具函数（技术指标、性能评估）
├── tools/             # 实用工具脚本
│   ├── analyze_real_trades.py    # 真实交易分析
│   ├── analyze_vs_benchmark.py   # 基准对比分析
│   └── fetch_all_stocks.py       # A股数据批量获取
├── examples/          # 示例策略代码
├── docs/              # 文档
│   ├── technical-indicators.md      # 技术指标说明
│   ├── portfolio-analysis-guide.md  # 持仓分析指南
│   ├── dual-momentum-strategy.md    # 双动量策略说明
│   └── macro-analysis-notes.md      # 宏观分析笔记
├── reports/           # 分析报告输出目录
│   └── trading-analysis/  # 交易分析报告
├── my_portfolio.py    # 你的持仓分析（个人使用）
├── my_trades.py       # 你的交易分析（个人使用）
└── requirements.txt   # Python依赖
```

## 实用工具

### 交易分析工具

- **真实交易分析**: 分析历史交易记录，计算胜率、盈亏比、期望收益
- **基准对比分析**: 对比沪深300，计算夏普比率、Beta、Alpha
- **A股数据获取**: 批量下载所有A股历史数据

详见：[工具使用说明](tools/README.md)

## 技术指标

框架内置12个常用技术指标：

**趋势指标**: MA, EMA, MACD, 布林带  
**动量指标**: RSI, KDJ, Momentum  
**成交量指标**: OBV, VWAP  
**波动率指标**: ATR, Historical Volatility

详见：[技术指标文档](docs/technical-indicators.md)

## 量化评估指标

完整的策略性能评估体系：

- 收益指标：总收益率、年化收益率、Alpha
- 风险指标：波动率、最大回撤、VaR、CVaR
- 风险调整收益：夏普比率、索提诺比率、卡玛比率
- 交易效率：胜率、盈亏比、期望收益

## 持仓分析

6个维度全面评估你的持仓：

1. 收益维度 - 总收益、个股表现
2. 风险维度 - 集中度、波动率、回撤
3. 结构维度 - 行业分布、市值配置
4. 时间维度 - 持仓周期、风格判断
5. 效率维度 - 换手率、资金利用率
6. 综合评级 - 100分制评分

详见：[持仓分析指南](docs/portfolio-analysis-guide.md)

## 宏观分析

记录宏观经济分析笔记：

- 费雪公式 (MV=PT)
- GDP构成公式
- 经济周期与产业分析
- 投资增速与失业率关系

详见：[宏观分析笔记](docs/macro-analysis-notes.md)

## 学习资源

- 量化学习笔记：`.kiro/skills/quant-learning.md`
- 参考书籍：《量化投资技术分析实战：解码股票与期货交易模型》

## 数据隐私

- ✅ 所有数据保存在本地
- ✅ 不会上传到任何服务器
- ✅ 你的持仓和交易数据完全私密
- ✅ `my_portfolio.py` 和 `my_trades.py` 已加入 `.gitignore`

## 开发计划

- [x] 基础框架搭建
- [x] 技术指标库
- [x] 量化评估指标
- [x] 持仓分析工具
- [ ] 接入实时数据源
- [ ] 实盘交易接口
- [ ] 机器学习策略支持
- [ ] Web可视化界面

## 协作说明

本项目支持多人协作，详见 [COLLABORATION.md](COLLABORATION.md)

## License

MIT License
