---
name: dayan-ppt
description: 从基础材料到可直接交付的专业PPT生产与持续学习系统。用于任何行业的汇报、方案、课件、路演、研究、传播、验收或客户提案，尤其适合用户只提供Word、PDF、Excel、多工作表清单、图片或既有PPT时；先识别I01-I15行业、H01-H12横向应用、受众和阶段，再组合页面原型、图表语义、动效与视觉规则，完成数据溯源、制作、逐页QA和交付后经验沉淀。所有事实和数字必须来自原始材料或可复核计算，禁止编造。
---

# 大琰PPT Skill

把PPT视为“分类判断 + 证据架构 + 演示叙事 + 可编辑制作 + 放映验收 + 经验沉淀”的完整生产任务。视觉风格可以变化，事实边界、场景逻辑和质量门禁不可变化。

执行命令时，将当前 `SKILL.md` 所在目录解析为 `SKILL_DIR`。

## 核心契约

1. **数据零编造**：数字、金额、比例、数量、日期、排名、案例、政策、客户、奖项和成效必须回到原始材料或明确公式。缺证据时删去、标记待补或改写为建议，不得补数。
2. **先分类后制作**：先确定 `I01-I15 × H01-H12 × 受众 × 阶段 × 观看方式`，再选叙事、页面、图表、视觉和动效。
3. **内部判断不外显**：用户说的“重点、星标、领导会关心、必须突出”用于内容选择，不能直接变成“领导关切、星标任务、校验重点”等观众可见文案。
4. **风格可变**：模板、主题色、图片语言和版式随行业、受众、品牌、地域及用户偏好变化。不得把某次蓝色、红金或某个模板固化为同类PPT的唯一风格。
5. **从材料到交付**：不得停在提纲或半成品。完成可编辑PPTX、全页渲染、数据核对、文件完整性检查和明确的剩余风险。
6. **学习必须有证据**：只沉淀被用户确认或经QA证明有效的规则；把失败做法记录为禁用模式。不得把单个项目的客户名称、敏感数字或路径写进全局学习库。

## 必须联合使用的能力

- 创建或编辑PPT时，加载并遵守 `Presentations` 技能，使用 `@oai/artifact-tool`，不得使用 `python-pptx`。
- 处理Excel/CSV时，加载 `Spreadsheets` 技能；处理PDF/Word时分别加载对应文档技能。
- 用户提供既有PPT、品牌模板、参考作品或截图时，先读取 [template-style-study.md](references/template-style-study.md)，输出项目级 `style profile`。模板只决定视觉与版式，不能覆盖项目事实、数据口径、保密边界和可读性。
- 页面缺少合适图片、人物、产品、纹理或场景图时，先读取 [visual-asset-reverse-brief.md](references/visual-asset-reverse-brief.md)，形成并校验 `visual-asset-plan.json`；仅在允许生成时加载 `imagegen`，默认走其内置 Image 2 路径生成单个可组合位图素材。
- 需要真实视频/GIF或6-10秒动态锚点且无用户媒体时，先按素材规格生成静态首帧；仅在低文字密度、大主视觉的 M05/M08 页面实际需要运动时，加载 `hyperframes` 制作确定性的低速循环。动态必须记录“图片结构 -> 焦点 -> 运动路径 -> 时长 -> 静态首帧降级”。Image 2 不生成视频；没有可靠视频能力时交付静态首帧和演讲顺序，不得虚称已生成动态媒体。

## 第一步：完整盘点材料

1. 递归列出用户指定范围内的文件，确认文档、工作簿、图片、视频、模板和既有PPT。
2. 对每个工作簿读取**全部工作表**，不得只读活动表或汇总表。运行：

```bash
python "$SKILL_DIR/scripts/audit_workbooks.py" <workbook...> --output <source-ledger.json>
```

3. 记录每份源文件的哈希、每个工作表、非空单元格、公式、合并区域和星号标记。星号只代表“必须覆盖的证据”，不能在正式PPT中显示为内部标签。
4. 建立事实账本：`事实/数字 -> 文件 -> 工作表/页码 -> 单元格/段落 -> 状态`。状态只能是 `confirmed`、`calculated`、`needs_confirmation`、`excluded`。
5. 发现资料冲突时保留双方来源并暂停强结论；不得自行选择更好看的数字。

## 第二步：完成分类与生产清单

1. 读取 [industry-scenario-matrix.md](references/industry-scenario-matrix.md) 判定行业I码和横向应用H码。
2. 读取 [scenario-blueprints.md](references/scenario-blueprints.md) 获取该H码必须回答的问题、必备页面、证据和页数范围。
3. 读取 [industry-visual-cards.md](references/industry-visual-cards.md) 获取行业视觉对象、色彩倾向和禁止项。
4. 查询同类已验收经验：

```bash
python "$SKILL_DIR/scripts/learning_registry.py" query --industry I__ --scenario H__
```

5. 按 [parameter-schema.md](references/parameter-schema.md) 生成 `production-manifest.yaml`，区分 confirmed、inferred、default、blocker、residual risk。
6. 只在受众/最终行动、外发数据口径、保密边界或播放环境会改变结果时提1-3个关键问题；其余低风险参数采用安全默认值继续。

