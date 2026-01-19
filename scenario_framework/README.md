# 场景框架 (Scenario Framework)

统一的场景分类体系，用于支持**数据均衡去重**和**CoC标注**两个核心任务。

## 概述

本框架基于 Alpamayo-R1 论文的 Chain of Causation (CoC) 设计思路，提供：

1. **统一的场景分类体系** - L1-L2-L3层级结构（5个L1，30个L2，95个L3）
2. **驾驶决策闭集** - 9种纵向决策 + 9种横向决策
3. **完整的标注规格** - 每个场景的Keyframe规则、起止时刻、关键因素
4. **数据交换格式** - JSON Schema定义的标准化数据格式

## 目录结构

```
scenario_framework/
├── README.md                    # 本文件（入口导航）
├── docs/
│   ├── SPEC.md                  # 核心规格（设计原则 + 标注规格）
│   ├── DATA_FORMAT.md           # 数据交换格式规范
│   └── TAXONOMY.md              # 场景分类全集（L1-L2-L3）
├── schema/
│   ├── scenario_taxonomy.yaml   # 场景分类Schema
│   ├── labeling_spec_schema.json
│   └── coc_output_schema.json   # CoC输出Schema
├── examples/                    # 标注示例
│   ├── cutin_urgent_example.json
│   ├── lane_change_example.json
│   ├── vru_crossing_example.json
│   └── blind_spot_example.json
├── requirements/                # 需求文档
└── *.yaml                       # (legacy) 旧版配置文件
```

## 快速开始

| 目标 | 文档 | 内容 |
|------|------|------|
| 了解设计理念 | [SPEC.md](docs/SPEC.md) §1-2 | 设计原则、主轴选择、层级划分 |
| 查看场景分类 | [TAXONOMY.md](docs/TAXONOMY.md) | 完整的L1-L2-L3场景列表 |
| 执行标注任务 | [SPEC.md](docs/SPEC.md) §3-6 | 标注流程、决策闭集、分场景规格 |
| 对接数据格式 | [DATA_FORMAT.md](docs/DATA_FORMAT.md) | 输入输出格式、Schema校验 |
| 参考标注示例 | [examples/](examples/) | 各场景的标注JSON示例 |
| 查看需求来源 | [requirements/](requirements/) | 原始需求和变更历史 |

## 使用场景

### 数据均衡去重

1. 使用 `schema/scenario_taxonomy.yaml` 中的 L2 场景作为保护维度
2. 确保每个 L2 类别的数据量不低于设定阈值
3. 优先保护稀有场景和长尾场景

### CoC标注

1. 使用 [SPEC.md](docs/SPEC.md) 指导标注规格设计
2. 使用 `schema/coc_output_schema.json` 校验标注结果
3. 参考 `examples/` 中的示例数据

### 数据挖掘

1. 使用 `schema/scenario_taxonomy.yaml` 中的 `mining_conditions` 定义挖掘规则
2. 使用 [DATA_FORMAT.md](docs/DATA_FORMAT.md) 中定义的接口格式

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.0.0 | 2026-01-19 | 文档重构：合并为 SPEC + DATA_FORMAT + TAXONOMY |
| 1.0.0 | 2026-01-15 | 完整文档体系：整体设计、标注规格、数据接口 |
| 0.1.0 | 2026-01-14 | 初始版本：基础分类体系 |

## 参考文献

- Alpamayo-R1: Bridging Reasoning and Action Prediction for Generalizable Autonomous Driving in the Long Tail (arXiv:2511.00088)
