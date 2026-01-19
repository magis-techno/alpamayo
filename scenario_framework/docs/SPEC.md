# 场景框架核心规格

> 版本: 2.0.0  
> 更新日期: 2026-01-19  
> 状态: Draft

本文档定义场景框架的设计原则和标注规格，是设计和标注的唯一权威来源。

---

## 1. 设计原则

### 1.1 主轴选择：决策触发事件

**核心问题**：什么导致ego需要做这个决策？

```
主轴 = 决策触发事件（Decision Trigger）
```

| 不选择的主轴 | 原因 |
|-------------|------|
| 自车行为 | 行为在Driving Decision中定义，不应作为场景分类主轴 |
| 道路结构 | 结构是背景，不是触发因素 |
| 功能模块 | 模块是系统实现，与场景语义无关 |

**主轴选择的好处**：
1. 场景与Driving Decision正交，职责清晰
2. 同一场景可以有不同的Driving Decision响应
3. 便于定义标注规格（触发事件 → 关键帧 → 推理要素）

### 1.2 层级划分标准

```
L1: 决策触发的大类（5个）
    ↓
L2: 具体触发事件（30个）
    ↓
L3: 事件的关键变体（95个，仅当标注规格有差异时细分）
```

| 层级 | 划分标准 | 数量 |
|------|----------|------|
| **L1** | 触发源的本质类型 | 5个 |
| **L2** | 具体的触发事件，决定标注规格 | 30个 |
| **L3** | L2内的变体，仅当keyframe/起止/要素有差异时细分 | 95个 |

> 完整场景列表详见 [TAXONOMY.md](TAXONOMY.md)

### 1.3 粒度控制原则

```yaml
原则1: 同一L2场景共享同一套标注规格
  - Keyframe定义相同
  - 起止时刻规则相同
  - Critical Components要素相同

原则2: 如果标注规格不同，必须细分为不同的L2或L3
  - 例：紧急cutin vs 缓慢cutin，起始时刻规则不同 → 细分为L3

原则3: 如果标注规格相同但业务想区分，用标签而非层级
  - 例：大车cutin vs 小车cutin，规格相同 → 用属性标签区分
```

### 1.4 MECE原则与边界处理

**MECE要求**：
- L1层：互斥完备
- L2层：在各自L1下互斥
- 一条数据：归属到唯一的叶子节点

**边界情况处理**：

| 情况 | 处理方式 |
|------|----------|
| 多事件并发 | 选择**主触发事件**（决定ego响应的主因） |
| 事件边界模糊 | 按Keyframe规则判断，有明确时间点的优先 |
| 无法归类 | 归入`other`子类，积累后考虑新增场景 |

---

## 2. Driving Decision 闭集

### 2.1 纵向决策（9种）

| ID | 中文 | 定义 | 排除 |
|----|------|------|------|
| `set_speed_tracking` | 速度保持 | 无约束下保持/达到目标速度 | 跟车、让行、刹停 |
| `lead_following` | 跟车 | 对同向前车保持安全时距 | 几何减速、Gap匹配 |
| `road_speed_adaptation` | 道路减速 | 因道路几何特征减速 | 因前车、因规则 |
| `gap_matching` | Gap匹配 | 为横向机动调整速度 | 普通跟车 |
| `acceleration_for_passing` | 超车加速 | 配合横向机动加速 | 普通加速 |
| `yield_to_agent` | 让行 | 对有路权参与者让行 | 跟车、规则刹停 |
| `stop_for_regulation` | 规则刹停 | 对规则性约束刹停 | 障碍刹停 |
| `stop_for_obstacle` | 障碍刹停 | 对前方障碍物刹停 | 规则刹停 |
| `resume` | 起步 | 从静止状态起步 | 跟车加速 |

### 2.2 横向决策（9种）