分类卡至少包含：

```text
分类：I__ × H__
受众：谁看、谁决策
阶段：规划/执行/复盘/验收/传播/比赛
沟通任务：演示结束时谁应因为什么证据作出什么判断或行动
观看：现场/线上/自读，预计时长
证据边界：可用材料、不可虚构、保密与外发边界
```

## 第三步：把资料转成证据架构

1. 不把原始资料做成设备清单或文字搬运；先归纳观众必须理解、相信或批准的主张。
2. 每个主张至少绑定一项原始证据；每项关键数字必须有来源、时间、单位和口径。
3. 关键数字包括：标题数字、KPI、预算、比例、数量、时间、排名、图表数据、结论所依赖的差异值。
4. 对关键数字创建 `fact-claims.json`，运行：

```bash
python "$SKILL_DIR/scripts/verify_workbook_claims.py" <fact-claims.json>
```

5. 计算值必须记录公式和输入单元格；图表必须使用同一口径的可编辑数据。无法验证的数字不得进入正式版。

## 第四步：设计叙事与分镜

1. 从H码蓝图确定叙事，不用同一套目录覆盖所有场景：
   - H03回答“为什么做、怎么做、需要什么资源”。
   - H04回答“做到哪、卡在哪里、需要谁协同”。
   - H05回答“是否完成、证据是什么、遗留问题怎么处理”。
   - H06必须有解释、示例、练习、反馈和迁移。
   - H09必须有痛点、方案、差异、验证、路径、团队和请求。
   - H03/H07/H09，以及以问题和方案为主的工作汇报，可选择 `SCQA` 组织开场：S情境 -> C冲突 -> Q核心问题 -> A答案/行动；在分镜中记录所属段落。课件、验收、纯数据复盘不因形式而强套SCQA。
2. 读取 [page-archetypes.md](references/page-archetypes.md) 选择P01-P18；读取 [chart-semantics.md](references/chart-semantics.md) 选择C01-C12；需要动效时读取 [motion-media-recipes.md](references/motion-media-recipes.md) 选择M01-M08。
3. 每页定义：主张、证据、意义、视觉焦点、P码、讲述顺序、动效/静态降级、来源。
4. 生成 `deck-plan.json`，并在制作前运行：

```bash
node "$SKILL_DIR/scripts/validate-deck-plan.mjs" <deck-plan.json>
```

5. 阻断项未清零不得排版。连续三页同一轮廓、数据页无来源口径、动效无静态降级均需先修复。

## 第五步：写观众可见文案

1. 站在实际汇报方角度写，标题表达结论，不写制作说明或对用户指令的复述。
2. “领导关心什么”只用于决定先讲什么、用什么证据；页面上写项目事实、方案逻辑、结果、风险和行动。
3. “星标/重点/必须有”只用于保证内容覆盖；在PPT中自然融入对应章节，除非原材料本身要求公开标识。
4. 避免“校验版、重点判断、需闭环、需确认、资料可证据化、内部”等生产过程措辞。
5. 不编造成效、服务时限、团队资质、客户评价、政策引用或验收结论。

## 第六步：建立可变视觉系统

视觉优先级：事实/合规/播放限制 > 用户授权模板/品牌资产 > 项目真实对象和观看场景 > 行业视觉卡 > 安全默认值。

- 先定义视觉母题，再定70/20/10色板、字体、图片对象和页面节奏。
- 同类型PPT可使用不同色彩和样式；只要符合受众、行业、品牌和播放环境即可。
- 每页一个主结论、一个主视觉焦点；不把内容默认做成卡片墙、假仪表盘或泛化科技网格。
- 封面、关键场景和结尾优先使用真实或可追溯的高质量视觉；图片不承担未经来源支持的事实。
- 10页以上且存在3个以上目录板块时，默认在正文页顶部加入轻量目录导航；封面、目录页和结束页保持简洁。用户不需要章节页时，不额外插入空章节页。
- 当资料没有合适视觉但页面需要视觉时，先按页面反推素材，而不是先随机生图：`页面主张与P码 -> 文字安全区/视觉焦点 -> 图层与图片槽位 -> 比例/主体位置/裁切 -> 标题信号+风格词+主体+场景 -> 素材规格 -> Image 2提示词 -> 组合与QA`。复杂背景、产品定位或多景合成先画无文字草图，再生成；运行：

```bash
node "$SKILL_DIR/scripts/validate-visual-asset-plan.mjs" <visual-asset-plan.json>
```

- 不让生成图承担真实地点、真实产品外观、真实人物、客户、工程成果或数据证据；这类页面优先用户、官方或授权素材。生成图只承担氛围、概念或明确标记的示意，并记录提示词、来源、页面和可替换边界。对人物仅可在授权下做不改变身份事实的去背、裁切和光色修正；禁止换脸、虚构职业形象或以生成图替代真实人物。对产品仅可做不改变型号、结构、标识和性能的去背、清洁修图或场景合成。

