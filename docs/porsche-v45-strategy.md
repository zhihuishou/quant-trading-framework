# 保时捷 V4.5 选股策略

## 策略概述

保时捷 V4.5 是一个多因子技术选股引擎，核心思想是通过严格的趋势、动量、波动率和乖离率筛选，找出处于最佳买入时机的强势股票。

## 策略命名

"保时捷"寓意追求速度与精准，V4.5 代表第 4.5 版本的优化迭代。

---

## 核心逻辑

### 1. 欧奈尔趋势模板 (The Template)

基于威廉·欧奈尔的 CANSLIM 理论，要求股票必须处于明确的上升趋势中：

```
条件：
- 收盘价 > MA50
- MA50 > MA150  
- MA150 > MA200
- MA200 > 20日前的MA200（MA200 向上）
```

**逻辑**：只有多条均线呈多头排列，且长期均线向上，才说明趋势健康。

---

### 2. RPS 硬指标（相对强度排名）

RPS (Relative Price Strength) 衡量股票相对于全市场的强度排名：

```
条件：
- RPS60 >= 95  或
- RPS220 >= 90
```

**解读**：
- RPS60：近 60 日涨幅排名，要求在全市场前 5%
- RPS220：近 220 日涨幅排名，要求在全市场前 10%
- 只要满足其中一个即可，兼顾短期和中期强度

**注意**：RPS 需要在预处理阶段计算全市场排名。

---

### 3. VCP 波动挤压（Volatility Contraction Pattern）

VCP 是马克·米奈尔维尼提出的经典形态，要求股票在突破前波动率收缩：

```
计算：
- H5 = 近 5 日最高价
- L5 = 近 5 日最低价
- H20 = 近 20 日最高价
- L20 = 近 20 日最低价
- VCP_Ratio = (H5 - L5) / (H20 - L20)

条件：
- VCP_Ratio < 0.45
```

**逻辑**：
- 近期波幅相对中期波幅越小，说明"弹簧"压得越紧
- 0.45 是严格的阈值（相比 V1.7 的 0.48 更加苛刻）
- 波动收缩后往往伴随突破

---

### 4. 乖离率拦截（Bias）

乖离率衡量股价偏离均线的程度，防止追高：

```
计算：
- Bias20 = (收盘价 - MA20) / MA20 × 100

条件：
- Bias20 < 12%
```

**逻辑**：
- 股价离 20 日均线太远（>12%）说明"超速"，容易回调
- 这是 V4.5 相比早期版本的核心优化，增加风控
- 拦截涨飞的票，等待回踩再介入

---

### 5. 当日涨幅限制

```
条件：
- 当日涨幅 < 7%
```

**逻辑**：
- 避免追涨停板或大幅高开的股票
- 降低买入成本，提高安全边际

---

## 评分系统

综合多个维度计算股票得分，得分越高越优先：

```python
score = (
    rps60 × 0.4 +           # RPS60 权重 40%
    rps220 × 0.3 +          # RPS220 权重 30%
    (1 - vcp_ratio) × 30 +  # VCP 压缩越紧，得分越高
    (12 - bias20) × 2       # 乖离率越低，得分越高
)
```

**权重说明**：
- 短期强度（RPS60）最重要，占 40%
- 中期强度（RPS220）次之，占 30%
- VCP 和 Bias 作为辅助因子，优化买入时机

---

## 完整代码实现

```python
import pandas as pd
import numpy as np

def porsche_v45_engine(df):
    """
    保时捷 V4.5 核心引擎
    
    优化点：
    - 加速计算（向量化）
    - 引入乖离率拦截
    - 硬核 RPS 门槛
    
    参数：
        df: DataFrame，必须包含以下字段
            - ts_code: 股票代码
            - close: 收盘价
            - high: 最高价
            - low: 最低价
            - pct_chg: 涨跌幅
            - rps60: 60日相对强度（需预先计算）
            - rps220: 220日相对强度（需预先计算）
    
    返回：
        DataFrame: 筛选后的股票，按得分降序排列
    """
    
    # 1. 向量化计算均线（比 transform 快 10 倍）
    ma_windows = [5, 20, 50, 150, 200]
    for w in ma_windows:
        df[f'ma{w}'] = df.groupby('ts_code')['close'].transform(
            lambda x: x.rolling(w).mean()
        )
    
    # 2. 计算乖离率 (Bias) - 核心风控
    # 逻辑：股价离 20 日均线太远就代表"超速"，必须拦截
    df['bias20'] = (df['close'] - df['ma20']) / df['ma20'] * 100
    
    # 3. 欧奈尔趋势模板 (The Template)
    cond_trend = (
        (df['close'] > df['ma50']) & 
        (df['ma50'] > df['ma150']) & 
        (df['ma150'] > df['ma200']) &
        (df['ma200'] > df.groupby('ts_code')['ma200'].shift(20))  # MA200 向上
    )
    
    # 4. RPS 硬指标（要求 95/90）
    # 注意：此处假设你已在预处理阶段算好了全市场的 rps60 和 rps220
    cond_rps = (df['rps60'] >= 95) | (df['rps220'] >= 90)
    
    # 5. VCP 波动挤压（更加严格的收缩比）
    # 逻辑：近期(5日)波幅与中期(20日)波幅对比，弹簧必须压得死死的
    h5 = df.groupby('ts_code')['high'].transform(lambda x: x.rolling(5).max())
    l5 = df.groupby('ts_code')['low'].transform(lambda x: x.rolling(5).min())
    h20 = df.groupby('ts_code')['high'].transform(lambda x: x.rolling(20).max())
    l20 = df.groupby('ts_code')['low'].transform(lambda x: x.rolling(20).min())
    
    df['vcp_ratio'] = (h5 - l5) / (h20 - l20 + 1e-6)
    cond_vcp = df['vcp_ratio'] < 0.45  # 相比 V1.7 版的 0.48 更加严苛
    
    # 6. 综合拦截逻辑
    # 相比 V1.7，增加了对偏离度的控制（Bias < 12%）
    mask = (
        cond_trend & 
        cond_rps & 
        cond_vcp & 
        (df['bias20'] < 12) &   # 拦截涨飞的票
        (df['pct_chg'] < 7)     # 当日涨幅不宜过大
    )
    
    # 7. 保时捷评分系统
    # 逻辑：RPS 越高、VCP 压缩越紧、乖离率越适中，得分越高
    df['score'] = (
        df['rps60'] * 0.4 + 
        df['rps220'] * 0.3 + 
        (1 - df['vcp_ratio']) * 30 +
        (12 - df['bias20']) * 2  # 乖离率越低，加分越多
    )
    
    return df[mask].sort_values(by='score', ascending=False)
```

