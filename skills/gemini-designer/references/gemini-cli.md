# Gemini CLI Reference

Use this reference when invoking Gemini CLI for interface design or redesign work.

## Command patterns

Verify the CLI exists:

```bash
gemini --version
```

Select the current Gemini model before calling Gemini:

```bash
MODEL="$(python <skill-dir>/scripts/select_gemini_model.py)"
```

Run a headless prompt:

```bash
gemini --model "$MODEL" -p "Give a design critique of @src/App.vue and propose concrete improvements."
```

Pipe context into Gemini:

```bash
git diff -- src | gemini --model "$MODEL" -p "Review this frontend diff for visual regressions and weak UI hierarchy."
```

Let Gemini edit files only when the task is design-focused and the workspace is ready:

```bash
gemini --model "$MODEL" --approval-mode=auto_edit -p "Redesign @src/views/Home.vue visually. Preserve existing behavior, data flow, routing, and public component contracts."
```

Use JSON output only when a downstream script needs structured parsing:

```bash
gemini --model "$MODEL" --output-format json -p "Return a JSON object with issues, recommendations, and file_targets."
```

Consider sandbox or approval settings before allowing tool execution:

```bash
gemini --model "$MODEL" --sandbox -p "Review the interface files and return recommendations only."
gemini --model "$MODEL" --approval-mode=plan -p "Plan a redesign for this screen before editing files."
```

## Context selection

Pass only the files Gemini needs:

- Page or route component: `@src/views/Home.vue`, `@src/pages/index.tsx`, `@app/page.tsx`.
- Shared layout and UI components used by the page.
- Styling config: `@uno.config.ts`, `@tailwind.config.*`, global CSS, theme tokens.
- Router or data shape files only when they affect visible structure.
- Screenshot path if Gemini CLI can read it in the current environment; otherwise summarize the visual observations yourself.

Do not pass secrets, `.env` files, credentials, production customer data, or broad directories when a few targeted files are enough.

## Model selection

Models.dev provides a public API at `https://models.dev/api.json`. Use `scripts/select_gemini_model.py` to fetch that API, filter Google Gemini text-capable models, ignore deprecated and non-interface variants, and prefer Pro models.

Useful commands:

```bash
python <skill-dir>/scripts/select_gemini_model.py
python <skill-dir>/scripts/select_gemini_model.py --format json
python <skill-dir>/scripts/select_gemini_model.py --list --format json
python <skill-dir>/scripts/select_gemini_model.py --stable-only
```

If Models.dev is unreachable, use `gemini --model auto` or the user's configured Gemini default and say model selection was blocked.

## Prompt templates

### Critic mode

```text
You are a senior product designer reviewing this existing interface.

Goal: <user goal>
Audience: <target users>
Stack and constraints: <framework, design system, CSS approach, AGENTS.md rules>
Current visual observations: <screenshot notes or browser findings>
Files: <@file references>

Return:
1. Top 5 design problems, ordered by user impact.
2. A redesign direction with layout, hierarchy, spacing, color, and interaction guidance.
3. Concrete implementation suggestions mapped to files/components.
4. Mobile-specific risks.
5. Suggestions to avoid because they would conflict with the product or codebase.
```

### Designer mode

```text
Design a new interface for this product.

Goal: <screen purpose>
Audience: <target users>
Required content and actions: <content>
Stack and constraints: <framework, design system, CSS approach, AGENTS.md rules>
Relevant existing components: <@file references>

Return a concise design plan with page structure, responsive behavior, key states, component reuse, and file-level implementation notes.
```

### Editor mode

```text
Redesign this interface directly in the codebase.

Goal: <user goal>
Audience: <target users>
Stack and constraints: <framework, design system, CSS approach, AGENTS.md rules>
Files: <@file references>

You may edit frontend presentation code, component composition, styling, spacing, responsive behavior, and UI states.
Do not change business logic, data fetching semantics, routing behavior, persistence, authentication, validation rules, or public APIs unless explicitly required.
After editing, summarize changed files and the visual rationale.
```

### Implementation reviewer mode

```text
Review this implemented frontend change for visual quality.

Goal: <user goal>
Constraints: <design system, accessibility, responsive targets>
Diff or files: <piped git diff or @file references>
Screenshot observations: <current browser findings>

Return only actionable issues and polish suggestions. Include severity and likely file targets.
```

## Operating rules

- Prefer `gemini -p` headless calls so results can be captured in the Codex transcript.
- Use the Models.dev-selected model with `--model` when possible, preferring Pro.
- Let Gemini edit files for design-focused tasks, but constrain the prompt to visual/interface code and inspect the resulting diff.
- If Gemini edits files, inspect the diff before continuing and never revert unrelated user changes.
- If authentication is missing, ask the user to authenticate Gemini CLI or set the required environment variables; do not invent Gemini output.
- If network or sandbox restrictions block Gemini CLI, surface the blocker and continue with local implementation if the user still wants progress.
- Treat Gemini output as advice. Apply only changes that fit the codebase, product goal, and user's request.
