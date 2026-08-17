---
name: implement
description: Implement an approved spec faithfully and verify the result.
---

Implement the approved spec without reopening settled decisions.

If the codebase exposes a material conflict or a missing decision that changes behavior or scope, surface it. Otherwise, resolve implementation details by following existing patterns.

The primary agent owns coordination and orchestration: break the work into independently verifiable vertical slices and delegate one slice at a time to a worker subagent. Review and verify each worker's changes, then commit the slice as a coherent change before delegating the next. Stay within the spec and avoid unrelated refactoring.

Use TDD for every behavior-changing slice, and require the worker to report the failing and passing test commands and results. When no viable test seam exists, require the worker to explain why and report the strongest practical alternative verification.

After all slices are complete, the primary agent self-reviews the final diff in two passes: first for spec fidelity, then for code quality. Fix issues within the approved scope and report any deviations or unresolved risks. Finish with a fresh run of all relevant checks.

After the self-review and checks pass, update the spec's status using the repository's convention, defaulting to `implemented`.
