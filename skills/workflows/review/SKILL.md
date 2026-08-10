---
name: review
description: Review an implementation interactively against its spec and refine it to completion.
---

Review the implemented spec and its implementation interactively until we reach a shared understanding of the final result. Establish the smallest relevant review range from the user's fixed point or the commit history, exclude unrelated changes, and report the range before proceeding.

Follow the user's lead one topic at a time. Inspect the relevant code, tests, spec, and surrounding context; explain the current behavior, trade-offs, and recommendation; and evaluate suggestions against the codebase rather than accepting them blindly. Apply requested or agreed changes directly, keep the same spec synchronized with final decisions, and run focused checks after each coherent change. Stay within the implemented feature unless a concrete risk requires broader inspection.

When the user indicates that the review is ready to finish, inspect the review-stage changes and affected areas. Expand to the full implementation only when the review materially changed the architecture, behavior, or spec, or when the user requests a full pass. Run fresh relevant checks, resolve any findings, and report unresolved risks.

After the checks pass and the user approves the result, update the spec's status using the repository's convention, defaulting to `completed`.
