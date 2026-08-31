# PPT 生产参数字典

## 使用规则

每次生成先形成 `production manifest`。参数分为：`required` 必须明确或推断、`recommended` 影响质量、`default` 可采用安全默认值、`blocker` 缺失时不能把内容当事实交付。

## A. 分类与演示任务

| 参数 | 级别 | 取值/说明 | 缺失处理 |
|---|---|---|---|
| `industry_code` | required | I01-I15 | 从资料推断；置信度低于 0.8 时确认 |
| `scenario_code` | required | H01-H12 | 从主题、受众和阶段推断；冲突时确认 |
| `audience` | blocker | 谁看、谁决策、专业程度 | 不明确时只出创意简报，不做最终叙事 |
| `project_stage` | required | 规划/执行/复盘/验收/对外传播/比赛 | 从资料推断；影响页面骨架 |
| `communication_job` | blocker | 希望观众批准、学习、合作、购买、评审或理解什么 | 不明确时先给 2-3 个候选目标供确认 |
| `duration_minutes` | recommended | 现场演讲时长 | 缺失时按 10-15 页、10 分钟估算 |
| `viewing_mode` | required | 现场/线上/自读 | 缺失时默认现场演讲；影响密度与动效 |
| `language` | default | 中文/双语/英文 | 默认中文；双语需预留更大文本空间 |

## B. 内容、数据与事实

| 参数 | 级别 | 取值/说明 | 缺失处理 |
|---|---|---|---|
| `topic` | required | 本次 PPT 的具体主题 | 从文件标题和正文提取 |
| `core_claim` | required | 一句最重要结论 | 从材料归纳；标记为“建议主张”直到确认 |
| `must_include` | recommended | 必须出现的章节、领导意见、产品/案例 | 按资料出现频次和用户提示提取 |
| `must_exclude` | required | 禁止内容、敏感内容、竞品、保密信息 | 缺失时不主动添加竞争性或敏感判断 |
| `data_source` | blocker | 数据出处、时间范围、单位、统计口径 | 缺失时可展示原始数据，但不做强结论 |
| `evidence_assets` | required | 文档、表格、案例、图片、视频、访谈 | 建立资产清单与可用页映射 |
| `fact_status` | required | 已核验/待核验/仅建议/不可公开 | 所有待核验内容不得写成既成事实 |
| `confidentiality` | blocker | 公开/内部/保密/脱敏要求 | 默认内部交流稿，外发前要求确认 |

## C. 页面与叙事

| 参数 | 级别 | 取值/说明 | 安全默认 |
|---|---|---|---|
| `slide_count` | default | 根据时长、资料密度、场景决定 | 5 分钟 6-9 页；10 分钟 10-14 页；20 分钟 15-22 页 |
| `narrative_arc` | required | 由 H 场景蓝图指定 | 先结论/问题/证据/路径/行动，不使用空目录页 |
| `page_mix` | recommended | 场景、观点、数据、案例、路径、结束页比例 | 15 页中纯文字不超过 2 页；至少 40% 场景视觉 |
| `key_decision_page` | required | 需要观众拍板/记住的页面 | 每套至少 1 页，结尾或中段明确出现 |
| `speaker_notes` | default | 讲述重点、动效顺序、资料口径 | 默认交付；自读版可弱化 |

## D. 视觉与品牌

| 参数 | 级别 | 取值/说明 | 安全默认 |
|---|---|---|---|
| `brand_assets` | recommended | Logo、标准色、字体、模板、VI、人物/产品图 | 用户资产优先；缺失时不伪造品牌 |
| `style_reference` | recommended | 用户模板PPTX、品牌模板、参考作品或截图 | 先建立项目级style profile；未提供时按行业/场景推断 |
| `style_mode` | default | strict_rebuild / visual_inspiration / brand_extension | 默认 visual_inspiration |
| `style_rights` | required | user_owned / licensed / reference_only / unknown | 权限不清时只学习抽象规律，不复用模板资产 |
| `visual_motif` | required | 地点、产品、人物、生产线、实验、服务现场等 | 由 I 行业视觉卡和资料共同推断 |
| `mood` | recommended | 庄重/可信/增长/探索/教学/人文/高端 | 由受众和 H 场景推断 |
| `palette` | default | 70/20/10 基底/主色/强调色 | 行业视觉卡默认；用户 VI 覆盖 |
| `type_style` | default | 字体气质、标题/正文层级 | 中文默认清晰现代；不得用极细或装饰字体承担正文 |
| `image_policy` | required | 用户图片优先、可联网检索、可 AI 生图、仅本地素材 | 未声明时使用用户素材优先，外部素材必须记录来源 |
| `visual_asset_plan` | required | 每页的图片/视频槽位、比例、文本安全区、图层与来源策略 | 仅有生成素材或动态素材时必须建立；先校验再生成 |
| `image_generation_provider` | default | `imagegen` 内置 Image 2 / 不生成 | 未声明时不生成；缺图仅提出建议 |
| `layout_density` | default | 现场/自读/双语的文字密度 | 现场低密度、自读中密度；不靠缩小字体塞内容 |
| `avoid_list` | recommended | 禁止颜色、元素、风格、竞品、人物形象 | 默认禁用卡片墙、泛化赛博网格、无意义装饰线 |