| ID | 中文 | 定义 | 需指明方向 |
|----|------|------|-----------|
| `lane_keeping` | 居中保持 | 车道内居中行驶 | 否 |
| `in_lane_nudge` | 道内偏移 | 不跨线的车道内偏移 | 是(L/R) |
| `out_of_lane_nudge` | 借道偏移 | 短暂跨线后回原车道 | 是(L/R) |
| `lane_change` | 换道 | 完整的相邻车道转移 | 是(L/R) |
| `merge_or_split` | Merge/Split | 匝道汇入汇出 | 否 |
| `turn` | 转弯 | 路口/环岛/U-turn转向 | 是(L/R/U) |
| `pull_over` | 靠边 | 向路边靠近 | 否 |
| `maneuver_abort` | 机动中止 | 取消进行中的横向机动 | 否 |
| `reverse` | 倒车 | 向后行驶 | 否 |

---

## 3. Critical Components（开集）

Critical Components 采用**开集设计**，标注时根据实际场景自由描述影响决策的关键因素，不限于预定义类别。

### 3.1 参考类别

以下类别仅供参考，可根据实际情况自由扩展：

| 参考类别 | 描述示例 |
|----------|----------|
| 关键目标 | 切入车辆、横穿行人、前方障碍物等 |
| 交通控制 | 信号灯状态、停止标志、让行标志等 |
| 道路环境 | 弯道、坡道、盲区、施工区域等 |
| 车道信息 | 车道数变化、车道线类型、可用空间等 |
| 导航意图 | 需要换道、即将驶出、目标方向等 |
| 其他约束 | 天气条件、特殊规则、ODD限制等 |

### 3.2 描述原则

- **自然语言描述**：用简洁的语言描述影响决策的因素，避免堆砌数值
- **因果相关性**：只描述与当前决策直接相关的因素
- **定性优先**：优先使用定性描述（如"较近"、"较快"），必要时补充定量信息

### 3.3 不确定性标记

当存在盲区、遮挡或意图不明确时，需标记不确定性：

```yaml
uncertainty: high  # 目标行为不确定（盲区、遮挡、意图不明）
```

---

## 4. Keyframe 定义

### 4.1 类型

| 类型 | 定义 | 适用场景 |
|------|------|----------|
| **Reactive** | 单一时间点（通常是动作发生前0.5s） | 需要立即响应（cutin、红灯、VRU突现） |
| **Proactive** | 时间范围（start → end） | 需要持续评估（换道、盲区通行） |

### 4.2 起止时刻确定原则

```yaml
起始时刻:
  - 优先: 事件触发条件首次满足的时刻
  - 兜底: keyframe前固定秒数（场景相关）
  
结束时刻:
  - 优先: 状态恢复稳定的时刻
  - 兜底: keyframe后固定秒数（场景相关）
  
打包范围:
  - 起始前扩展: 提供上下文（通常1-5s）
  - 结束后扩展: 确认稳定（通常1-3s）
```

---

## 5. 标注流程

### 5.1 两阶段流程

```
Stage I (历史窗口 0-2s)
├── 识别Critical Components
├── 确认仅使用keyframe前的观测信息
└── 避免因果混淆

Stage II (预测窗口 0-8s)
├── 安全排除检查（排除违法/不安全行为）
├── 选择Driving Decision（纵向+横向）
├── 撰写CoC推理链
└── 关联Critical Components与Decision
```

### 5.2 标注质量要求

| 维度 | 要求 |
|------|------|
| **因果正确性** | 推理链必须基于可观测的历史信息 |
| **决策对齐** | Decision必须与轨迹行为一致 |
| **要素相关性** | 描述与决策直接相关的关键因素 |
| **表达自然性** | 使用自然语言描述，避免堆砌数值 |

### 5.3 CoC推理链组织原则

```yaml
原则:
  1. 决策锚定: 每条推理链锚定到一个具体决策
  2. 因果局部性: 所有证据必须来自历史观测窗口
  3. 标注经济性: 只包含决策相关的因素
  
结构:
  1. 场景描述: 关键目标/环境的状态
  2. 因果分析: 为什么需要做这个决策
  3. 决策陈述: 明确纵向+横向决策
```

---

## 6. 分场景标注规格

> 完整场景列表详见 [TAXONOMY.md](TAXONOMY.md)  
> 标注示例详见 [examples/](../examples/)