---

## 使用示例

```python
import pandas as pd
from src.data import DataLoader

# 1. 加载数据
loader = DataLoader()
df = loader.get_all_stocks_daily(start_date='2024-01-01')

# 2. 预处理：计算 RPS
# 注意：RPS 需要全市场数据计算排名
df['rps60'] = df.groupby('trade_date')['pct_chg_60d'].rank(pct=True) * 100
df['rps220'] = df.groupby('trade_date')['pct_chg_220d'].rank(pct=True) * 100

# 3. 运行保时捷引擎
result = porsche_v45_engine(df)

# 4. 查看结果
print(result[['ts_code', 'name', 'close', 'score', 'rps60', 'rps220', 'vcp_ratio', 'bias20']].head(20))
```

---

## 策略特点

### 优势
- **多维度筛选**：趋势、动量、波动率、乖离率四重保险
- **严格门槛**：RPS 95/90 + VCP < 0.45，只选最强的票
- **风控优先**：乖离率拦截，避免追高
- **量化评分**：综合得分排序，优中选优

### 适用场景
- 牛市或震荡市中寻找强势股
- 中短线交易（持仓周期 10-60 天）
- 追求高胜率的趋势跟踪

### 局限性
- 熊市中可能选不出股票（条件过于严格）
- 需要全市场数据计算 RPS（数据量大）
- 不适合长线价值投资

---

## 参数调优建议

### 保守型（降低风险）
```python
cond_rps = (df['rps60'] >= 98) | (df['rps220'] >= 95)  # 更高的 RPS 要求
cond_vcp = df['vcp_ratio'] < 0.40  # 更严格的波动收缩
df['bias20'] < 10  # 更低的乖离率
```

### 激进型（增加机会）
```python
cond_rps = (df['rps60'] >= 90) | (df['rps220'] >= 85)  # 放宽 RPS
cond_vcp = df['vcp_ratio'] < 0.50  # 放宽波动要求
df['bias20'] < 15  # 允许更高乖离率
```

---

## 版本历史

### V4.5（当前版本）
- ✅ 引入乖离率（Bias）拦截，防止追高
- ✅ VCP 阈值从 0.48 降至 0.45，更严格
- ✅ 优化评分系统，增加乖离率权重

### V1.7（前一版本）
- VCP 阈值 0.48
- 无乖离率控制
- 评分系统较简单

---

## 相关资料

- **欧奈尔趋势模板**：《笑傲股市》（How to Make Money in Stocks）
- **VCP 形态**：马克·米奈尔维尼《超级绩效》（Trade Like a Stock Market Wizard）
- **RPS 指标**：威廉·欧奈尔 IBD 方法论

---

## 实战建议

1. **数据准备**：
   - 确保有全市场日线数据
   - 提前计算好 RPS60 和 RPS220
   - 数据需要复权处理

2. **选股时机**：
   - 每日收盘后运行一次
   - 关注得分 Top 20 的股票
   - 结合基本面做最终决策

3. **买入策略**：
   - 不要追涨，等待回踩 MA20 附近
   - 分批建仓，控制单只仓位 < 20%
   - 设置止损位（如 -8%）

4. **卖出策略**：
   - 跌破 MA50 考虑减仓
   - 止损：-8% 无条件止损
   - 止盈：+20% 可考虑部分止盈

5. **风险控制**：
   - 同时持仓不超过 5-8 只
   - 单只股票仓位 < 20%
   - 总仓位根据市场环境调整（牛市 80%，震荡 50%，熊市 20%）

---

**相关代码**：可以将此策略集成到 `src/strategy/` 目录下

**数据需求**：需要使用 `tools/fetch_all_stocks.py` 获取全市场数据
