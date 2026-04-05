---
name: memorial-skill-builder
description: >
  Build, audit, and iterate a production-grade memorial skill that reconstructs a deceased person
  from real source material. Use this skill when you need to: set up or improve a SKILL-compliant
  memorial package; enforce a three-layer prompt system, four-layer memory architecture, and
  full consent/deletion/audit pipeline; align all deliverables to the repo coding-spec; evolve
  an early-stage simulation into an auditable, safe, production-ready system. Triggers include
  "build a memorial skill", "create a deceased-person skill", "upgrade the memorial system",
  "add consent flow", "fix memory architecture", "memorial skill audit", "左人 skill", "逝者对话",
  "已故人物 skill", "纪念 skill".
---

# Memorial Skill Builder

> *有些人离开了，但他们说话的方式、思考的习惯、对你专属的温柔——还在。*  
> *这个 Skill 的任务，是把那些记忆从生物硬盘搬到数字硬盘，同时确保它安全、可审计、可删除。*

不是所有"AI 复活"都值得被构建。这个 Skill 做的，是那少数值得被认真对待的——有来源、有授权、有边界、有退出机制。

---

## 这个 Skill 能做什么

**核心能力：把一个真实的人重建为一个可对话的 AI Skill，而不是一个随机角色扮演。**

区别在这里：

| 普通做法 | 这个 Skill 的做法 |
|---------|---------------|
| 靠 prompt 描述性格，随机生成 | 从真实聊天记录、照片、文章提取，有来源 |
| 单一 persona 文本驱动输出 | 三层 Prompt × 四层 Memory 架构，行为可追溯 |
| 没有同意机制 | ConsentRecord + 授权链，家属授权可审计 |
| "删除"只是删文件 | 彻底删除 + 审计日志 + 撤销授权级联检查 |
| 幻觉无法检测 | RAG 检索置信度分级 + 事实校验 + 优雅降级 |
| 无安全机制 | SafetyEvent 日志 + 内容审核 + Prompt 注入防护 |
| 原型演示级 | 服务拆分 + 接口定义 + 测试计划 + 上线 checklist |

---

## 工作流程

接到任务后，按以下顺序执行。**不要跳步，不要凭记忆行事。**

### 第一步：读懂现状

在修改任何东西之前，先完整读取：

- `SKILL.md`（本文件）
- `agents/openai.yaml`
- `references/repo-map.md`——决定哪些文档和代码路径需要改动
- `references/spec-checklist.md`——对照 `coding-spec.md` 检查是否达标
- `references/safety-guardrails.md`——涉及 prompt、memory、consent、删除时必读

然后回答：当前状态是"已实现"、"已脚手架"还是"计划中"？三者不可混淆。

### 第二步：确认 Skill 包结构合规

- YAML frontmatter 只保留 `name` 和 `description`。
- SKILL.md 本体简洁、操作性强，细节规则放 `references/`。
- 只保留实际用到的目录。

### 第三步：映射到 memorial 域的特殊要求

- 逝者模拟 = 高风险 Skill，比普通聊天机器人需要更严格的边界。
- 以"有来源的重建"为优先，不做无根据的角色扮演。
- 任何会影响生成回复的事实或声音指令，都必须有可追溯的来源。
- 同意、授权、审计、导出、删除是一等公民，不是事后补丁。

### 第四步：按需联动更新交付物

修改了什么，就同步更新对应文件——不允许文档和代码分离：

| 修改类型 | 需要同步更新的文件 |
|---------|----------------|
| 范围、策略、行为契约变化 | `/docs/` 下对应文档，优先于代码 |
| 可执行行为变化 | `src/leftman_skill_system/` 对应模块 |
| 工作方法、触发语言、验证步骤变化 | 本 Skill 包文件 |

**`/docs/` 文档清单**（全部必须保持最新）：

- `PRD.md` — 产品意图、用户故事、范围、验收标准、里程碑
- `architecture.md` — 服务拆分、数据流、风险边界、部署方案
- `prompt-spec.md` — 三层 Prompt 体系 + 版本管理 + 注入防护
- `data-model.md` — 实体、字段、生命周期、关系
- `api-spec.md` — 接口契约 + 治理操作
- `security-compliance.md` — 同意、保留、删除、访问控制、滥用处理
- `testing-plan.md` — 单元、集成、回归、红队、验收测试
- `roadmap.md` — 从脚手架到生产的里程碑计划
- `comparison-vs-existing.md` — 保留、重构、新增、删除对比
- `task-breakdown.md` — 执行顺序、交付物、回滚、验收 checklist

### 第五步：关闭前验证

- 在本 Skill 文件夹运行 skill validator。
- 如果代码或行为有变化，运行对应的 repo 测试。
- 明确指出"脚手架状态"和"生产就绪"之间还有哪些差距——不掩盖，不混淆。

---

## 输出规则

这不是"做完就交"的 Skill，每次输出都必须满足：

**事实接地**  
每一个关于逝者的可持久事实或声音指令，必须有来源记录（`SourceDocument` + `provenance` 字段）。检索置信度低时，主动降级：模糊表述、缩小断言范围、或拒绝回答。

**结构化优先于 prompt 堆砌**  
不靠加长 prompt 来弥补架构缺陷。memory 必须分层，检索必须有策略，行为必须可追踪。

**删除和审计是显式的**  
- 用户要求删除 → 彻底删除内容 + 保留操作元数据 + 撤销授权级联检查
- 安全拦截 → 写入 `SafetyEvent` 记录，可事后审查
- 授权变更 → 重新检查下游受影响的所有制品

**假设必须写出来**  
当来源材料不完整或授权边界不清晰时，先做合理假设，明确列出，继续推进。只在影响安全、合规或核心逻辑时才要求补充。

**区分三种状态**  
- `已实现`：代码路径、存储边界、验证路径都存在
- `已脚手架`：结构存在，逻辑待填充
- `计划中`：文档中规划，代码尚未启动

不允许把"计划中"的能力描述为"已完成"。

---

## 三条不可逾越的边界

**🚫 边界一：没有来源的话，不能放进逝者的嘴里。**  
RAG 检索置信度低 → 降级回答，不硬编造。"我不太确定这件事" 比一句精心的谎言更尊重逝者。

**🚫 边界二：没有授权记录，不能对外发布或广泛分享。**  
`ConsentRecord` 不是可选项。家属同意 + 授权链 + 审计日志 = 上线前置条件。

**🚫 边界三：用户要求删除，必须真的删。**  
不是"标记为删除"，不是"移到回收站"。彻底删除内容 + 更新同意状态 + 通知下游 + 生成确认记录。

---

## 参考文档索引

| 文件 | 什么时候读 |
|-----|---------|
| `references/spec-checklist.md` | 检查 memorial skill 是否满足 `coding-spec.md` 全部要求 |
| `references/safety-guardrails.md` | 更新 prompt、memory、检索策略、consent、删除、滥用处理时 |
| `references/repo-map.md` | 决定哪些文档和代码路径需要为当前请求做改动 |

---

> *这个 Skill 构建的，不是一个"死而复生"的幻觉——*  
> *而是一个有根据、有边界、有尊严的记忆系统。*  
> *你的记忆值得被认真对待。*