## E. 媒体与动效

| 参数 | 级别 | 取值/说明 | 安全默认 |
|---|---|---|---|
| `motion_level` | required | L0 静态 / L1 克制 / L2 叙事 / L3 舞台 | 汇报 L1；路演/课件 L2；可靠大屏活动才 L3 |
| `dynamic_anchor_count` | default | GIF/视频/关键动态场景数量 | 12 页以上 L2 演示为 2-4 个；L1 为 0-1 个 |
| `playback_environment` | blocker | PowerPoint 版本、是否联网、声音、屏幕比例、现场是否可播放 | 缺失时禁止依赖音频和复杂原生动画 |
| `animation_policy` | default | 原生动画/GIF/视频/备注 | 优先可播放 GIF 或稳定对象；原生动画不足则写备注 |
| `motion_fallback` | required | 动态失效时的首帧与静态讲述方式 | 所有动态页都要可静态阅读 |
| `motion_render_provider` | recommended | 用户视频 / HyperFrames低速循环 / 不生成 | 未声明时不生成视频，使用静态首帧 |

## F. 交付与质量

| 参数 | 级别 | 取值/说明 | 安全默认 |
|---|---|---|---|
| `output_format` | default | PPTX、PDF、图片预览、演讲稿、素材说明 | 默认 PPTX + 素材/许可说明 |
| `editable_scope` | required | 文字、数据、图表、路径是否可编辑 | 默认全部业务对象可编辑 |
| `source_record` | required | 数据、图片、AI 图、字体、许可、提示词记录 | 默认记录，不把未授权素材伪装成自有 |
| `qa_threshold` | default | 最低交付分 | 85/100；硬失败项见生产门禁 |
| `reviewer` | recommended | 最终审核人/部门 | 缺失时标注“用户复核待完成” |
| `residual_risk` | required | 数据、版权、原生动画、播放环境等未完成事项 | 必须如实交付，不得隐瞒 |

## 文档/图片自动解析策略

1. 从文档提取主题、主张候选、数据、时间、组织、案例和敏感信息；从图片提取地点、对象、场景和品牌线索。
2. 为每个推断值记录 `source`、`confidence`、`status`：`confirmed`、`inferred`、`needs_confirmation`、`blocked`。
3. 仅在以下情形暂停并提问：受众/最终行动不明；数据或事实需外发却无来源；品牌/保密边界不明；播放环境决定动效可行性；资料互相矛盾。
4. 其他缺失项使用安全默认值，并在 manifest 中公开说明。

## Production Manifest 模板

```yaml
project:
  classification: "I__ × H__"
  audience: { value: "", status: needs_confirmation }
  stage: { value: "", status: inferred }
  communication_job: { value: "", status: needs_confirmation }
  duration_minutes: { value: 10, status: default }
content:
  core_claim: { value: "", status: inferred }
  evidence: []
  data_gaps: []
  confidentiality: internal
design:
  visual_motif: ""
  palette: ""
  style_reference: { value: "", status: default }
  style_mode: { value: visual_inspiration, status: default }
  visual_asset_plan: []
  image_generation_provider: { value: none, status: default }
  page_archetype_mix: [P01, P04, P06, P08, P18]
  image_policy: user_assets_first
  motion_level: L1
delivery:
  formats: [pptx, source_notes]
  qa_threshold: 85
  residual_risks: []
```
