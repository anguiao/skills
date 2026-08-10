---
name: implement
description: Implement an approved spec faithfully and verify the result.
---

Implement the approved spec without reopening settled decisions.

If the codebase exposes a material conflict or a missing decision that changes behavior or scope, surface it. Otherwise, resolve implementation details by following existing patterns.

Break the work into independently verifiable vertical slices. Use TDD where possible, at pre-agreed seams. Implement and verify one slice at a time, then commit it as a coherent change before moving to the next. Stay within the spec and avoid unrelated refactoring.

Self-review the final diff in two passes: first for spec fidelity, then for code quality. Fix issues within the approved scope and report any deviations or unresolved risks. Finish with a fresh run of all relevant checks.

After the self-review and checks pass, update the spec's status using the repository's convention, defaulting to `implemented`.
