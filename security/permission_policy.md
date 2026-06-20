# Permission Policy

`simple-dev` is a declarative Skill and requires no privileged runtime capability.

- No runtime scripts are shipped.
- No network, file-write, subprocess, interactive, credential, or account access is declared.
- `none_required` is a machine-readable sentinel so installers can distinguish an explicit zero-capability review from a missing policy.
- If a future version adds executable resources, its real capabilities must be declared, reviewed, and represented in every target adapter before release.

Review date: `2026-06-20`. Next review: `2026-09-20`.
