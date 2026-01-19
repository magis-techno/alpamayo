# 数据交换格式规范

> 版本: 2.0.0  
> 更新日期: 2026-01-19  
> 状态: Draft

本文档定义场景框架中各模块之间的数据交换格式。

---

## 1. 概述

### 1.1 设计目标

- **一致性**：各系统使用统一的数据格式
- **可验证性**：数据格式可通过Schema自动校验
- **可扩展性**：支持新增场景和字段

### 1.2 数据流向

```
场景分类定义:     框架 → 挖掘系统/标注系统
标注任务下发:     挖掘系统 → 标注系统
标注结果输出:     标注系统 → 训练系统
数据统计:         各系统 → 分析系统
```

### 1.3 版本管理

```yaml
版本格式: major.minor.patch
  - major: 不兼容的格式变更
  - minor: 向后兼容的新增字段
  - patch: 文档修订/bug修复

当前版本: 2.0.0
```

### 1.4 Schema文件

| Schema | 路径 | 用途 |
|--------|------|------|
| 场景分类 | `schema/scenario_taxonomy.yaml` | 定义L1-L2-L3场景分类 |
| 标注输出 | `schema/coc_output_schema.json` | 校验CoC标注结果 |
| 标注规格 | `schema/labeling_spec_schema.json` | 定义标注规格格式 |

---

## 2. 场景分类数据格式

### 2.1 场景定义格式 (YAML)

场景分类体系使用YAML格式定义，存放于 `schema/scenario_taxonomy.yaml`：

```yaml
# scenario_taxonomy.yaml 结构示例
version: "1.0.0"
description: "场景分类体系定义"

l1_categories:
  - id: "reactive_agent"
    name_zh: "交互响应"
    name_en: "Reactive to Agent"
    definition: "对动态交通参与者的响应"

l2_scenarios:
  reactive_agent:
    - id: "cutin"
      name_zh: "Cutin响应"
      definition: "他车切入自车前方"
      typical_decisions:
        longitudinal: ["yield_to_agent"]
        lateral: ["lane_keeping", "in_lane_nudge"]
      mining_conditions:
        - "他车横向位移 > 0.5m 进入自车车道"
      labeling_spec_ref: "SPEC.md#cutin"

l3_variants:
  cutin:
    - id: "urgent"
      name_zh: "紧急Cutin"
      condition: "TTC < 3s"
```

### 2.2 场景标签格式

用于标注数据的场景标签：

```json
{
  "scenario_label": {
    "l1": "reactive_agent",
    "l2": "cutin",
    "l3": "urgent",
    "full_id": "reactive_agent.cutin.urgent"
  }
}
```

---

## 3. 标注输入数据格式

### 3.1 Clip元数据

标注任务下发时的Clip信息：

```json
{
  "clip_metadata": {
    "clip_id": "clip_20260115_103000_001",
    "source": "vehicle_001",
    "capture_time": "2026-01-15T10:30:00.000Z",
    "duration_sec": 20.0,
    "frame_rate": 10,
    "total_frames": 200,
    
    "data_sources": {
      "video": ["front_camera", "left_camera", "right_camera"],
      "sensor": ["lidar", "radar"],
      "can": true,
      "map": true
    },
    
    "pre_labels": {
      "scenario": { "l1": "reactive_agent", "l2": "cutin" },
      "mining_score": 0.85,
      "mining_method": "rule_based"
    }
  }
}
```

### 3.2 场景预标签

挖掘系统输出的场景预标签：

```json
{
  "scenario_pre_label": {
    "l1": "reactive_agent",
    "l2": "cutin",
    "l3": null,
    "confidence": 0.85,
    "mining_conditions_matched": ["他车横向位移 > 0.5m", "TTC < 5s"],
    "suggested_l3": "urgent"
  }
}
```

### 3.3 Keyframe建议

挖掘系统建议的Keyframe：

```json
{
  "keyframe_suggestion": {
    "type": "reactive",
    "suggested_timestamp": "2026-01-15T10:30:15.500Z",
    "suggested_frame_idx": 155,
    "detection_rule": "他车车轮越过车道线",
    
    "context_range": {
      "start_timestamp": "2026-01-15T10:30:10.000Z",
      "end_timestamp": "2026-01-15T10:30:20.000Z",
      "start_frame_idx": 100,
      "end_frame_idx": 200
    }
  }
}
```