用户模板按 `strict_rebuild`、`visual_inspiration`、`brand_extension` 三种模式使用。未说明时默认 `visual_inspiration`；只学习构图、层级和节奏，不复用模板中的旧项目事实、原图、文案、Logo 或私有资产。严格延续仅适用于用户自有或明确获授权模板，且必须先抽取母版、字体、色彩、网格、P/C/M 映射和禁止项。

详细视觉规则按需读取 [visual-and-motion-handbook.md](references/visual-and-motion-handbook.md)。

## 第七步：完成结尾闭环

不得突然结束在设备、图表、实施步骤或单独“谢谢”页。根据场景用以下一种方式收口：

- 方案/项目：实施 -> 验收交付 -> 预期成效 -> 服务保障 -> 方案总结/下一步。
- 汇报/复盘：结论 -> 风险 -> 行动 -> 待决事项。
- 课件：复盘 -> 练习反馈 -> 迁移任务。
- 路演：验证 -> 路径 -> 明确请求。

最后一页先回扣开场主张，再给行动或“汇报完毕，敬请指导”；不要只放感谢语。

## 第八步：制作与交付门禁

按 [production-gates.md](references/production-gates.md) 执行，至少完成：

1. 使用artifact-tool生成可编辑PPTX，保留旧版本并输出独立新版本，除非用户明确要求覆盖。
2. 渲染每一页并逐页查看大图；联系表只用于整体节奏，不代替全尺寸检查。
3. 运行溢出检查；修复标题换行、正文溢出、孤立标点、专业词拆行、图表遮挡和连接线穿字。
4. 对比最终PPT中的关键数字与事实账本；检查图表单位、时间、口径和来源。
5. 检查PPTX压缩包完整性、页数、页码、页脚、目录导航和媒体嵌入。
6. 低于85分或出现硬失败项不得交付。硬失败包括：虚构数据、关键事实无来源、文字溢出、流程线穿字、文件损坏、把未实现动画宣称为已交付。

## 第九步：持续学习

1. 开始同类任务前查询学习库。`stable_patterns` 和 `stable_rules` 可作为同类经验；`advisory_patterns` 只能用于避免重复问题，不能覆盖当前要求、源材料或事实账本。
2. 交付过程中在scratch持续更新学习候选：用户指出的问题、原做法、修改动作、结果、已接受版本、未采用样式和QA证据。
3. **每次最终交付都必须自动写入候选经验**，不等待用户另行要求。只有PPT已完成、总分不低于85、无溢出、文件完整且无硬失败时，才使用 [assets/learning-record-template.json](assets/learning-record-template.json) 生成匿名精简记录并运行：

```bash
python "$SKILL_DIR/scripts/learning_registry.py" record --file <learning-record.json>
```

4. 新记录使用 `status=candidate`，作为低权重建议立即供后续同类任务查询。用户后续提出修改时，创建带 `supersedes` 的新版本，把问题写入 `rejected_patterns`；查询自动忽略旧版本，禁止静默覆盖历史。
5. 用户明确表示满意、通过、采用或验收后，才将新版本记为 `status=accepted`。**沉默不是验收信号**；系统无法从“暂时没有下一条消息”可靠推断满意，禁止据此升级稳定规则。
6. 每条记录只保留各不超过8项的可复用抽象：分类、场景、受众类型、材料类型、有效叙事、失败模式、数据规则、视觉可变量和QA结论。脚本自动去重，禁止写客户名称、人员信息、账号密钥、保密数据、完整原文、绝对路径或未经许可的素材。
7. 同一I×H没有历史案例时，首次候选自动形成该分支，不另建笨重行业文档。只有用户允许匿名化、3个不同项目评分不低于85、无事实/版权/播放硬失败且人工确认后，才可标为 `promoted` 并作为同类任务默认规则；模板 style profile 默认项目专属。

持续学习协议详见 [continuous-learning.md](references/continuous-learning.md)。

## 资源路由

- 15行业×12横向应用：[industry-scenario-matrix.md](references/industry-scenario-matrix.md)
- 12类场景蓝图：[scenario-blueprints.md](references/scenario-blueprints.md)
- 15行业视觉卡：[industry-visual-cards.md](references/industry-visual-cards.md)
- P01-P18页面原型：[page-archetypes.md](references/page-archetypes.md)
- C01-C12图表语义：[chart-semantics.md](references/chart-semantics.md)
- M01-M08动效配方：[motion-media-recipes.md](references/motion-media-recipes.md)
- 模板学习与风格复用：[template-style-study.md](references/template-style-study.md)
- 页面反推素材与Image 2：[visual-asset-reverse-brief.md](references/visual-asset-reverse-brief.md)
- 六类基准样例与回归：[benchmark-suite.md](references/benchmark-suite.md)
- 生产参数与默认值：[parameter-schema.md](references/parameter-schema.md)
- 生产门禁与评分：[production-gates.md](references/production-gates.md)
- 交付类型分流：[deck-types.md](references/deck-types.md)
- 可选叙事模式：[narrative-patterns.md](references/narrative-patterns.md)
- 当前政务信息化方案分支：[case-i01-h03-government-it-solution.md](references/case-i01-h03-government-it-solution.md)
- 原项目知识索引：[source-index.md](references/source-index.md)
