# 模板学习与风格复用

## 三种模式

| 模式 | 适用 | 可以复用 | 不可以复用 |
|---|---|---|---|
| `strict_rebuild` | 用户自有或明确获授权的PPTX模板 | 母版、版式、色彩、字体、图形和动效语言 | 模板中的旧项目事实、过期数据、无关客户内容 |
| `visual_inspiration` | 截图、参考作品、第三方模板或只要求类似气质 | 构图逻辑、信息层级、留白、节奏和抽象配色关系 | 原图、完整文案、Logo、专有插画、逐页机械复刻 |
| `brand_extension` | 品牌手册或已有品牌模板 | 已授权VI、字体层级、色彩角色和组件规律 | 伪造未提供的品牌资产，牺牲可读性强套VI |

未明确时使用 `visual_inspiration`。严格延续模式只在模板权限清楚时使用。

## 执行流程

1. 用 `presentations` 技能检查PPTX的母版、页面比例、字体、色板、网格、动画与媒体；截图不能代替PPTX的完整检查。
2. 先输出项目级 `style profile`：来源、模式、授权状态、视觉母题、色彩角色、字体层级、边距网格、图片裁切、形状线条、P/C/M映射、必须沿用项和禁止项。
3. 将 style profile 与当前项目的行业、场景、受众、证据和数据口径合并。模板只回答“怎么呈现”，项目资料回答“呈现什么”。
4. 先制作2-3页代表页面验证风格，再扩展全套。严格延续模式优先复用用户模板母版；视觉借鉴模式必须使用新的内容结构和视觉组合。
5. 交付时记录模板/参考来源、使用模式、授权状态、复用资产和残余风险。

## Style Profile 最小字段

```text
style_source: user_template | brand_guide | reference_deck | screenshots
style_mode: strict_rebuild | visual_inspiration | brand_extension
rights_status: user_owned | licensed | reference_only | unknown
canvas_and_grid: 比例、留白、对齐系统
palette_and_type: 色彩角色、字体层级与可替代字体
image_and_shape: 裁切、材质、图形、线条和图标气质
page_language: 推荐P码组合、密度、章节和结尾处理
motion_language: 推荐M码、速度、媒体限制和静态降级
must_keep: 必须沿用的设计原则
must_avoid: 不可复用的元素或内容
status: project_only | candidate | promoted
```

## 学习边界

style profile 默认 `project_only`。只有用户允许匿名化、规律已脱离模板原始素材/文案/品牌、并由至少3个不同项目验证后，才可升级为大琰PPT的通用Profile。不要沉淀“像某份模板”；要沉淀“为什么这种层级、留白或动效适合某类观众”。