### 6.1 交互响应类 (reactive_agent)

#### Cutin响应 `reactive_agent.cutin`

**场景定义**: 他车从相邻车道切入自车前方，自车需要响应

**Keyframe**: Reactive - 他车任一车轮越过车道线（压线时刻）

**起止时刻**:
| 时刻 | 定义 | 规则 | 兜底 |
|------|------|------|------|
| 起始 | 切入意图显现 | min(转向灯亮起, keyframe-5s) | keyframe-2s |
| 结束 | 他车回正 | 他车中心距车道中心<0.5m | keyframe+3s |

**打包范围**: 起始前3s，结束后3s

**Driving Decision（典型）**:
- 纵向: `yield_to_agent`
- 横向: `lane_keeping` 或 `in_lane_nudge`

**Critical Components（建议描述）**:
- 切入车辆类型和位置
- 切入紧迫程度（距离/时间）
- 是否有转向灯等预警信号

**L3细分**:
| L3 ID | 条件 | 规格差异 |
|-------|------|----------|
| `cutin.urgent` | TTC < 3s | 起始=keyframe-2s |
| `cutin.slow` | TTC >= 3s | 起始=keyframe-5s或转向灯 |
| `cutin.large_vehicle` | 大车/异形车 | 额外记录遮挡情况 |

**CoC参考写法**:
> 左侧车辆正在切入我方车道，距离较近，需要及时响应。切入车辆未打转向灯，切入意图突然。决策：减速让行，保持当前车道。

---

#### VRU横穿响应 `reactive_agent.vru_crossing`

**场景定义**: VRU横向或斜向穿越道路，自车需要响应

**Keyframe**: Reactive - VRU进入自车后验轨迹左右7m范围

**起止时刻**:
| 时刻 | 定义 | 规则 | 兜底 |
|------|------|------|------|
| 起始 | VRU进入ROI | 进入自车轨迹横向7m，纵向50m | keyframe |
| 结束 | VRU驶离 | VRU驶离后验通道横向1.5m | keyframe+3s |

**打包范围**: 起始前3s，结束后min(自车达5kph, 3s)

**Driving Decision（典型）**:
- 纵向: `yield_to_agent`
- 横向: `lane_keeping` 或 `in_lane_nudge`

**Critical Components（建议描述）**:
- VRU类型和横穿方向
- 横穿位置（斑马线/非斑马线）
- 横穿速度快慢

---

#### VRU突现响应 `reactive_agent.vru_emergence`

**场景定义**: VRU从遮挡物后突然出现（鬼探头）

**Keyframe**: Reactive - VRU从遮挡后进入视野的时刻

**起止时刻**:
| 时刻 | 定义 | 规则 | 兜底 |
|------|------|------|------|
| 起始 | VRU出现 | VRU首次可见 | keyframe |
| 结束 | VRU驶离或停止 | VRU离开路径或停止 | keyframe+3s |

**打包范围**: 起始前5s（包含遮挡上下文），结束后3s

**Critical Components（建议描述）**:
- VRU类型和出现位置
- 遮挡源（什么遮挡了视线）
- **uncertainty: high**（盲区场景必标）

---

#### 路口交互 `reactive_agent.intersection_interaction`

**场景定义**: 路口内与其他车辆的交互博弈

**Keyframe**: Proactive - 从进入路口影响区到通过路口

**L3细分**:
| L3 ID | 场景 | 特殊要素 |
|-------|------|----------|
| `unprotected_left` | 无保护左转 | 对向来车情况、可用gap |
| `right_vs_straight` | 右转对直行 | 直行车距离和速度 |
| `same_direction_turn` | 同向转弯 | 相邻车辆路径 |

---

### 6.2 路况适应类 (reactive_road)

#### 盲区减速 `reactive_road.blind_spot_slowdown`

**场景定义**: 因存在盲区需要减速的场景

**Keyframe**: Proactive - 盲区条件满足的整个范围

**Critical Components（建议描述）**:
- 盲区类型和方向
- 潜在风险来源
- **uncertainty: high**（盲区场景必标）

