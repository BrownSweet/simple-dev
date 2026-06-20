# Simple Dev

`simple-dev` 是一个跨平台 Agent Skill，用于在规划、实现、重构和代码评审中约束代理选择最小正确方案：遵循现有项目模式、减少无效抽象、执行轻量测试优先，并主动检查 N+1。

当前版本为 `1.0.0-beta`。标准格式兼容 OpenAI Codex、Claude Code、通用 Agent Skills 客户端和 VS Code/GitHub Copilot。通用包已通过规范、归档和安装模拟；Codex 的 provider-backed smoke test 未完成，Claude 和 VS Code 客户端在当前环境中不可用，因此三个原生运行状态均明确标记为 `missing evidence`。

## 能力边界

规则优先级：

1. 正确性、安全性和明确需求。
2. 项目约定与公开接口。
3. 当前任务验收标准。
4. 简单化偏好。

本 Skill 负责：

- 限制非必要功能、文件、抽象、跳转和嵌套。
- 在修改前后执行相关验证。
- 避免 N+1，并在语义允许时采用批量数据库操作。
- 为规划、实现、重构和只读评审提供明确输出。

本 Skill 不替代完整 TDD、架构设计、性能诊断、安全审计或大型迁移。这些专业流程可以主导任务，`simple-dev` 只补充简单化约束。

## 安装

从 Release 下载 `simple-dev-1.0.0.zip` 并解压。压缩包顶层应为完整的 `simple-dev/` 目录，不要只复制 `SKILL.md`。

### OpenAI Codex

用户级安装：

```bash
mkdir -p "$HOME/.agents/skills"
cp -R simple-dev "$HOME/.agents/skills/simple-dev"
```

项目级安装：

```bash
mkdir -p .agents/skills
cp -R simple-dev .agents/skills/simple-dev
```

通过 `$simple-dev` 显式调用。Codex 也会根据 `description` 隐式匹配；如果新安装未显示，请重启 Codex。

官方说明：[Codex Agent Skills](https://developers.openai.com/codex/skills)

### Claude Code

用户级安装：

```bash
mkdir -p "$HOME/.claude/skills"
cp -R simple-dev "$HOME/.claude/skills/simple-dev"
```

项目级安装：

```bash
mkdir -p .claude/skills
cp -R simple-dev .claude/skills/simple-dev
```

通过 `/simple-dev` 显式调用。Claude Code 也可以依据 `description` 自动加载 Skill。

官方说明：[Claude Code Skills](https://code.claude.com/docs/en/skills)

### VS Code / GitHub Copilot

个人 Skill 可放入以下任一目录：

- `~/.copilot/skills/simple-dev`
- `~/.claude/skills/simple-dev`
- `~/.agents/skills/simple-dev`

项目 Skill 可放入：

- `.github/skills/simple-dev`
- `.claude/skills/simple-dev`
- `.agents/skills/simple-dev`

在 Chat 中通过 `/simple-dev` 调用。避免在多个目录安装同名副本。

官方说明：[VS Code Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills)

### 其他 Agent Skills 客户端

将完整 `simple-dev/` 目录放入客户端配置的 Skill 搜索路径。客户端至少需要支持包含 YAML frontmatter 的 `SKILL.md`。

格式规范：[Agent Skills Specification](https://agentskills.io/specification)

## 使用

只有当请求明确包含“最小改动、简单实现、少抽象、少文件、减少层级、测试优先或检查 N+1”等意图时，才应隐式触发。

规划：

```text
使用 $simple-dev，规划这个导出功能的最小实现范围，不要设计未来扩展框架。
```

实现：

```text
使用 $simple-dev，以最小改动修复空值崩溃；修改前后运行相关测试。
```

重构：

```text
使用 $simple-dev，减少这个模块的无效层级，保持行为和公开接口不变。
```

评审：

```text
使用 $simple-dev，只读评审这个 PR 的过度抽象、复杂分支、N+1 和验证缺口。
```

数据库例外：

```text
使用 $simple-dev 实现逐条加锁更新；如果不能批量处理，请说明事务语义和处理规模。
```

Claude Code 和 VS Code/Copilot 中，将 `$simple-dev` 分别替换为 `/simple-dev`。

## 输出契约

Skill 的最终交付应简要包含：

- `实际范围`
- `复杂度取舍`
- `修改前验证`
- `修改后验证`
- `数据库检查`
- `未解决风险`

规划或只读评审中不适用的字段应写为“不适用”，不能伪造测试或运行证据。

## 更新、禁用和卸载

- 复制安装：备份旧目录后，用新版本完整目录替换；不要混合两个版本的文件。
- 软链接安装：更新源码目录即可；客户端未刷新时重新启动。
- Codex 可在 `~/.codex/config.toml` 中使用 `[[skills.config]]` 和 `enabled = false` 禁用 Skill。
- 卸载前建议把目录移动为 `simple-dev.disabled`，确认不再需要后再删除。
- 同名 Skill 不会自动合并；出现重复项时，只保留一个有效安装位置。

## 排障

### Skill 没有出现

确认目录结构为 `<skills-root>/simple-dev/SKILL.md`，并检查 frontmatter 中 `name: simple-dev`。首次创建顶层 Skill 目录后，客户端可能需要重启。

### 普通开发任务没有触发

这是预期行为。`simple-dev` 不应接管所有开发请求；请显式调用，或明确写出“最小改动”“少抽象”等约束。

### 调用了错误的专业流程

严格 TDD、架构、性能和安全任务应由对应流程主导。可以同时调用 `simple-dev`，但它只负责控制复杂度。

### 修改没有生效

检查是否存在多个同名安装目录。Claude Code 通常能监听现有目录变化；Codex 或新创建的顶层目录可能需要重启。

## 维护和发布

开发环境需要 Python 3.12：

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python tools/release.py check
python tools/release.py build
python tools/release.py verify
```

发布产物：

- `dist/simple-dev-1.0.0.zip`：标准安装包。
- `dist/simple-dev-1.0.0-compatibility.zip`：目标适配、兼容矩阵和审查证据。
- `dist/SHA256SUMS`：发布资产校验和。

`evals/output/cases.jsonl` 使用 recorded fixtures。它们用于可复现的断言检查，不是 provider-backed 模型执行证据。

推送 `v1.0.0` 标签后，GitHub Actions 会重新检查、构建、验证并上传 Release 资产。标签必须与 `manifest.json` 的版本严格一致。

本项目不提供 Codex/Claude Marketplace 包、VS Code 扩展或自动账户配置。

## 许可证

[Apache License 2.0](LICENSE)
