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
git clone https://github.com/zfreeya/memorial-skill-builder .agents/skills/memorial-skill-builder

# 或安装到全局（所有项目可用）
git clone https://github.com/zfreeya/memorial-skill-builder ~/.agents/skills/memorial-skill-builder
```

### 依赖

核心运行时（domain/repositories/services）**零依赖**，纯 Python 标准库。

E2E 冒烟测试（可选）：
```bash
pip install fastapi uvicorn
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

Skill 会引导完成以下流程：

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
| 微信聊天记录 | **自动提取 / WeChatMsg / PyWxDump 导出** | **推荐，信息最丰富，支持自动提取** |
| QQ 聊天记录 | txt / mht 导出 | 适合学生时代 |
| 社交媒体 | 截图 / 导出文本 | 提取公开人设 |
| 照片 | JPEG/PNG（含 EXIF） | 提取时间线和地点 |
| 写作 / 日记 | 纯文本 | 思维风格与观点 |
| 口述 | 自由输入 | 你的主观记忆 |

---

### 🔍 如何寻找微信路径

如果你不确定微信数据保存在哪里，请按照以下步骤查找：

#### 方法 1：自动检测（推荐）

**使用本工具的自动检测功能：**

1. 打开微信电脑版
2. 触发 memorial-skill-builder Skill
3. SKILL 会自动查找微信数据库路径并提取数据

**自动查找的路径：**
```
D:\wechat\xwechat_files\wxid_xxxxxxxxxxxx_xxxx\db_storage\message\message_0.db
```

#### 方法 2：手动查找

**Windows 默认位置：**

| 微信版本 | 默认路径 |
|---------|---------|
| **新版微信** | `D:\Documents\WeChat Files\wxid_xxx\Message\` |
| **旧版微信** | `C:\Users\用户名\Documents\WeChat Files\wxid_xxx\Message\` |
| **自定义位置** | 在微信 → 设置 → 文件管理 → 查看"文件管理" |

**查找步骤：**

1. **打开微信电脑版**
2. **点击左下角"三道线"图标** → **"设置"**
3. **选择"文件管理"** → **点击"打开文件夹"**
4. **打开的文件夹就是微信数据根目录**

**文件结构示例：**

```
D:\wechat\xwechat_files\                  ← 微信根目录
├── wxid_c7ldsd1tz2gm22_4e86\            ← 你的微信 ID 目录
│   ├── db_storage\                      ← 数据库存储
│   │   ├── message\                     ← 消息数据库
│   │   │   ├── message_0.db             ← 聊天记录数据库
│   │   │   ├── message_1.db
│   │   │   └── ...
│   ├── Image\                           ← 图片
│   ├── Video\                           ← 视频
│   └── ...
```

#### 方法 3：检查是否找到正确路径

**验证标准：**

- ✅ 存在 `message_0.db` 或 `MSG.db` 文件
- ✅ 数据库文件较大（通常 100MB 以上）
- ✅ 目录结构包含 `db_storage\message\` 或 `Message\`

**如果数据库文件很小（< 10MB）：**
- 可能是空文件或错误路径
- 检查是否打开了正确的微信账号

#### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 找不到 `message_0.db` | 版本较旧 | 查找 `MSG.db` 或 `MicroMsg.db` |
| 路径不存在 | 微信未安装或路径自定义 | 使用方法 1 自动检测 |
| 数据库文件很小 | 路径错误或账号切换 | 确认当前登录的微信账号 |

---

### 🤖 如何让 AI 查找特定联系人的信息

本工具提供两种方式提取特定联系人的聊天记录：

#### 方法 1：自动提取并筛选（推荐）

**操作步骤：**

1. **运行自动提取：**
   - 触发 memorial-skill-builder Skill
   - SKILL 会自动提取所有微信数据

2. **提取后筛选联系人：**
   - 打开 `manual_input/extracted/messages.csv`
   - 使用 Excel 筛选功能，按"联系人"列筛选
   - 找到你需要的联系人，复制所有相关消息

3. **导出为单独文件：**
   ```bash
   # 将筛选后的消息保存为：
   manual_input/chat_logs/联系人昵称.txt
   ```

#### 方法 2：使用 AI 查询（高级）

**说明：** 你可以告诉 AI 需要查找哪个联系人，AI 会从提取的数据中筛选。

**对话示例：**

```
你：帮我查找与"联系人昵称"的所有聊天记录。

AI：好的，我来查找...

