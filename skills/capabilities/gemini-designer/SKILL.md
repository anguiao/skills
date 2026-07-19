---
name: gemini-designer
description: Use Gemini as an independent design partner to create, redesign, polish, or review frontend interfaces while preserving application logic. Use for visual hierarchy, layout, responsive behavior, interaction states, and presentation-layer implementation.
---

# Gemini Designer

## Goal

Use Gemini as an independent product design partner, not as the final authority. Provide accurate interface context, filter its recommendations or patches through the actual codebase, and verify the resulting implementation before delivery.

Read [the current invocation reference](references/antigravity-cli.md) before calling Gemini.

## Workflow

1. Read repository instructions, the frontend stack, the target route or component, and the user's goal.
2. Inspect the relevant source. For an existing interface, capture or inspect both desktop and mobile states when possible.
3. Write a concise design brief covering the goal, audience, required content, hard constraints, and permitted edit scope.
4. Choose critique, proposal, implementation draft, or review mode.
5. Give Gemini only the source excerpts, diff, and visual observations needed for the task.
6. Review Gemini's response and apply approved changes with the caller's own file-editing tools.
7. Inspect the resulting diff, run the repository's verification workflow, and check key viewports and states in a browser.

## Choose a mode

- **Critique**: Diagnose hierarchy, density, readability, or responsive problems. Request prioritized, actionable findings.
- **Proposal**: Define a new screen or redesign direction. Request structure and file-level implementation guidance.
- **Implementation draft**: Request an implementation-ready patch or replacement content. Gemini must not access or edit the workspace; the caller reviews and applies the result.
- **Implementation review**: Provide the implemented diff and visual observations. Request only remaining actionable issues.

Honor the user's choice between Gemini Pro and Gemini Flash; default to Pro when no preference is given. Use the latest available version and highest reasoning level within the chosen family. If that family is unavailable, stop and report the blocker rather than switching families without the user's approval.

## Write the design brief

Include:

- The target page, route, component, or screenshot.
- The user task, audience, and observable success criteria.
- Content, interactions, and product semantics that must remain intact.
- Design system, component library, CSS approach, responsive, and accessibility constraints.
- Source excerpts or diffs with repository-relative file paths.
- Business logic, data flow, routing, authentication, persistence, validation, and public APIs that must not change.

Do not request generic inspiration. Require Gemini to map findings, recommendations, and proposed changes to specific files, components, or states.

## Apply safety boundaries

- Do not provide secrets, `.env` files, credentials, production customer data, or irrelevant private context.
- Do not grant Gemini filesystem, terminal, network, or workspace access. Treat the invocation as text-only.
- Inspect the working tree before applying a patch and the complete diff afterward. Preserve existing user changes.
- Limit proposed changes to layout, styling, component composition, copy density, responsive behavior, and visible UI states unless the user explicitly requests behavioral changes.
- Reject incomplete, malformed, out-of-scope, or context-incompatible patches instead of forcing them into the codebase.
- If the invocation path is unavailable or fails, report the blocker. Continue with local design judgment when appropriate, but never fabricate Gemini output.

## Verify and report

Check desktop and mobile layout, text overflow, primary-action visibility, focus treatment, contrast, and applicable empty, loading, error, hover, and active states. Invoke one additional implementation-review pass only when the interface is complex or the first result still has visible weaknesses.

Tell the user whether Gemini ran successfully, which Gemini model was selected, the adopted design direction, the files changed by the caller, and which verification steps passed or remained blocked.
