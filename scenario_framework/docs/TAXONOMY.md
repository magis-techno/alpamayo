# 场景分类全集 (L1-L2-L3)

> 版本: 2.0.0  
> 更新日期: 2026-01-19  
> 总计: 5个L1 | 30个L2 | 95个L3

本文档是场景分类的唯一权威来源。标注规格详见 [SPEC.md](SPEC.md)。

---

## 分类统计

| L1 | 名称 | L2数量 | L3数量 |
|----|------|--------|--------|
| `reactive_agent` | 交互响应 | 8 | 32 |
| `reactive_road` | 路况适应 | 5 | 21 |
| `reactive_rule` | 规则遵从 | 7 | 22 |
| `proactive` | 主动机动 | 7 | 16 |
| `safety` | 安全临界 | 3 | 4 |
| **总计** | - | **30** | **95** |

---

## L1: 交互响应 (reactive_agent)

> **定义**: 对动态交通参与者的响应，他车/VRU/动物等动态目标触发ego的决策

### L2: cutin - Cutin响应

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `urgent` | 紧急Cutin | TTC < 3s | 起始=keyframe-2s |
| `slow` | 缓慢Cutin | TTC >= 3s | 起始=keyframe-5s或转向灯 |
| `large_vehicle` | 大车Cutin | 切入车辆为大车/异形车 | 需额外记录遮挡情况 |
| `from_stationary` | 起步Cutin | 他车从静止起步切入 | 起始=他车开始移动 |
| `ramp` | 匝道Cutin | 匝道汇入处切入 | 记录汇入位置 |
| `congestion` | 拥堵Cutin | 拥堵场景中切入 | - |
| `intersection` | 路口Cutin | 路口内切入/挤压 | - |

### L2: vru_crossing - VRU横穿响应

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `horizontal` | 横穿 | VRU与道路垂直穿越 | - |
| `diagonal` | 斜穿 | VRU与道路斜向穿越 | - |
| `crosswalk` | 斑马线横穿 | 在斑马线处横穿 | 记录是否有信号灯 |

### L2: vru_emergence - VRU突现响应（鬼探头）

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `static_occlusion` | 静态遮挡突现 | 被建筑/停车等静态物遮挡 | - |
| `dynamic_occlusion` | 动态遮挡突现 | 被大车等动态物遮挡 | 记录遮挡车辆信息 |

### L2: vru_invasion - VRU入侵车道

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `vru_cutin` | VRU切入 | VRU从侧方进入车道 | - |
| `same_direction` | 顺行VRU | VRU在车道内同向行驶 | - |
| `opposite_direction` | 逆向VRU | VRU在车道内逆向行驶 | - |

### L2: vehicle_abnormal - 他车异常响应

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `reversing` | 他车倒车 | 他车正在倒车 | keyframe=他车开始移动 |
| `cutout_reveal` | Cutout露障碍 | 前车cutout露出障碍物 | 双keyframe(cutout+障碍) |
| `sudden_brake` | 他车急刹 | 他车突然急刹 | - |
| `abnormal_motion` | 异常运动 | 他车蛇形/逆行等 | - |

### L2: intersection_interaction - 路口交互

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `unprotected_left` | 无保护左转交互 | 左转时对向来车 | 记录对向车辆gap |
| `right_vs_straight` | 右转对直行 | 右转时直行来车 | - |
| `same_direction_turn` | 同向转弯交互 | 相邻车辆同向转弯 | - |
| `cross_conflict` | 交叉冲突 | 路口内他车横穿 | - |

### L2: following - 跟车响应

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `steady` | 稳态跟车 | 稳定车速跟车 | - |
| `stop_and_go` | 频繁启停 | 拥堵走走停停 | - |
| `creeping` | 蠕行跟车 | 极低速蠕行 | - |
| `follow_start` | 跟车起步 | 前车起步跟随 | - |
| `follow_stop` | 跟车停止 | 跟随前车停止 | - |
| `lead_sudden_brake` | 前车急刹 | 前车突然急刹 | - |

### L2: passing - 会车响应

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `narrow_road` | 窄路会车 | 窄路对向来车 | 记录可用宽度 |
| `large_vehicle` | 大车会车 | 与大车对向会车 | - |
| `construction` | 施工区会车 | 施工区域会车 | - |

### L2: animal - 动物响应

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `crossing` | 动物横穿 | 动物穿越道路 | - |
| `on_road` | 动物在道路上 | 动物在道路上停留/移动 | - |

---

## L1: 路况适应 (reactive_road)

> **定义**: 对道路状况的适应性响应，道路几何/盲区/路面等触发ego的决策

