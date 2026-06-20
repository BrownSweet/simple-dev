# Output Risk Profile

Skill: `simple-dev`

## Why This Exists

Generated skills often fail in small output details: generic headings, cluttered citations, fragile screenshots, weak Markdown rendering, or missing execution assumptions. This profile predicts the most likely output mistakes before the skill is used heavily.

## Matched Risk Families

### Code and command safety
- Matched keywords: code, 代码, 接口
- Score: `3`

## Likely Output Mistakes

- Commands can omit environment assumptions, working directory, or rollback notes.
- Code snippets can look runnable while missing required inputs.

## Output Constraints To Apply

- Name the working directory, required inputs, and expected output for each command.
- Mark destructive or external side-effect operations explicitly.

## Self-Repair Checks

- Scan each command for cwd, input, output, and side-effect assumptions.
- Remove speculative error handling that is not tied to a real failure mode.

## Reviewer Note

Use this report before deepening the package and again before approving example outputs.