**L3细分**:
| L3 ID | 场景 | 挖掘条件 |
|-------|------|----------|
| `unsignalized` | 无灯路口盲区 | 距路口60m；盲区射线角度<90° |
| `merge` | 汇入盲区 | 有laneMerge标志；汇入方向有盲区 |
| `dynamic` | 动态遮挡盲区 | 大车造成动态遮挡 |

**CoC参考写法**:
> 前方路口右侧存在盲区，视野受限，可能有车辆或行人突然出现。不确定性较高。决策：减速通过，加强观察。

---

#### 几何适应 `reactive_road.geometry_adaptation`

**场景定义**: 因道路几何特征需要调整速度/路径

**Keyframe**: Proactive - 几何特征影响范围

**L3细分**:
| L3 ID | 场景 | 关键要素 |
|-------|------|----------|
| `high_curvature` | 大曲率弯道 | 曲率、建议速度 |
| `slope_up/down` | 坡道 | 坡度、上/下坡 |
| `narrow` | 窄道 | 道路宽度、两侧情况 |
| `tunnel` | 隧道 | 光照变化 |

---

### 6.3 规则遵从类 (reactive_rule)

#### 信号灯刹停 `reactive_rule.traffic_light.red_stop`

**场景定义**: 对红灯的减速刹停

**Keyframe**: Reactive - max(0.5s before ego开始减速, 灯变红/黄)

**Driving Decision**:
- 纵向: `stop_for_regulation`
- 横向: `lane_keeping`

---

#### 信号灯起步 `reactive_rule.traffic_light.resume_first`

**场景定义**: 绿灯起步

**Keyframe**: Reactive - max(0.5s before ego开始加速, 灯变绿)

**Critical Components（建议描述）**:
- 信号灯状态变化
- 自车位置（头车/跟随）
- 前车情况（如有）

**Driving Decision**:
- 纵向: `resume`
- 横向: `lane_keeping` 或 `turn`

---

#### 特殊设施通行 `reactive_rule.special_facility`

**L3细分**:
| L3 ID | 场景 | 特殊要素 |
|-------|------|----------|
| `toll_etc` | ETC通道 | 通道类型 |
| `gate` | 闸机通行 | 闸杆状态、起步时机 |
| `roundabout` | 环岛通行 | 环内车流、目标出口 |

---

### 6.4 主动机动类 (proactive)

#### 换道 `proactive.lane_change`

**场景定义**: ego主动发起的换道机动

**Keyframe**: Proactive - routing command → 横向稳定

**阶段划分**:
```
准备阶段 (Prepare): routing command → 开始Gap Matching
执行阶段 (Execute): 开始偏离中心线 → 进入目标车道50%
完成阶段 (Complete): 进入目标车道50% → 目标车道居中稳定
```

**起止时刻**:
| 时刻 | 定义 | 规则 |
|------|------|------|
| 起始 | 换道意图产生 | routing command或效率判断 |
| 结束 | 换道完成 | 横向速度<0.1m/s且距中心线<0.3m持续2s |

**打包范围**: 起始前4s（含prepare），结束后1s

**Driving Decision（典型）**:
- 纵向: `gap_matching` 或 `acceleration_for_passing`
- 横向: `lane_change`

**Critical Components（建议描述）**:
- 换道方向和原因
- 目标车道间隙是否充足
- 目标车道车流情况

**L3细分**:
| L3 ID | 触发条件 | 差异 |
|-------|----------|------|
| `navigation` | 导航指示 | 记录剩余距离 |
| `efficiency` | 前车慢 | 记录速度差 |
| `escape` | 道路阻塞 | 记录阻塞原因 |
| `overtake` | 超车意图 | 记录被超车辆 |
| `abort` | 换道取消 | keyframe=开始回中 |

**CoC参考写法**:
> 导航指示前方需要驶出，需换至右侧车道。目标车道有合适的间隙，前后车距离充足。决策：调整速度匹配目标车流，执行向右换道。

---

#### 避障 `proactive.obstacle_avoidance`

**场景定义**: 对障碍物的主动避让

**Keyframe**: Reactive - 自车横向累计偏差>0.4m

