# Intent Confidence

- Confidence score: `100/100`
- Confidence band: `high`
- Gate passed: `True`
- Recommended action: Intent is clear enough to package the first routeable version.

## Current Reading

Apply an explicit simplicity constraint across software planning, implementation, refactoring, and read-only review so the agent produces the smallest correct change that follows project conventions and remains verifiable. Primary output: A minimal plan, implementation, refactor, or review followed by a concise handoff containing actual scope, complexity tradeoff, before and after verification, database check, and unresolved risks.. Exclusions: generic software development requests without an explicit simplicity signal, strict red-green-refactor TDD workflows, architecture design or large migrations that need dedicated system-level reasoning, performance diagnosis and security audit workflows, mechanical simplification that would violate correctness, safety, project conventions, public interfaces, or transaction semantics.

## Strong Signals

- The recurring job is concrete enough to anchor the package.
- Real input shape is explicit.
- The hand-back output is concrete.
- Boundary exclusions are already explicit.
- Operational constraints are visible.

## Gaps To Close

- No major intent gaps detected.

## Follow-Up Questions

- No extra follow-up questions required before the first package.
