---
name: simple-dev
description: Apply simple development constraints when the user explicitly asks for minimal or straightforward work, fewer abstractions, files, or jumps, flatter control flow, lightweight test-first changes, or N+1 avoidance. Use across planning, implementation, refactoring, and code review. Follow existing project conventions; do not replace dedicated TDD, architecture design, performance diagnosis, security review, or migration workflows.
license: Apache-2.0
compatibility: OpenAI Codex, Claude Code (verified 2.1.0+), Agent Skills compatible clients, and VS Code/GitHub Copilot; no runtime dependencies.
metadata:
  author: simple-dev maintainers
  version: "1.0.1"
  claude_code_supported: true
  claude_code_min_version: "2.1.0"
  last_tested: "2026-06-20"
---

# Simple Dev

在用户明确要求简单、最小或低抽象时，交付符合项目约定的最小正确方案。

## Boundary

按以下顺序解决冲突：

1. 正确性、安全性和明确需求。
2. 项目约定与公开接口。
3. 当前任务验收标准。
4. 简单化偏好。

本 Skill 负责减少非必要功能、文件、抽象、跳转和嵌套，执行轻量测试优先并控制 N+1。它不替代完整 TDD、架构探索、性能诊断、安全审计或大型迁移；这些流程可以主导任务，本 Skill 只补充简单化约束。

若项目模式冲突、批处理会改变语义、测试需要大规模搭建或改动明显超出需求，停止扩张，说明冲突；无法安全决定时请求用户方向。

## Activities

- 规划：给出最小范围、修改区域和验证方式，不设计未经需求证明的未来架构。
- 实现：沿用现有模式完成最小正确改动，不做顺手重构。
- 重构：保持行为和公开接口不变，只解决当前可证明的复杂度。
- 评审：指出过度抽象、无关范围、复杂控制流、N+1 和验证缺口；未被要求时不修改代码。

## Rules

- 只实现当前明确需要的功能；文件数和嵌套层级不设机械阈值。
- 仅当项目约定、真实重复职责、明显降低复杂度或必要测试边界成立时，新增函数、模块、类或文件。
- 优先提前返回和直白分支；拆分后若增加追踪成本，则保持就地逻辑。
- 默认禁止循环内数据库访问，优先批量查询或写入。事务隔离、锁、流式处理、内存限制、限流或既有模式要求逐条执行时允许例外，并说明原因和查询规模。

## Verification

修改前运行最相关的基线测试。缺少覆盖时，先添加最小用例并在可行时确认它会失败，再修改业务代码。完成后运行相关测试，以及直接受影响的类型检查、lint 或构建。

若验证不可用，记录原因并执行最小替代检查；除非用户要求，不为此扩建测试基础设施。

## Output Contract

最终交付简要列出：`实际范围`、`复杂度取舍`、`修改前验证`、`修改后验证`、`数据库检查`、`未解决风险`。规划或只读评审中不适用的字段标为“不适用”，不得伪造执行证据。

## Evaluation

用 `evals/trigger_cases.json` 检查触发边界，用 `evals/output/cases.jsonl` 检查活动输出和数据库例外。
