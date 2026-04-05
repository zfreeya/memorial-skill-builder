# Auto Iteration Specification

本文档定义 memorial-skill-builder 的自动化迭代规则。自动化 agent 按此规范自主执行迭代。

## 核心原则

1. **每次只做一件事**：每次迭代只改进一个明确的问题，不要贪心
2. **测试驱动**：所有测试必须通过，失败就回滚
3. **安全第一**：不破坏 Hard Boundaries，不删除 public API
4. **质量优先**：保持 Python 3.9 兼容，domain/repositories/services 层零依赖
5. **不弄虚作假**：测试必须验证真实行为，禁止空壳测试、跳过断言、mock 掉核心逻辑

## 执行流程

### Step 1: 读取状态（按此顺序）

1. 读取 `.codebuddy/automations/memorial-skill-auto-iterate/memory.md`（上次执行记录）
2. 读取 `AUTO_ITERATION_SPEC.md`（本文件）
3. 运行 `python scripts/validate_skill_package.py` 检查结构
4. 运行 `python scripts/run_unit_tests.py` 检查测试
5. 运行 `git status` 查看未提交更改

> **为什么先读 memory？** 上次迭代可能失败并记录了未完成项或需跟进的 blocker，优先处理这些。

### Step 2: 智能选题

按优先级扫描，选**最高优先级中的第一项**。同优先级内，按实际影响排序。

#### 2.1 P0 — 必须先做（阻塞一切）

| 条件 | 动作 | exit condition |
|------|------|----------------|
| git working tree 不干净 | 提交或撤销 | `git status` 显示 clean |
| 有失败测试 | 修复对应测试 | `run_unit_tests.py` 全 PASS |
| 结构验证失败 | 修复失败项 | `validate_skill_package.py` 全 PASS |
| memory.md 中有未完成的 P0 | 继续上次工作 | 对应项验证通过 |

#### 2.2 P1 — 质量改进

按以下覆盖度差距选择优先改哪个模块：

1. 统计 `runtime/leftman_skill_system/services/` 下每个 service 的测试覆盖情况
2. 有单元测试文件 → 检查是否有空壳测试（无 assert 的 test 方法）
3. 无单元测试文件 → 列入待补充队列
4. 选覆盖最差的模块写测试

**P1 候选池（持续更新）：**

| 模块 | 测试文件 | 状态 |
|------|---------|------|
| memory_service | tests/test_memory_service.py | ✅ 有 2 个测试 |
| skill_service (create/delete/source) | tests/test_skill_flow.py | ✅ 有 3 个测试 |
| auth_service | — | ❌ 无独立测试 |
| policy_service | — | ❌ 无独立测试 |
| prompt_service | — | ❌ 无独立测试 |
| retrieval_service | — | ❌ 无独立测试 |
| source_service | — | ❌ 无独立测试 |
| conversation_service | tests/test_skill_flow.py (部分) | ⚠️ 只测了 consent 拦截 |
| audit_service | — | ❌ 无独立测试 |
| content_guard_service | — | ❌ 无独立测试 |
| delete_export_service | tests/test_skill_flow.py (部分) | ⚠️ 只测了 happy path |
| wechat_extraction | — | ❌ 无独立测试 |

#### 2.3 P2 — 功能增强

- 新增小型功能（必须有测试）
- 改进提示词模板
- 优化检索逻辑

#### 2.4 P3 — 清理工作

- 删除无用代码
- 重命名不清晰的变量
- 改进代码注释

### Step 3: 执行改进

- 创建新分支：`git checkout -b auto-iter-{YYYYMMDD}-{HHMMSS}`
- 进行修改
- 运行所有测试验证
- 如果测试失败：`git checkout .` 回滚 working tree，然后 `git checkout master`
- 修改内容必须可被一句 commit message 完整描述

### Step 4: 提交与推送

- 通过后：`git commit -m "auto-iter: {one-line description}"`
- 合并到主分支：`git checkout master && git merge auto-iter-{timestamp}`
- 推送：`git push`
- 清理分支：`git branch -D auto-iter-{timestamp}`

### Step 5: 更新记忆

在 `.codebuddy/automations/memorial-skill-auto-iterate/memory.md` 中追加记录：

```markdown
## {YYYY-MM-DD HH:MM}

### Iteration {N}
- **Type**: {Px} - {类别}
- **Description**: {一句话描述具体做了什么}
- **Result**: {成功/失败}
- **Commit**: {short hash}
- **Files changed**: {改了哪些文件}
```

> 如果失败，额外记录失败原因和下次建议的修复方向。

## 约束清单

每次迭代必须检查：

- [ ] 只改了一个明确的问题（一个 commit message 能概括）
- [ ] 所有单元测试通过（`run_unit_tests.py` exit code 0）
- [ ] 结构验证通过（`validate_skill_package.py` exit code 0）
- [ ] 没有破坏 public API
- [ ] 没有违反 Hard Boundaries
- [ ] 保持 Python 3.9 兼容
- [ ] domain/repositories/services 层无新依赖
- [ ] 新增测试有真实断言（不是空壳测试）
- [ ] memory.md 已更新

## 回滚规则

出现以下情况必须回滚：
- 任何测试失败
- 结构验证失败
- 破坏了已有功能
- 违反了 Hard Boundaries

回滚步骤：
1. `git checkout .`（丢弃 working tree 改动）
2. `git checkout master`
3. `git branch -D auto-iter-{timestamp}`
4. 在 memory.md 中记录失败原因和建议

## 测试质量红线

以下行为视为"弄虚作假"，绝对禁止：

1. **空壳测试**：test 方法里没有 assert
2. **mock 掉被测对象**：测试 X 却 mock 了 X 的核心逻辑，等于没测
3. **断言缺失**：只调方法不检查返回值
4. **硬编码通过**：直接 `self.assertTrue(True)` 或类似写法
5. **跳过测试**：`@unittest.skip` 不加修复计划

每个测试方法至少要有 **1 个 assert**，且 assert 检查的是**被测逻辑的实际输出**。

## 覆盖度评估方法

每次 P1 迭代前，运行以下检查获取当前覆盖度：

```python
# 伪代码 — agent 执行时用搜索工具完成
for each service in runtime/leftman_skill_system/services/:
    test_file = tests/test_{service_name}.py
    if test_file exists:
        count methods with "def test_"
        count assert statements
        report: "X methods, Y asserts"
    else:
        report: "NO TESTS"
```

用这个数据更新 P1 候选池的状态列。

## 输出摘要

每次执行完成后，输出一行摘要：
```
[Auto Iteration] {Px}: {一句话描述} - {成功/失败}
```

示例：
```
[Auto Iteration] P1: 增加删除服务单元测试 - 成功
[Auto Iteration] P1: 补充 auth_service consent 拦截测试 - 成功
[Auto Iteration] P0: 修复 memory_service 批量删除空指针异常 - 成功
[Auto Iteration] P0: 修复 wechat_extraction 测试空壳断言 - 失败
```

## 增量健康评估

每 5 次迭代（或每次 P0 后），输出健康快照：

```
=== Health Snapshot (Iteration {N}) ===
Unit tests:     X/Y passing
Test coverage:  {N}/{M} services have tests
Git status:     clean/dirty
P1 backlog:     {remaining items}
Last 5 results: {✅✅✅❌✅}
```

> 健康快照不写入文件，仅在输出中展示。