### L2: blind_spot_slowdown - 盲区减速

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `unsignalized` | 无灯路口盲区 | 无信号灯路口存在盲区 | uncertainty=high必标 |
| `ramp` | 匝道盲区 | 匝道汇入/汇出盲区 | uncertainty=high必标 |
| `curve` | 弯道盲区 | 弯道内侧盲区 | - |
| `slope` | 坡道盲区 | 坡顶/坡底盲区 | - |
| `vehicle` | 车辆遮挡盲区 | 大车等造成动态遮挡 | 记录遮挡车辆 |
| `gap` | 豁口盲区 | 中央护栏豁口盲区 | - |
| `construction` | 施工盲区 | 施工区域盲区 | - |

### L2: geometry_adaptation - 几何适应

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `high_curvature` | 大曲率弯道 | 道路曲率大 | 记录曲率值 |
| `slope_up` | 上坡 | 道路上坡 | 记录坡度 |
| `slope_down` | 下坡 | 道路下坡 | 记录坡度 |
| `narrow` | 窄道 | 道路宽度受限 | 记录可用宽度 |
| `tunnel` | 隧道 | 在隧道内行驶 | 记录光照变化 |
| `rural` | 乡村道路 | 非铺装或路况较差 | - |
| `mountain` | 山路 | 山区道路特征 | - |
| `dead_end` | 断头路 | 道路无出口 | - |
| `unstructured` | 非结构化道路 | 无明确车道线/边界 | - |
| `laneline_abnormal` | 车道线异常 | 车道线缺失/模糊/错误 | - |

### L2: surface_adaptation - 路面适应

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `wet` | 湿滑路面 | 路面积水/湿滑 | - |
| `puddle` | 积水 | 路面有积水坑 | - |
| `snow_ice` | 积雪/结冰 | 路面有积雪或结冰 | - |
| `pothole` | 坑洼路面 | 路面有凹坑/颠簸 | - |
| `speed_bump` | 减速带 | 前方有减速带 | - |

### L2: lighting_adaptation - 光照适应

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `glare` | 炫光 | 强光直射（阳光/对向灯光） | - |
| `low_light` | 弱光 | 夜间/隧道低光照 | - |
| `transition` | 光照变化 | 进出隧道等光照突变 | - |

### L2: weather_adaptation - 天气适应

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `rain` | 雨天 | 降雨天气 | - |
| `fog` | 雾天 | 大雾天气 | 记录能见度 |
| `snow` | 雪天 | 降雪天气 | - |

---

## L1: 规则遵从 (reactive_rule)

> **定义**: 对交通规则/信号的响应，信号灯/标志/车道规则触发ego的决策

### L2: traffic_light - 信号灯响应

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `red_stop` | 红灯刹停 | 红灯前刹停 | - |
| `yellow_stop` | 黄灯刹停 | 黄灯前刹停 | - |
| `green_pass` | 绿灯通行 | 绿灯正常通行 | - |
| `resume_first` | 头车起步 | 停止线第一辆车起步 | - |
| `resume_follow` | 跟随起步 | 非头车跟随起步 | - |
| `wait_area_entry` | 待行区进入 | 驶入待行区 | - |
| `warning_light` | 警示灯注意 | 黄闪等警示灯 | - |

### L2: traffic_sign - 交通标志响应

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `stop_sign` | 停止标志 | 对停止标志响应 | - |
| `yield_sign` | 让行标志 | 对让行标志响应 | - |
| `lane_arrow` | 车道箭头牌 | 对车道指示响应 | - |
| `prohibition` | 禁令标志 | 对禁令标志响应 | - |
| `warning` | 警告标志 | 对警告标志响应 | - |

### L2: speed_limit - 限速响应

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `sign_limit` | 标志限速 | 对限速标志响应 | - |
| `nav_limit` | 导航限速 | 对导航限速响应 | - |
| `bump_limit` | 减速带限速 | 减速带前限速 | - |
| `crosswalk_limit` | 斑马线限速 | 斑马线前限速 | - |

### L2: lane_rule - 车道规则遵从

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `laneline_normal` | 普通车道线 | 遵从普通车道线 | - |
| `guidance_line` | 路口引导线 | 遵从路口引导线 | - |

### L2: special_lane - 特殊车道

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `bus_lane` | 公交车道 | 公交专用车道通行 | - |
| `tidal_lane` | 潮汐车道 | 潮汐车道通行 | - |
| `variable_lane` | 可变车道 | 可变导向车道 | - |
| `turn_only_right` | 右转专用道 | 右转专用车道 | - |
| `turn_only_left` | 左转/掉头专用道 | 左转掉头专用车道 | - |

