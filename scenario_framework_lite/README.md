# Scenario Framework Lite (挑战者方案)

> 版本: 1.0.0  
> 更新日期: 2026-01-15  
> 状态: Experimental

---

## 1. 方案概述

### 1.1 设计理念

**核心思想**：用 L1 级抽象原则 + LLM 涌现能力，替代细化的 L2/L3 规格体系。

| 维度 | 本方案 | 完整规格方案 |
|------|--------|-------------|
| 场景分类 | L1 (5类) | L1-L2-L3 (95类) |
| Keyframe 规则 | L1 原则 (5条) | L2 规则 (30条) |
| CC 规则 | L1 级通用 | L2 级模板 |
| CoC 生成 | LLM 涌现 | 模板引导 |
| 前期成本 | 低 (几天) | 高 (数周) |

### 1.2 适用场景

- ✅ 快速原型验证
- ✅ 小规模数据（< 5000 条）
- ✅ 探索性研究
- ⚠️ 大规模生产需验证一致性

### 1.3 核心假设

1. **LLM 能正确理解 L1 原则**：根据抽象原则推断具体场景的 Keyframe
2. **LLM 输出足够一致**：同类场景的处理方式相似
3. **L1 原则足够通用**：能覆盖大部分场景

---

## 2. 文件结构

```
scenario_framework_lite/
├── README.md                    # 本文件
├── l1_principles.yaml           # L1 级原则定义（核心）
├── output_schema.json           # 输出格式约束
├── driving_decisions.yaml       # 闭集决策定义（必须）
├── examples/                    # 示例数据
│   ├── cutin_example.json
│   └── blind_spot_example.json
└── prompts/                     # LLM Prompt 模板
    └── coc_generation.md
```

---

## 3. 与完整方案的对比

### 3.1 简化了什么

| 组件 | 完整方案 | 本方案 | 说明 |
|------|---------|--------|------|
| L2 分类 | 30 个 | ❌ 不需要 | LLM 自行理解场景 |
| L3 分类 | 95 个 | ❌ 不需要 | 用属性描述替代 |
| Keyframe 规则 | 30 条 | 5 条 L1 原则 | LLM 根据原则推断 |
| CC 模板 | 30 套 | 5 套 L1 级 | 通用模板 |
| Start/End 规则 | 详细定义 | 通用原则 | LLM 自行判断 |

### 3.2 保留了什么

| 组件 | 保留原因 |
|------|---------|
| **L1 分类** | 数据组织的基本粒度 |
| **Keyframe 原则** | 确保因果正确性（核心约束） |
| **Driving Decision 闭集** | 训练监督信号（不可省略） |
| **输出 Schema** | 格式一致性 |

---

## 4. 使用流程

### 4.1 数据标注流程

```
1. 数据筛选
   └── 按 L1 粗分类筛选数据片段

2. Keyframe 标注
   ├── 方式 A: 人工根据 L1 原则标注（推荐初期）
   └── 方式 B: LLM 根据 L1 原则推断（需验证一致性）

3. CoC 生成
   ├── 输入: 视频/传感器数据 + Keyframe
   ├── 处理: LLM 根据 prompt 模板生成
   └── 输出: CoC JSON

4. 质量检查
   ├── Schema 校验
   ├── Decision 合理性检查
   └── 抽样人工审核
```

### 4.2 LLM 调用示例

```python
from openai import OpenAI

def generate_coc(video_description: str, l1_scenario: str, keyframe_info: str):
    """
    使用 LLM 生成 CoC
    """
    client = OpenAI()
    
    # 读取 prompt 模板
    with open("prompts/coc_generation.md") as f:
        prompt_template = f.read()
    
    # 读取 L1 原则
    with open("l1_principles.yaml") as f:
        l1_principles = f.read()
    
    prompt = f"""
{prompt_template}

## L1 原则参考
{l1_principles}

## 当前任务
- L1 场景: {l1_scenario}
- Keyframe 信息: {keyframe_info}
- 场景描述: {video_description}

请生成 CoC JSON。
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    return response.choices[0].message.content
```

---

## 5. 验证计划

### 5.1 一致性验证

在正式使用前，需要验证 LLM 能否一致地解读 L1 原则：

```
验证步骤:
1. 准备 50 个测试用例（覆盖各 L1 场景）
2. 对每个用例运行 3 次 LLM 生成
3. 检查:
   - Keyframe 选择是否一致（同一用例）
   - 同类场景的处理逻辑是否相似
   - Driving Decision 是否合理

验收标准:
- 同一用例，3 次运行的 Keyframe 偏差 < 0.5s: > 90%
- 同类场景，Driving Decision 一致: > 95%
- 人工审核 CoC 质量合格: > 85%
```

### 5.2 与完整方案对比

```
对比实验:
1. 同一批 100 条数据
2. 分别用本方案和完整方案标注
3. 比较:
   - 标注一致性
   - 标注效率
   - 人工审核质量评分
```

---

## 6. 已知风险与缓解

| 风险 | 严重程度 | 缓解措施 |
|------|---------|---------|
| Keyframe 不一致 | 🔴 高 | 初期人工标注，后期验证 LLM |
| LLM 输出不稳定 | 🟡 中 | 固定 temperature=0，多次采样取众数 |
| 新场景无规则 | 🟢 低 | L1 原则设计要通用 |
| 边界情况处理 | 🟡 中 | 抽样审核，积累 FAQ |

---

## 7. 迭代路径

```
阶段 1: 验证可行性
├── 50 条数据验证 LLM 一致性
└── 确定是否需要细化规则

阶段 2: 小规模试点
├── 500 条数据标注
├── 质量评估
└── 迭代 L1 原则

阶段 3: 决策点
├── 如果质量足够: 继续本方案
└── 如果质量不足: 引入 L2 关键规则（混合方案）
```

---

## 附录 A: 与完整方案的兼容性

本方案的输出格式与完整方案兼容：
- 输出 Schema 相同
- Driving Decision 闭集相同
- 可以无缝切换或混合使用

## 附录 B: 参考文档

- [完整规格方案](../scenario_framework/README.md)
- [Alpamayo-R1 论文](https://arxiv.org/abs/2511.00088)
