# 协作说明

## 项目结构

本项目由两个助手协作维护：

### 助手A（学习记录）
负责更新学习笔记和策略要点：
- `.kiro/skills/quant-learning.md` - 学习笔记和策略要点

### 助手B（代码实现）
负责代码开发和维护：
- `src/` - 核心框架代码
- `examples/` - 示例策略实现
- `tests/` - 测试代码

## 工作流程

1. 学习新策略 → 更新 `.kiro/skills/quant-learning.md`
2. 提交到Git → 另一个助手拉取更新
3. 根据笔记实现策略代码 → 提交代码
4. 循环迭代

## Git提交规范

```bash
# 学习笔记更新
git commit -m "docs: 添加[策略名称]学习笔记"

# 代码实现
git commit -m "feat: 实现[策略名称]"

# 优化改进
git commit -m "refactor: 优化[模块名称]"
```

## 分支策略

- `main` - 稳定版本
- `learning` - 学习笔记更新
- `dev` - 代码开发