### L2: special_facility - 特殊设施通行

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `toll_etc` | ETC通道 | 通过ETC不停车 | - |
| `toll_manual` | 人工收费 | 人工收费通道 | - |
| `toll_plaza` | 收费站广场选道 | 收费站前广场 | - |
| `gate` | 闸机通行 | 通过闸机 | keyframe=闸杆抬起 |
| `roundabout` | 环岛通行 | 通过环岛 | 记录目标出口 |

### L2: road_change - 现场变更响应

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `construction` | 施工改道 | 施工导致道路变更 | - |
| `cone` | 锥桶改道 | 锥桶指示的临时改道 | - |
| `accident` | 事故占道 | 事故导致占道 | - |

---

## L1: 主动机动 (proactive)

> **定义**: ego主动发起的机动，换道/避障/转弯等主动行为

### L2: lane_change - 换道

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `navigation` | 导航换道 | 导航指示换道（路口转向/出匝道） | 记录剩余距离 |
| `efficiency` | 效率换道 | 为提高效率换道（压速车/排短队） | 记录速度差 |
| `escape` | 脱困换道 | 为脱离阻塞换道 | 记录阻塞原因 |
| `overtake` | 超车换道 | 为超车换道 | 记录被超车辆 |
| `abort` | 换道中止 | 换道取消回中 | keyframe=开始回中 |

### L2: merge_interaction - 汇入交互

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `normal_merge` | 普通汇入 | 正常匝道汇入 | - |
| `zipper_merge` | 交替汇入 | 交替汇入场景 | - |
| `split_exit` | 匝道驶出 | 从主路驶出匝道 | - |

### L2: obstacle_avoidance - 避障

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `in_lane` | 道内避障 | 不跨线避让 | 横向=in_lane_nudge |
| `borrow_lane` | 借道避障 | 需要跨线借道 | 横向=out_of_lane_nudge |
| `ignore` | 无视通过 | 判断可安全通过不避让 | - |

### L2: turn - 路口转弯

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `straight` | 直行 | 路口直行通过 | - |
| `left_normal` | 常规左转 | 标准左转 | - |
| `left_unprotected` | 无保护左转 | 无专用灯左转 | 记录对向车流 |
| `left_cut_corner` | 左转内切 | 左转内切 | 记录内切程度 |
| `right_normal` | 常规右转 | 标准右转 | - |
| `uturn` | U-turn | 掉头 | 记录掉头空间 |

### L2: irregular_intersection - 异形路口

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `route_selection` | 出口选路 | 异形路口选择出口 | - |
| `lane_selection` | 出口选道 | 异形路口选择车道 | - |

### L2: roundabout - 环岛通行

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `entry` | 环岛进入 | 进入环岛 | - |
| `exit` | 环岛驶出 | 离开环岛 | 记录目标出口 |
| `lane_in_roundabout` | 环岛内选道 | 环岛内车道选择 | - |

### L2: pull_over - 靠边停车

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `normal` | 常规靠边 | 正常靠边停车 | - |
| `gate_stop` | 闸机停车 | 闸机前停车等待 | - |

---

## L1: 安全临界 (safety)

> **定义**: 安全临界场景，AEB触发/紧急避险等安全相关场景

### L2: aeb - 紧急制动

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `vehicle` | 对车AEB | 对车辆触发AEB | - |
| `vru` | 对VRU AEB | 对行人/骑行者AEB | - |
| `large_vehicle` | 对大车AEB | 对大车/异形车AEB | - |

### L2: emergency_maneuver - 紧急避险

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `steering` | 紧急转向 | 紧急转向避险 | - |

### L2: near_miss - 险情未遂

| L3 ID | 名称 | 条件 | 标注规格差异 |
|-------|------|------|-------------|
| `general` | 一般险情 | TTC曾小于安全阈值但未碰撞 | - |

---

## 完整ID格式

```
{L1}.{L2}.{L3}

示例:
- reactive_agent.cutin.urgent
- reactive_agent.cutin.ramp
- reactive_road.blind_spot_slowdown.slope
- reactive_rule.special_lane.bus_lane
- proactive.lane_change.navigation
- proactive.turn.left_unprotected
```

---

## 场景树状图

