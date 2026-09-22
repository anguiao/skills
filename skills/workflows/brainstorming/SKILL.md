---
name: brainstorming
description: Clarify a product or engineering idea through focused questions and design alternatives, then produce one draft spec before implementation.
---

# Brainstorming Ideas Into Designs

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design and get user approval.

<HARD-GATE>
Do NOT write implementation code, scaffold a project, commit changes, invoke another workflow, or take any implementation action while using this skill. Finish with one draft spec and return control to the user.
</HARD-GATE>

## Scale the Process to the Task

Use this workflow only when the user explicitly invokes it. Scale the depth of the discussion and the resulting spec to the idea's complexity. A straightforward change may need only a short design, while a nuanced feature may need deeper exploration.

## Checklist

You MUST create a task for each of these items and complete them in order:

1. **Explore project context** — check files, docs, recent commits
2. **Use visual aids when helpful** — follow [Visual Aids](#visual-aids).
3. **Ask clarifying questions** — one at a time, understand purpose/constraints/success criteria
4. **Propose 2-3 approaches** — with trade-offs and your recommendation
5. **Present design** — in sections scaled to their complexity, get user approval after each section
6. **Write one draft spec** — use the requested or repository-standard location; otherwise save to `docs/specs/YYYY-MM-DD-<topic>.md`
7. **Spec self-review** — quick inline check for placeholders, contradictions, ambiguity, scope (see below)
8. **Return control** — ask the user to review the draft spec, then stop

## Process Flow

```dot
digraph brainstorming {
    "Explore project context" [shape=box];
    "Ask clarifying questions" [shape=box];
    "Propose 2-3 approaches" [shape=box];
    "Present design sections" [shape=box];
    "User approves design?" [shape=diamond];
    "Write draft spec" [shape=box];
    "Spec self-review\n(fix inline)" [shape=box];
    "Ask user to review draft spec" [shape=box];
    "Stop and return control" [shape=doublecircle];

    "Explore project context" -> "Ask clarifying questions";
    "Ask clarifying questions" -> "Propose 2-3 approaches";
    "Propose 2-3 approaches" -> "Present design sections";
    "Present design sections" -> "User approves design?";
    "User approves design?" -> "Present design sections" [label="no, revise"];
    "User approves design?" -> "Write draft spec" [label="yes"];
    "Write draft spec" -> "Spec self-review\n(fix inline)";
    "Spec self-review\n(fix inline)" -> "Ask user to review draft spec";
    "Ask user to review draft spec" -> "Stop and return control";
}
```

**The terminal state is returning control to the user with one draft spec.** Do NOT invoke another workflow, start implementation, or commit the spec.

## The Process

**Understanding the idea:**

- Check out the current project state first (files, docs, recent commits)
- Before asking detailed questions, assess scope: if the request describes multiple independent subsystems (e.g., "build a platform with chat, file storage, billing, and analytics"), flag this immediately. Don't spend questions refining details of a project that needs to be decomposed first.
- If the project is too large for a single spec, help the user decompose it into sub-projects: what are the independent pieces, how do they relate, and what order should they be designed? Then brainstorm the first sub-project through the normal design flow. Each sub-project gets its own draft spec.
- For appropriately-scoped projects, ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible, but open-ended is fine too
- Only one question per message - if a topic needs more exploration, break it into multiple questions
- Focus on understanding: purpose, constraints, success criteria

**Exploring approaches:**

- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why
- YAGNI ruthlessly - remove unnecessary features from every approach and design

**Presenting the design:**

- Once you believe you understand what you're building, present the design
- Scale each section to its complexity: a few sentences if straightforward, up to 200-300 words if nuanced
- Ask after each section whether it looks right so far
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify if something doesn't make sense

**Design for isolation and clarity:**

- Break the system into smaller units that each have one clear purpose, communicate through well-defined interfaces, and can be understood and tested independently
- For each unit, you should be able to answer: what does it do, how do you use it, and what does it depend on?
- Can someone understand what a unit does without reading its internals? Can you change the internals without breaking consumers? If not, the boundaries need work.
- Smaller, well-bounded units are also easier for you to work with - you reason better about code you can hold in context at once, and your edits are more reliable when files are focused. When a file grows large, that's often a signal that it's doing too much.

**Working in existing codebases:**

- Explore the current structure before proposing changes. Follow existing patterns.
- Where existing code has problems that affect the work (e.g., a file that's grown too large, unclear boundaries, tangled responsibilities), include targeted improvements as part of the design - the way a good developer improves code they're working in.
- Don't propose unrelated refactoring. Stay focused on what serves the current goal.

## After the Design

**Documentation:**

- Write the validated design to the path requested by the user.
- Otherwise, follow the repository's existing spec location and naming convention.
- If no convention exists, save it to `docs/specs/YYYY-MM-DD-<topic>.md`.
- Maintain one spec file and mark it as `draft` using the repository's convention. If no convention exists, use YAML frontmatter with `status: draft`.
- Do not commit the spec.

**Spec Self-Review:**
After writing the spec document, look at it with fresh eyes:

1. **Placeholder scan:** Any "TBD", "TODO", incomplete sections, or vague requirements? Fix them.
2. **Internal consistency:** Do any sections contradict each other? Does the architecture match the feature descriptions?
3. **Scope check:** Is this focused enough for a single coherent spec, or does it need decomposition?
4. **Ambiguity check:** Could any requirement be interpreted two different ways? If so, pick one and make it explicit.

Fix any issues inline. No need to re-review — just fix and move on.

**Return Control:**
After the spec review loop passes, ask the user to review the written draft:

> "Draft spec written to `<path>`. Please review it and let me know if you want to make any changes."

Stop after asking for review. If the user later requests changes, update the same spec and re-run the self-review. Do not start implementation, commit the spec, or invoke another workflow unless the user explicitly requests that as a separate next step.

## Visual Aids

Use visuals only when they clarify a question. Honor the user's preferred medium; otherwise:

- If `visualize` is available and the client supports inline rendering, read and follow that skill.
- Otherwise follow [the browser companion guide](./visual-companion.md).

Confirm design decisions in the conversation and record them in the draft spec.
