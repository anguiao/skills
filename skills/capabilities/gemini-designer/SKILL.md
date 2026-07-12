---
name: gemini-designer
description: Use Gemini CLI as an external design partner for creating, redesigning, or polishing frontend screens and web interfaces. Use when Codex is asked to use Gemini CLI for interface design, redesign, visual critique, layout direction, UI polish, frontend design review, or a second-pass design proposal, including cases where Gemini may directly edit code while keeping functionality and business logic stable.
---

# Gemini Designer

## Goal

Use Gemini CLI for an outside interface design pass, then turn that pass into concrete frontend changes. Gemini may edit files when useful, but its main job is visual/interface design; preserve existing functionality and application logic unless the user explicitly asks to change behavior.

## Quick Start

1. Read the local project instructions, frontend stack, current route or component, and user goal.
2. Gather enough interface context: relevant source files, current screenshot or visual observations when available, current design constraints, and any failing UX problem.
3. Run `scripts/select_gemini_model.py` to fetch the latest Gemini model list from Models.dev and choose a Pro model when available.
4. Read `references/gemini-cli.md` before invoking Gemini CLI.
5. Ask Gemini CLI for a structured design critique, redesign plan, or design-focused edit.
6. Inspect Gemini's changes or recommendations, keep only what fits the repo, and verify the result in the browser or available test workflow.

## Workflow

### 1. Frame the design brief

Build a short brief before calling Gemini:

- Target screen, route, component, or screenshot.
- User intent: create, redesign, polish, critique, compare variants, or fix a specific visual problem.
- Product context and audience.
- Hard constraints from `AGENTS.md`, design systems, component libraries, accessibility requirements, responsive breakpoints, and existing copy.
- What Gemini should return or edit: diagnosis, layout direction, visual hierarchy, interaction states, and implementation notes.

Do not ask Gemini for generic inspiration. Make the prompt interface-specific and include the constraints that would otherwise be easy to violate.

### 2. Select the Gemini model

Always query Models.dev before choosing a model, because Gemini availability changes over time.

```bash
python <skill-dir>/scripts/select_gemini_model.py
```

Use the returned model id with `gemini --model <model-id>`. The selector prefers Google Gemini Pro models, excludes non-text variants such as embedding, image, live audio, and TTS models, and ignores deprecated models. If no Pro model is available, use the best available text-capable Gemini model.

### 3. Choose the Gemini role

- Use **critic mode** when the interface already exists and the user wants polish, visual QA, or redesign direction.
- Use **designer mode** when the user wants a new screen and the repo already has a stack or design system.
- Use **editor mode** when Gemini should directly edit frontend files. Tell Gemini to focus on visual/interface changes and preserve behavior.
- Use **implementation reviewer mode** after local edits when a second pass should catch visual regressions, responsive issues, or weak hierarchy.

### 4. Call Gemini CLI safely

Prefer headless Gemini CLI calls so the result is easy to capture and compare. Load `references/gemini-cli.md` for command patterns, authentication notes, sandbox options, and prompt templates.

Default behavior:

- Prefer analysis and recommendations when the request is ambiguous.
- Allow Gemini to edit code for design tasks when that is the fastest route, but explicitly constrain it to visual structure, styling, layout, component composition, copy density, responsive behavior, and UI states.
- Tell Gemini not to change business logic, API contracts, routing semantics, data fetching, persistence, authentication, validation rules, or unrelated tests.
- Inspect `git diff` after Gemini edits before continuing.
- If Gemini CLI is missing, unauthenticated, blocked by network, or fails, report that clearly and continue with local design judgment when possible.
- Do not paste secrets, private credentials, or unnecessary proprietary context into Gemini.

### 5. Convert feedback into edits

Filter Gemini's suggestions through the actual codebase:

- Keep changes consistent with the existing framework, routing, state management, component conventions, and CSS system.
- Prefer concrete improvements to hierarchy, spacing, responsive structure, contrast, interaction states, and information density.
- Avoid broad rewrites when Gemini proposes changes outside the requested scope.
- Preserve working behavior unless the redesign explicitly changes it.

### 6. Verify visually

Run the relevant dev server or static preview, then inspect the result. For frontend apps, capture screenshots or use browser verification when available.

Check:

- Desktop and mobile layout.
- Text overflow, clipping, and overlap.
- Primary action visibility.
- Empty, loading, error, hover, focus, and active states when applicable.
- Asset loading and color contrast.

Loop once with Gemini in implementation reviewer mode only when the interface is visually complex or the first result still feels weak.

## Output

When responding to the user, summarize:

- Whether Gemini CLI was used successfully.
- Which Gemini model was selected from Models.dev, or why model selection was blocked.
- The design direction chosen from Gemini's feedback.
- The files changed and how to preview the interface.
- Any verification performed or blocked.

## Resources

- Run `scripts/select_gemini_model.py` to fetch and choose the current Gemini model from Models.dev.
- Read `references/gemini-cli.md` for Gemini CLI command patterns and interface-design prompt templates.