```
场景分类体系 v2.0 (5 L1 | 30 L2 | 95 L3)
│
├── reactive_agent (交互响应) [8 L2, 32 L3]
│   ├── cutin [7]: urgent, slow, large_vehicle, from_stationary, ramp, congestion, intersection
│   ├── vru_crossing [3]: horizontal, diagonal, crosswalk
│   ├── vru_emergence [2]: static_occlusion, dynamic_occlusion
│   ├── vru_invasion [3]: vru_cutin, same_direction, opposite_direction
│   ├── vehicle_abnormal [4]: reversing, cutout_reveal, sudden_brake, abnormal_motion
│   ├── intersection_interaction [4]: unprotected_left, right_vs_straight, same_direction_turn, cross_conflict
│   ├── following [6]: steady, stop_and_go, creeping, follow_start, follow_stop, lead_sudden_brake
│   ├── passing [3]: narrow_road, large_vehicle, construction
│   └── animal [2]: crossing, on_road
│
├── reactive_road (路况适应) [5 L2, 21 L3]
│   ├── blind_spot_slowdown [7]: unsignalized, ramp, curve, slope, vehicle, gap, construction
│   ├── geometry_adaptation [10]: high_curvature, slope_up, slope_down, narrow, tunnel, rural, mountain, dead_end, unstructured, laneline_abnormal
│   ├── surface_adaptation [5]: wet, puddle, snow_ice, pothole, speed_bump
│   ├── lighting_adaptation [3]: glare, low_light, transition
│   └── weather_adaptation [3]: rain, fog, snow
│
├── reactive_rule (规则遵从) [7 L2, 22 L3]
│   ├── traffic_light [7]: red_stop, yellow_stop, green_pass, resume_first, resume_follow, wait_area_entry, warning_light
│   ├── traffic_sign [5]: stop_sign, yield_sign, lane_arrow, prohibition, warning
│   ├── speed_limit [4]: sign_limit, nav_limit, bump_limit, crosswalk_limit
│   ├── lane_rule [2]: laneline_normal, guidance_line
│   ├── special_lane [5]: bus_lane, tidal_lane, variable_lane, turn_only_right, turn_only_left
│   ├── special_facility [5]: toll_etc, toll_manual, toll_plaza, gate, roundabout
│   └── road_change [3]: construction, cone, accident
│
├── proactive (主动机动) [7 L2, 16 L3]
│   ├── lane_change [5]: navigation, efficiency, escape, overtake, abort
│   ├── merge_interaction [3]: normal_merge, zipper_merge, split_exit
│   ├── obstacle_avoidance [3]: in_lane, borrow_lane, ignore
│   ├── turn [6]: straight, left_normal, left_unprotected, left_cut_corner, right_normal, uturn
│   ├── irregular_intersection [2]: route_selection, lane_selection
│   ├── roundabout [3]: entry, exit, lane_in_roundabout
│   └── pull_over [2]: normal, gate_stop
│
└── safety (安全临界) [3 L2, 4 L3]
    ├── aeb [3]: vehicle, vru, large_vehicle
    ├── emergency_maneuver [1]: steering
    └── near_miss [1]: general
```

---

## 版本变更记录

### v2.0.0 (2026-01-19)

- 文档重构：从 `appendix_full_taxonomy.md` 重命名为 `TAXONOMY.md`
- 作为场景分类的唯一权威来源

### v1.1.0 (2026-01-15)

**新增场景（参考外部版本补充）：**

| 分类 | 新增L2/L3 | 来源 |
|------|-----------|------|
| reactive_agent | `cutin.ramp`, `cutin.congestion`, `cutin.intersection` | 匝道/拥堵/路口cutin |
| reactive_agent | `vru_invasion` (L2) | VRU入侵车道 |
| reactive_agent | `following` 细分 | 跟车场景细分 |
| reactive_agent | `passing` (L2) | 会车场景 |
| reactive_agent | `animal` (L2) | 动物响应 |
| reactive_road | `blind_spot_slowdown` 细分 | 盲区类型细化 |
| reactive_road | `geometry_adaptation` 扩展 | 山路/断头路/非结构化 |
| reactive_road | `weather_adaptation` (L2) | 天气适应独立 |
| reactive_rule | `traffic_light` 合并扩展 | 信号灯场景合并 |
| reactive_rule | `traffic_sign` 细分 | 交通标志细分 |
| reactive_rule | `speed_limit` (L2) | 限速类型独立 |
| reactive_rule | `lane_rule` (L2) | 车道线遵从 |
| reactive_rule | `special_lane` (L2) | 特殊车道 |
| reactive_rule | `road_change` (L2) | 现场变更 |
| proactive | `merge_interaction` (L2) | 汇入交互细分 |
| proactive | `turn.straight`, `turn.left_unprotected` | 路口场景扩展 |
| proactive | `irregular_intersection` (L2) | 异形路口 |
| proactive | `roundabout` (L2) | 环岛独立 |

---

## 文档引用

- **核心规格**：[SPEC.md](SPEC.md) - 设计原则、标注规格
- **数据格式**：[DATA_FORMAT.md](DATA_FORMAT.md) - 数据交换格式
- **标注示例**：[examples/](../examples/) - JSON示例文件
