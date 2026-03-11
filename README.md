# 量化交易框架

一个简洁高效的Python量化交易框架，支持策略开发、回测和风险管理。

## 功能特性

- 📊 多数据源支持（股票、期货、加密货币）
- 🎯 灵活的策略开发接口
- 📈 完整的回测引擎
- ⚠️ 风险管理模块
- 📉 性能分析和可视化

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行示例策略
python examples/simple_ma_strategy.py
```

## 项目结构

- `src/data/` - 数据获取和处理模块
- `src/strategy/` - 策略基类和实现
- `src/backtest/` - 回测引擎
- `src/risk/` - 风险管理工具
- `examples/` - 示例策略代码

## 开发计划

- [x] 基础框架搭建
- [ ] 接入实时数据源
- [ ] 实盘交易接口
- [ ] 机器学习策略支持
