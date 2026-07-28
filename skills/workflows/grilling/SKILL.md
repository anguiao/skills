---
name: grilling
description: Stress-test and refine a draft spec through rigorous one-at-a-time questioning before implementation.
---

Read the draft spec first, then examine it relentlessly for material ambiguities, assumptions, conflicts, trade-offs, and hidden consequences until we reach a shared understanding. Treat clear, internally consistent decisions already in the spec as settled unless that examination exposes a material issue. Follow each unresolved decision through its consequences one-by-one, and provide your recommended answer for every question.

Ask the questions one at a time, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.

If a *fact* can be found by exploring the environment (filesystem, tools, etc.), look it up rather than asking me. The unresolved material decisions are mine — put each one to me and wait for my answer. Do not ask me to reconfirm settled choices or decide pure implementation details.

Keep the same spec updated and in `draft` as decisions are resolved; do not implement, commit, or invoke another workflow. After resolving all material decisions, make a final consistency pass and ask me to approve the spec. On approval, update its status using the repository's convention, defaulting to `approved`, then stop.
