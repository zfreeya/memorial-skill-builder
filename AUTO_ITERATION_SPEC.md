# Auto Iteration Specification

本文档定义 memorial-skill-builder 的自动化迭代规则。自动化 agent 按此规范自主执行迭代。

## 核心原则

1. **每次只做一件事**：每次迭代只改进一个明确的问题，不要贪心
2. **测试驱动**：所有测试必须通过，失败就回滚
3. **安全第一**：不破坏 Hard Boundaries，不删除 public API
4. **质量优先**：保持 Python 3.9 兼容，domain/repositories/services 层零依赖

## 执行流程

### Step 1: 读取状态

- 读取 `AUTO_ITERATION_SPEC.md`（本文件）
- 读取 `.codebuddy/automations/memorial-skill-auto-iterate/memory.md`（如果存在）
- 运行 `python scripts/validate_skill_package.py` 检查结构
- 运行 `python scripts/run_unit_tests.py` 检查测试
- 运行 `git status` 查看未提交更改

### Step 2: 选择改进项

按优先级选择一个改进项：

**P0 - 必须先做：**
- 清理 git 状态（提交或撤销未提交的更改）
- 修复失败的测试
- 修复结构验证失败
- 补充缺失的参考文档

**P1 - 质量改进：**
- 增加单元测试覆盖率
- 优化现有代码（不改变行为）
- 改进错误处理
- 补充文档中的示例

**P2 - 功能增强：**
- 新增小型功能（必须有测试）
- 改进提示词模板
- 优化检索逻辑

**P3 - 清理工作：**
- 删除无用代码
- 重命名不清晰的变量
- 改进代码注释

### Step 3: 执行改进

- 创建新分支：`git checkout -b auto-iter-{timestamp}`
- 进行修改
- 运行所有测试验证
- 如果测试失败：`git checkout master` 回滚

### Step 4: 提交与推送

- 通过后：`git commit -m "auto-iter: {one-line description}"`
- 合并到主分支：`git checkout master && git merge auto-iter-{timestamp}`
- 推送：`git push`
- 清理分支：`git branch -D auto-iter-{timestamp}`

### Step 5: 更新记忆

在 `.codebuddy/automations/memorial-skill-auto-iterate/memory.md` 中记录：
- 执行时间
- 改进项类型
- 一句话描述
- 结果（成功/失败）

## 约束清单

每次迭代必须检查：

- [ ] 只改了一个明确的问题
- [ ] 所有单元测试通过
- [ ] 结构验证通过
- [ ] 没有破坏 public API
- [ ] 没有违反 Hard Boundaries
- [ ] 保持 Python 3.9 兼容
- [ ] domain/repositories/services 层无新依赖

## 回滚规则

出现以下情况必须回滚：
- 任何测试失败
- 结构验证失败
- 破坏了已有功能
- 违反了 Hard Boundaries

回滚步骤：
1. `git checkout master`
2. `git branch -D auto-iter-{timestamp}`
3. 在 memory.md 中记录失败原因

## 示例迭代

### 示例 1: 清理 git 状态
```
选择: P0 - 清理 git 状态
操作: git add . && git commit -m "chore: clean up working directory"
验证: git status 显示干净
```

### 示例 2: 增加测试
```
选择: P1 - 增加单元测试覆盖率
操作: 在 tests/ 中新增 test_xxx.py
验证: python scripts/run_unit_tests.py 全部通过
```

### 示例 3: 修复文档
```
选择: P1 - 补充文档中的示例
操作: 更新 references/xxx.md 添加代码示例
验证: python scripts/validate_skill_package.py 通过
```

## 输出摘要

每次执行完成后，输出一行摘要：
```
[Auto Iteration] {类型}: {一句话描述} - {成功/失败}
```

示例：
```
[Auto Iteration] P1: 增加删除服务单元测试 - 成功
```