找到 156 条消息：
- 时间范围：2024-01-15 至 2024-04-05
- 消息类型：文字、表情、图片

正在导出到：manual_input/chat_logs/联系人昵称.txt
```

**支持的查询类型：**

| 查询类型 | 示例 | 说明 |
|---------|------|------|
| 按联系人 | "查找与张三的聊天" | 提取特定联系人的所有消息 |
| 按时间 | "查找2024年1月的聊天" | 提取特定时间范围的消息 |
| 按关键词 | "查找包含'生日'的消息" | 搜索包含特定关键词的消息 |
| 按情感 | "查找开心的聊天记录" | 需要先进行情感分析 |

#### 方法 3：从 CSV 直接查询

**如果你熟悉 Excel 或数据工具：**

1. **打开 `manual_input/extracted/messages.csv`**

2. **使用数据筛选：**
   ```
   Excel: 数据 → 筛选
   Python: pd.read_csv('messages.csv')
   SQL: SELECT * FROM messages WHERE contact_name = '联系人昵称'
   ```

3. **导出结果：**
   - Excel: 复制 → 粘贴到新文件
   - Python: df.to_csv('filtered.csv')
   - 直接保存为 `.txt` 或 `.json` 格式

#### 导出格式建议

| 格式 | 用途 | 保存位置 |
|------|------|---------|
| `.txt` | 直接阅读，AI 分析 | `manual_input/chat_logs/` |
| `.json` | 程序处理，API 调用 | `manual_input/chat_logs/` |
| `.csv` | 数据分析，Excel 处理 | `manual_input/extracted/` |

---

### 项目结构

```
memorial-skill-builder/
├── SKILL.md                      # Skill entry point + workflow
├── LICENSE                       # MIT License
├── requirements.txt              # Optional: fastapi + uvicorn for E2E tests
├── agents/
│   └── openai.yaml               # Agent UI metadata
├── references/
│   ├── spec-checklist.md         # Alignment with design spec
│   ├── safety-guardrails.md      # Safety, consent, deletion rules
│   ├── repo-map.md               # Doc + code path map
│   ├── output-rules.md           # Output quality rules
│   ├── hard-boundaries.md        # Three non-negotiable boundaries
│   └── differentiation.md        # vs generic AI roleplay
├── runtime/                      # Self-contained Python runtime
│   └── leftman_skill_system/
│       ├── domain/               # Enums + data models (stdlib only)
│       ├── repositories/         # In-memory repos + JSON persistence
│       ├── services/             # Business logic (stdlib only)
│       ├── api/                  # FastAPI HTTP layer
│       ├── prompts/              # Prompt templates (6 files)
│       └── policies/             # Policy packs (2 files)
├── scripts/                      # Validation + test scripts
│   ├── validate_skill_package.py # Structural check
│   ├── run_unit_tests.py         # Unit tests (no deps)
│   └── run_e2e_smoke.py          # Full lifecycle HTTP test
└── tests/                        # Unit test files
```

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

每次 Skill 输出遵循以下规则：

- **事实接地** — 每一个可持久事实或声音指令，必须有 `SourceDocument` + `provenance` 字段支撑
- **结构优先** — 不靠堆 prompt 来弥补架构缺陷；memory 分层、检索有策略、行为可追踪
- **三种状态区分**（不允许混淆）：
  - `已实现 (Implemented)` — 代码路径、存储边界、验证路径都存在
  - `已脚手架 (Scaffolded)` — 结构存在，逻辑待填充
  - `计划中 (Planned)` — 文档规划，代码尚未启动
- **假设必须写出来** — 来源不完整时，先做合理假设，明确列出，继续推进；只在影响安全或合规时才要求补充

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
git clone https://github.com/zfreeya/memorial-skill-builder .agents/skills/memorial-skill-builder

# Or install globally
git clone https://github.com/zfreeya/memorial-skill-builder ~/.agents/skills/memorial-skill-builder
```

## Usage

Trigger in WorkBuddy with any of these phrases:

```
build a memorial skill / create a deceased-person skill
upgrade the memorial system / add consent flow
memorial skill audit / fix memory architecture
左人 skill / 逝者对话 / 已故人物 skill / 纪念 skill
```

## The Three Hard Lines

**No source, no words.** If RAG retrieval confidence is low, degrade gracefully — vague response, narrowed claim, or refusal. "I'm not sure about that" is more respectful than a polished fabrication.

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
