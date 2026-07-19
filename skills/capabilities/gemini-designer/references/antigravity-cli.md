# Antigravity CLI Invocation Reference

## Command pattern

Confirm the installed interface first. Treat current CLI help as authoritative when it differs from this reference.

```bash
agy --version
agy --help
```

List available models and record the exact displayed name selected from the user's preferred Gemini family:

```bash
agy models
GEMINI_FAMILY="<Pro or Flash; default Pro>"
GEMINI_MODEL="<exact latest model name in the selected family>"
```

Run every design task as a text-only, headless call:

```bash
agy --model "$GEMINI_MODEL" --mode plan --print-timeout 10m -p "$PROMPT"
```

Do not add the repository as a workspace, enable edit mode, grant file permissions, or use `--dangerously-skip-permissions`. The calling agent reads and writes files; Gemini only analyzes supplied context and proposes changes.

## Model selection

Select the model deterministically from the current `agy models` output:

1. Use `Pro` unless the user explicitly chooses `Flash`.
2. Keep only entries whose displayed names contain both `Gemini` and the selected family name.
3. Choose the highest model version represented in those names.
4. If that version has reasoning variants, choose the highest variant, such as `High`.
5. Pass the exact displayed name to every `agy` call with `--model`.
6. Stop and report the blocker when the selected family is unavailable. Do not switch between Pro and Flash without the user's approval, and never select a non-Gemini model.

Do not hard-code a model name or reintroduce an external model catalog or custom selector. The live CLI list is the source of truth.

## Context contract

Build the prompt from context already read by the calling agent:

- Include repository-relative paths for every excerpt or diff.
- Include complete current content for each small file that Gemini should rewrite.
- For large files, include the relevant component or style blocks plus the interfaces they depend on.
- Include existing design tokens, component conventions, and visual observations only when they affect the task.
- If the supplied context is insufficient, require Gemini to identify the missing file or information instead of guessing.
- Never include secrets, credentials, `.env` contents, customer data, or unrelated proprietary source.

Explicitly tell Gemini not to use tools, access files, run commands, or claim that it edited the workspace.

## Prompt templates

### Critique or redesign proposal

```text
Act as a senior product designer. Use only the context in this prompt and do not use tools.

Goal: <user goal>
Audience: <target users>
Success criteria: <observable outcomes>
Visual observations: <desktop and mobile findings>
Constraints: <design system, CSS approach, accessibility, repository rules>
Must preserve: <content, behavior, product semantics>

Source context:
--- <repository-relative path> ---
<relevant source or diff>

Return:
1. The highest-impact design problems, ordered by user impact.
2. One coherent redesign direction covering structure, hierarchy, spacing, responsive behavior, and interaction states.
3. Concrete implementation guidance mapped to files and components.
4. Mobile and accessibility risks.
5. Any missing context required before implementation.
```

### Implementation draft

```text
Act as a senior product designer and frontend engineer. Use only the context in this prompt and do not use tools, access files, or claim to have edited the workspace.

Goal: <user goal>
Audience: <target users>
Constraints: <design system, CSS approach, accessibility, repository rules>
Allowed scope: presentation markup, component composition, styling, spacing, responsive behavior, visible copy density, and UI states.
Must preserve: business logic, data-fetching semantics, routing behavior, persistence, authentication, validation rules, public APIs, and unrelated tests.

Current source:
--- <repository-relative path> ---
<complete file or sufficient excerpt>

Return:
1. A concise design rationale.
2. An implementation-ready unified diff using repository-relative paths.
3. A verification checklist.

If the context is insufficient for a safe patch, return the missing context instead of inventing code.
```

### Implementation review

```text
Review this frontend implementation for visual quality. Use only the supplied diff and observations; do not use tools.

Goal: <user goal>
Constraints: <design system, accessibility, responsive targets>
Visual observations: <browser findings>

Implemented diff:
<git diff>

Return only actionable remaining issues, each with severity, rationale, and likely file target. Omit stylistic preferences that do not improve usability or coherence.
```

## Process the result

Treat Gemini's output as a candidate solution. The calling agent must inspect every proposed change, reject behavioral or unrelated edits, adapt the patch to repository conventions when necessary, and apply it with its own file-editing tools. Then inspect the actual diff, run repository verification commands, and perform browser-based visual checks.
