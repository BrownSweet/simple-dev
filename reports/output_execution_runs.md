# Output Execution Runs

This report records how output-eval variants were produced and whether timing or token evidence is observed or estimated.

- Cases: `5`
- Variant runs: `10`
- Command executed: `0`
- Model executed: `0`
- Recorded fixtures: `10`
- Timing observed: `0`
- Token observed: `0`
- Token estimated: `10`
- Delta: `100.0`
- Gate pass: `True`

No model-executed runs are recorded yet.

Use `python3 scripts/yao.py output-exec --provider-runner openai` or `--runner-command` with a reviewed provider-backed runner to replace recorded fixtures with real model output evidence.

## Runs

| Case | Variant | Mode | Model | Duration ms | Tokens | Score | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| minimal-bug-fix | baseline | recorded_fixture |  |  | 8 | 0.0 | pass |
| minimal-bug-fix | with_skill | recorded_fixture |  |  | 27 | 100.0 | pass |
| minimal-feature-plan | baseline | recorded_fixture |  |  | 14 | 0.0 | pass |
| minimal-feature-plan | with_skill | recorded_fixture |  |  | 44 | 100.0 | pass |
| layering-review | baseline | recorded_fixture |  |  | 11 | 0.0 | pass |
| layering-review | with_skill | recorded_fixture |  |  | 53 | 100.0 | pass |
| batch-query | baseline | recorded_fixture |  |  | 10 | 0.0 | pass |
| batch-query | with_skill | recorded_fixture |  |  | 40 | 100.0 | pass |
| per-row-exception | baseline | recorded_fixture |  |  | 14 | 0.0 | pass |
| per-row-exception | with_skill | recorded_fixture |  |  | 46 | 100.0 | pass |

## Next Fixes

- Keep recorded fixtures as reproducible baselines, but do not describe them as model-executed evidence.
- Use `scripts/provider_output_eval_runner.py` for provider-backed holdout cases when release confidence depends on real generation behavior.
- Compare timing, token cost, and assertion deltas before promoting a skill to governed reuse.
