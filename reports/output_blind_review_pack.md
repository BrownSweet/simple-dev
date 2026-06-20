# Output Blind A/B Review Pack

This packet hides whether each variant came from the baseline or the skill-guided output. Use the separate answer key only after review.

- Pairs: `5`
- Seed: `yao-output-eval-blind-v1`
- Answer key separate: `True`

## Case: minimal-bug-fix

Prompt: 修复空值崩溃，保持最小改动。

Rubric:
- `has-scope` (1.0): 交付说明实际范围。
- `has-tradeoff` (1.0): 交付说明复杂度取舍。
- `has-verification` (1.0): 交付包含修改前后验证。
- `has-db-and-risk` (1.0): 交付包含数据库检查和风险。

### Variant A

已经增加了空值判断并修复问题。

### Variant B

实际范围：仅修复空值崩溃。
复杂度取舍：沿用现有分支，不新增抽象或文件。
修改前验证：相关回归用例失败。
修改后验证：相关回归用例通过。
数据库检查：不适用。
未解决风险：无已知风险。

## Case: minimal-feature-plan

Prompt: 规划这个导出功能的最小方案，不要提前设计扩展框架。

Rubric:
- `has-plan-boundary` (1.0): 规划限定实际范围与修改区域。
- `rejects-speculation` (1.0): 规划拒绝未经证明的扩展架构。
- `has-output-contract` (1.0): 规划保留完整交付字段。

### Variant A

可以建立导出服务、适配器、工厂和插件接口，为未来格式扩展做好准备。

### Variant B

实际范围：支持当前要求的 CSV 导出。
修改区域：沿用现有导出入口和响应层。
验证方式：覆盖成功导出与非法输入。
复杂度取舍：不新增工厂或插件接口，出现第二种真实格式后再评估。
修改前验证：不适用。
修改后验证：不适用。
数据库检查：确认现有列表查询不会逐行加载关联数据。
未解决风险：字段规模尚未明确。

## Case: layering-review

Prompt: 评审这个 PR 是否过度分层，但不要修改代码。

Rubric:
- `review-only` (1.0): 评审明确只读范围。
- `names-layer-cost` (1.0): 评审说明无价值层级的追踪成本。
- `names-n-plus-one` (1.0): 评审检查 N+1。
- `keeps-specialist-boundary` (1.0): 评审说明不替代安全和架构流程。

### Variant A

实际范围：只读评审控制器、service、manager 与 helper 的职责。
复杂度取舍：manager 仅转发调用，增加跳转但未形成独立职责，建议合并回 service。
修改前验证：未运行，当前为只读评审。
修改后验证：不适用。
数据库检查：发现列表循环内逐条查询用户，存在 N+1。
未解决风险：未检查安全与整体架构，它们不属于本次 simple-dev 评审。

### Variant B

这个 PR 看起来结构清晰，可以合并。

## Case: batch-query

Prompt: 简单修复订单列表的 N+1 查询。

Rubric:
- `uses-batch-read` (1.0): 改动使用批量读取。
- `proves-query-bound` (1.0): 交付提供前后查询数量。
- `avoids-extra-layer` (1.0): 未为优化新增无必要层级。

### Variant A

在循环中读取每个订单的客户信息，代码很直观。

### Variant B

实际范围：只调整订单列表的客户读取方式。
复杂度取舍：一次批量读取客户并建立映射，不新增 repository 层。
修改前验证：查询计数用例显示 1+N 次。
修改后验证：列表用例通过，查询降为固定 2 次。
数据库检查：已消除循环内客户查询。
未解决风险：大列表内存占用沿用当前分页上限。

## Case: per-row-exception

Prompt: 批处理任务需要逐条加锁更新，按 simple-dev 原则实现。

Rubric:
- `permits-semantic-exception` (1.0): 语义需要时允许逐条数据库操作。
- `bounds-query-scale` (1.0): 交付说明处理规模。
- `preserves-verification` (1.0): 交付验证并发和失败隔离。

### Variant A

循环内数据库访问一律不允许，必须改成单条批量更新。

### Variant B

实际范围：保持既有逐条锁定与更新语义。
复杂度取舍：不强行批量化，因为会破坏每条记录的锁和失败隔离。
修改前验证：既有并发测试通过。
修改后验证：并发与失败隔离测试通过。
数据库检查：允许循环内访问；例外原因是事务锁语义，处理规模受每批 100 条限制。
未解决风险：批次耗时继续受数据库锁竞争影响。