---

## 4. CoC标注输出格式

### 4.1 JSON Schema

完整的标注结果格式定义详见 [`schema/coc_output_schema.json`](../schema/coc_output_schema.json)。

### 4.2 字段说明

#### scenario 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| l1 | string | 是 | L1大类ID |
| l2 | string | 是 | L2场景ID |
| l3 | string | 否 | L3变体ID（如有） |
| full_id | string | 否 | 完整场景ID |

#### keyframe 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| timestamp | datetime | 是 | 关键帧时间戳 |
| frame_idx | int | 是 | 关键帧索引 |
| type | enum | 是 | `reactive` 或 `proactive` |
| range_start | datetime | 条件 | Proactive场景必填 |
| range_end | datetime | 条件 | Proactive场景必填 |

#### driving_decision 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| longitudinal | enum/null | 是 | 纵向决策（9种+null） |
| lateral | enum/null | 是 | 横向决策（9种+null） |
| lateral_direction | enum/null | 条件 | 需方向的横向决策必填 |

> 决策枚举值详见 [SPEC.md §2](SPEC.md#2-driving-decision-闭集)

#### critical_components 字段

Critical Components 采用**开集设计**，可自由描述影响决策的关键因素。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 否 | 参考类别（可自定义） |
| description | string | 是 | 自然语言描述 |
| uncertainty | enum | 条件 | 盲区/遮挡场景标记 `high` |

> 描述原则详见 [SPEC.md §3](SPEC.md#3-critical-components开集)

### 4.3 校验规则

```yaml
1. 基础校验:
   - 必填字段不可为空
   - 枚举值必须在定义范围内
   - 时间戳格式正确（ISO 8601）

2. 业务校验:
   - Proactive场景必须有 range_start 和 range_end
   - 需方向的横向决策必须有 lateral_direction
   - 盲区/遮挡场景的 critical_components 必须标记 uncertainty

3. 一致性校验:
   - keyframe 在 time_range 范围内
   - coc_trace 提到的决策与 driving_decision 一致
```

---

## 5. 数据挖掘接口

### 5.1 场景挖掘查询

用于数据挖掘系统的场景筛选条件：

```json
{
  "mining_query": {
    "scenario_id": "reactive_agent.cutin",
    "conditions": [
      { "field": "target_vehicle.lateral_offset", "operator": ">", "value": 0.5, "unit": "m" },
      { "field": "ttc", "operator": "<", "value": 5, "unit": "s" }
    ],
    "time_constraints": {
      "condition_duration_min": 0.5,
      "condition_duration_max": null
    },
    "output_limit": 1000
  }
}
```

### 5.2 挖掘结果格式

挖掘系统输出的结果格式：

```json
{
  "mining_result": {
    "query_id": "query_20260115_001",
    "scenario_id": "reactive_agent.cutin",
    "total_matched": 1523,
    "returned": 1000,
    
    "clips": [
      {
        "clip_id": "clip_20260115_103000_001",
        "match_score": 0.95,
        "keyframe_suggestion": {
          "timestamp": "2026-01-15T10:30:15.500Z",
          "frame_idx": 155
        },
        "conditions_matched": [
          { "condition": "target_vehicle.lateral_offset > 0.5m", "actual_value": 0.8 }
        ]
      }
    ],
    
    "statistics": {
      "score_distribution": { "0.9-1.0": 523, "0.8-0.9": 312, "0.7-0.8": 165 }
    }
  }
}
```

---

## 6. 示例数据

完整的标注结果示例详见 [`examples/`](../examples/) 目录：

| 示例文件 | 场景 |
|----------|------|
| `cutin_urgent_example.json` | 紧急Cutin响应 |
| `lane_change_example.json` | 导航换道 |
| `vru_crossing_example.json` | VRU横穿响应 |
| `blind_spot_example.json` | 盲区减速 |

---

## 附录：文档引用

- **核心规格**：[SPEC.md](SPEC.md) - Driving Decision、Critical Components定义
- **场景分类**：[TAXONOMY.md](TAXONOMY.md) - 完整L1-L2-L3列表
- **JSON Schema**：[schema/coc_output_schema.json](../schema/coc_output_schema.json)
