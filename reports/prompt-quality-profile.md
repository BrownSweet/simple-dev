# Prompt Quality Profile

Skill: `simple-dev`
Relevance: `prompt-aware`
Overall quality score: `85.0/100`

## Primary Task Family

**Execution operation**
- Matched keywords: workflow, 流程, 执行

## Complexity

- Band: `medium`
- Score: `4`
- Reason: some judgment and multi-step structure are needed

## Need Model

- Explicit Need: Apply simple development constraints when the user explicitly asks for minimal or straightforward work, fewer abstractions, files, or jumps, flatter control flow, lightweight test-first changes, or N+1 avoidance. Use across planning, implementation, refactoring, and code review. Follow existing project conventions; do not replace dedicated TDD, architecture design, performance diagnosis, security review, or migration workflows.
- Implicit Need: The reusable skill needs a stable role, task, and output contract rather than a one-off prompt.
- Scenario: not yet explicit
- User Level: infer from examples and standards; ask only if it changes output depth
- Success Standard: usable output with clear validation cues

## RTF To Skill Mapping

- Role: Use an operator role with explicit boundaries, inputs, outputs, and failure handling.
- Task: Convert the job into ordered steps with validation checks and stop conditions.
- Format: Return a runbook-like handoff with commands, checks, owners, and next actions when relevant.

## Quality Matrix

### Completeness — 80/100
- Matched signals: output, constraint, 输出, 约束, 标准
- Repair: Name missing inputs, outputs, constraints, or success standards before deepening the package.

### Clarity — 85/100
- Matched signals: 明确
- Repair: Replace broad verbs with observable actions and define what done means.

### Consistency — 90/100
- Matched signals: boundary, 边界
- Repair: Check that role, task, format, exclusions, and examples do not contradict each other.

### Practicality — 95/100
- Matched signals: action, use, workflow, 执行
- Repair: Add runnable steps, examples, or verification cues instead of abstract advice.

### Specificity — 75/100
- Matched signals: 用户
- Repair: Anchor wording in the user's audience, domain nouns, and target outcome.

## Matched Task Families

### Execution operation
- Score: `3`
- Keywords: workflow, 流程, 执行
- Role: Use an operator role with explicit boundaries, inputs, outputs, and failure handling.
- Task: Convert the job into ordered steps with validation checks and stop conditions.
- Format: Return a runbook-like handoff with commands, checks, owners, and next actions when relevant.

### Analytical reasoning
- Score: `1`
- Keywords: 诊断
- Role: Use an analyst role that separates evidence, inference, uncertainty, and recommendation.
- Task: State assumptions, compare alternatives, and make the decision path inspectable.
- Format: Return findings, evidence, tradeoffs, recommendation, and residual risks.

## Self-Repair Checks

- Check explicit need, implicit need, scenario, user level, and success standard before deepening.
- Map Role, Task, and Format into skill behavior, not decorative prompt labels.
- Ask one focused clarification only when missing information changes the package boundary.
- Add tests or examples for prompt-heavy behavior before treating it as reusable.
- Keep prompt methodology in references and reports instead of bloating SKILL.md.

## Reviewer Note

Use this profile when the package depends on prompt behavior, role design, output contracts, or conversation quality.