**起止时刻**:
| 时刻 | 定义 | 规则 |
|------|------|------|
| 起始 | 避障发起前 | 避障发起时刻-3s |
| 结束 | 避障完成 | 超过障碍物后居中行驶1s以上 |

**Critical Components（建议描述）**:
- 障碍物类型和位置
- 避让方向和方式
- 是否需要借道

**L3细分**:
| L3 ID | 场景 | 规格差异 |
|-------|------|----------|
| `in_lane` | 道内避障 | 横向=in_lane_nudge |
| `borrow_lane` | 借道避障 | 横向=out_of_lane_nudge |

---

#### 路口转弯 `proactive.turn`

**场景定义**: 路口内的转向机动

**Keyframe**: Reactive - 0.5s before ego航向角开始变化

**Driving Decision（典型）**:
- 纵向: `road_speed_adaptation`
- 横向: `turn`

**L3细分**:
| L3 ID | 场景 | 关键要素 |
|-------|------|----------|
| `left_normal` | 常规左转 | 对向来车、行人 |
| `left_unprotected` | 无保护左转 | 对向车流gap |
| `right_normal` | 常规右转 | VRU、直行来车 |
| `uturn` | U-turn | 掉头空间、来车 |

---

#### 汇入汇出 `proactive.merge_interaction`

**场景定义**: 匝道汇入或分离

**Keyframe**: Proactive - 进入加速车道 → 汇入主路完成

**Driving Decision（典型）**:
- 纵向: `gap_matching`
- 横向: `merge_or_split`

**Critical Components（建议描述）**:
- 汇入/汇出方向
- 主路车流情况
- 目标间隙是否可用

---

### 6.5 安全临界类 (safety)

#### AEB触发 `safety.aeb`

**场景定义**: 触发AEB紧急制动

**Keyframe**: Reactive - AEB系统激活时刻

**Driving Decision**:
- 纵向: `stop_for_obstacle`
- 横向: `lane_keeping` 或 `in_lane_nudge`

**Critical Components（建议描述）**:
- 触发目标类型和位置
- 紧急程度
- 避撞结果

**L3细分**:
| L3 ID | 场景 |
|-------|------|
| `vehicle` | 对车AEB |
| `vru` | 对VRU AEB |
| `large_vehicle` | 对大车AEB |

---

#### 紧急避险 `safety.emergency_maneuver`

**场景定义**: 紧急避险机动

**Keyframe**: Reactive - 自车开始紧急横向机动

**起止时刻**:
| 时刻 | 定义 | 规则 |
|------|------|------|
| 起始 | 紧急机动前 | keyframe-2s |
| 结束 | 紧急机动完成 | 横向位移恢复或避险完成 |

**Critical Components（建议描述）**:
- 紧急原因
- 避险方向和方式
- 避险结果

---

## 附录A：场景边界判断FAQ

| 问题 | 解答 |
|------|------|
| Cutin和VRU横穿同时发生？ | 选择主触发事件（决定ego响应的主因） |
| 换道中遇到cutin？ | 如果cutin是换道中止的原因，标注cutin |
| 盲区减速但无实际目标出现？ | 仍标注盲区减速，uncertainty=high |

## 附录B：术语表

| 术语 | 定义 |
|------|------|
| **Driving Decision** | 驾驶决策，分为纵向和横向，闭集定义 |
| **Critical Components** | 影响决策的关键因素，开集定义 |
| **Keyframe** | 关键帧，标注的参考时间点 |
| **CoC (Chain of Causation)** | 因果链，描述决策的因果推理过程 |
| **MECE** | Mutually Exclusive, Collectively Exhaustive，互斥且完备 |
| **TTC** | Time To Collision，碰撞时间 |
| **ROI** | Region of Interest，感兴趣区域 |

## 附录C：文档引用

- **完整场景分类**：[TAXONOMY.md](TAXONOMY.md)
- **数据接口格式**：[DATA_FORMAT.md](DATA_FORMAT.md)
- **标注示例**：[examples/](../examples/)
- **参考论文**：Alpamayo-R1 (arXiv:2511.00088)
