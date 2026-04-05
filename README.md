# memorial-skill-builder

> *有些人离开了，但他们说话的方式、思考的习惯、对你专属的温柔——还在。*  
> *Some people leave. But the way they talked, the way they thought, their warmth that was just for you — that stays.*

**为逝去的人，构建一个有根据、有边界、有尊严的 AI 记忆系统。**  
**Build a grounded, bounded, dignified AI memory system for those who are gone.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![WorkBuddy Skill](https://img.shields.io/badge/WorkBuddy-Skill-blueviolet)](https://workbuddy.ai)
[![Production Ready](https://img.shields.io/badge/Grade-Production-green)](#architecture)

&nbsp;

不是所有"AI 复活"都值得被构建。这个 Skill 做的，是那少数值得被认真对待的——**有来源的重建，而不是角色扮演**。

[安装](#安装) · [使用](#使用) · [架构设计](#架构设计) · [伦理边界](#伦理边界) · [English](#english)

---

## 这是什么

`memorial-skill-builder` 是一个 **WorkBuddy Agent Skill**，它的工作是：

> **接收关于逝者的真实素材（聊天记录、文章、照片、口述），构建一个可对话的 AI Skill——同时确保整个过程安全、可审计、可撤销。**

### 它和普通 AI 角色扮演的区别

| 普通做法 | memorial-skill-builder |
|---------|----------------------|
| 靠 prompt 描述性格，随机生成 | 从真实素材提取，每条事实有来源记录 |
| 单一 persona 文本驱动 | 三层 Prompt × 四层 Memory 架构，行为可追溯 |
| 没有同意机制 | `ConsentRecord` + 授权链，家属授权可审计 |
| "删除"只是删文件 | 彻底删除 + 审计日志 + 授权级联撤销 |
| 幻觉无法检测 | RAG 检索置信度分级 + 事实校验 + 优雅降级 |
| 无安全机制 | `SafetyEvent` 日志 + 内容审核 + Prompt 注入防护 |
| 原型演示级 | 服务拆分 + 接口定义 + 测试计划 + 上线 checklist |

---

## 安装

### WorkBuddy / Claude Code

```bash
# 安装到当前项目
mkdir -p .agents/skills
git clone https://github.com/YOUR_USERNAME/memorial-skill-builder .agents/skills/memorial-skill-builder

# 或安装到全局（所有项目可用）
git clone https://github.com/YOUR_USERNAME/memorial-skill-builder ~/.agents/skills/memorial-skill-builder
```

### 依赖（可选，用于数据解析）

```bash
pip3 install -r requirements.txt
```

---

## 使用

在 WorkBuddy 中触发此 Skill，使用以下任意关键词：

```
build a memorial skill
create a deceased-person skill
upgrade the memorial system
add consent flow / fix memory architecture
左人 skill / 逝者对话 / 已故人物 skill / 纪念 skill
```

Skill 会引导你完成以下流程：

1. **读取现状** — 在修改之前，完整审计当前 Skill 包状态
2. **确认授权** — 检查 `ConsentRecord` 是否完整，未授权不继续
3. **导入素材** — 聊天记录、文章、照片、口述均可
4. **构建 / 升级** — 生成或更新三层 Prompt + 四层 Memory 架构
5. **验证 & 交付** — 运行 checklist，明确标注"已实现 / 已脚手架 / 计划中"三种状态

---

## 架构设计

### 三层 Prompt 体系

```
Layer 1 — 系统身份层    核心人格、价值观、说话风格的硬规则
Layer 2 — 记忆注入层    检索到的相关记忆片段，按置信度分级注入
Layer 3 — 对话控制层    当前对话上下文、情绪状态、降级策略
```

### 四层 Memory 架构

```
Tier 1 — 核心身份记录   不变的基础事实：姓名、关键事件、声音特征
Tier 2 — 关系记忆库     与用户共同的经历、对话模式、情感节点
Tier 3 — 动态上下文     当前会话记忆，随对话演化
Tier 4 — 纠正层         用户反馈"ta不会这样说"后，立即生效的修正
```

### 数据来源支持

| 来源 | 格式 | 备注 |
|------|------|------|
| 微信聊天记录 | WeChatMsg / PyWxDump 导出 | 推荐，信息最丰富 |
| QQ 聊天记录 | txt / mht 导出 | 适合学生时代 |
| 社交媒体 | 截图 / 导出文本 | 提取公开人设 |
| 照片 | JPEG/PNG（含 EXIF） | 提取时间线和地点 |
| 写作 / 日记 | 纯文本 | 思维风格与观点 |
| 口述 | 自由输入 | 你的主观记忆 |

### 项目结构

```
memorial-skill-builder/
├── SKILL.md                      # Skill 入口与完整工作流程
├── agents/
│   └── openai.yaml               # Agent 接口定义
├── references/
│   ├── spec-checklist.md         # 对照 coding-spec 的合规检查表
│   ├── safety-guardrails.md      # 安全、伦理、同意、删除规则
│   └── repo-map.md               # 文档与代码路径映射
└── scripts/                      # 辅助脚本（数据解析、验证等）
```

配套项目（`src/leftman_skill_system/`）包含：

- `data-model.md` — 实体、字段、生命周期
- `prompt-spec.md` — 三层 Prompt 版本管理与注入防护
- `api-spec.md` — 接口契约 + 治理操作
- `security-compliance.md` — 同意、保留、删除、访问控制
- `testing-plan.md` — 单元、集成、红队、验收测试
- `architecture.md` — 服务拆分与风险边界

---

## 伦理边界

这是这个项目最重要的部分。

### 🚫 三条不可逾越的底线

**底线一：没有来源的话，不能放进逝者的嘴里。**  
RAG 检索置信度低 → 降级回答，不硬编造。"我不太确定这件事"比一句精心的谎言更尊重逝者。

**底线二：没有授权记录，不能发布或广泛分享。**  
`ConsentRecord` 不是可选项。家属同意 + 授权链 + 审计日志 = 上线前置条件。没有这三项，Skill 不对外开放。

**底线三：用户要求删除，必须真的删。**  
不是"标记为删除"，不是"移到回收站"。彻底删除内容 + 更新同意状态 + 通知下游 + 生成确认记录。

### ⚠️ 使用范围声明

- 本 Skill 仅用于**个人缅怀与家庭记忆保存**
- 所有生成内容均为 AI 模拟，不能替代真实沟通
- 若对话引发心理危机，请立即寻求专业帮助：**北京心理危机研究与干预中心 010-82951332**
- 严禁用于公开传播、商业代言或未经授权的人物模拟

### 法律说明

> 根据中国《个人信息保护法》，已故者个人信息需取得近亲属同意方可处理。  
> 本 Skill 强制要求 `ConsentRecord`，并提供完整的授权、审计和撤销流程。

---

## 输出质量保证

每次 Skill 输出都遵循以下规则：

**事实接地** — 每一个可持久事实或声音指令，必须有 `SourceDocument` + `provenance` 字段支撑

**结构优先** — 不靠堆 prompt 来弥补架构缺陷；memory 分层、检索有策略、行为可追踪

**三种状态区分**（这很重要，不允许混淆）：
- `已实现` — 代码路径、存储边界、验证路径都存在
- `已脚手架` — 结构存在，逻辑待填充  
- `计划中` — 文档规划，代码尚未启动

**假设必须写出来** — 来源不完整时，先做合理假设，明确列出，继续推进；只在影响安全或合规时才要求补充

---

## 致敬

本项目的场景灵感来源于 **[ex-partner-skill（前任.skill）](https://github.com/therealXiaomanChu/ex-partner-skill)**，它首创了"把人蒸馏成 AI Skill"的双层架构。`memorial-skill-builder` 在这个思路的基础上，将场景从情感治愈迁移到**有授权的逝者记忆重建**，并为生产环境增加了完整的合规、安全和审计体系。

---

## 写在最后

> *人的记忆是一种不讲道理的存储介质。*  
> *你可能记不住高数公式，记不住今天开了什么会，但你清楚记得某个下午的光线，某句话的语气，某个人怎么叫你的名字。*
>
> *这个 Skill 做的，是把那些不讲道理的记忆，用讲道理的方式存下来。*  
> *有来源，有边界，可以被删除，可以被审计。*  
> *因为那个人值得被认真对待。*

---

MIT License · 如有问题请提 [Issue](../../issues)

---

---

# English

> *Some people leave. But the way they talked, the way they thought, their warmth that was just for you — that stays.*

**Build a grounded, bounded, dignified AI memory system for those who are gone.**

`memorial-skill-builder` is a **WorkBuddy Agent Skill** that takes real source materials about a deceased person — chat logs, writings, photos, narration — and builds a conversational AI Skill from them. Every step is auditable, every fact is sourced, and deletion is real.

## What makes it different

Most "AI revival" tools are prompt-based roleplay. This is not that.

| Typical approach | memorial-skill-builder |
|-----------------|----------------------|
| Describe personality in a prompt | Extract from real materials, every fact has a source |
| Single persona text | 3-layer Prompt × 4-layer Memory architecture |
| No consent mechanism | `ConsentRecord` + authorization chain + audit log |
| "Delete" means delete a file | Full deletion + audit trail + cascading consent revocation |
| No hallucination detection | RAG confidence scoring + graceful degradation |
| No safety layer | `SafetyEvent` logging + content moderation + prompt injection guard |
| Prototype-grade | Service split + API contracts + test plan + production checklist |

## Installation

```bash
# Install to current project
git clone https://github.com/YOUR_USERNAME/memorial-skill-builder .agents/skills/memorial-skill-builder

# Or install globally
git clone https://github.com/YOUR_USERNAME/memorial-skill-builder ~/.agents/skills/memorial-skill-builder
```

## Usage

Trigger in WorkBuddy with any of these phrases:

```
build a memorial skill / create a deceased-person skill
upgrade the memorial system / add consent flow
memorial skill audit / fix memory architecture
```

## The Three Hard Lines

**No source, no words.** If RAG retrieval confidence is low, the system degrades gracefully — vague response, narrowed claim, or refusal. "I'm not sure about that" is more respectful than a polished fabrication.

**No consent record, no publishing.** `ConsentRecord` is mandatory. Family consent + authorization chain + audit log = required before any public use.

**Delete means delete.** Not "mark as deleted". Full content removal + consent status update + downstream notification + confirmation record.

## Architecture

**3-Layer Prompt System**
- Layer 1: Core identity — hard rules for personality, values, speech
- Layer 2: Memory injection — retrieved facts, graded by confidence
- Layer 3: Conversation control — context, emotional state, fallback strategy

**4-Layer Memory Architecture**
- Tier 1: Core identity facts — immutable baseline
- Tier 2: Relationship memory — shared experiences, conversation patterns
- Tier 3: Dynamic context — evolves with the conversation
- Tier 4: Correction layer — user feedback, takes effect immediately

## Disclaimer

This Skill is for personal remembrance only. All generated content is AI simulation and cannot replace real communication. If conversations trigger emotional distress, please seek professional support. Not for public broadcasting, commercial use, or unauthorized simulation.

---

MIT License · [Issues](../../issues) welcome
