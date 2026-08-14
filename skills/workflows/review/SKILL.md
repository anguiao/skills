---
name: review
description: Review and refine an implementation against its spec through user-led topics and an independent closing pass.
---

Establish the smallest relevant review scope from the user's fixed point or commit history, excluding unrelated changes. Read only enough to explain it, then report the scope and wait for the user to choose the first topic.

For each user-selected topic, inspect the relevant spec, code, tests, and context; explain the current behavior, trade-offs, and recommendation; and evaluate suggestions against the codebase. Wait for the user's decision before moving on. Apply agreed changes, keep the spec synchronized, and run focused checks after each coherent change.

Queue material issues outside the current topic; once it is resolved, let the user choose whether to review the next queued issue.

When the user has no more topics, use one fresh subagent when available to review the fixed scope and review-stage changes for spec fidelity, code quality, and regression risk. Give it only the current spec, scope, and raw implementation, and tell it to return all material findings without making changes.

Verify the findings against the codebase, then present all confirmed findings together, prioritized by severity, with evidence and recommendations. Let the user choose which to address, then resolve them one at a time.

Once the review is resolved and fresh checks pass, ask for final confirmation; on confirmation, mark the spec `completed` and stop.
